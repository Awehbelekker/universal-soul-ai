"""
Core Synchronization Engine
===========================

Main synchronization engine that orchestrates data sync across devices
while maintaining privacy-first, local-processing architecture.
"""

import asyncio
import hashlib
import json
import time
from typing import Dict, Any, List, Optional, Set
import logging
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from ..interfaces import UserContext
from ..exceptions import ThinkMeshException, ErrorCode
from ..logging import get_logger

logger = get_logger(__name__)


class SyncMethod(Enum):
    """Available synchronization methods"""
    LOCAL_NETWORK = "local_network"
    ENCRYPTED_CLOUD = "encrypted_cloud"
    MANUAL_TRANSFER = "manual_transfer"
    QR_CODE = "qr_code"


class SyncStatus(Enum):
    """Synchronization status"""
    IDLE = "idle"
    SYNCING = "syncing"
    CONFLICT = "conflict"
    ERROR = "error"
    COMPLETED = "completed"


class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    LATEST_WINS = "latest_wins"
    MANUAL_MERGE = "manual_merge"
    DEVICE_PRIORITY = "device_priority"
    USER_CHOICE = "user_choice"


@dataclass
class SyncItem:
    """Represents an item to be synchronized"""
    item_id: str
    item_type: str
    data: Dict[str, Any]
    timestamp: float
    device_id: str
    checksum: str
    version: int = 1


@dataclass
class SyncResult:
    """Result of synchronization operation"""
    success: bool
    items_synced: int
    conflicts_resolved: int
    errors: List[str]
    sync_time: float
    method_used: SyncMethod


@dataclass
class SyncConflict:
    """Represents a synchronization conflict"""
    item_id: str
    local_item: SyncItem
    remote_item: SyncItem
    conflict_type: str
    resolution_strategy: ConflictResolution


