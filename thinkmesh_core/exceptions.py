"""
ThinkMesh Exception Hierarchy
============================

Comprehensive exception system with specific error codes,
user-friendly messages, and debugging information.
"""

from typing import Dict, Any, Optional
from enum import Enum


class ErrorCode(Enum):
    """ThinkMesh error codes for categorization and handling"""
    
    # General system errors (1000-1099)
    SYSTEM_INITIALIZATION_FAILED = 1001
    CONFIGURATION_ERROR = 1002
    DEPENDENCY_INJECTION_ERROR = 1003
    COMPONENT_NOT_FOUND = 1004
    INVALID_OPERATION = 1005
    
    # HRM Engine errors (1100-1199)
    HRM_MODEL_LOAD_FAILED = 1101
    HRM_INFERENCE_FAILED = 1102
    HRM_CONTEXT_OVERFLOW = 1103
    HRM_QUANTIZATION_ERROR = 1104
    HRM_MEMORY_INSUFFICIENT = 1105
    
    # Multi-Agent errors (1200-1299)
    AGENT_CREATION_FAILED = 1201
    AGENT_EXECUTION_TIMEOUT = 1202
    AGENT_COMMUNICATION_ERROR = 1203
    CONTEXT_STORE_FULL = 1204
    ORCHESTRATOR_OVERLOAD = 1205
    
    # Voice Interface errors (1300-1399)
    VOICE_STT_FAILED = 1301
    VOICE_TTS_FAILED = 1302
    VOICE_VAD_ERROR = 1303
    AUDIO_DEVICE_ERROR = 1304
    VOICE_SESSION_EXPIRED = 1305
    
    # Local AI errors (1400-1499)
    LOCAL_AI_SERVER_DOWN = 1401
    MODEL_DOWNLOAD_FAILED = 1402
    MODEL_INCOMPATIBLE = 1403
    INFERENCE_QUEUE_FULL = 1404
    GPU_ACCELERATION_FAILED = 1405
    
    # Data Management errors (1500-1599)
    DATA_ENCRYPTION_FAILED = 1501
    DATA_CORRUPTION_DETECTED = 1502
    STORAGE_QUOTA_EXCEEDED = 1503
    SEARCH_INDEX_ERROR = 1504
    BACKUP_FAILED = 1505
    
    # Mobile Optimization errors (1600-1699)
    BATTERY_CRITICALLY_LOW = 1601
    THERMAL_THROTTLING_ACTIVE = 1602
    MEMORY_PRESSURE_HIGH = 1603
    NETWORK_UNAVAILABLE = 1604
    DEVICE_INCOMPATIBLE = 1605
    
    # Security errors (1700-1799)
    ENCRYPTION_KEY_MISSING = 1701
    PERMISSION_DENIED = 1702
    AUTHENTICATION_FAILED = 1703
    DATA_INTEGRITY_VIOLATION = 1704
    PRIVACY_POLICY_VIOLATION = 1705


class ThinkMeshException(Exception):
    """Base exception class for all ThinkMesh errors"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        recovery_suggestions: Optional[list] = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
        self.user_message = user_message or self._generate_user_message()
        self.recovery_suggestions = recovery_suggestions or []
        
    def _generate_user_message(self) -> str:
        """Generate user-friendly error message"""
        user_messages = {
            ErrorCode.SYSTEM_INITIALIZATION_FAILED: 
                "ThinkMesh is having trouble starting up. Please restart the app.",
            ErrorCode.HRM_MODEL_LOAD_FAILED:
                "The AI brain couldn't load properly. Please check your device storage.",
            ErrorCode.VOICE_STT_FAILED:
                "I couldn't understand what you said. Please try speaking again.",
            ErrorCode.BATTERY_CRITICALLY_LOW:
                "Your battery is very low. ThinkMesh will reduce functionality to save power.",
            ErrorCode.NETWORK_UNAVAILABLE:
                "No internet connection detected. ThinkMesh will work offline.",
        }
        
        return user_messages.get(
            self.error_code, 
            "ThinkMesh encountered an unexpected issue. Please try again."
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization"""
        return {
            "error_code": self.error_code.value,
            "error_name": self.error_code.name,
            "message": str(self),
            "user_message": self.user_message,
            "details": self.details,
            "recovery_suggestions": self.recovery_suggestions
        }


