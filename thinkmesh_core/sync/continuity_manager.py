"""
Continuity Manager
=================

Manages seamless continuity across devices, allowing users to start
a conversation on one device and continue on another without losing context.
"""

import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
from enum import Enum

from ..interfaces import UserContext
from ..exceptions import ThinkMeshException, ErrorCode
from ..logging import get_logger

logger = get_logger(__name__)


class SessionState(Enum):
    """Session states"""
    ACTIVE = "active"
    PAUSED = "paused"
    TRANSFERRED = "transferred"
    EXPIRED = "expired"


@dataclass
class DeviceContext:
    """Context information for a device"""
    device_id: str
    device_type: str
    device_name: str
    capabilities: List[str]
    last_active: float
    battery_level: float
    network_quality: str
    location: Optional[str] = None


@dataclass
class SessionTransfer:
    """Represents a session transfer between devices"""
    transfer_id: str
    source_device: str
    target_device: str
    session_data: Dict[str, Any]
    transfer_time: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class ContinuitySession:
    """Represents a continuity session"""
    session_id: str
    user_id: str
    conversation_context: Dict[str, Any]
    device_contexts: Dict[str, DeviceContext]
    current_device: str
    state: SessionState
    created_time: float
    last_updated: float
    expires_at: float


class ContinuityManager:
    """Manages cross-device continuity and session transfers"""
    
    def __init__(self, device_id: str, user_id: str):
        self.device_id = device_id
        self.user_id = user_id
        
        self.context_synchronizer = ContextSynchronizer(device_id)
        self.session_manager = SessionManager(device_id, user_id)
        self.transfer_handler = TransferHandler(device_id)
        
        self.active_sessions = {}
        self.device_contexts = {}
        
    async def start_session(self, conversation_context: Dict[str, Any],
                           device_context: DeviceContext) -> str:
        """Start a new continuity session"""
        
        try:
            session_id = str(uuid.uuid4())
            current_time = time.time()
            
            # Create session
            session = ContinuitySession(
                session_id=session_id,
                user_id=self.user_id,
                conversation_context=conversation_context,
                device_contexts={self.device_id: device_context},
                current_device=self.device_id,
                state=SessionState.ACTIVE,
                created_time=current_time,
                last_updated=current_time,
                expires_at=current_time + 3600  # 1 hour default
            )
            
            # Store session
            self.active_sessions[session_id] = session
            
            # Sync session to other devices
            await self.context_synchronizer.sync_session(session)
            
            logger.info(f"Started continuity session {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            raise ThinkMeshException(
                f"Session start failed: {e}",
                ErrorCode.SESSION_START_FAILED
            )
    
    async def transfer_session(self, session_id: str, target_device_id: str,
                              user_context: UserContext) -> SessionTransfer:
        """Transfer session to another device"""
        
        start_time = time.time()
        transfer_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Transferring session {session_id} to device {target_device_id}")
            
            # Get session
            session = self.active_sessions.get(session_id)
            if not session:
                raise ThinkMeshException(
                    f"Session {session_id} not found",
                    ErrorCode.SESSION_NOT_FOUND
                )
            
            # Check if target device is available
            target_context = await self._get_device_context(target_device_id)
            if not target_context:
                raise ThinkMeshException(
                    f"Target device {target_device_id} not available",
                    ErrorCode.DEVICE_NOT_AVAILABLE
                )
            
            # Prepare transfer data
            transfer_data = await self._prepare_transfer_data(session, user_context)
            
            # Execute transfer
            transfer_result = await self.transfer_handler.execute_transfer(
                transfer_data, target_device_id
            )
            
            if transfer_result.success:
                # Update session state
                session.current_device = target_device_id
                session.state = SessionState.TRANSFERRED
                session.last_updated = time.time()
                
                # Add target device context
                session.device_contexts[target_device_id] = target_context
                
                # Sync updated session
                await self.context_synchronizer.sync_session(session)
                
                logger.info(f"Session {session_id} transferred successfully")
                
                return SessionTransfer(
                    transfer_id=transfer_id,
                    source_device=self.device_id,
                    target_device=target_device_id,
                    session_data=transfer_data,
                    transfer_time=time.time() - start_time,
                    success=True
                )
            else:
                raise ThinkMeshException(
                    f"Transfer execution failed: {transfer_result.error}",
                    ErrorCode.TRANSFER_EXECUTION_FAILED
                )
                
        except Exception as e:
            logger.error(f"Session transfer failed: {e}")
            
            return SessionTransfer(
                transfer_id=transfer_id,
                source_device=self.device_id,
                target_device=target_device_id,
                session_data={},
                transfer_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    async def receive_session(self, transfer_data: Dict[str, Any],
                             source_device_id: str) -> bool:
        """Receive transferred session from another device"""
        
        try:
            logger.info(f"Receiving session transfer from device {source_device_id}")
            
            # Extract session data
            session_data = transfer_data.get("session")
            if not session_data:
                raise ThinkMeshException(
                    "Invalid transfer data: missing session",
                    ErrorCode.INVALID_TRANSFER_DATA
                )
            
            # Reconstruct session
            session = ContinuitySession(**session_data)
            
            # Update for current device
            session.current_device = self.device_id
            session.state = SessionState.ACTIVE
            session.last_updated = time.time()
            
            # Store session
            self.active_sessions[session.session_id] = session
            
            # Restore conversation context
            await self._restore_conversation_context(session.conversation_context)
            
            logger.info(f"Session {session.session_id} received and activated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to receive session: {e}")
            return False
    
    async def pause_session(self, session_id: str) -> bool:
        """Pause a session for later resumption"""
        
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            session.state = SessionState.PAUSED
            session.last_updated = time.time()
            
            # Sync paused session
            await self.context_synchronizer.sync_session(session)
            
            logger.info(f"Session {session_id} paused")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause session {session_id}: {e}")
            return False
    
    async def resume_session(self, session_id: str) -> bool:
        """Resume a paused session"""
        
        try:
            session = self.active_sessions.get(session_id)
            if not session or session.state != SessionState.PAUSED:
                return False
            
            session.state = SessionState.ACTIVE
            session.current_device = self.device_id
            session.last_updated = time.time()
            
            # Restore conversation context
            await self._restore_conversation_context(session.conversation_context)
            
            # Sync resumed session
            await self.context_synchronizer.sync_session(session)
            
            logger.info(f"Session {session_id} resumed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume session {session_id}: {e}")
            return False
    
    async def end_session(self, session_id: str) -> bool:
        """End a continuity session"""
        
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            session.state = SessionState.EXPIRED
            session.last_updated = time.time()
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            # Sync session end
            await self.context_synchronizer.sync_session_end(session)
            
            logger.info(f"Session {session_id} ended")
            return True
            
        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")
            return False
    
    async def get_available_devices(self) -> List[DeviceContext]:
        """Get list of available devices for transfer"""
        
        try:
            # Discover devices through sync engine
            from .sync_engine import DeviceSyncManager
            sync_manager = DeviceSyncManager(self.device_id)
            
            device_ids = await sync_manager.discover_devices()
            
            # Get device contexts
            available_devices = []
            for device_id in device_ids:
                context = await self._get_device_context(device_id)
                if context:
                    available_devices.append(context)
            
            return available_devices
            
        except Exception as e:
            logger.error(f"Failed to get available devices: {e}")
            return []
    
    async def _prepare_transfer_data(self, session: ContinuitySession,
                                   user_context: UserContext) -> Dict[str, Any]:
        """Prepare data for session transfer"""
        
        transfer_data = {
            "session": asdict(session),
            "user_context": {
                "user_id": user_context.user_id,
                "preferences": user_context.preferences,
                "conversation_history": getattr(user_context, 'conversation_history', [])
            },
            "device_state": {
                "device_id": self.device_id,
                "timestamp": time.time(),
                "active_tasks": []  # Would include current tasks
            }
        }
        
        return transfer_data
    
    async def _restore_conversation_context(self, context: Dict[str, Any]):
        """Restore conversation context on current device"""
        
        try:
            # This would integrate with the conversation system
            # to restore the conversation state
            logger.info("Restoring conversation context")
            
            # Placeholder implementation
            # In practice, this would:
            # 1. Restore conversation history
            # 2. Restore active tasks
            # 3. Restore user preferences
            # 4. Restore AI state
            
        except Exception as e:
            logger.error(f"Failed to restore conversation context: {e}")
    
    async def _get_device_context(self, device_id: str) -> Optional[DeviceContext]:
        """Get context information for a device"""
        
        try:
            # Check cached contexts
            if device_id in self.device_contexts:
                context = self.device_contexts[device_id]
                # Check if context is recent (within 5 minutes)
                if time.time() - context.last_active < 300:
                    return context
            
            # Request fresh context from device
            context = await self._request_device_context(device_id)
            
            if context:
                self.device_contexts[device_id] = context
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get device context for {device_id}: {e}")
            return None
    
    async def _request_device_context(self, device_id: str) -> Optional[DeviceContext]:
        """Request device context from remote device"""
        
        try:
            # This would use the sync system to request device context
            # For now, return a placeholder
            
            return DeviceContext(
                device_id=device_id,
                device_type="unknown",
                device_name=f"Device-{device_id[:8]}",
                capabilities=["sync", "automation"],
                last_active=time.time(),
                battery_level=0.8,
                network_quality="good"
            )
            
        except Exception as e:
            logger.error(f"Failed to request device context from {device_id}: {e}")
            return None


class ContextSynchronizer:
    """Synchronizes context data across devices"""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
    
    async def sync_session(self, session: ContinuitySession):
        """Synchronize session data across devices"""
        
        try:
            # Add session to sync items
            from .sync_engine import SyncEngine
            sync_engine = SyncEngine(self.device_id)
            
            await sync_engine.add_sync_item(
                item_type="continuity_session",
                data=asdict(session)
            )
            
            logger.debug(f"Session {session.session_id} synced")
            
        except Exception as e:
            logger.error(f"Failed to sync session: {e}")
    
    async def sync_session_end(self, session: ContinuitySession):
        """Sync session end across devices"""
        
        try:
            # Mark session as ended in sync
            from .sync_engine import SyncEngine
            sync_engine = SyncEngine(self.device_id)
            
            await sync_engine.add_sync_item(
                item_type="session_end",
                data={
                    "session_id": session.session_id,
                    "end_time": time.time(),
                    "final_device": self.device_id
                }
            )
            
            logger.debug(f"Session end {session.session_id} synced")
            
        except Exception as e:
            logger.error(f"Failed to sync session end: {e}")


class SessionManager:
    """Manages session lifecycle and storage"""
    
    def __init__(self, device_id: str, user_id: str):
        self.device_id = device_id
        self.user_id = user_id
        self.session_timeout = 3600  # 1 hour
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        
        try:
            current_time = time.time()
            
            # This would clean up expired sessions from storage
            logger.debug("Cleaning up expired sessions")
            
        except Exception as e:
            logger.error(f"Session cleanup failed: {e}")


class TransferHandler:
    """Handles the actual transfer of sessions between devices"""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
    
    async def execute_transfer(self, transfer_data: Dict[str, Any],
                              target_device_id: str) -> 'TransferResult':
        """Execute session transfer to target device"""
        
        try:
            # Use sync system to send transfer data
            from .sync_engine import SyncEngine
            sync_engine = SyncEngine(self.device_id)
            
            # Add transfer as sync item
            await sync_engine.add_sync_item(
                item_type="session_transfer",
                data={
                    "target_device": target_device_id,
                    "transfer_data": transfer_data,
                    "transfer_time": time.time()
                }
            )
            
            # Sync with target device
            result = await sync_engine.sync_with_device(target_device_id)
            
            return TransferResult(
                success=result.success,
                error=None if result.success else "Sync failed"
            )
            
        except Exception as e:
            return TransferResult(
                success=False,
                error=str(e)
            )


@dataclass
class TransferResult:
    """Result of transfer execution"""
    success: bool
    error: Optional[str] = None