class SyncEngine:
    """Main synchronization engine"""
    
    def __init__(self, device_id: str, storage_path: str = "sync_data"):
        self.device_id = device_id
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.sync_status = SyncStatus.IDLE
        self.sync_methods = {}
        self.conflict_resolver = ConflictResolver()
        self.sync_history = []
        
        # Initialize sync methods
        self._initialize_sync_methods()

    def _initialize_sync_methods(self):
        """Initialize available synchronization methods"""
        try:
            from .local_sync import LocalNetworkSync
            self.sync_methods[SyncMethod.LOCAL_NETWORK] = LocalNetworkSync(self.device_id)
        except ImportError:
            logger.warning("LocalNetworkSync not available")

        try:
            from .encrypted_backup import EncryptedCloudBackup
            self.sync_methods[SyncMethod.ENCRYPTED_CLOUD] = EncryptedCloudBackup(self.device_id)
        except ImportError:
            logger.warning("EncryptedCloudBackup not available")
    
    async def sync_with_device(self, target_device_id: str, 
                              method: SyncMethod = SyncMethod.LOCAL_NETWORK,
                              user_context: Optional[UserContext] = None) -> SyncResult:
        """Synchronize data with another device"""
        
        start_time = time.time()
        self.sync_status = SyncStatus.SYNCING
        
        try:
            logger.info(f"Starting sync with device {target_device_id} using {method.value}")
            
            # Get local sync items
            local_items = await self._get_local_sync_items()
            
            # Get sync method handler
            sync_handler = self.sync_methods.get(method)
            if not sync_handler:
                raise ThinkMeshException(
                    f"Sync method {method.value} not available",
                    ErrorCode.SYNC_METHOD_UNAVAILABLE
                )
            
            # Perform synchronization
            remote_items = await sync_handler.get_remote_items(target_device_id)
            
            # Detect conflicts
            conflicts = await self._detect_conflicts(local_items, remote_items)
            
            # Resolve conflicts
            resolved_items = await self._resolve_conflicts(conflicts, user_context)
            
            # Apply synchronized data
            sync_result = await self._apply_sync_data(resolved_items, sync_handler, target_device_id)
            
            # Update sync history
            sync_time = time.time() - start_time
            sync_result.sync_time = sync_time
            sync_result.method_used = method
            
            self.sync_history.append({
                "timestamp": time.time(),
                "target_device": target_device_id,
                "method": method.value,
                "result": asdict(sync_result)
            })
            
            self.sync_status = SyncStatus.COMPLETED
            logger.info(f"Sync completed successfully in {sync_time:.2f}s")
            
            return sync_result
            
        except Exception as e:
            self.sync_status = SyncStatus.ERROR
            logger.error(f"Sync failed: {e}")
            
            return SyncResult(
                success=False,
                items_synced=0,
                conflicts_resolved=0,
                errors=[str(e)],
                sync_time=time.time() - start_time,
                method_used=method
            )
    
    async def _get_local_sync_items(self) -> List[SyncItem]:
        """Get all local items that need to be synchronized"""
        
        sync_items = []
        
        # Load sync items from storage
        sync_file = self.storage_path / "sync_items.json"
        if sync_file.exists():
            try:
                with open(sync_file, 'r') as f:
                    items_data = json.load(f)
                
                for item_data in items_data:
                    sync_item = SyncItem(**item_data)
                    sync_items.append(sync_item)
                    
            except Exception as e:
                logger.error(f"Failed to load sync items: {e}")
        
        return sync_items
    
    async def _detect_conflicts(self, local_items: List[SyncItem], 
                               remote_items: List[SyncItem]) -> List[SyncConflict]:
        """Detect conflicts between local and remote items"""
        
        conflicts = []
        
        # Create lookup dictionaries
        local_lookup = {item.item_id: item for item in local_items}
        remote_lookup = {item.item_id: item for item in remote_items}
        
        # Check for conflicts
        all_item_ids = set(local_lookup.keys()) | set(remote_lookup.keys())
        
        for item_id in all_item_ids:
            local_item = local_lookup.get(item_id)
            remote_item = remote_lookup.get(item_id)
            
            if local_item and remote_item:
                # Both exist - check for conflicts
                if local_item.checksum != remote_item.checksum:
                    conflict_type = self._determine_conflict_type(local_item, remote_item)
                    
                    conflict = SyncConflict(
                        item_id=item_id,
                        local_item=local_item,
                        remote_item=remote_item,
                        conflict_type=conflict_type,
                        resolution_strategy=ConflictResolution.LATEST_WINS  # Default
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def _determine_conflict_type(self, local_item: SyncItem, remote_item: SyncItem) -> str:
        """Determine the type of conflict between items"""
        
        if local_item.timestamp > remote_item.timestamp:
            return "local_newer"
        elif remote_item.timestamp > local_item.timestamp:
            return "remote_newer"
        else:
            return "simultaneous_edit"
    
    async def _resolve_conflicts(self, conflicts: List[SyncConflict],
                               user_context: Optional[UserContext]) -> List[SyncItem]:
        """Resolve synchronization conflicts"""
        
        resolved_items = []
        
        for conflict in conflicts:
            try:
                resolved_item = await self.conflict_resolver.resolve_conflict(
                    conflict, user_context
                )
                resolved_items.append(resolved_item)
                
            except Exception as e:
                logger.error(f"Failed to resolve conflict for {conflict.item_id}: {e}")
                # Use local item as fallback
                resolved_items.append(conflict.local_item)
        
        return resolved_items
    
    async def _apply_sync_data(self, resolved_items: List[SyncItem],
                              sync_handler, target_device_id: str) -> SyncResult:
        """Apply synchronized data to local storage"""
        
        items_synced = 0
        conflicts_resolved = len(resolved_items)
        errors = []
        
        try:
            # Save resolved items locally
            await self._save_sync_items(resolved_items)
            items_synced = len(resolved_items)
            
            # Send items to remote device
            await sync_handler.send_items(resolved_items, target_device_id)
            
            return SyncResult(
                success=True,
                items_synced=items_synced,
                conflicts_resolved=conflicts_resolved,
                errors=errors,
                sync_time=0.0,  # Will be set by caller
                method_used=SyncMethod.LOCAL_NETWORK  # Will be set by caller
            )
            
        except Exception as e:
            errors.append(str(e))
            return SyncResult(
                success=False,
                items_synced=items_synced,
                conflicts_resolved=conflicts_resolved,
                errors=errors,
                sync_time=0.0,
                method_used=SyncMethod.LOCAL_NETWORK
            )
    
    async def _save_sync_items(self, items: List[SyncItem]):
        """Save sync items to local storage"""
        
        sync_file = self.storage_path / "sync_items.json"
        
        try:
            items_data = [asdict(item) for item in items]
            
            with open(sync_file, 'w') as f:
                json.dump(items_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save sync items: {e}")
            raise
    
    async def add_sync_item(self, item_type: str, data: Dict[str, Any]) -> str:
        """Add an item to be synchronized"""
        
        # Generate unique item ID
        item_id = hashlib.sha256(
            f"{item_type}_{time.time()}_{self.device_id}".encode()
        ).hexdigest()[:16]
        
        # Calculate checksum
        data_str = json.dumps(data, sort_keys=True)
        checksum = hashlib.sha256(data_str.encode()).hexdigest()
        
        # Create sync item
        sync_item = SyncItem(
            item_id=item_id,
            item_type=item_type,
            data=data,
            timestamp=time.time(),
            device_id=self.device_id,
            checksum=checksum
        )
        
        # Load existing items
        existing_items = await self._get_local_sync_items()
        existing_items.append(sync_item)
        
        # Save updated items
        await self._save_sync_items(existing_items)
        
        logger.info(f"Added sync item {item_id} of type {item_type}")
        return item_id
    
    async def remove_sync_item(self, item_id: str) -> bool:
        """Remove an item from synchronization"""
        
        try:
            existing_items = await self._get_local_sync_items()
            updated_items = [item for item in existing_items if item.item_id != item_id]
            
            if len(updated_items) < len(existing_items):
                await self._save_sync_items(updated_items)
                logger.info(f"Removed sync item {item_id}")
                return True
            else:
                logger.warning(f"Sync item {item_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove sync item {item_id}: {e}")
            return False
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """Get current synchronization status"""
        
        local_items = await self._get_local_sync_items()
        
        return {
            "status": self.sync_status.value,
            "device_id": self.device_id,
            "local_items_count": len(local_items),
            "last_sync": self.sync_history[-1] if self.sync_history else None,
            "available_methods": [method.value for method in self.sync_methods.keys()]
        }


class ConflictResolver:
    """Handles conflict resolution during synchronization"""
    
    async def resolve_conflict(self, conflict: SyncConflict,
                              user_context: Optional[UserContext]) -> SyncItem:
        """Resolve a synchronization conflict"""
        
        if conflict.resolution_strategy == ConflictResolution.LATEST_WINS:
            return await self._resolve_latest_wins(conflict)
        elif conflict.resolution_strategy == ConflictResolution.MANUAL_MERGE:
            return await self._resolve_manual_merge(conflict, user_context)
        elif conflict.resolution_strategy == ConflictResolution.DEVICE_PRIORITY:
            return await self._resolve_device_priority(conflict, user_context)
        elif conflict.resolution_strategy == ConflictResolution.USER_CHOICE:
            return await self._resolve_user_choice(conflict, user_context)
        else:
            # Default to latest wins
            return await self._resolve_latest_wins(conflict)
    
    async def _resolve_latest_wins(self, conflict: SyncConflict) -> SyncItem:
        """Resolve conflict by choosing the item with latest timestamp"""
        
        if conflict.local_item.timestamp >= conflict.remote_item.timestamp:
            logger.info(f"Conflict resolved: local item wins for {conflict.item_id}")
            return conflict.local_item
        else:
            logger.info(f"Conflict resolved: remote item wins for {conflict.item_id}")
            return conflict.remote_item
    
    async def _resolve_manual_merge(self, conflict: SyncConflict,
                                   user_context: Optional[UserContext]) -> SyncItem:
        """Resolve conflict by manually merging data"""
        
        # This would involve sophisticated merging logic
        # For now, fall back to latest wins
        logger.warning(f"Manual merge not implemented, using latest wins for {conflict.item_id}")
        return await self._resolve_latest_wins(conflict)
    
    async def _resolve_device_priority(self, conflict: SyncConflict,
                                      user_context: Optional[UserContext]) -> SyncItem:
        """Resolve conflict based on device priority"""
        
        # Check if user context has device priority settings
        if user_context and hasattr(user_context, 'device_priorities'):
            local_priority = user_context.device_priorities.get(conflict.local_item.device_id, 0)
            remote_priority = user_context.device_priorities.get(conflict.remote_item.device_id, 0)
            
            if local_priority >= remote_priority:
                return conflict.local_item
            else:
                return conflict.remote_item
        
        # Fall back to latest wins
        return await self._resolve_latest_wins(conflict)
    
    async def _resolve_user_choice(self, conflict: SyncConflict,
                                  user_context: Optional[UserContext]) -> SyncItem:
        """Resolve conflict by asking user to choose"""
        
        # This would involve presenting options to the user
        # For now, fall back to latest wins
        logger.warning(f"User choice not implemented, using latest wins for {conflict.item_id}")
        return await self._resolve_latest_wins(conflict)


class DeviceSyncManager:
    """Manages synchronization across multiple devices"""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.sync_engine = SyncEngine(device_id)
        self.known_devices = {}
        self.sync_schedules = {}
        
    async def discover_devices(self, method: SyncMethod = SyncMethod.LOCAL_NETWORK) -> List[str]:
        """Discover available devices for synchronization"""
        
        try:
            sync_handler = self.sync_engine.sync_methods.get(method)
            if not sync_handler:
                return []
            
            if hasattr(sync_handler, 'discover_devices'):
                devices = await sync_handler.discover_devices()
                
                # Update known devices
                for device_id in devices:
                    self.known_devices[device_id] = {
                        "last_seen": time.time(),
                        "method": method.value
                    }
                
                return devices
            else:
                return []
                
        except Exception as e:
            logger.error(f"Device discovery failed: {e}")
            return []
    
    async def sync_with_all_devices(self, method: SyncMethod = SyncMethod.LOCAL_NETWORK) -> Dict[str, SyncResult]:
        """Synchronize with all known devices"""
        
        results = {}
        
        # Discover devices first
        available_devices = await self.discover_devices(method)
        
        # Sync with each device
        for device_id in available_devices:
            if device_id != self.device_id:  # Don't sync with self
                try:
                    result = await self.sync_engine.sync_with_device(device_id, method)
                    results[device_id] = result
                except Exception as e:
                    logger.error(f"Sync with {device_id} failed: {e}")
                    results[device_id] = SyncResult(
                        success=False,
                        items_synced=0,
                        conflicts_resolved=0,
                        errors=[str(e)],
                        sync_time=0.0,
                        method_used=method
                    )
        
        return results
    
    async def schedule_sync(self, device_id: str, interval_minutes: int,
                           method: SyncMethod = SyncMethod.LOCAL_NETWORK):
        """Schedule automatic synchronization with a device"""
        
        self.sync_schedules[device_id] = {
            "interval_minutes": interval_minutes,
            "method": method,
            "last_sync": 0,
            "enabled": True
        }
        
        logger.info(f"Scheduled sync with {device_id} every {interval_minutes} minutes")
    
    async def run_scheduled_syncs(self):
        """Run scheduled synchronizations"""
        
        current_time = time.time()
        
        for device_id, schedule in self.sync_schedules.items():
            if not schedule["enabled"]:
                continue
            
            interval_seconds = schedule["interval_minutes"] * 60
            time_since_last = current_time - schedule["last_sync"]
            
            if time_since_last >= interval_seconds:
                try:
                    logger.info(f"Running scheduled sync with {device_id}")
                    result = await self.sync_engine.sync_with_device(
                        device_id, schedule["method"]
                    )
                    
                    schedule["last_sync"] = current_time
                    
                    if result.success:
                        logger.info(f"Scheduled sync with {device_id} completed successfully")
                    else:
                        logger.warning(f"Scheduled sync with {device_id} failed: {result.errors}")
                        
                except Exception as e:
                    logger.error(f"Scheduled sync with {device_id} failed: {e}")
    
    async def get_sync_overview(self) -> Dict[str, Any]:
        """Get overview of synchronization status"""
        
        sync_status = await self.sync_engine.get_sync_status()
        
        return {
            "device_id": self.device_id,
            "sync_status": sync_status,
            "known_devices": len(self.known_devices),
            "scheduled_syncs": len(self.sync_schedules),
            "sync_history_count": len(self.sync_engine.sync_history)
        }