class HRMEngineException(ThinkMeshException):
    """Exceptions related to HRM engine operations"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        if error_code.value < 1100 or error_code.value >= 1200:
            raise ValueError("HRMEngineException requires HRM-specific error code")
        super().__init__(message, error_code, **kwargs)


class MultiAgentException(ThinkMeshException):
    """Exceptions related to multi-agent operations"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        if error_code.value < 1200 or error_code.value >= 1300:
            raise ValueError("MultiAgentException requires agent-specific error code")
        super().__init__(message, error_code, **kwargs)


class VoiceInterfaceException(ThinkMeshException):
    """Exceptions related to voice interface operations"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        if error_code.value < 1300 or error_code.value >= 1400:
            raise ValueError("VoiceInterfaceException requires voice-specific error code")
        super().__init__(message, error_code, **kwargs)


class LocalAIException(ThinkMeshException):
    """Exceptions related to local AI operations"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        if error_code.value < 1400 or error_code.value >= 1500:
            raise ValueError("LocalAIException requires local AI-specific error code")
        super().__init__(message, error_code, **kwargs)


class DataManagerException(ThinkMeshException):
    """Exceptions related to data management operations"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        if error_code.value < 1500 or error_code.value >= 1600:
            raise ValueError("DataManagerException requires data-specific error code")
        super().__init__(message, error_code, **kwargs)


class MobileOptimizationException(ThinkMeshException):
    """Exceptions related to mobile optimization"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        if error_code.value < 1600 or error_code.value >= 1700:
            raise ValueError("MobileOptimizationException requires mobile-specific error code")
        super().__init__(message, error_code, **kwargs)


class SecurityException(ThinkMeshException):
    """Exceptions related to security and privacy"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        if error_code.value < 1700 or error_code.value >= 1800:
            raise ValueError("SecurityException requires security-specific error code")
        super().__init__(message, error_code, **kwargs)


# Utility functions for exception handling
def handle_exception_gracefully(func):
    """Decorator for graceful exception handling with user-friendly messages"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ThinkMeshException as e:
            # Log technical details
            from .logging import get_logger
            logger = get_logger(func.__module__)
            logger.error(f"ThinkMesh error in {func.__name__}: {e.to_dict()}")
            
            # Return user-friendly error
            return {
                "success": False,
                "error": e.user_message,
                "error_code": e.error_code.value,
                "recovery_suggestions": e.recovery_suggestions
            }
        except Exception as e:
            # Handle unexpected errors
            from .logging import get_logger
            logger = get_logger(func.__module__)
            logger.exception(f"Unexpected error in {func.__name__}: {str(e)}")
            
            return {
                "success": False,
                "error": "ThinkMesh encountered an unexpected issue. Please try again.",
                "error_code": ErrorCode.INVALID_OPERATION.value,
                "recovery_suggestions": ["Restart the app", "Check device resources"]
            }
    
    return wrapper


def create_recovery_suggestions(error_code: ErrorCode) -> list:
    """Generate recovery suggestions based on error code"""
    suggestions = {
        ErrorCode.HRM_MODEL_LOAD_FAILED: [
            "Check available storage space",
            "Restart the app",
            "Clear app cache",
            "Update to latest version"
        ],
        ErrorCode.BATTERY_CRITICALLY_LOW: [
            "Connect device to charger",
            "Enable battery saver mode",
            "Close other apps",
            "Reduce ThinkMesh usage"
        ],
        ErrorCode.NETWORK_UNAVAILABLE: [
            "Check WiFi connection",
            "Try mobile data",
            "Move to area with better signal",
            "Continue using offline features"
        ],
        ErrorCode.MEMORY_PRESSURE_HIGH: [
            "Close other apps",
            "Restart device",
            "Clear app cache",
            "Free up device storage"
        ]
    }
    
    return suggestions.get(error_code, [
        "Restart the app",
        "Check device resources",
        "Contact support if issue persists"
    ])
