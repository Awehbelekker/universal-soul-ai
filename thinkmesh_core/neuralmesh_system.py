"""
NeuralMesh™ Enterprise AI Platform System Orchestrator
=====================================================

Main enterprise system coordinator that manages all SynergyCore™ components,
handles initialization, shutdown, and enterprise-wide coordination with
comprehensive cost optimization and compliance monitoring.

Copyright (c) 2025 SynergyCore™ AI Systems
"""

import asyncio
import signal
import sys
import time
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from .enterprise_interfaces import *
from .enterprise_config import get_enterprise_config, NeuralMeshConfig
from .container import get_container, register_instance
from .health import HealthChecker
from .logging import get_logger, log_system_event
from .exceptions import ThinkMeshException, ErrorCode, handle_exception_gracefully

logger = get_logger(__name__)


class NeuralMeshSystem:
    """
    NeuralMesh™ Enterprise AI Platform System Orchestrator
    
    Coordinates all enterprise AI components with:
    - SynergyCore™ Orchestration Platform
    - CogniFlow™ Reasoning Engine  
    - EdgeMind™ Local AI Service
    - OptiCore™ Resource Optimizer
    - CodeSwarm™ Development Agents
    - Enterprise compliance and cost optimization
    """
    
    def __init__(self, config: Optional[NeuralMeshConfig] = None):
        self.config = config or get_enterprise_config()
        self.container = get_container()
        self.health_checker = HealthChecker()
        
        # Enterprise component references
        self.cogniflow_engine: Optional[ICogniFlowEngine] = None
        self.synergycore_orchestrator: Optional[ISynergyCoreOrchestrator] = None
        self.voice_interface: Optional[IVoiceInterface] = None
        self.edgemind_service: Optional[IEdgeMindService] = None
        self.neuralmesh_data_manager: Optional[INeuralMeshDataManager] = None
        self.opticore_optimizer: Optional[IOptiCoreOptimizer] = None
        
        # Enterprise-specific components
        self.compliance_manager: Optional[IEnterpriseCompliance] = None
        self.cost_optimizer: Optional[IEnterpriseCostOptimizer] = None
        
        # System state
        self.is_initialized = False
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Enterprise performance tracking
        self.startup_time: Optional[float] = None
        self.component_load_times: Dict[str, float] = {}
        self.total_cost_savings: float = 0.0
        self.compliance_score: float = 100.0
        
        logger.info("NeuralMesh™ Enterprise AI Platform created")
    
    async def initialize(self) -> None:
        """Initialize all NeuralMesh™ enterprise components"""
        if self.is_initialized:
            logger.warning("NeuralMesh™ system already initialized")
            return
        
        try:
            start_time = time.time()
            
            logger.info("Initializing NeuralMesh™ Enterprise AI Platform...")
            
            # Register enterprise configuration
            register_instance(NeuralMeshConfig, self.config)
            register_instance(HealthChecker, self.health_checker)
            
            # Initialize enterprise components in dependency order
            await self._initialize_neuralmesh_data_manager()
            await self._initialize_edgemind_service()
            await self._initialize_cogniflow_engine()
            await self._initialize_synergycore_orchestrator()
            await self._initialize_voice_interface()
            await self._initialize_opticore_optimizer()
            
            # Initialize enterprise-specific components
            await self._initialize_compliance_manager()
            await self._initialize_cost_optimizer()
            
            # Start enterprise health monitoring
            await self.health_checker.start_monitoring()
            
            # Register signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            self.startup_time = time.time() - start_time
            self.is_initialized = True
            
            log_system_event(
                logger, "neuralmesh_system_initialized", "neuralmesh_enterprise",
                {
                    "startup_time_seconds": self.startup_time,
                    "component_count": len(self.component_load_times),
                    "component_load_times": self.component_load_times,
                    "enterprise_mode": self.config.enterprise_mode,
                    "compliance_mode": self.config.compliance_mode
                }
            )
            
            logger.info(f"NeuralMesh™ Enterprise AI Platform initialized successfully in {self.startup_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize NeuralMesh™ system: {e}")
            await self.shutdown()
            raise ThinkMeshException(
                f"NeuralMesh™ system initialization failed: {str(e)}",
                ErrorCode.SYSTEM_INITIALIZATION_FAILED,
                details={"error": str(e)}
            )
    
    async def _initialize_neuralmesh_data_manager(self) -> None:
        """Initialize NeuralMesh™ data management component"""
        try:
            start_time = time.time()
            
            # Import and create enterprise data manager
            from .data import NeuralMeshDataManager
            self.neuralmesh_data_manager = NeuralMeshDataManager(self.config.data)
            await self.neuralmesh_data_manager.initialize()
            
            # Register in container
            register_instance(INeuralMeshDataManager, self.neuralmesh_data_manager)
            self.health_checker.register_health_check("neuralmesh_data_manager", self.neuralmesh_data_manager)
            
            load_time = time.time() - start_time
            self.component_load_times["neuralmesh_data_manager"] = load_time
            
            logger.info(f"NeuralMesh™ data manager initialized in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize NeuralMesh™ data manager: {e}")
            raise
    
    async def _initialize_edgemind_service(self) -> None:
        """Initialize EdgeMind™ local AI service"""
        try:
            start_time = time.time()
            
            # Import and create EdgeMind™ service
            from .edgemind import EdgeMindService
            self.edgemind_service = EdgeMindService(self.config.edgemind)
            await self.edgemind_service.initialize()
            
            # Register in container
            register_instance(IEdgeMindService, self.edgemind_service)
            self.health_checker.register_health_check("edgemind_service", self.edgemind_service)
            
            load_time = time.time() - start_time
            self.component_load_times["edgemind_service"] = load_time
            
            logger.info(f"EdgeMind™ service initialized in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize EdgeMind™ service: {e}")
            raise
    
    async def _initialize_cogniflow_engine(self) -> None:
        """Initialize CogniFlow™ reasoning engine"""
        try:
            start_time = time.time()
            
            # Import and create CogniFlow™ engine
            from .cogniflow import CogniFlowEngine
            self.cogniflow_engine = CogniFlowEngine(self.config.cogniflow)
            await self.cogniflow_engine.initialize()
            
            # Register in container
            register_instance(ICogniFlowEngine, self.cogniflow_engine)
            self.health_checker.register_health_check("cogniflow_engine", self.cogniflow_engine)
            
            load_time = time.time() - start_time
            self.component_load_times["cogniflow_engine"] = load_time
            
            logger.info(f"CogniFlow™ engine initialized in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize CogniFlow™ engine: {e}")
            raise
    
    async def _initialize_synergycore_orchestrator(self) -> None:
        """Initialize SynergyCore™ orchestrator"""
        try:
            start_time = time.time()
            
            # Import and create SynergyCore™ orchestrator
            from .synergycore import SynergyCoreOrchestrator
            self.synergycore_orchestrator = SynergyCoreOrchestrator(self.config.synergycore)
            await self.synergycore_orchestrator.initialize()
            
            # Register in container
            register_instance(ISynergyCoreOrchestrator, self.synergycore_orchestrator)
            self.health_checker.register_health_check("synergycore_orchestrator", self.synergycore_orchestrator)
            
            load_time = time.time() - start_time
            self.component_load_times["synergycore_orchestrator"] = load_time
            
            logger.info(f"SynergyCore™ orchestrator initialized in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize SynergyCore™ orchestrator: {e}")
            raise
    
    async def _initialize_voice_interface(self) -> None:
        """Initialize voice interface"""
        try:
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
    
    async def _initialize_opticore_optimizer(self) -> None:
        """Initialize OptiCore™ optimizer"""
        try:
            start_time = time.time()
            
            # Import and create OptiCore™ optimizer
            from .opticore import OptiCoreOptimizer
            self.opticore_optimizer = OptiCoreOptimizer(self.config.opticore)
            await self.opticore_optimizer.initialize()
            
            # Register in container
            register_instance(IOptiCoreOptimizer, self.opticore_optimizer)
            self.health_checker.register_health_check("opticore_optimizer", self.opticore_optimizer)
            
            load_time = time.time() - start_time
            self.component_load_times["opticore_optimizer"] = load_time
            
            logger.info(f"OptiCore™ optimizer initialized in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize OptiCore™ optimizer: {e}")
            raise
    
    async def _initialize_compliance_manager(self) -> None:
        """Initialize enterprise compliance manager"""
        try:
            start_time = time.time()
            
            # Import and create compliance manager
            from .compliance import EnterpriseComplianceManager
            self.compliance_manager = EnterpriseComplianceManager(self.config)
            await self.compliance_manager.initialize()
            
            # Register in container
            register_instance(IEnterpriseCompliance, self.compliance_manager)
            self.health_checker.register_health_check("compliance_manager", self.compliance_manager)
            
            load_time = time.time() - start_time
            self.component_load_times["compliance_manager"] = load_time
            
            logger.info(f"Enterprise compliance manager initialized in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize compliance manager: {e}")
            raise
    
    async def _initialize_cost_optimizer(self) -> None:
        """Initialize enterprise cost optimizer"""
        try:
            start_time = time.time()
            
            # Import and create cost optimizer
            from .cost_optimizer import EnterpriseCostOptimizer
            self.cost_optimizer = EnterpriseCostOptimizer(self.config)
            await self.cost_optimizer.initialize()
            
            # Register in container
            register_instance(IEnterpriseCostOptimizer, self.cost_optimizer)
            self.health_checker.register_health_check("cost_optimizer", self.cost_optimizer)
            
            load_time = time.time() - start_time
            self.component_load_times["cost_optimizer"] = load_time
            
            logger.info(f"Enterprise cost optimizer initialized in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize cost optimizer: {e}")
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
        """Start the NeuralMesh™ enterprise system"""
        if not self.is_initialized:
            await self.initialize()
        
        if self.is_running:
            logger.warning("NeuralMesh™ system already running")
            return
        
        try:
            self.is_running = True
            
            log_system_event(
                logger, "neuralmesh_system_started", "neuralmesh_enterprise",
                {
                    "startup_time": self.startup_time,
                    "enterprise_mode": self.config.enterprise_mode,
                    "compliance_mode": self.config.compliance_mode
                }
            )
            
            logger.info("NeuralMesh™ Enterprise AI Platform started successfully")
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"Error during NeuralMesh™ system operation: {e}")
            raise
    
    @handle_exception_gracefully
    async def process_enterprise_request(self, request: str, context: EnterpriseContext) -> Dict[str, Any]:
        """Process an enterprise request through the NeuralMesh™ system"""
        if not self.is_running:
            raise ThinkMeshException(
                "NeuralMesh™ system not running",
                ErrorCode.INVALID_OPERATION
            )
        
        try:
            # Validate compliance requirements
            if self.compliance_manager:
                compliance_check = await self.compliance_manager.validate_compliance(
                    "process_request", context
                )
                if not compliance_check.get("compliant", False):
                    raise ThinkMeshException(
                        f"Request failed compliance validation: {compliance_check.get('reason')}",
                        ErrorCode.PERMISSION_DENIED
                    )
            
            # Use CogniFlow™ engine for primary processing
            response = await self.cogniflow_engine.process_enterprise_request(request, context)
            
            # Track cost optimization
            if self.cost_optimizer:
                cost_analysis = await self.cost_optimizer.analyze_cost_efficiency({
                    "request": request,
                    "response": response,
                    "context": context.__dict__
                })
                self.total_cost_savings += cost_analysis.get("savings", 0.0)
            
            return {
                "success": True,
                "response": response,
                "processing_time": 0.0,  # TODO: Add timing
                "compliance_status": "compliant",
                "cost_savings": self.total_cost_savings
            }
            
        except Exception as e:
            logger.error(f"Error processing enterprise request: {e}")
            raise
    
    async def get_enterprise_status(self) -> Dict[str, Any]:
        """Get comprehensive enterprise system status"""
        health_summary = await self.health_checker.get_health_summary()
        
        return {
            "system_info": {
                "platform": "NeuralMesh™ Enterprise AI Platform",
                "version": "1.0.0",
                "initialized": self.is_initialized,
                "running": self.is_running,
                "startup_time": self.startup_time,
                "component_load_times": self.component_load_times,
                "enterprise_mode": self.config.enterprise_mode,
                "compliance_mode": self.config.compliance_mode
            },
            "health": health_summary,
            "enterprise_metrics": {
                "total_cost_savings": self.total_cost_savings,
                "compliance_score": self.compliance_score,
                "feature_flags": self.config.feature_flags
            },
            "configuration": {
                "environment": self.config.environment,
                "debug_mode": self.config.debug_mode
            }
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the NeuralMesh™ enterprise system"""
        if not self.is_running and not self.is_initialized:
            return
        
        logger.info("Shutting down NeuralMesh™ Enterprise AI Platform...")
        
        try:
            # Signal shutdown
            self.shutdown_event.set()
            self.is_running = False
            
            # Stop health monitoring
            await self.health_checker.stop_monitoring()
            
            # Shutdown enterprise components in reverse order
            components = [
                ("cost_optimizer", self.cost_optimizer),
                ("compliance_manager", self.compliance_manager),
                ("opticore_optimizer", self.opticore_optimizer),
                ("voice_interface", self.voice_interface),
                ("synergycore_orchestrator", self.synergycore_orchestrator),
                ("cogniflow_engine", self.cogniflow_engine),
                ("edgemind_service", self.edgemind_service),
                ("neuralmesh_data_manager", self.neuralmesh_data_manager),
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
                logger, "neuralmesh_system_shutdown", "neuralmesh_enterprise",
                {
                    "graceful_shutdown": True,
                    "total_cost_savings": self.total_cost_savings,
                    "compliance_score": self.compliance_score
                }
            )
            
            logger.info("NeuralMesh™ Enterprise AI Platform shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during NeuralMesh™ shutdown: {e}")


# Context manager for enterprise system lifecycle
@asynccontextmanager
async def neuralmesh_enterprise_system(config: Optional[NeuralMeshConfig] = None):
    """Context manager for NeuralMesh™ enterprise system lifecycle"""
    system = NeuralMeshSystem(config)
    try:
        await system.initialize()
        yield system
    finally:
        await system.shutdown()


# Global enterprise system instance
_enterprise_system: Optional[NeuralMeshSystem] = None


def get_enterprise_system() -> Optional[NeuralMeshSystem]:
    """Get global NeuralMesh™ enterprise system instance"""
    return _enterprise_system


def set_enterprise_system(system: NeuralMeshSystem) -> None:
    """Set global NeuralMesh™ enterprise system instance"""
    global _enterprise_system
    _enterprise_system = system


# Backward compatibility aliases
ThinkMeshSystem = NeuralMeshSystem  # Backward compatibility
thinkmesh_system = neuralmesh_enterprise_system  # Backward compatibility
get_system = get_enterprise_system  # Backward compatibility
set_system = set_enterprise_system  # Backward compatibility
