"""
ThinkMesh Dependency Injection Container
=======================================

Lightweight dependency injection system for loose coupling,
testability, and modular architecture.
"""

import inspect
from typing import Dict, Any, Type, TypeVar, Callable, Optional, Union
from threading import Lock

from .interfaces import IDependencyContainer
from .logging import get_logger
from .exceptions import ThinkMeshException, ErrorCode

logger = get_logger(__name__)

T = TypeVar('T')


class DependencyContainer(IDependencyContainer):
    """Lightweight dependency injection container"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singleton_flags: Dict[Type, bool] = {}
        self._lock = Lock()
    
    def register(self, interface_type: Type[T], implementation: Union[T, Type[T], Callable[[], T]], 
                singleton: bool = True) -> None:
        """Register implementation for interface type"""
        with self._lock:
            if inspect.isclass(implementation):
                # Class type - store for instantiation
                self._services[interface_type] = implementation
                self._singleton_flags[interface_type] = singleton
            elif callable(implementation):
                # Factory function
                self._factories[interface_type] = implementation
                self._singleton_flags[interface_type] = singleton
            else:
                # Instance - always treated as singleton
                self._singletons[interface_type] = implementation
                self._singleton_flags[interface_type] = True
            
            logger.debug(f"Registered {interface_type.__name__} -> {implementation}")
    
    def register_instance(self, interface_type: Type[T], instance: T) -> None:
        """Register a specific instance (always singleton)"""
        self.register(interface_type, instance, singleton=True)
    
    def register_factory(self, interface_type: Type[T], factory: Callable[[], T], 
                        singleton: bool = True) -> None:
        """Register a factory function"""
        self.register(interface_type, factory, singleton=singleton)
    
    def resolve(self, interface_type: Type[T]) -> T:
        """Resolve implementation for interface type"""
        with self._lock:
            # Check if already instantiated as singleton
            if interface_type in self._singletons:
                return self._singletons[interface_type]
            
            # Check if factory exists
            if interface_type in self._factories:
                instance = self._factories[interface_type]()
                
                # Store as singleton if configured
                if self._singleton_flags.get(interface_type, True):
                    self._singletons[interface_type] = instance
                
                return instance
            
            # Check if class is registered
            if interface_type in self._services:
                implementation_class = self._services[interface_type]
                instance = self._create_instance(implementation_class)
                
                # Store as singleton if configured
                if self._singleton_flags.get(interface_type, True):
                    self._singletons[interface_type] = instance
                
                return instance
            
            # Try to instantiate the interface type directly
            if inspect.isclass(interface_type):
                try:
                    instance = self._create_instance(interface_type)
                    
                    # Auto-register as singleton for future use
                    self._singletons[interface_type] = instance
                    
                    return instance
                except Exception as e:
                    logger.error(f"Failed to auto-instantiate {interface_type.__name__}: {e}")
            
            raise ThinkMeshException(
                f"No registration found for {interface_type.__name__}",
                ErrorCode.DEPENDENCY_INJECTION_ERROR,
                details={"interface_type": interface_type.__name__}
            )
    
    def _create_instance(self, implementation_class: Type[T]) -> T:
        """Create instance with dependency injection"""
        try:
            # Get constructor signature
            signature = inspect.signature(implementation_class.__init__)
            parameters = signature.parameters
            
            # Skip 'self' parameter
            param_names = [name for name in parameters.keys() if name != 'self']
            
            if not param_names:
                # No dependencies - simple instantiation
                return implementation_class()
            
            # Resolve dependencies
            kwargs = {}
            for param_name in param_names:
                param = parameters[param_name]
                
                # Skip parameters with default values if we can't resolve them
                if param.annotation == inspect.Parameter.empty:
                    if param.default != inspect.Parameter.empty:
                        continue
                    else:
                        raise ThinkMeshException(
                            f"Cannot resolve parameter '{param_name}' for {implementation_class.__name__} - no type annotation",
                            ErrorCode.DEPENDENCY_INJECTION_ERROR
                        )
                
                # Try to resolve the parameter type
                try:
                    dependency = self.resolve(param.annotation)
                    kwargs[param_name] = dependency
                except ThinkMeshException:
                    # If resolution fails and parameter has default, skip it
                    if param.default != inspect.Parameter.empty:
                        continue
                    else:
                        raise
            
            return implementation_class(**kwargs)
            
        except Exception as e:
            logger.error(f"Failed to create instance of {implementation_class.__name__}: {e}")
            raise ThinkMeshException(
                f"Failed to create instance of {implementation_class.__name__}: {str(e)}",
                ErrorCode.DEPENDENCY_INJECTION_ERROR,
                details={"class_name": implementation_class.__name__, "error": str(e)}
            )
    
    def is_registered(self, interface_type: Type) -> bool:
        """Check if interface type is registered"""
        with self._lock:
            return (interface_type in self._services or 
                   interface_type in self._singletons or 
                   interface_type in self._factories)
    
    def unregister(self, interface_type: Type) -> None:
        """Unregister interface type"""
        with self._lock:
            self._services.pop(interface_type, None)
            self._singletons.pop(interface_type, None)
            self._factories.pop(interface_type, None)
            self._singleton_flags.pop(interface_type, None)
            
            logger.debug(f"Unregistered {interface_type.__name__}")
    
    def clear(self) -> None:
        """Clear all registrations"""
        with self._lock:
            self._services.clear()
            self._singletons.clear()
            self._factories.clear()
            self._singleton_flags.clear()
            
            logger.debug("Cleared all registrations")
    
    def get_registrations(self) -> Dict[str, str]:
        """Get summary of all registrations"""
        with self._lock:
            registrations = {}
            
            for interface_type in self._services:
                registrations[interface_type.__name__] = f"Class: {self._services[interface_type].__name__}"
            
            for interface_type in self._singletons:
                registrations[interface_type.__name__] = f"Instance: {type(self._singletons[interface_type]).__name__}"
            
            for interface_type in self._factories:
                registrations[interface_type.__name__] = f"Factory: {self._factories[interface_type].__name__}"
            
            return registrations


# Global container instance
_container: Optional[DependencyContainer] = None
_container_lock = Lock()


def get_container() -> DependencyContainer:
    """Get global dependency injection container"""
    global _container
    if _container is None:
        with _container_lock:
            if _container is None:
                _container = DependencyContainer()
    return _container


def set_container(container: DependencyContainer) -> None:
    """Set global dependency injection container"""
    global _container
    with _container_lock:
        _container = container


def register(interface_type: Type[T], implementation: Union[T, Type[T], Callable[[], T]], 
            singleton: bool = True) -> None:
    """Register implementation in global container"""
    get_container().register(interface_type, implementation, singleton)


def register_instance(interface_type: Type[T], instance: T) -> None:
    """Register instance in global container"""
    get_container().register_instance(interface_type, instance)


def register_factory(interface_type: Type[T], factory: Callable[[], T], 
                    singleton: bool = True) -> None:
    """Register factory in global container"""
    get_container().register_factory(interface_type, factory, singleton)


def resolve(interface_type: Type[T]) -> T:
    """Resolve from global container"""
    return get_container().resolve(interface_type)


def is_registered(interface_type: Type) -> bool:
    """Check if registered in global container"""
    return get_container().is_registered(interface_type)


# Decorator for automatic dependency injection
def inject(*dependencies: Type):
    """Decorator for automatic dependency injection"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Resolve dependencies and add to kwargs
            for dep_type in dependencies:
                if dep_type.__name__.lower() not in kwargs:
                    kwargs[dep_type.__name__.lower()] = resolve(dep_type)
            
            return func(*args, **kwargs)
        
        async def async_wrapper(*args, **kwargs):
            # Resolve dependencies and add to kwargs
            for dep_type in dependencies:
                if dep_type.__name__.lower() not in kwargs:
                    kwargs[dep_type.__name__.lower()] = resolve(dep_type)
            
            return await func(*args, **kwargs)
        
        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    return decorator


def configure_default_container() -> None:
    """Configure container with default ThinkMesh services"""
    from .config import get_config
    
    container = get_container()
    config = get_config()
    
    # Register configuration
    container.register_instance(type(config), config)
    
    logger.info("Configured default dependency container")


# Auto-configure on import
try:
    configure_default_container()
except Exception as e:
    logger.warning(f"Failed to auto-configure container: {e}")
