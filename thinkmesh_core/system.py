"""
ThinkMesh System Orchestrator
============================

Main system coordinator that manages all ThinkMesh components,
handles initialization, shutdown, and system-wide coordination.
"""

import asyncio
import signal
import sys
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from .interfaces import *
from .config import get_config, ThinkMeshConfig
from .container import get_container, register_instance
from .health import HealthChecker
from .logging import get_logger, log_system_event
from .exceptions import ThinkMeshException, ErrorCode, handle_exception_gracefully

logger = get_logger(__name__)


class ThinkMeshSystem:
    """Main ThinkMesh system orchestrator"""
    
    def __init__(self, config: Optional[ThinkMeshConfig] = None):
        self.config = config or get_config()
        self.container = get_container()
        self.health_checker = HealthChecker()
        
        # Component references
        self.hrm_engine: Optional[IAIEngine] = None
        self.agent_orchestrator: Optional[IAgentOrchestrator] = None
        self.voice_interface: Optional[IVoiceInterface] = None
        self.local_ai_service: Optional[ILocalAIService] = None
        self.data_manager: Optional[IDataManager] = None
        self.mobile_optimizer: Optional[IMobileOptimizer] = None
        
        # System state
        self.is_initialized = False
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Performance tracking
        self.startup_time: Optional[float] = None
        self.component_load_times: Dict[str, float] = {}
        
        logger.info("ThinkMesh system created")
    
    async def initialize(self) -> None:
        """Initialize all ThinkMesh components"""
        if self.is_initialized:
            logger.warning("System already initialized")
            return
        
        try:
            import time
            start_time = time.time()
            
            logger.info("Initializing ThinkMesh system...")
            
            # Register system configuration
            register_instance(ThinkMeshConfig, self.config)
            register_instance(HealthChecker, self.health_checker)
            
            # Initialize components in dependency order
            await self._initialize_data_manager()
            await self._initialize_local_ai_service()
            await self._initialize_hrm_engine()
            await self._initialize_agent_orchestrator()
            await self._initialize_voice_interface()
            await self._initialize_mobile_optimizer()
            
            # Start health monitoring
            await self.health_checker.start_monitoring()
            
            # Register signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            self.startup_time = time.time() - start_time
            self.is_initialized = True
            
            log_system_event(
                logger, "system_initialized", "thinkmesh_system",
                {
                    "startup_time_seconds": self.startup_time,
                    "component_count": len(self.component_load_times),
                    "component_load_times": self.component_load_times
                }
            )
            
            logger.info(f"ThinkMesh system initialized successfully in {self.startup_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize ThinkMesh system: {e}")
            await self.shutdown()
            raise ThinkMeshException(
                f"System initialization failed: {str(e)}",
                ErrorCode.SYSTEM_INITIALIZATION_FAILED,
                details={"error": str(e)}
            )
    
    async def _initialize_data_manager(self) -> None:
        """Initialize data management component"""
        try:
            import time
            start_time = time.time()
            
            # Import and create data manager
            from .data import DataManager
            self.data_manager = DataManager(self.config.data)
            await self.data_manager.initialize()
            
            # Register in container
            register_instance(IDataManager, self.data_manager)
            self.health_checker.register_health_check("data_manager", self.data_manager)
            
            load_time = time.time() - start_time
            self.component_load_times["data_manager"] = load_time
            
            logger.info(f"Data manager initialized in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize data manager: {e}")
            raise
    
    async def _initialize_local_ai_service(self) -> None:
        """Initialize local AI service"""
        try:
            import time
            start_time = time.time()
            
            # Import and create local AI service
            from .local_ai import LocalAIService
            self.local_ai_service = LocalAIService(self.config.local_ai)
            await self.local_ai_service.initialize()
            
            # Register in container
            register_instance(ILocalAIService, self.local_ai_service)
            self.health_checker.register_health_check("local_ai_service", self.local_ai_service)
            
            load_time = time.time() - start_time
            self.component_load_times["local_ai_service"] = load_time
            
            logger.info(f"Local AI service initialized in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize local AI service: {e}")
            raise
    
    async def _initialize_hrm_engine(self) -> None:
        """Initialize HRM reasoning engine"""
        try:
            import time
            start_time = time.time()
            
            # Import and create HRM engine
            from .hrm import HRMEngine
            self.hrm_engine = HRMEngine(self.config.hrm)
            await self.hrm_engine.initialize()
            
            # Register in container
            register_instance(IAIEngine, self.hrm_engine)
            self.health_checker.register_health_check("hrm_engine", self.hrm_engine)
            
            load_time = time.time() - start_time
            self.component_load_times["hrm_engine"] = load_time
            
            logger.info(f"HRM engine initialized in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize HRM engine: {e}")
            raise
    
    async def _initialize_agent_orchestrator(self) -> None:
        """Initialize multi-agent orchestrator"""
        try:
            import time
            start_time = time.time()
            
            # Import and create agent orchestrator
            from .agents import MultiAgentOrchestrator
            self.agent_orchestrator = MultiAgentOrchestrator(self.config.agents)
            await self.agent_orchestrator.initialize()
            
            # Register in container
            register_instance(IAgentOrchestrator, self.agent_orchestrator)
            self.health_checker.register_health_check("agent_orchestrator", self.agent_orchestrator)
            
            load_time = time.time() - start_time
            self.component_load_times["agent_orchestrator"] = load_time
            
            logger.info(f"Agent orchestrator initialized in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent orchestrator: {e}")
            raise
    
    async def _initialize_voice_interface(self) -> None:
        """Initialize voice interface"""
        try:
            import time
            start_time = time.time()
            
            # Import and create voice interface
            from .voice import VoiceInterface
            self.voice_interface = VoiceInterface(self.config.voice)
            await self.voice_interface.initialize()
            
            # Register in container
            register_instance(IVoiceInterface, self.voice_interface)
            self.health_checker.register_health_check("voice_interface", self.voice_interface)
            
            load_time = time.time() - start_time
            self.component_load_times["voice_interface"] = load_time
            
            logger.info(f"Voice interface initialized in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize voice interface: {e}")
            raise
    
    async def _initialize_mobile_optimizer(self) -> None:
        """Initialize mobile optimizer"""
        try:
            import time
            start_time = time.time()
            
            # Import and create mobile optimizer
            from .mobile import MobileOptimizer
            self.mobile_optimizer = MobileOptimizer(self.config.mobile)
            await self.mobile_optimizer.initialize()
            
            # Register in container
            register_instance(IMobileOptimizer, self.mobile_optimizer)
            self.health_checker.register_health_check("mobile_optimizer", self.mobile_optimizer)
            
            load_time = time.time() - start_time
            self.component_load_times["mobile_optimizer"] = load_time
            
            logger.info(f"Mobile optimizer initialized in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize mobile optimizer: {e}")
            raise
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        if sys.platform != "win32":
            # Unix-like systems
            loop = asyncio.get_event_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))
        else:
            # Windows
            signal.signal(signal.SIGINT, lambda sig, frame: asyncio.create_task(self.shutdown()))
    
    async def start(self) -> None:
        """Start the ThinkMesh system"""
        if not self.is_initialized:
            await self.initialize()
        
        if self.is_running:
            logger.warning("System already running")
            return
        
        try:
            self.is_running = True
            
            log_system_event(
                logger, "system_started", "thinkmesh_system",
                {"startup_time": self.startup_time}
            )
            
            logger.info("ThinkMesh system started successfully")
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"Error during system operation: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the ThinkMesh system"""
        if not self.is_running and not self.is_initialized:
            return
        
        logger.info("Shutting down ThinkMesh system...")
        
        try:
            # Signal shutdown
            self.shutdown_event.set()
            self.is_running = False
            
            # Stop health monitoring
            await self.health_checker.stop_monitoring()
            
            # Shutdown components in reverse order
            components = [
                ("mobile_optimizer", self.mobile_optimizer),
                ("voice_interface", self.voice_interface),
                ("agent_orchestrator", self.agent_orchestrator),
                ("hrm_engine", self.hrm_engine),
                ("local_ai_service", self.local_ai_service),
                ("data_manager", self.data_manager),
            ]
            
            for name, component in components:
                if component and hasattr(component, 'shutdown'):
                    try:
                        await component.shutdown()
                        logger.info(f"Shutdown {name}")
                    except Exception as e:
                        logger.error(f"Error shutting down {name}: {e}")
            
            self.is_initialized = False
            
            log_system_event(
                logger, "system_shutdown", "thinkmesh_system",
                {"graceful_shutdown": True}
            )
            
            logger.info("ThinkMesh system shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    @handle_exception_gracefully
    async def process_user_request(self, request: str, user_context: UserContext) -> Dict[str, Any]:
        """Process a user request through the ThinkMesh system"""
        if not self.is_running:
            raise ThinkMeshException(
                "System not running",
                ErrorCode.INVALID_OPERATION
            )
        
        try:
            # Use HRM engine for primary processing
            response = await self.hrm_engine.process_request(request, user_context)
            
            return {
                "success": True,
                "response": response,
                "processing_time": 0.0  # TODO: Add timing
            }
            
        except Exception as e:
            logger.error(f"Error processing user request: {e}")
            raise
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        health_summary = await self.health_checker.get_health_summary()
        
        return {
            "system_info": {
                "initialized": self.is_initialized,
                "running": self.is_running,
                "startup_time": self.startup_time,
                "component_load_times": self.component_load_times
            },
            "health": health_summary,
            "configuration": {
                "environment": self.config.environment,
                "debug_mode": self.config.debug_mode,
                "feature_flags": self.config.feature_flags
            }
        }


# Context manager for system lifecycle
@asynccontextmanager
async def thinkmesh_system(config: Optional[ThinkMeshConfig] = None):
    """Context manager for ThinkMesh system lifecycle"""
    system = ThinkMeshSystem(config)
    try:
        await system.initialize()
        yield system
    finally:
        await system.shutdown()


# Global system instance
_system: Optional[ThinkMeshSystem] = None


def get_system() -> Optional[ThinkMeshSystem]:
    """Get global system instance"""
    return _system


def set_system(system: ThinkMeshSystem) -> None:
    """Set global system instance"""
    global _system
    _system = system
