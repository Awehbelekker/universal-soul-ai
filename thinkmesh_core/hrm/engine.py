"""
ThinkMesh HRM Engine Implementation
==================================

Main HRM engine that coordinates strategic planning and task execution
with mobile optimization and privacy-first design.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path

from ..interfaces import IAIEngine, IHealthCheck, ComponentStatus, HealthStatus, UserContext
from ..config import HRMConfig
from ..logging import get_logger, log_function_call, log_component_lifecycle
from ..exceptions import HRMEngineException, ErrorCode

from .strategic_planner import StrategicPlanner
from .task_executor import TaskExecutor
from .learning_engine import LearningEngine
from .mobile_optimizer import HRMMobileOptimizer

logger = get_logger(__name__)


@dataclass
class HRMRequest:
    """HRM processing request structure"""
    user_input: str
    context: UserContext
    priority: str = "normal"  # low, normal, high, critical
    timeout_seconds: Optional[int] = None
    mobile_constraints: Optional[Dict[str, Any]] = None


@dataclass
class HRMResponse:
    """HRM processing response structure"""
    response: str
    confidence: float
    reasoning_path: List[str]
    execution_time_ms: float
    tokens_used: int
    strategy_used: str
    learning_applied: bool
    mobile_optimizations: Dict[str, Any]


@log_component_lifecycle("hrm_engine")
class HRMEngine(IAIEngine, IHealthCheck):
    """
    Hierarchical Reasoning Model Engine
    
    Implements the revolutionary 27M parameter AI engine with:
    - Strategic planning (hours-to-days timescale)
    - Task execution (seconds-to-minutes timescale)
    - Continuous learning from user interactions
    - Mobile optimization with battery awareness
    """
    
    def __init__(self, config: HRMConfig):
        self.config = config
        self.is_initialized = False
        self.model_loaded = False
        
        # Core components
        self.strategic_planner: Optional[StrategicPlanner] = None
        self.task_executor: Optional[TaskExecutor] = None
        self.learning_engine: Optional[LearningEngine] = None
        self.mobile_optimizer: Optional[HRMMobileOptimizer] = None
        
        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.average_response_time = 0.0
        self.last_error: Optional[str] = None
        
        # Mobile state
        self.current_performance_mode = "normal"  # low, normal, high
        self.battery_level = 100.0
        self.thermal_state = "normal"  # normal, warm, hot
        
        logger.info("HRM Engine created")
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the HRM engine and all components"""
        if self.is_initialized:
            logger.warning("HRM Engine already initialized")
            return
        
        try:
            logger.info("Initializing HRM Engine...")
            
            # Update config if provided
            if config:
                for key, value in config.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
            
            # Initialize mobile optimizer first (affects other components)
            self.mobile_optimizer = HRMMobileOptimizer(self.config)
            await self.mobile_optimizer.initialize()
            
            # Initialize core components
            await self._initialize_strategic_planner()
            await self._initialize_task_executor()
            await self._initialize_learning_engine()
            
            # Load the HRM model
            await self._load_hrm_model()
            
            self.is_initialized = True
            logger.info("HRM Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize HRM Engine: {e}")
            raise HRMEngineException(
                f"HRM Engine initialization failed: {str(e)}",
                ErrorCode.HRM_MODEL_LOAD_FAILED,
                details={"error": str(e), "config": self.config.__dict__}
            )
    
    async def _initialize_strategic_planner(self) -> None:
        """Initialize the strategic planning component"""
        self.strategic_planner = StrategicPlanner(
            config=self.config,
            mobile_optimizer=self.mobile_optimizer
        )
        await self.strategic_planner.initialize()
        logger.info("Strategic planner initialized")
    
    async def _initialize_task_executor(self) -> None:
        """Initialize the task execution component"""
        self.task_executor = TaskExecutor(
            config=self.config,
            mobile_optimizer=self.mobile_optimizer
        )
        await self.task_executor.initialize()
        logger.info("Task executor initialized")
    
    async def _initialize_learning_engine(self) -> None:
        """Initialize the learning component"""
        self.learning_engine = LearningEngine(
            config=self.config,
            mobile_optimizer=self.mobile_optimizer
        )
        await self.learning_engine.initialize()
        logger.info("Learning engine initialized")
    
    async def _load_hrm_model(self) -> None:
        """Load the HRM model with mobile optimizations"""
        try:
            model_path = Path(self.config.model_path)
            
            if not model_path.exists():
                raise HRMEngineException(
                    f"HRM model not found at {model_path}",
                    ErrorCode.HRM_MODEL_LOAD_FAILED,
                    details={"model_path": str(model_path)}
                )
            
            # Apply mobile optimizations before loading
            optimized_config = await self.mobile_optimizer.optimize_model_loading(
                model_path=str(model_path),
                quantization=self.config.quantization,
                memory_limit_mb=self.config.memory_limit_mb
            )
            
            # Load model with optimized configuration
            # Note: This would integrate with actual model loading library (e.g., llama-cpp-python)
            logger.info(f"Loading HRM model from {model_path} with config: {optimized_config}")
            
            # Simulate model loading for now
            await asyncio.sleep(0.1)  # Simulate loading time
            
            self.model_loaded = True
            logger.info("HRM model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load HRM model: {e}")
            raise HRMEngineException(
                f"HRM model loading failed: {str(e)}",
                ErrorCode.HRM_MODEL_LOAD_FAILED,
                details={"error": str(e), "model_path": self.config.model_path}
            )
    
    @log_function_call()
    async def process_request(self, request: str, context: UserContext) -> str:
        """Process a user request using hierarchical reasoning"""
        if not self.is_initialized or not self.model_loaded:
            raise HRMEngineException(
                "HRM Engine not properly initialized",
                ErrorCode.HRM_INFERENCE_FAILED
            )
        
        start_time = time.time()
        self.total_requests += 1
        
        try:
            # Create HRM request
            hrm_request = HRMRequest(
                user_input=request,
                context=context,
                mobile_constraints=await self._get_mobile_constraints()
            )
            
            # Apply mobile optimizations
            optimized_request = await self.mobile_optimizer.optimize_request(hrm_request)
            
            # Strategic planning phase (high-level, abstract)
            strategic_plan = await self.strategic_planner.create_strategy(
                request=optimized_request.user_input,
                context=optimized_request.context,
                constraints=optimized_request.mobile_constraints
            )
            
            # Task execution phase (low-level, specific)
            execution_result = await self.task_executor.execute_strategy(
                strategy=strategic_plan,
                context=optimized_request.context
            )
            
            # Apply learning from interaction
            learning_applied = await self.learning_engine.learn_from_interaction(
                request=optimized_request.user_input,
                strategy=strategic_plan,
                result=execution_result,
                context=optimized_request.context
            )
            
            # Generate final response
            response = await self._generate_response(
                strategic_plan=strategic_plan,
                execution_result=execution_result,
                learning_applied=learning_applied
            )
            
            # Update performance metrics
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            self._update_performance_metrics(execution_time, success=True)
            
            self.successful_requests += 1
            
            logger.info(f"HRM request processed successfully in {execution_time:.2f}ms")
            return response
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self._update_performance_metrics(execution_time, success=False)
            self.last_error = str(e)
            
            logger.error(f"HRM request processing failed: {e}")
            raise HRMEngineException(
                f"HRM inference failed: {str(e)}",
                ErrorCode.HRM_INFERENCE_FAILED,
                details={"request": request, "error": str(e)}
            )
    
    async def _get_mobile_constraints(self) -> Dict[str, Any]:
        """Get current mobile device constraints"""
        return await self.mobile_optimizer.get_current_constraints()
    
    async def _generate_response(self, strategic_plan: Dict[str, Any], 
                               execution_result: Dict[str, Any],
                               learning_applied: bool) -> str:
        """Generate final response from strategic plan and execution result"""
        # Combine strategic insights with execution details
        response_parts = []
        
        if strategic_plan.get("user_message"):
            response_parts.append(strategic_plan["user_message"])
        
        if execution_result.get("response"):
            response_parts.append(execution_result["response"])
        
        if learning_applied and execution_result.get("learning_insights"):
            response_parts.append(execution_result["learning_insights"])
        
        return " ".join(response_parts) if response_parts else "I understand your request and I'm working on it."
    
    def _update_performance_metrics(self, execution_time_ms: float, success: bool) -> None:
        """Update performance tracking metrics"""
        # Update average response time (exponential moving average)
        alpha = 0.1  # Smoothing factor
        self.average_response_time = (
            alpha * execution_time_ms + 
            (1 - alpha) * self.average_response_time
        )
    
    async def learn_from_interaction(self, request: str, response: str, 
                                   feedback: Optional[Dict[str, Any]] = None) -> None:
        """Learn from user interaction and feedback"""
        if not self.learning_engine:
            return
        
        try:
            await self.learning_engine.process_feedback(
                request=request,
                response=response,
                feedback=feedback
            )
            
            logger.debug("Learning from interaction completed")
            
        except Exception as e:
            logger.error(f"Failed to learn from interaction: {e}")
    
    async def get_capabilities(self) -> List[str]:
        """Get list of HRM engine capabilities"""
        capabilities = [
            "hierarchical_reasoning",
            "strategic_planning", 
            "task_execution",
            "continuous_learning",
            "mobile_optimization",
            "battery_awareness",
            "thermal_management",
            "privacy_preservation",
            "offline_operation"
        ]
        
        if self.config.mobile_optimized:
            capabilities.extend([
                "adaptive_quantization",
                "memory_pressure_handling",
                "performance_scaling"
            ])
        
        return capabilities
    
    async def check_health(self) -> HealthStatus:
        """Check HRM engine health status"""
        try:
            # Determine status based on various factors
            if not self.is_initialized or not self.model_loaded:
                status = ComponentStatus.UNHEALTHY
                message = "HRM Engine not properly initialized"
            elif self.last_error:
                status = ComponentStatus.DEGRADED
                message = f"Recent error: {self.last_error}"
            elif self.average_response_time > 5000:  # 5 seconds
                status = ComponentStatus.DEGRADED
                message = "High response times detected"
            else:
                status = ComponentStatus.HEALTHY
                message = "HRM Engine operating normally"
            
            return HealthStatus(
                status=status,
                message=message,
                details={
                    "initialized": self.is_initialized,
                    "model_loaded": self.model_loaded,
                    "total_requests": self.total_requests,
                    "success_rate": self.successful_requests / max(self.total_requests, 1),
                    "average_response_time_ms": self.average_response_time,
                    "performance_mode": self.current_performance_mode,
                    "battery_level": self.battery_level,
                    "thermal_state": self.thermal_state
                },
                timestamp=time.time(),
                component_name="hrm_engine"
            )
            
        except Exception as e:
            return HealthStatus(
                status=ComponentStatus.UNKNOWN,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=time.time(),
                component_name="hrm_engine"
            )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get HRM engine performance metrics"""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "success_rate": self.successful_requests / max(self.total_requests, 1),
            "average_response_time_ms": self.average_response_time,
            "memory_usage_mb": await self._get_memory_usage(),
            "cpu_usage_percent": await self._get_cpu_usage(),
            "model_loaded": self.model_loaded,
            "performance_mode": self.current_performance_mode,
            "battery_level": self.battery_level,
            "thermal_state": self.thermal_state
        }
    
    async def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        # This would integrate with actual memory monitoring
        return 256.0  # Placeholder
    
    async def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        # This would integrate with actual CPU monitoring
        return 15.0  # Placeholder
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the HRM engine"""
        logger.info("Shutting down HRM Engine...")
        
        try:
            # Shutdown components in reverse order
            if self.learning_engine:
                await self.learning_engine.shutdown()
            
            if self.task_executor:
                await self.task_executor.shutdown()
            
            if self.strategic_planner:
                await self.strategic_planner.shutdown()
            
            if self.mobile_optimizer:
                await self.mobile_optimizer.shutdown()
            
            self.model_loaded = False
            self.is_initialized = False
            
            logger.info("HRM Engine shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during HRM Engine shutdown: {e}")
