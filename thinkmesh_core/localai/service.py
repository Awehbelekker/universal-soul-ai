"""
LocalAI Service
===============

Main local AI inference service providing OpenAI-compatible API
for local model inference with mobile optimization.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging

from ..interfaces import IAIEngine, IHealthCheck, ComponentStatus, HealthStatus, UserContext
from ..config import LocalAIConfig
from ..exceptions import ThinkMeshException, ErrorCode
from ..logging import get_logger, log_function_call, log_component_lifecycle

logger = get_logger(__name__)


class InferenceMode(Enum):
    """Inference modes for different use cases"""
    FAST = "fast"
    BALANCED = "balanced"
    QUALITY = "quality"
    MOBILE_OPTIMIZED = "mobile_optimized"


@dataclass
class InferenceRequest:
    """Request structure for local AI inference"""
    prompt: str
    context: UserContext
    model_name: Optional[str] = None
    max_tokens: int = 150
    temperature: float = 0.7
    mode: InferenceMode = InferenceMode.BALANCED
    stream: bool = False
    mobile_constraints: Optional[Dict[str, Any]] = None


@dataclass
class InferenceResult:
    """Result structure from local AI inference"""
    response: str
    model_used: str
    tokens_generated: int
    inference_time_ms: float
    confidence_score: float
    mode_used: InferenceMode
    mobile_optimizations: Dict[str, Any]
    metadata: Dict[str, Any]


@log_component_lifecycle("localai_service")
class LocalAIService(IAIEngine, IHealthCheck):
    """
    LocalAI Service
    
    Provides local AI inference with OpenAI-compatible API,
    optimized for mobile devices with privacy-first design.
    """
    
    def __init__(self, config: LocalAIConfig):
        self.config = config
        self.is_initialized = False
        
        # Core components
        self.model_manager = None
        self.inference_engine = None
        self.model_optimizer = None
        
        # Performance tracking
        self.total_inferences = 0
        self.successful_inferences = 0
        self.average_inference_time = 0.0
        self.model_usage: Dict[str, int] = {}
        
        # Mobile state
        self.current_mode = InferenceMode.BALANCED
        self.mobile_constraints: Dict[str, Any] = {}
        
        logger.info("LocalAI Service created")
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the LocalAI service"""
        if self.is_initialized:
            logger.warning("LocalAI Service already initialized")
            return
        
        try:
            logger.info("Initializing LocalAI Service...")
            
            # Update config if provided
            if config:
                for key, value in config.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
            
            # Initialize components
            await self._initialize_model_manager()
            await self._initialize_inference_engine()
            await self._initialize_model_optimizer()
            
            # Load default models
            await self._load_default_models()
            
            self.is_initialized = True
            logger.info("LocalAI Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LocalAI Service: {e}")
            raise ThinkMeshException(
                f"LocalAI Service initialization failed: {str(e)}",
                ErrorCode.LOCALAI_INITIALIZATION_FAILED,
                details={"error": str(e), "config": self.config.__dict__}
            )
    
    @log_function_call()
    async def process_request(self, request: str, context: UserContext) -> str:
        """Process inference request"""
        if not self.is_initialized:
            raise ThinkMeshException(
                "LocalAI Service not initialized",
                ErrorCode.LOCALAI_NOT_INITIALIZED
            )
        
        start_time = time.time()
        self.total_inferences += 1
        
        try:
            # Create inference request
            inference_request = InferenceRequest(
                prompt=request,
                context=context,
                model_name=self.config.default_model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                mode=self.current_mode,
                mobile_constraints=self.mobile_constraints.copy()
            )
            
            # Perform inference
            result = await self._perform_inference(inference_request)
            
            # Update performance metrics
            inference_time = (time.time() - start_time) * 1000
            self._update_performance_metrics(inference_time, True)
            
            self.successful_inferences += 1
            
            logger.info(f"LocalAI inference completed in {inference_time:.2f}ms")
            return result.response
            
        except Exception as e:
            inference_time = (time.time() - start_time) * 1000
            self._update_performance_metrics(inference_time, False)
            
            logger.error(f"LocalAI inference failed: {e}")
            raise ThinkMeshException(
                f"LocalAI inference failed: {str(e)}",
                ErrorCode.LOCALAI_INFERENCE_FAILED,
                details={"request": request, "error": str(e)}
            )
    
    async def _perform_inference(self, request: InferenceRequest) -> InferenceResult:
        """Perform the actual inference"""
        try:
            # Select optimal model
            model_name = await self._select_model(request)
            
            # Apply mobile optimizations
            optimized_request = await self.model_optimizer.optimize_request(
                request, self.mobile_constraints
            )
            
            # Perform inference
            inference_result = await self.inference_engine.infer(
                model_name=model_name,
                prompt=optimized_request.prompt,
                max_tokens=optimized_request.max_tokens,
                temperature=optimized_request.temperature,
                mode=optimized_request.mode
            )
            
            # Update model usage
            self.model_usage[model_name] = self.model_usage.get(model_name, 0) + 1
            
            return inference_result
            
        except Exception as e:
            logger.error(f"Inference execution failed: {e}")
            raise
    
    async def _select_model(self, request: InferenceRequest) -> str:
        """Select optimal model for the request"""
        if request.model_name:
            # Use specified model if available
            available_models = await self.model_manager.get_available_models()
            if request.model_name in available_models:
                return request.model_name
        
        # Select based on mode and constraints
        if request.mode == InferenceMode.FAST:
            return await self._select_fast_model(request)
        elif request.mode == InferenceMode.QUALITY:
            return await self._select_quality_model(request)
        elif request.mode == InferenceMode.MOBILE_OPTIMIZED:
            return await self._select_mobile_model(request)
        else:
            # Balanced mode
            return await self._select_balanced_model(request)
    
    async def _select_fast_model(self, request: InferenceRequest) -> str:
        """Select fastest available model"""
        # Prefer smaller, faster models
        fast_models = ["gpt-oss-20b-q4", "llama-7b-q4", "mistral-7b-q4"]
        available_models = await self.model_manager.get_available_models()
        
        for model in fast_models:
            if model in available_models:
                return model
        
        # Fallback to default
        return self.config.default_model
    
    async def _select_quality_model(self, request: InferenceRequest) -> str:
        """Select highest quality available model"""
        # Prefer larger, higher quality models
        quality_models = ["gpt-oss-120b-q8", "llama-70b-q8", "mixtral-8x7b-q8"]
        available_models = await self.model_manager.get_available_models()
        
        for model in quality_models:
            if model in available_models:
                return model
        
        # Fallback to default
        return self.config.default_model
    
    async def _select_mobile_model(self, request: InferenceRequest) -> str:
        """Select mobile-optimized model"""
        # Prefer models optimized for mobile
        mobile_models = ["hrm-27m-mobile", "gpt-oss-20b-mobile", "llama-7b-mobile"]
        available_models = await self.model_manager.get_available_models()
        
        for model in mobile_models:
            if model in available_models:
                return model
        
        # Fallback to smallest available model
        return await self._select_fast_model(request)
    
    async def _select_balanced_model(self, request: InferenceRequest) -> str:
        """Select balanced model for quality and speed"""
        # Balance between quality and speed
        balanced_models = ["gpt-oss-20b-q8", "llama-13b-q8", "mistral-7b-q8"]
        available_models = await self.model_manager.get_available_models()
        
        for model in balanced_models:
            if model in available_models:
                return model
        
        # Fallback to default
        return self.config.default_model
    
    async def update_mobile_constraints(self, constraints: Dict[str, Any]) -> None:
        """Update mobile device constraints"""
        try:
            self.mobile_constraints.update(constraints)
            
            # Adjust inference mode based on constraints
            battery_level = constraints.get("battery_level", 1.0)
            thermal_state = constraints.get("thermal_state", "normal")
            memory_pressure = constraints.get("memory_pressure", 0.0)
            
            if battery_level < 0.2 or thermal_state == "critical":
                self.current_mode = InferenceMode.MOBILE_OPTIMIZED
            elif battery_level < 0.5 or thermal_state == "hot" or memory_pressure > 0.8:
                self.current_mode = InferenceMode.FAST
            elif battery_level > 0.8 and thermal_state == "normal" and memory_pressure < 0.3:
                self.current_mode = InferenceMode.QUALITY
            else:
                self.current_mode = InferenceMode.BALANCED
            
            logger.debug(f"Updated mobile constraints, mode: {self.current_mode.value}")
            
        except Exception as e:
            logger.error(f"Failed to update mobile constraints: {e}")
    
    async def get_available_models(self) -> List[str]:
        """Get list of available models"""
        if not self.model_manager:
            return []
        
        return await self.model_manager.get_available_models()
    
    async def load_model(self, model_name: str, model_path: str,
                        quantization: Optional[str] = None) -> bool:
        """Load a new model"""
        try:
            if not self.model_manager:
                return False
            
            success = await self.model_manager.load_model(
                model_name=model_name,
                model_path=model_path,
                quantization=quantization
            )
            
            if success:
                logger.info(f"Model {model_name} loaded successfully")
            else:
                logger.error(f"Failed to load model {model_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            return False
    
    async def unload_model(self, model_name: str) -> bool:
        """Unload a model to free memory"""
        try:
            if not self.model_manager:
                return False
            
            success = await self.model_manager.unload_model(model_name)
            
            if success:
                logger.info(f"Model {model_name} unloaded successfully")
            else:
                logger.error(f"Failed to unload model {model_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Model unloading failed: {e}")
            return False
    
    def _update_performance_metrics(self, inference_time_ms: float, success: bool) -> None:
        """Update performance tracking metrics"""
        # Update average inference time
        alpha = 0.1
        self.average_inference_time = (
            alpha * inference_time_ms + 
            (1 - alpha) * self.average_inference_time
        )
    
    async def get_capabilities(self) -> List[str]:
        """Get LocalAI service capabilities"""
        return [
            "local_inference",
            "model_management",
            "mobile_optimization",
            "quantization_support",
            "openai_compatibility",
            "privacy_preservation",
            "offline_operation",
            "multi_model_support"
        ]
    
    async def check_health(self) -> HealthStatus:
        """Check LocalAI service health status"""
        try:
            if not self.is_initialized:
                status = ComponentStatus.UNHEALTHY
                message = "LocalAI Service not initialized"
            elif not self.model_manager or not await self.model_manager.has_loaded_models():
                status = ComponentStatus.DEGRADED
                message = "No models loaded"
            elif self.average_inference_time > 5000:  # 5 seconds
                status = ComponentStatus.DEGRADED
                message = "High inference times"
            else:
                status = ComponentStatus.HEALTHY
                message = "LocalAI Service operating normally"
            
            return HealthStatus(
                status=status,
                message=message,
                details={
                    "initialized": self.is_initialized,
                    "total_inferences": self.total_inferences,
                    "success_rate": self.successful_inferences / max(self.total_inferences, 1),
                    "average_inference_time_ms": self.average_inference_time,
                    "current_mode": self.current_mode.value,
                    "available_models": len(await self.get_available_models()) if self.is_initialized else 0,
                    "model_usage": self.model_usage
                },
                timestamp=time.time(),
                component_name="localai_service"
            )
            
        except Exception as e:
            return HealthStatus(
                status=ComponentStatus.UNKNOWN,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=time.time(),
                component_name="localai_service"
            )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get LocalAI service performance metrics"""
        return {
            "total_inferences": self.total_inferences,
            "successful_inferences": self.successful_inferences,
            "success_rate": self.successful_inferences / max(self.total_inferences, 1),
            "average_inference_time_ms": self.average_inference_time,
            "current_mode": self.current_mode.value,
            "model_usage": self.model_usage.copy(),
            "mobile_constraints": self.mobile_constraints.copy()
        }
    
    async def _initialize_model_manager(self) -> None:
        """Initialize the model manager"""
        from .model_manager import ModelManager
        self.model_manager = ModelManager(self.config)
        await self.model_manager.initialize()
        logger.debug("Model manager initialized")
    
    async def _initialize_inference_engine(self) -> None:
        """Initialize the inference engine"""
        from .inference_engine import InferenceEngine
        self.inference_engine = InferenceEngine(self.config)
        await self.inference_engine.initialize()
        logger.debug("Inference engine initialized")
    
    async def _initialize_model_optimizer(self) -> None:
        """Initialize the model optimizer"""
        from .model_optimizer import ModelOptimizer
        self.model_optimizer = ModelOptimizer(self.config)
        await self.model_optimizer.initialize()
        logger.debug("Model optimizer initialized")
    
    async def _load_default_models(self) -> None:
        """Load default models"""
        try:
            # Load HRM model as default
            if self.config.hrm_model_path:
                await self.load_model(
                    model_name="hrm-27m",
                    model_path=self.config.hrm_model_path,
                    quantization="int8"
                )
            
            # Load additional default models if configured
            for model_config in self.config.default_models:
                await self.load_model(
                    model_name=model_config["name"],
                    model_path=model_config["path"],
                    quantization=model_config.get("quantization", "int8")
                )
            
            logger.info("Default models loaded")
            
        except Exception as e:
            logger.warning(f"Failed to load some default models: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown the LocalAI service"""
        logger.info("Shutting down LocalAI Service...")
        
        try:
            # Shutdown components
            if self.model_optimizer:
                await self.model_optimizer.shutdown()
            
            if self.inference_engine:
                await self.inference_engine.shutdown()
            
            if self.model_manager:
                await self.model_manager.shutdown()
            
            self.is_initialized = False
            logger.info("LocalAI Service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during LocalAI Service shutdown: {e}")
