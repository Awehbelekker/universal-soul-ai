"""
Cross-Platform Synchronization System
====================================

Privacy-first synchronization system for Universal Soul AI.
Enables seamless continuity across devices while maintaining
complete data sovereignty and local-first architecture.
"""

from .sync_engine import (
    SyncEngine,
    SyncResult,
    SyncConflictResolution,
    DeviceSyncManager
)

from .local_sync import (
    LocalNetworkSync,
    PeerDiscovery,
    SecureLocalTransfer
)

from .encrypted_backup import (
    EncryptedCloudBackup,
    BackupProvider,
    BackupResult,
    RestoreResult
)

from .continuity_manager import (
    ContinuityManager,
    DeviceContext,
    SessionTransfer,
    ContextSynchronizer
)

__all__ = [
    # Core sync engine
    'SyncEngine',
    'SyncResult', 
    'SyncConflictResolution',
    'DeviceSyncManager',
    
    # Local network sync
    'LocalNetworkSync',
    'PeerDiscovery',
    'SecureLocalTransfer',
    
    # Encrypted backup
    'EncryptedCloudBackup',
    'BackupProvider',
    'BackupResult',
    'RestoreResult',
    
    # Continuity management
    'ContinuityManager',
    'DeviceContext',
    'SessionTransfer',
    'ContextSynchronizer'
]

__version__ = "1.0.0"
__author__ = "ThinkMesh AI Team"
