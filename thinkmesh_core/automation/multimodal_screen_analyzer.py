"""
Multi-Modal Screen Analyzer
===========================

Enhanced screen analyzer combining traditional computer vision with AI-powered semantic understanding.
Integrates multiple AI providers for comprehensive interface analysis.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

try:
    import cv2
    import numpy as np
    from PIL import Image
    VISION_LIBS_AVAILABLE = True
    ArrayType = np.ndarray
except ImportError:
    VISION_LIBS_AVAILABLE = False
    cv2 = None
    np = None
    Image = None
    ArrayType = Any

from ..ai_providers import MultiModalAIProvider, AIProvider, MultiModalAnalysisResult
from ..interfaces import UserContext
from ..exceptions import ThinkMeshException, ErrorCode
from .enhanced_screen_analyzer import EnhancedScreenAnalyzer, EnhancedScreenAnalysis

logger = logging.getLogger(__name__)


@dataclass
class TaskContext:
    """Context information for task analysis"""
    description: str
    user_context: UserContext
    platform: str
    complexity: str
    app_context: Optional[str] = None
    previous_actions: Optional[List[str]] = None


@dataclass
class MultiModalScreenAnalysis:
    """Comprehensive screen analysis result combining CV and AI"""
    # Traditional computer vision results
    cv_elements: List[Dict[str, Any]]
    cv_confidence: float
    
    # AI semantic analysis results
    ai_elements: List[Dict[str, Any]]
    ai_semantic_context: Dict[str, Any]
    ai_interaction_strategy: Dict[str, Any]
    ai_confidence: float
    
    # Fused results
    fused_elements: List[Dict[str, Any]]
    fused_confidence: float
    
    # Analysis metadata
    processing_time: float
    providers_used: List[str]
    analysis_method: str
    
    # Task-specific insights
    task_feasibility: float
    recommended_actions: List[str]
    potential_issues: List[str]


class AdaptiveConfidenceCalibrator:
    """Calibrates confidence scores based on historical performance"""
    
    def __init__(self):
        self.historical_performance = {}
        self.calibration_data = {}
        
    async def calibrate_confidence(self, fused_analysis: Dict[str, Any],
                                 historical_performance: Dict[str, Any],
                                 task_complexity: str) -> float:
        """Calibrate confidence based on historical performance"""
        
        base_confidence = fused_analysis.get("confidence", 0.7)
        
        # Adjust based on task complexity
        complexity_adjustments = {
            "simple": 0.1,
            "medium": 0.0,
            "complex": -0.1,
            "very_complex": -0.2
        }
        
        adjusted_confidence = base_confidence + complexity_adjustments.get(task_complexity, 0.0)
        
        # Adjust based on historical performance
        if historical_performance:
            success_rate = historical_performance.get("success_rate", 0.7)
            performance_adjustment = (success_rate - 0.7) * 0.2
            adjusted_confidence += performance_adjustment
        
        return max(0.1, min(0.95, adjusted_confidence))


class MultiModalScreenAnalyzer:
    """
    Enhanced screen analyzer with AI-powered semantic understanding
    Combines traditional computer vision with multi-modal AI analysis
    """
    
    def __init__(self, api_keys: Dict[str, str] = None):
        self.multimodal_ai = MultiModalAIProvider(api_keys)
        self.traditional_cv = EnhancedScreenAnalyzer() if VISION_LIBS_AVAILABLE else None
        self.confidence_calibrator = AdaptiveConfidenceCalibrator()
        self.performance_history = {}
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """Initialize all analysis components"""
        logger.info("Initializing Multi-Modal Screen Analyzer...")
        
        # Initialize AI providers
        await self.multimodal_ai.initialize()
        
        # Initialize traditional CV if available
        if self.traditional_cv:
            logger.info("Traditional computer vision available")
        else:
            logger.warning("Traditional computer vision not available - AI-only mode")
        
        self.is_initialized = True
        logger.info("Multi-Modal Screen Analyzer initialized successfully")
    
    async def analyze_screen_comprehensive(self, screenshot: Union[bytes, ArrayType], 
                                         task_context: TaskContext) -> MultiModalScreenAnalysis:
        """
        Comprehensive analysis combining traditional CV + AI
        
        Args:
            screenshot: Screenshot as bytes or numpy array
            task_context: Context about the task being performed
            
        Returns:
            MultiModalScreenAnalysis with comprehensive results
        """
        
        if not self.is_initialized:
            await self.initialize()
        
        start_time = time.time()
        
        # Convert screenshot to appropriate format
        screenshot_bytes = await self._prepare_screenshot(screenshot)
        
        # Run parallel analysis
        analysis_tasks = []
        providers_used = []
        
        # Traditional computer vision (fast, local)
        if self.traditional_cv and VISION_LIBS_AVAILABLE:
            analysis_tasks.append(self._run_traditional_cv_analysis(screenshot))
            providers_used.append("traditional_cv")
        
        # AI-powered semantic analysis (slower, more accurate)
        analysis_tasks.append(self._run_ai_semantic_analysis(screenshot_bytes, task_context))
        providers_used.append("multimodal_ai")
        
        # Execute analyses in parallel
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        # Process results
        cv_result = None
        ai_result = None
        
        if len(results) == 2 and self.traditional_cv:
            cv_result, ai_result = results
        elif len(results) == 1:
            ai_result = results[0]
        
        # Handle exceptions
        if isinstance(cv_result, Exception):
            logger.warning(f"Traditional CV analysis failed: {cv_result}")
            cv_result = None
        
        if isinstance(ai_result, Exception):
            logger.warning(f"AI analysis failed: {ai_result}")
            ai_result = None
        
        # Fuse analysis results
        fused_analysis = await self._fuse_analysis_results(
            cv_result=cv_result,
            ai_result=ai_result,
            task_context=task_context
        )
        
        # Calibrate confidence
        calibrated_confidence = await self.confidence_calibrator.calibrate_confidence(
            fused_analysis=fused_analysis,
            historical_performance=self._get_historical_performance(task_context),
            task_complexity=task_context.complexity
        )
        
        processing_time = time.time() - start_time
        
        # Create comprehensive analysis result
        analysis = MultiModalScreenAnalysis(
            cv_elements=cv_result.ui_elements if cv_result else [],
            cv_confidence=cv_result.confidence_score if cv_result else 0.0,
            ai_elements=ai_result.elements if ai_result else [],
            ai_semantic_context=ai_result.semantic_context if ai_result else {},
            ai_interaction_strategy=ai_result.interaction_strategy if ai_result else {},
            ai_confidence=ai_result.confidence if ai_result else 0.0,
            fused_elements=fused_analysis.get("elements", []),
            fused_confidence=calibrated_confidence,
            processing_time=processing_time,
            providers_used=providers_used,
            analysis_method="multimodal_fusion",
            task_feasibility=fused_analysis.get("task_feasibility", 0.7),
            recommended_actions=fused_analysis.get("recommended_actions", []),
            potential_issues=fused_analysis.get("potential_issues", [])
        )
        
        logger.info(f"Comprehensive analysis completed in {processing_time:.2f}s with confidence {calibrated_confidence:.2f}")
        return analysis
    
    async def _prepare_screenshot(self, screenshot: Union[bytes, ArrayType]) -> bytes:
        """Convert screenshot to bytes format for AI analysis"""
        
        if isinstance(screenshot, bytes):
            return screenshot
        
        if VISION_LIBS_AVAILABLE and isinstance(screenshot, np.ndarray):
            # Convert numpy array to bytes
            try:
                # Convert to PIL Image
                if len(screenshot.shape) == 3:
                    # Color image
                    image = Image.fromarray(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))
                else:
                    # Grayscale image
                    image = Image.fromarray(screenshot)
                
                # Convert to bytes
                import io
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='JPEG', quality=85)
                return img_bytes.getvalue()
                
            except Exception as e:
                logger.error(f"Failed to convert screenshot to bytes: {e}")
                raise ThinkMeshException("Screenshot conversion failed", ErrorCode.PROCESSING_ERROR)
        
        raise ThinkMeshException("Unsupported screenshot format", ErrorCode.INVALID_INPUT)
    
    async def _run_traditional_cv_analysis(self, screenshot: ArrayType) -> Optional[EnhancedScreenAnalysis]:
        """Run traditional computer vision analysis"""
        
        try:
            if self.traditional_cv:
                return await self.traditional_cv.analyze_screen_ensemble(screenshot)
            return None
        except Exception as e:
            logger.error(f"Traditional CV analysis failed: {e}")
            return None
    
    async def _run_ai_semantic_analysis(self, screenshot_bytes: bytes, 
                                      task_context: TaskContext) -> Optional[MultiModalAnalysisResult]:
        """Run AI-powered semantic analysis"""
        
        try:
            return await self.multimodal_ai.analyze_screen_semantically(
                screenshot=screenshot_bytes,
                task_context=task_context.description
            )
        except Exception as e:
            logger.error(f"AI semantic analysis failed: {e}")
            return None
    
    async def _fuse_analysis_results(self, cv_result: Optional[EnhancedScreenAnalysis],
                                   ai_result: Optional[MultiModalAnalysisResult],
                                   task_context: TaskContext) -> Dict[str, Any]:
        """Intelligently fuse CV and AI analysis results"""
        
        fused_elements = []
        recommended_actions = []
        potential_issues = []
        task_feasibility = 0.5
        
        # Combine elements from both analyses
        if cv_result:
            # Add CV elements with geometric accuracy
            for elem in cv_result.ui_elements:
                fused_elem = {
                    "source": "computer_vision",
                    "geometric_accuracy": "high",
                    "semantic_understanding": "low",
                    **elem
                }
                fused_elements.append(fused_elem)
        
        if ai_result:
            # Add AI elements with semantic understanding
            for elem in ai_result.elements:
                fused_elem = {
                    "source": "ai_semantic",
                    "geometric_accuracy": "medium",
                    "semantic_understanding": "high",
                    **elem
                }
                fused_elements.append(fused_elem)
            
            # Extract strategic insights from AI
            if ai_result.interaction_strategy:
                recommended_actions = ai_result.interaction_strategy.get("step_by_step", [])
                potential_issues = ai_result.interaction_strategy.get("risk_factors", [])
            
            # Calculate task feasibility
            if ai_result.semantic_context:
                confidence_data = ai_result.semantic_context.get("confidence_assessment", {})
                task_feasibility = confidence_data.get("task_completion_probability", 0.7)
        
        # Remove duplicate elements (same position, different sources)
        deduplicated_elements = await self._deduplicate_elements(fused_elements)
        
        return {
            "elements": deduplicated_elements,
            "confidence": self._calculate_fusion_confidence(cv_result, ai_result),
            "task_feasibility": task_feasibility,
            "recommended_actions": recommended_actions,
            "potential_issues": potential_issues
        }
    
    async def _deduplicate_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate elements from different sources"""
        
        deduplicated = []
        position_threshold = 50  # pixels
        
        for elem in elements:
            is_duplicate = False
            
            for existing in deduplicated:
                # Check if elements are at similar positions
                x_diff = abs(elem.get("x", 0) - existing.get("x", 0))
                y_diff = abs(elem.get("y", 0) - existing.get("y", 0))
                
                if x_diff < position_threshold and y_diff < position_threshold:
                    # Merge information from both sources
                    if elem.get("source") == "ai_semantic":
                        # Prefer AI semantic information
                        existing.update({
                            "purpose": elem.get("purpose", existing.get("purpose")),
                            "semantic_role": elem.get("semantic_role", existing.get("semantic_role")),
                            "interaction_method": elem.get("interaction_method", existing.get("interaction_method"))
                        })
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                deduplicated.append(elem)
        
        return deduplicated
    
    def _calculate_fusion_confidence(self, cv_result: Optional[EnhancedScreenAnalysis],
                                   ai_result: Optional[MultiModalAnalysisResult]) -> float:
        """Calculate confidence for fused analysis"""
        
        confidences = []
        
        if cv_result:
            confidences.append(cv_result.confidence_score * 0.4)  # CV weight: 40%
        
        if ai_result:
            confidences.append(ai_result.confidence * 0.6)  # AI weight: 60%
        
        if not confidences:
            return 0.3  # Fallback confidence
        
        return sum(confidences)
    
    def _get_historical_performance(self, task_context: TaskContext) -> Dict[str, Any]:
        """Get historical performance data for similar tasks"""
        
        task_type = task_context.description.split()[0].lower()  # Simple task categorization
        return self.performance_history.get(task_type, {"success_rate": 0.7, "avg_time": 2.0})
    
    async def get_analysis_capabilities(self) -> Dict[str, Any]:
        """Get current analysis capabilities"""
        
        capabilities = {
            "traditional_cv_available": self.traditional_cv is not None,
            "ai_providers_available": len(self.multimodal_ai.providers),
            "multimodal_fusion": True,
            "adaptive_confidence": True
        }
        
        if self.multimodal_ai:
            ai_performance = await self.multimodal_ai.get_performance_report()
            capabilities["ai_performance"] = ai_performance
        
        return capabilities
