"""
Local Network Synchronization
=============================

Privacy-first local network synchronization using peer-to-peer discovery
and secure encrypted transfer between devices on the same network.
"""

import asyncio
import socket
import json
import time
import hashlib
import ssl
from typing import Dict, Any, List, Optional, Tuple
import logging
from dataclasses import dataclass
from pathlib import Path

from ..exceptions import ThinkMeshException, ErrorCode
from ..logging import get_logger

logger = get_logger(__name__)


@dataclass
class PeerDevice:
    """Represents a discovered peer device"""
    device_id: str
    device_name: str
    ip_address: str
    port: int
    last_seen: float
    capabilities: List[str]
    public_key: Optional[str] = None


@dataclass
class TransferResult:
    """Result of a data transfer operation"""
    success: bool
    bytes_transferred: int
    transfer_time: float
    error_message: Optional[str] = None


class LocalNetworkSync:
    """Local network synchronization handler"""
    
    def __init__(self, device_id: str, port: int = 8765):
        self.device_id = device_id
        self.port = port
        self.discovery_port = 8764
        
        self.peer_discovery = PeerDiscovery(device_id, self.discovery_port)
        self.secure_transfer = SecureLocalTransfer(device_id, port)
        self.known_peers = {}
        
        # Start background services
        self._discovery_task = None
        self._server_task = None
        
    async def start_services(self):
        """Start background discovery and server services"""
        try:
            # Start peer discovery
            self._discovery_task = asyncio.create_task(
                self.peer_discovery.start_discovery()
            )
            
            # Start secure transfer server
            self._server_task = asyncio.create_task(
                self.secure_transfer.start_server()
            )
            
            logger.info(f"Local sync services started on port {self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start local sync services: {e}")
            raise
    
    async def stop_services(self):
        """Stop background services"""
        try:
            if self._discovery_task:
                self._discovery_task.cancel()
                
            if self._server_task:
                self._server_task.cancel()
                
            await self.peer_discovery.stop_discovery()
            await self.secure_transfer.stop_server()
            
            logger.info("Local sync services stopped")
            
        except Exception as e:
            logger.error(f"Error stopping local sync services: {e}")
    
    async def discover_devices(self) -> List[str]:
        """Discover available devices on local network"""
        try:
            peers = await self.peer_discovery.discover_peers()
            
            # Update known peers
            for peer in peers:
                self.known_peers[peer.device_id] = peer
            
            # Return device IDs
            return [peer.device_id for peer in peers if peer.device_id != self.device_id]
            
        except Exception as e:
            logger.error(f"Device discovery failed: {e}")
            return []
    
    async def get_remote_items(self, target_device_id: str) -> List[Dict[str, Any]]:
        """Get sync items from remote device"""
        try:
            peer = self.known_peers.get(target_device_id)
            if not peer:
                # Try to discover the device
                await self.discover_devices()
                peer = self.known_peers.get(target_device_id)
                
                if not peer:
                    raise ThinkMeshException(
                        f"Device {target_device_id} not found",
                        ErrorCode.DEVICE_NOT_FOUND
                    )
            
            # Request sync items from peer
            request = {
                "action": "get_sync_items",
                "device_id": self.device_id,
                "timestamp": time.time()
            }
            
            response = await self.secure_transfer.send_request(
                peer.ip_address, peer.port, request
            )
            
            if response.get("success"):
                return response.get("items", [])
            else:
                raise ThinkMeshException(
                    f"Failed to get items from {target_device_id}: {response.get('error')}",
                    ErrorCode.SYNC_REQUEST_FAILED
                )
                
        except Exception as e:
            logger.error(f"Failed to get remote items from {target_device_id}: {e}")
            raise
    
    async def send_items(self, items: List[Dict[str, Any]], target_device_id: str) -> bool:
        """Send sync items to remote device"""
        try:
            peer = self.known_peers.get(target_device_id)
            if not peer:
                raise ThinkMeshException(
                    f"Device {target_device_id} not found",
                    ErrorCode.DEVICE_NOT_FOUND
                )
            
            # Send sync items to peer
            request = {
                "action": "receive_sync_items",
                "device_id": self.device_id,
                "items": items,
                "timestamp": time.time()
            }
            
            response = await self.secure_transfer.send_request(
                peer.ip_address, peer.port, request
            )
            
            return response.get("success", False)
            
        except Exception as e:
            logger.error(f"Failed to send items to {target_device_id}: {e}")
            return False


