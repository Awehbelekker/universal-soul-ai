"""
Advanced Multi-Modal AI Provider System
======================================

Comprehensive multi-modal AI integration for Universal Soul AI system.
Supports GPT-4 Vision, Claude Vision, Gemini Pro, and local fallbacks.
"""

import asyncio
import base64
import json
import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import io

try:
    import openai
    from anthropic import Anthropic
    import google.generativeai as genai
    from PIL import Image
    EXTERNAL_AI_AVAILABLE = True
except ImportError:
    EXTERNAL_AI_AVAILABLE = False
    openai = None
    Anthropic = None
    genai = None
    Image = None

from ..exceptions import ThinkMeshException, ErrorCode
from ..interfaces import UserContext

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Available AI providers for multi-modal analysis"""
    GPT4_VISION = "gpt4_vision"
    CLAUDE_VISION = "claude_vision"
    GEMINI_PRO_VISION = "gemini_pro_vision"
    LOCAL_VISION = "local_vision"


@dataclass
class MultiModalAnalysisResult:
    """Result from multi-modal AI analysis"""
    provider: AIProvider
    elements: List[Dict[str, Any]]
    semantic_context: Dict[str, Any]
    interaction_strategy: Dict[str, Any]
    confidence: float
    processing_time: float
    error: Optional[str] = None


@dataclass
class UIElement:
    """Enhanced UI element with semantic understanding"""
    id: str
    type: str
    purpose: str
    x: int
    y: int
    width: int
    height: int
    text: Optional[str]
    confidence: float
    interaction_method: str
    semantic_role: str


class MultiModalAIProvider:
    """
    Advanced multi-modal AI provider system
    Integrates multiple AI providers for comprehensive screen analysis
    """
    
    def __init__(self, api_keys: Dict[str, str] = None):
        self.api_keys = api_keys or {}
        self.providers = {}
        self.fallback_order = [
            AIProvider.GPT4_VISION,
            AIProvider.CLAUDE_VISION, 
            AIProvider.GEMINI_PRO_VISION,
            AIProvider.LOCAL_VISION
        ]
        self.performance_metrics = {
            provider: {"success_rate": 0.0, "avg_time": 0.0, "total_calls": 0}
            for provider in AIProvider
        }
        
    async def initialize(self) -> None:
        """Initialize all available AI providers"""
        logger.info("Initializing Multi-Modal AI Provider system...")
        
        # Initialize external providers if available
        if EXTERNAL_AI_AVAILABLE:
            await self._initialize_external_providers()
        
        # Always initialize local fallback
        await self._initialize_local_provider()
        
        logger.info(f"Initialized {len(self.providers)} AI providers")
    
    async def _initialize_external_providers(self) -> None:
        """Initialize external AI providers"""
        
        # GPT-4 Vision
        if "OPENAI_API_KEY" in self.api_keys:
            try:
                self.providers[AIProvider.GPT4_VISION] = GPT4VisionProvider(
                    api_key=self.api_keys["OPENAI_API_KEY"]
                )
                await self.providers[AIProvider.GPT4_VISION].initialize()
                logger.info("✅ GPT-4 Vision provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize GPT-4 Vision: {e}")
        
        # Claude Vision
        if "ANTHROPIC_API_KEY" in self.api_keys:
            try:
                self.providers[AIProvider.CLAUDE_VISION] = ClaudeVisionProvider(
                    api_key=self.api_keys["ANTHROPIC_API_KEY"]
                )
                await self.providers[AIProvider.CLAUDE_VISION].initialize()
                logger.info("✅ Claude Vision provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Claude Vision: {e}")
        
        # Gemini Pro Vision
        if "GOOGLE_AI_API_KEY" in self.api_keys:
            try:
                self.providers[AIProvider.GEMINI_PRO_VISION] = GeminiProVisionProvider(
                    api_key=self.api_keys["GOOGLE_AI_API_KEY"]
                )
                await self.providers[AIProvider.GEMINI_PRO_VISION].initialize()
                logger.info("✅ Gemini Pro Vision provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Pro Vision: {e}")
    
    async def _initialize_local_provider(self) -> None:
        """Initialize local vision provider as fallback"""
        try:
            from ..voice.providers import SelfHostedVisionProvider
            self.providers[AIProvider.LOCAL_VISION] = SelfHostedVisionProvider()
            await self.providers[AIProvider.LOCAL_VISION].initialize()
            logger.info("✅ Local Vision provider initialized")
        except Exception as e:
            logger.error(f"Failed to initialize local vision provider: {e}")
    
    async def analyze_screen_semantically(self, screenshot: bytes, task_context: str,
                                        preferred_provider: Optional[AIProvider] = None) -> MultiModalAnalysisResult:
        """
        Perform semantic screen analysis using multi-modal AI
        
        Args:
            screenshot: Screenshot image as bytes
            task_context: Context about the task being performed
            preferred_provider: Preferred AI provider to use first
            
        Returns:
            MultiModalAnalysisResult with semantic understanding
        """
        
        # Determine provider order
        provider_order = self._get_provider_order(preferred_provider)
        
        # Try providers in order until one succeeds
        for provider in provider_order:
            if provider not in self.providers:
                continue
                
            try:
                start_time = time.time()
                
                result = await self._analyze_with_provider(
                    provider=provider,
                    screenshot=screenshot,
                    task_context=task_context
                )
                
                processing_time = time.time() - start_time
                result.processing_time = processing_time
                
                # Update performance metrics
                await self._update_performance_metrics(provider, True, processing_time)
                
                logger.info(f"✅ Screen analysis completed with {provider.value} in {processing_time:.2f}s")
                return result
                
            except Exception as e:
                logger.warning(f"Provider {provider.value} failed: {e}")
                await self._update_performance_metrics(provider, False, 0)
                continue
        
        # If all providers fail, return basic analysis
        logger.error("All AI providers failed, returning basic analysis")
        return await self._create_fallback_analysis(screenshot, task_context)
    
    async def _analyze_with_provider(self, provider: AIProvider, screenshot: bytes,
                                   task_context: str) -> MultiModalAnalysisResult:
        """Analyze screenshot with specific provider"""
        
        provider_instance = self.providers[provider]
        
        if provider == AIProvider.LOCAL_VISION:
            # Local vision analysis
            description = await provider_instance.analyze_image(
                screenshot, 
                f"Analyze this mobile interface for task: {task_context}. "
                "Identify interactive elements and their purposes."
            )
            return self._parse_local_vision_result(description, provider)
        else:
            # External AI provider analysis
            return await provider_instance.analyze_ui_semantically(screenshot, task_context)
    
    def _get_provider_order(self, preferred_provider: Optional[AIProvider]) -> List[AIProvider]:
        """Get provider order based on preference and performance"""
        
        if preferred_provider and preferred_provider in self.providers:
            # Put preferred provider first
            order = [preferred_provider]
            order.extend([p for p in self.fallback_order if p != preferred_provider])
            return order
        
        # Sort by success rate and availability
        available_providers = [p for p in self.fallback_order if p in self.providers]
        return sorted(available_providers, 
                     key=lambda p: self.performance_metrics[p]["success_rate"], 
                     reverse=True)
    
    async def _update_performance_metrics(self, provider: AIProvider, success: bool, 
                                        processing_time: float) -> None:
        """Update performance metrics for provider"""
        metrics = self.performance_metrics[provider]
        metrics["total_calls"] += 1
        
        if success:
            # Update success rate
            current_successes = metrics["success_rate"] * (metrics["total_calls"] - 1)
            metrics["success_rate"] = (current_successes + 1) / metrics["total_calls"]
            
            # Update average time
            current_time_total = metrics["avg_time"] * (metrics["total_calls"] - 1)
            metrics["avg_time"] = (current_time_total + processing_time) / metrics["total_calls"]
        else:
            # Update success rate only
            current_successes = metrics["success_rate"] * (metrics["total_calls"] - 1)
            metrics["success_rate"] = current_successes / metrics["total_calls"]
    
    def _parse_local_vision_result(self, description: str, provider: AIProvider) -> MultiModalAnalysisResult:
        """Parse local vision analysis result"""
        
        # Basic parsing of local vision description
        elements = []
        semantic_context = {"description": description, "provider": "local"}
        interaction_strategy = {"method": "basic", "confidence": 0.6}
        
        return MultiModalAnalysisResult(
            provider=provider,
            elements=elements,
            semantic_context=semantic_context,
            interaction_strategy=interaction_strategy,
            confidence=0.6,
            processing_time=0.0
        )
    
    async def _create_fallback_analysis(self, screenshot: bytes, task_context: str) -> MultiModalAnalysisResult:
        """Create basic fallback analysis when all providers fail"""
        
        return MultiModalAnalysisResult(
            provider=AIProvider.LOCAL_VISION,
            elements=[],
            semantic_context={"error": "All providers failed", "fallback": True},
            interaction_strategy={"method": "basic", "confidence": 0.3},
            confidence=0.3,
            processing_time=0.0,
            error="All AI providers failed"
        )
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report for all providers"""
        return {
            "providers": dict(self.performance_metrics),
            "available_providers": list(self.providers.keys()),
            "total_providers": len(self.providers)
        }


