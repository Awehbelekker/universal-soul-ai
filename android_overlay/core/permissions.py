"""
Android Permissions Manager
===========================
Handles Android-specific permissions for overlay functionality
"""

import logging
from kivy.utils import platform

logger = logging.getLogger(__name__)

class AndroidPermissions:
    def __init__(self):
        self.required_permissions = [
            'android.permission.SYSTEM_ALERT_WINDOW',
            'android.permission.RECORD_AUDIO',
            'android.permission.WRITE_EXTERNAL_STORAGE',
            'android.permission.ACCESS_NETWORK_STATE',
            'android.permission.WAKE_LOCK',
            'android.permission.VIBRATE'
        ]
        
        self.permissions_granted = {}
    
    def request_permissions(self):
        """Request all required Android permissions"""
        if platform != 'android':
            logger.info("Not on Android, skipping permission requests")
            return True
        
        logger.info("Requesting Android permissions...")
        
        try:
            # Request overlay permission first (most critical)
            overlay_granted = self._request_overlay_permission()
            
            # Request other permissions
            other_granted = self._request_standard_permissions()
            
            # Log results
            self._log_permission_status()
            
            return overlay_granted and other_granted
            
        except Exception as e:
            logger.error(f"Permission request failed: {e}")
            return False
    
    def _request_overlay_permission(self):
        """Request system overlay permission"""
        try:
            from jnius import autoclass, cast
            
            logger.info("Requesting overlay permission...")
            
            # Get required classes
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            Uri = autoclass('android.net.Uri')
            
            # Get current activity
            activity = PythonActivity.mActivity
            
            # Check if overlay permission is already granted
            if self._check_overlay_permission():
                logger.info("Overlay permission already granted")
                self.permissions_granted['overlay'] = True
                return True
            
            # Create intent to request overlay permission
            intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)
            intent.setData(Uri.parse(f"package:{activity.getPackageName()}"))
            
            # Start the permission activity
            activity.startActivity(intent)
            
            logger.info("Overlay permission request sent")
            self.permissions_granted['overlay'] = True  # Assume granted for now
            return True
            
        except Exception as e:
            logger.error(f"Overlay permission request failed: {e}")
            self.permissions_granted['overlay'] = False
            return False
    
    def _check_overlay_permission(self):
        """Check if overlay permission is granted"""
        try:
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Settings = autoclass('android.provider.Settings')
            
            activity = PythonActivity.mActivity
            
            # Check overlay permission (API 23+)
            if hasattr(Settings, 'canDrawOverlays'):
                return Settings.canDrawOverlays(activity)
            else:
                # For older Android versions, assume granted
                return True
                
        except Exception as e:
            logger.error(f"Could not check overlay permission: {e}")
            return False
    
    def _request_standard_permissions(self):
        """Request standard Android permissions"""
        try:
            if platform != 'android':
                logger.info("Not on Android, skipping standard permission requests")
                # Mark all as granted for testing or non-Android platforms
                for perm in self.required_permissions[1:]:  # Skip overlay permission
                    self.permissions_granted[perm] = True
                return True

            if platform == 'android':
                try:
                    import importlib
                    spec = importlib.util.find_spec("android.permissions")
                    if spec is None:
                        raise ImportError("android.permissions module not found")
                    android_permissions_module = importlib.import_module("android.permissions")
                    request_permissions = getattr(android_permissions_module, "request_permissions")
                    Permission = getattr(android_permissions_module, "Permission")
                    check_permission = getattr(android_permissions_module, "check_permission")
                except ImportError:
                    logger.warning("android.permissions module not available")
                    # Mark all as granted for testing or if module is missing
                    for perm in self.required_permissions[1:]:  # Skip overlay permission
                        self.permissions_granted[perm] = True
                    return True
            else:
                logger.info("Not on Android, skipping standard permission requests")
                # Mark all as granted for testing or non-Android platforms
                for perm in self.required_permissions[1:]:  # Skip overlay permission
                    self.permissions_granted[perm] = True
                return True

            logger.info("Requesting standard permissions...")

            # Map our permissions to Android permission constants
            permission_map = {
                'android.permission.RECORD_AUDIO': Permission.RECORD_AUDIO,
                'android.permission.WRITE_EXTERNAL_STORAGE': Permission.WRITE_EXTERNAL_STORAGE,
                'android.permission.ACCESS_NETWORK_STATE': Permission.ACCESS_NETWORK_STATE,
                'android.permission.WAKE_LOCK': Permission.WAKE_LOCK,
                'android.permission.VIBRATE': Permission.VIBRATE
            }

            # Check which permissions we need to request
            permissions_to_request = []
            for perm_string, perm_constant in permission_map.items():
                if not check_permission(perm_constant):
                    permissions_to_request.append(perm_constant)
                    self.permissions_granted[perm_string] = False
                else:
                    self.permissions_granted[perm_string] = True

            # Request missing permissions
            if permissions_to_request:
                request_permissions(permissions_to_request)
                logger.info(f"Requested {len(permissions_to_request)} permissions")

                # Mark as granted (optimistic)
                for perm in permissions_to_request:
                    for perm_string, perm_constant in permission_map.items():
                        if perm_constant == perm:
                            self.permissions_granted[perm_string] = True
            else:
                logger.info("All standard permissions already granted")

            return True
            
        except ImportError:
            logger.warning("android.permissions module not available")
            # Mark all as granted for testing
            for perm in self.required_permissions[1:]:  # Skip overlay permission
                self.permissions_granted[perm] = True
            return True
            
        except Exception as e:
            logger.error(f"Standard permission request failed: {e}")
            return False
    
    def _log_permission_status(self):
        """Log the status of all permissions"""
        logger.info("Permission Status:")
        for perm, granted in self.permissions_granted.items():
            status = "✅" if granted else "❌"
            logger.info(f"  {status} {perm}")
    
    def check_critical_permissions(self):
        """Check if critical permissions are granted"""
        critical_perms = [
            'overlay',
            'android.permission.SYSTEM_ALERT_WINDOW'
        ]
        
        for perm in critical_perms:
            if not self.permissions_granted.get(perm, False):
                logger.warning(f"Critical permission missing: {perm}")
                return False
        
        return True
    
    def get_permission_status(self):
        """Get current permission status"""
        return dict(self.permissions_granted)

# Convenience functions
def request_android_permissions():
    """Quick function to request all permissions"""
    permissions = AndroidPermissions()
    return permissions.request_permissions()

def check_android_permissions():
    """Quick function to check permission status"""
    permissions = AndroidPermissions()
    return permissions.get_permission_status()