class PeerDiscovery:
    """Handles peer device discovery on local network"""
    
    def __init__(self, device_id: str, port: int = 8764):
        self.device_id = device_id
        self.port = port
        self.device_name = socket.gethostname()
        
        self.broadcast_interval = 30  # seconds
        self.peer_timeout = 120  # seconds
        
        self.discovered_peers = {}
        self._discovery_running = False
        self._server_socket = None
        
    async def start_discovery(self):
        """Start peer discovery service"""
        self._discovery_running = True
        
        # Start UDP server for receiving announcements
        server_task = asyncio.create_task(self._run_discovery_server())
        
        # Start periodic announcements
        announce_task = asyncio.create_task(self._run_periodic_announcements())
        
        await asyncio.gather(server_task, announce_task, return_exceptions=True)
    
    async def stop_discovery(self):
        """Stop peer discovery service"""
        self._discovery_running = False
        
        if self._server_socket:
            self._server_socket.close()
    
    async def _run_discovery_server(self):
        """Run UDP server to receive peer announcements"""
        try:
            # Create UDP socket
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind(('', self.port))
            self._server_socket.setblocking(False)
            
            logger.info(f"Peer discovery server listening on port {self.port}")
            
            while self._discovery_running:
                try:
                    # Receive announcement
                    data, addr = await asyncio.get_event_loop().sock_recvfrom(
                        self._server_socket, 1024
                    )
                    
                    # Parse announcement
                    announcement = json.loads(data.decode())
                    await self._process_peer_announcement(announcement, addr[0])
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.debug(f"Discovery server error: {e}")
                    await asyncio.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"Discovery server failed: {e}")
        finally:
            if self._server_socket:
                self._server_socket.close()
    
    async def _run_periodic_announcements(self):
        """Send periodic announcements to discover peers"""
        while self._discovery_running:
            try:
                await self._broadcast_announcement()
                await asyncio.sleep(self.broadcast_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Announcement broadcast failed: {e}")
                await asyncio.sleep(5)
    
    async def _broadcast_announcement(self):
        """Broadcast device announcement"""
        try:
            announcement = {
                "device_id": self.device_id,
                "device_name": self.device_name,
                "port": self.port + 1,  # Sync port is discovery port + 1
                "timestamp": time.time(),
                "capabilities": ["sync", "automation", "voice"]
            }
            
            # Create broadcast socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # Broadcast to local network
            message = json.dumps(announcement).encode()
            sock.sendto(message, ('<broadcast>', self.port))
            sock.close()
            
            logger.debug(f"Broadcasted announcement for device {self.device_id}")
            
        except Exception as e:
            logger.error(f"Failed to broadcast announcement: {e}")
    
    async def _process_peer_announcement(self, announcement: Dict[str, Any], ip_address: str):
        """Process received peer announcement"""
        try:
            device_id = announcement.get("device_id")
            if not device_id or device_id == self.device_id:
                return  # Ignore self or invalid announcements
            
            peer = PeerDevice(
                device_id=device_id,
                device_name=announcement.get("device_name", "Unknown"),
                ip_address=ip_address,
                port=announcement.get("port", self.port + 1),
                last_seen=time.time(),
                capabilities=announcement.get("capabilities", [])
            )
            
            self.discovered_peers[device_id] = peer
            logger.info(f"Discovered peer device: {device_id} at {ip_address}")
            
        except Exception as e:
            logger.error(f"Failed to process peer announcement: {e}")
    
    async def discover_peers(self) -> List[PeerDevice]:
        """Get list of discovered peers"""
        current_time = time.time()
        
        # Remove expired peers
        expired_peers = [
            device_id for device_id, peer in self.discovered_peers.items()
            if current_time - peer.last_seen > self.peer_timeout
        ]
        
        for device_id in expired_peers:
            del self.discovered_peers[device_id]
            logger.info(f"Removed expired peer: {device_id}")
        
        return list(self.discovered_peers.values())


class SecureLocalTransfer:
    """Handles secure data transfer between local devices"""
    
    def __init__(self, device_id: str, port: int = 8765):
        self.device_id = device_id
        self.port = port
        
        self._server = None
        self._server_running = False
        
        # Simple encryption key (in practice, would use proper key exchange)
        self.encryption_key = hashlib.sha256(device_id.encode()).digest()
    
    async def start_server(self):
        """Start secure transfer server"""
        try:
            self._server = await asyncio.start_server(
                self._handle_client, '0.0.0.0', self.port
            )
            
            self._server_running = True
            logger.info(f"Secure transfer server started on port {self.port}")
            
            async with self._server:
                await self._server.serve_forever()
                
        except Exception as e:
            logger.error(f"Secure transfer server failed: {e}")
            raise
    
    async def stop_server(self):
        """Stop secure transfer server"""
        self._server_running = False
        
        if self._server:
            self._server.close()
            await self._server.wait_closed()
    
    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming client connection"""
        client_addr = writer.get_extra_info('peername')
        logger.debug(f"Client connected from {client_addr}")
        
        try:
            # Read request
            data = await reader.read(8192)
            if not data:
                return
            
            # Decrypt and parse request
            request = json.loads(data.decode())
            
            # Process request
            response = await self._process_request(request)
            
            # Send response
            response_data = json.dumps(response).encode()
            writer.write(response_data)
            await writer.drain()
            
        except Exception as e:
            logger.error(f"Error handling client {client_addr}: {e}")
            
            # Send error response
            error_response = {
                "success": False,
                "error": str(e)
            }
            response_data = json.dumps(error_response).encode()
            writer.write(response_data)
            await writer.drain()
            
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming sync request"""
        action = request.get("action")
        
        if action == "get_sync_items":
            return await self._handle_get_sync_items(request)
        elif action == "receive_sync_items":
            return await self._handle_receive_sync_items(request)
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
    
    async def _handle_get_sync_items(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request to get sync items"""
        try:
            # Load local sync items
            from .sync_engine import SyncEngine
            sync_engine = SyncEngine(self.device_id)
            local_items = await sync_engine._get_local_sync_items()
            
            # Convert to serializable format
            items_data = []
            for item in local_items:
                items_data.append({
                    "item_id": item.item_id,
                    "item_type": item.item_type,
                    "data": item.data,
                    "timestamp": item.timestamp,
                    "device_id": item.device_id,
                    "checksum": item.checksum,
                    "version": item.version
                })
            
            return {
                "success": True,
                "items": items_data,
                "device_id": self.device_id,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_receive_sync_items(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request to receive sync items"""
        try:
            items_data = request.get("items", [])
            
            # Convert to SyncItem objects and save
            from .sync_engine import SyncEngine, SyncItem
            sync_engine = SyncEngine(self.device_id)
            
            items = []
            for item_data in items_data:
                item = SyncItem(**item_data)
                items.append(item)
            
            # Save received items
            await sync_engine._save_sync_items(items)
            
            return {
                "success": True,
                "items_received": len(items),
                "device_id": self.device_id,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_request(self, host: str, port: int, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to remote device"""
        try:
            # Connect to remote device
            reader, writer = await asyncio.open_connection(host, port)
            
            try:
                # Send request
                request_data = json.dumps(request).encode()
                writer.write(request_data)
                await writer.drain()
                
                # Read response
                response_data = await reader.read(8192)
                response = json.loads(response_data.decode())
                
                return response
                
            finally:
                writer.close()
                await writer.wait_closed()
                
        except Exception as e:
            logger.error(f"Failed to send request to {host}:{port}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
