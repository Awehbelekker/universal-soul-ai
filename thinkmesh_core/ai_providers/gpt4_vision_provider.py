"""
GPT-4 Vision Provider Implementation
===================================

Advanced GPT-4 Vision integration for semantic UI analysis and understanding.
"""

import asyncio
import base64
import json
import logging
import time
from typing import Dict, Any, List, Optional
import io

try:
    import openai
    from PIL import Image
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None
    Image = None

from ..exceptions import ThinkMeshException, ErrorCode
from .multimodal_ai_provider import MultiModalAnalysisResult, AIProvider, UIElement

logger = logging.getLogger(__name__)


class GPT4VisionProvider:
    """
    GPT-4 Vision provider for semantic UI analysis
    Provides advanced understanding of mobile interfaces and user intent
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self.model = "gpt-4-vision-preview"
        self.max_tokens = 1500
        self.temperature = 0.1  # Low temperature for consistent analysis
        
    async def initialize(self) -> None:
        """Initialize GPT-4 Vision client"""
        if not OPENAI_AVAILABLE:
            raise ThinkMeshException("OpenAI library not available", ErrorCode.DEPENDENCY_ERROR)
        
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
        
        # Test connection
        try:
            await self._test_connection()
            logger.info("GPT-4 Vision provider initialized successfully")
        except Exception as e:
            raise ThinkMeshException(f"Failed to initialize GPT-4 Vision: {e}", ErrorCode.API_ERROR)
    
    async def _test_connection(self) -> None:
        """Test API connection"""
        try:
            # Simple test call
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10
            )
            logger.debug("GPT-4 Vision connection test successful")
        except Exception as e:
            logger.error(f"GPT-4 Vision connection test failed: {e}")
            raise
    
    async def analyze_ui_semantically(self, screenshot: bytes, task_context: str) -> MultiModalAnalysisResult:
        """
        Analyze mobile UI with semantic understanding using GPT-4 Vision
        
        Args:
            screenshot: Screenshot image as bytes
            task_context: Context about the task being performed
            
        Returns:
            MultiModalAnalysisResult with semantic analysis
        """
        
        start_time = time.time()
        
        try:
            # Convert screenshot to base64
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            
            # Create comprehensive analysis prompt
            prompt = self._create_analysis_prompt(task_context)
            
            # Call GPT-4 Vision
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url", 
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{screenshot_b64}",
                                "detail": "high"
                            }
                        }
                    ]
                }],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Parse response
            analysis_text = response.choices[0].message.content
            parsed_result = await self._parse_gpt4_response(analysis_text, task_context)
            
            processing_time = time.time() - start_time
            parsed_result.processing_time = processing_time
            
            logger.debug(f"GPT-4 Vision analysis completed in {processing_time:.2f}s")
            return parsed_result
            
        except Exception as e:
            logger.error(f"GPT-4 Vision analysis failed: {e}")
            raise ThinkMeshException(f"GPT-4 Vision analysis error: {e}", ErrorCode.API_ERROR)
    
    def _create_analysis_prompt(self, task_context: str) -> str:
        """Create comprehensive analysis prompt for GPT-4 Vision"""
        
        return f"""
Analyze this mobile interface screenshot for the task: "{task_context}"

Please provide a comprehensive analysis in JSON format with the following structure:

{{
    "interface_type": "app_name or interface_type",
    "ui_elements": [
        {{
            "id": "unique_element_id",
            "type": "button|input|text|image|icon|menu|etc",
            "purpose": "what this element does",
            "text": "visible text if any",
            "coordinates": {{"x": 0, "y": 0, "width": 0, "height": 0}},
            "interaction_method": "tap|swipe|long_press|type|etc",
            "semantic_role": "primary_action|navigation|content|input|etc",
            "confidence": 0.0-1.0
        }}
    ],
    "semantic_context": {{
        "app_state": "current state of the app",
        "user_flow_position": "where user is in the workflow",
        "available_actions": ["list of possible actions"],
        "primary_goal_elements": ["elements most relevant to the task"]
    }},
    "interaction_strategy": {{
        "recommended_approach": "best way to accomplish the task",
        "step_by_step": ["ordered steps to complete task"],
        "alternative_paths": ["backup approaches if primary fails"],
        "risk_factors": ["potential issues or complications"],
        "success_indicators": ["how to know if task succeeded"]
    }},
    "confidence_assessment": {{
        "overall_confidence": 0.0-1.0,
        "element_detection_confidence": 0.0-1.0,
        "task_completion_probability": 0.0-1.0,
        "complexity_level": "simple|medium|complex|very_complex"
    }}
}}

Focus on:
1. Identifying ALL interactive elements with precise coordinates
2. Understanding the PURPOSE and FUNCTION of each element
3. Determining the optimal interaction strategy for the given task
4. Assessing the likelihood of successful task completion
5. Providing fallback strategies if the primary approach fails