# Provider implementations will be added in separate files
class GPT4VisionProvider:
    """GPT-4 Vision provider implementation"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
    
    async def initialize(self) -> None:
        """Initialize GPT-4 Vision client"""
        if not openai:
            raise ThinkMeshException("OpenAI library not available", ErrorCode.DEPENDENCY_ERROR)
        
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
    
    async def analyze_ui_semantically(self, screenshot: bytes, task_context: str) -> MultiModalAnalysisResult:
        """Analyze UI with GPT-4 Vision"""
        from .gpt4_vision_provider import GPT4VisionProvider
        provider = GPT4VisionProvider(self.api_key)
        await provider.initialize()
        return await provider.analyze_ui_semantically(screenshot, task_context)


class ClaudeVisionProvider:
    """Claude Vision provider implementation"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None

    async def initialize(self) -> None:
        """Initialize Claude Vision client"""
        if not Anthropic:
            raise ThinkMeshException("Anthropic library not available", ErrorCode.DEPENDENCY_ERROR)

        self.client = Anthropic(api_key=self.api_key)

    async def analyze_ui_semantically(self, screenshot: bytes, task_context: str) -> MultiModalAnalysisResult:
        """Analyze UI with Claude Vision"""
        from .claude_vision_provider import ClaudeVisionProvider
        provider = ClaudeVisionProvider(self.api_key)
        await provider.initialize()
        return await provider.analyze_ui_semantically(screenshot, task_context)


class GeminiProVisionProvider:
    """Gemini Pro Vision provider implementation"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = None

    async def initialize(self) -> None:
        """Initialize Gemini Pro Vision"""
        if not genai:
            raise ThinkMeshException("Google AI library not available", ErrorCode.DEPENDENCY_ERROR)

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')

    async def analyze_ui_semantically(self, screenshot: bytes, task_context: str) -> MultiModalAnalysisResult:
        """Analyze UI with Gemini Pro Vision"""
        # Implementation will be added in next phase
        pass
