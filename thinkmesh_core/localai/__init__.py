"""
LocalAI Service Integration
===========================

Local AI inference service with model management, quantization,
and mobile optimization for privacy-first AI processing.

Components:
- LocalAIService: Main local AI inference service
- ModelManager: Model loading, quantization, and lifecycle management
- InferenceEngine: Optimized inference with mobile constraints
- ModelOptimizer: Model optimization for mobile deployment
"""

from .service import LocalAIService, InferenceRequest, InferenceResult
# TODO: Implement missing modules for full functionality
# from .model_manager import ModelManager, ModelConfig, ModelStatus
# from .inference_engine import InferenceEngine, InferenceConfig
# from .model_optimizer import ModelOptimizer, OptimizationConfig

__all__ = [
    # Main service
    "LocalAIService",
    "InferenceRequest",
    "InferenceResult",

    # TODO: Add when modules are implemented
    # "ModelManager",
    # "ModelConfig",
    # "ModelStatus",
    # "InferenceEngine",
    # "InferenceConfig",
    # "ModelOptimizer",
    # "OptimizationConfig"
]