Be precise with coordinates and confident in your assessments.
"""
    
    async def _parse_gpt4_response(self, response_text: str, task_context: str) -> MultiModalAnalysisResult:
        """Parse GPT-4 Vision response into structured result"""
        
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[json_start:json_end]
            analysis_data = json.loads(json_text)
            
            # Convert to UIElement objects
            elements = []
            for elem_data in analysis_data.get("ui_elements", []):
                element = UIElement(
                    id=elem_data.get("id", f"elem_{len(elements)}"),
                    type=elem_data.get("type", "unknown"),
                    purpose=elem_data.get("purpose", ""),
                    x=elem_data.get("coordinates", {}).get("x", 0),
                    y=elem_data.get("coordinates", {}).get("y", 0),
                    width=elem_data.get("coordinates", {}).get("width", 0),
                    height=elem_data.get("coordinates", {}).get("height", 0),
                    text=elem_data.get("text"),
                    confidence=elem_data.get("confidence", 0.8),
                    interaction_method=elem_data.get("interaction_method", "tap"),
                    semantic_role=elem_data.get("semantic_role", "unknown")
                )
                elements.append(element)
            
            # Extract semantic context
            semantic_context = analysis_data.get("semantic_context", {})
            semantic_context["interface_type"] = analysis_data.get("interface_type", "unknown")
            semantic_context["task_context"] = task_context
            
            # Extract interaction strategy
            interaction_strategy = analysis_data.get("interaction_strategy", {})
            
            # Calculate overall confidence
            confidence_data = analysis_data.get("confidence_assessment", {})
            overall_confidence = confidence_data.get("overall_confidence", 0.8)
            
            return MultiModalAnalysisResult(
                provider=AIProvider.GPT4_VISION,
                elements=[elem.__dict__ for elem in elements],
                semantic_context=semantic_context,
                interaction_strategy=interaction_strategy,
                confidence=overall_confidence,
                processing_time=0.0  # Will be set by caller
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse GPT-4 response as JSON: {e}")
            
            # Fallback: create basic analysis from text
            return self._create_fallback_analysis(response_text, task_context)
    
    def _create_fallback_analysis(self, response_text: str, task_context: str) -> MultiModalAnalysisResult:
        """Create fallback analysis when JSON parsing fails"""
        
        # Extract key information from text response
        semantic_context = {
            "raw_analysis": response_text,
            "task_context": task_context,
            "parsing_method": "fallback_text_analysis"
        }
        
        interaction_strategy = {
            "recommended_approach": "manual_analysis_required",
            "confidence": 0.5,
            "fallback": True
        }
        
        return MultiModalAnalysisResult(
            provider=AIProvider.GPT4_VISION,
            elements=[],
            semantic_context=semantic_context,
            interaction_strategy=interaction_strategy,
            confidence=0.5,
            processing_time=0.0
        )
    
    async def analyze_ui_elements_detailed(self, screenshot: bytes, 
                                         element_types: List[str] = None) -> List[UIElement]:
        """
        Detailed analysis focusing on specific UI element types
        
        Args:
            screenshot: Screenshot image as bytes
            element_types: Specific element types to focus on
            
        Returns:
            List of detailed UIElement objects
        """
        
        element_types = element_types or ["button", "input", "text", "icon", "menu"]
        
        prompt = f"""
Analyze this mobile interface and identify all {', '.join(element_types)} elements.

For each element, provide:
1. Exact pixel coordinates (x, y, width, height)
2. Element type and purpose
3. Visible text content
4. Recommended interaction method
5. Confidence level (0.0-1.0)

Return as JSON array of elements.
"""
        
        try:
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"}
                        }
                    ]
                }],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Parse elements from response
            response_text = response.choices[0].message.content
            elements_data = json.loads(response_text)
            
            elements = []
            for elem_data in elements_data:
                element = UIElement(
                    id=elem_data.get("id", f"elem_{len(elements)}"),
                    type=elem_data.get("type", "unknown"),
                    purpose=elem_data.get("purpose", ""),
                    x=elem_data.get("x", 0),
                    y=elem_data.get("y", 0),
                    width=elem_data.get("width", 0),
                    height=elem_data.get("height", 0),
                    text=elem_data.get("text"),
                    confidence=elem_data.get("confidence", 0.8),
                    interaction_method=elem_data.get("interaction_method", "tap"),
                    semantic_role=elem_data.get("semantic_role", "unknown")
                )
                elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"Detailed element analysis failed: {e}")
            return []
    
    async def predict_ui_changes(self, current_screenshot: bytes, planned_action: str) -> Dict[str, Any]:
        """
        Predict how the UI will change after performing an action
        
        Args:
            current_screenshot: Current interface state
            planned_action: Action about to be performed
            
        Returns:
            Prediction of UI changes
        """
        
        prompt = f"""
Analyze this mobile interface and predict what will happen when this action is performed: "{planned_action}"

Predict:
1. What elements will appear/disappear
2. What the new interface state will be
3. What new actions will become available
4. Potential issues or complications
5. Success indicators to look for

Provide detailed predictions in JSON format.
"""
        
        try:
            screenshot_b64 = base64.b64encode(current_screenshot).decode('utf-8')
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"}
                        }
                    ]
                }],
                max_tokens=800,
                temperature=0.2
            )
            
            prediction_text = response.choices[0].message.content
            
            # Parse prediction
            try:
                prediction_data = json.loads(prediction_text)
                return prediction_data
            except json.JSONDecodeError:
                return {"raw_prediction": prediction_text, "parsed": False}
                
        except Exception as e:
            logger.error(f"UI change prediction failed: {e}")
            return {"error": str(e), "prediction_available": False}
