"""
ThinkMesh Logging System
=======================

Comprehensive logging with structured formats, performance metrics,
privacy-aware logging, and mobile-optimized log management.
"""

import logging
import logging.handlers
import json
import time
import sys
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from functools import wraps

from .config import get_config


class ThinkMeshFormatter(logging.Formatter):
    """Custom formatter for ThinkMesh logs with structured JSON output"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = getattr(record, 'user_id')
        
        if hasattr(record, 'session_id'):
            log_entry["session_id"] = getattr(record, 'session_id')
        
        if hasattr(record, 'performance_metrics'):
            log_entry["performance"] = getattr(record, 'performance_metrics')
        
        if hasattr(record, 'privacy_level'):
            log_entry["privacy_level"] = getattr(record, 'privacy_level')
        
        return json.dumps(log_entry, ensure_ascii=False)


class PrivacyAwareFilter(logging.Filter):
    """Filter to prevent logging of sensitive information"""
    
    SENSITIVE_PATTERNS = [
        'password', 'token', 'key', 'secret', 'credential',
        'ssn', 'social_security', 'credit_card', 'phone_number',
        'email', 'address', 'location', 'gps', 'biometric'
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        # Check if message contains sensitive information
        message = record.getMessage().lower()
        
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in message:
                # Replace sensitive content with placeholder
                record.msg = "[PRIVACY_FILTERED] " + record.msg
                break
        
        return True


class PerformanceLogger:
    """Logger for performance metrics and timing"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_timing(self, operation: str, duration: float, 
                   metadata: Optional[Dict[str, Any]] = None):
        """Log operation timing"""
        self.logger.info(
            f"Performance: {operation} completed in {duration:.3f}s",
            extra={
                'performance_metrics': {
                    'operation': operation,
                    'duration_seconds': duration,
                    'metadata': metadata or {}
                }
            }
        )
    
    def log_resource_usage(self, component: str, metrics: Dict[str, Any]):
        """Log resource usage metrics"""
        self.logger.info(
            f"Resource usage for {component}",
            extra={
                'performance_metrics': {
                    'component': component,
                    'metrics': metrics
                }
            }
        )


def setup_logging() -> None:
    """Setup ThinkMesh logging configuration"""
    config = get_config()
    
    # Create logs directory
    log_path = Path(config.monitoring.log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.monitoring.log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    json_formatter = ThinkMeshFormatter()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=config.monitoring.log_file_path,
        maxBytes=config.monitoring.log_rotation_size_mb * 1024 * 1024,
        backupCount=config.monitoring.log_retention_days
    )
    file_handler.setFormatter(json_formatter)
    file_handler.addFilter(PrivacyAwareFilter())
    
    # Console handler for development
    if config.debug_mode:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(PrivacyAwareFilter())
        root_logger.addHandler(console_handler)
    
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance for component"""
    logger = logging.getLogger(f"thinkmesh.{name}")
    
    # Add performance logging capability
    if not hasattr(logger, 'performance'):
        logger.performance = PerformanceLogger(logger)
    
    return logger


def log_user_interaction(logger: logging.Logger, user_id: str, 
                        interaction_type: str, details: Dict[str, Any]):
    """Log user interaction with privacy considerations"""
    # Filter out sensitive details
    filtered_details = {
        k: v for k, v in details.items() 
        if not any(sensitive in k.lower() for sensitive in 
                  ['password', 'token', 'key', 'location', 'personal'])
    }
    
    logger.info(
        f"User interaction: {interaction_type}",
        extra={
            'user_id': user_id,
            'interaction_type': interaction_type,
            'details': filtered_details,
            'privacy_level': 'user_interaction'
        }
    )


def log_system_event(logger: logging.Logger, event_type: str, 
                    component: str, details: Dict[str, Any]):
    """Log system events"""
    logger.info(
        f"System event: {event_type} in {component}",
        extra={
            'event_type': event_type,
            'component': component,
            'details': details,
            'privacy_level': 'system'
        }
    )


def log_error_with_context(logger: logging.Logger, error: Exception, 
                          context: Dict[str, Any]):
    """Log error with contextual information"""
    logger.error(
        f"Error occurred: {str(error)}",
        extra={
            'error_type': type(error).__name__,
            'context': context,
            'privacy_level': 'error'
        },
        exc_info=True
    )


# Decorators for automatic logging
def log_function_call(logger: Optional[logging.Logger] = None):
    """Decorator to log function calls with timing"""
    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = get_logger(func.__module__)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = f"{func.__module__}.{func.__name__}"
            
            logger.debug(f"Starting {function_name}")
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.performance.log_timing(
                    operation=function_name,
                    duration=duration,
                    metadata={'args_count': len(args), 'kwargs_count': len(kwargs)}
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                log_error_with_context(
                    logger, e, 
                    {
                        'function': function_name,
                        'duration': duration,
                        'args_count': len(args),
                        'kwargs_count': len(kwargs)
                    }
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = f"{func.__module__}.{func.__name__}"
            
            logger.debug(f"Starting {function_name}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.performance.log_timing(
                    operation=function_name,
                    duration=duration,
                    metadata={'args_count': len(args), 'kwargs_count': len(kwargs)}
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                log_error_with_context(
                    logger, e,
                    {
                        'function': function_name,
                        'duration': duration,
                        'args_count': len(args),
                        'kwargs_count': len(kwargs)
                    }
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def log_component_lifecycle(component_name: str):
    """Decorator to log component lifecycle events"""
    def decorator(cls):
        original_init = cls.__init__
        
        @wraps(original_init)
        def new_init(self, *args, **kwargs):
            logger = get_logger(component_name)
            logger.info(f"Initializing {component_name}")
            
            try:
                result = original_init(self, *args, **kwargs)
                logger.info(f"Successfully initialized {component_name}")
                return result
            except Exception as e:
                log_error_with_context(
                    logger, e, 
                    {'component': component_name, 'lifecycle_stage': 'initialization'}
                )
                raise
        
        cls.__init__ = new_init
        return cls
    
    return decorator


# Initialize logging when module is imported
try:
    setup_logging()
except Exception as e:
    # Fallback to basic logging if setup fails
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.getLogger(__name__).warning(f"Failed to setup advanced logging: {e}")
