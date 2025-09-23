"""
Claude Vision Provider Implementation
====================================

Advanced Claude Vision integration for contextual UI understanding and reasoning.
"""

import asyncio
import base64
import json
import logging
import time
from typing import Dict, Any, List, Optional

try:
    from anthropic import Anthropic
    from PIL import Image
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None
    Image = None

from ..exceptions import ThinkMeshException, ErrorCode
from .multimodal_ai_provider import MultiModalAnalysisResult, AIProvider, UIElement

logger = logging.getLogger(__name__)


class ClaudeVisionProvider:
    """
    Claude Vision provider for contextual UI understanding
    Specializes in reasoning about user workflows and interface context
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self.model = "claude-3-sonnet-20240229"
        self.max_tokens = 1500
        
    async def initialize(self) -> None:
        """Initialize Claude Vision client"""
        if not ANTHROPIC_AVAILABLE:
            raise ThinkMeshException("Anthropic library not available", ErrorCode.DEPENDENCY_ERROR)
        
        self.client = Anthropic(api_key=self.api_key)
        
        # Test connection
        try:
            await self._test_connection()
            logger.info("Claude Vision provider initialized successfully")
        except Exception as e:
            raise ThinkMeshException(f"Failed to initialize Claude Vision: {e}", ErrorCode.API_ERROR)
    
    async def _test_connection(self) -> None:
        """Test API connection"""
        try:
            # Simple test call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Test connection"}]
            )
            logger.debug("Claude Vision connection test successful")
        except Exception as e:
            logger.error(f"Claude Vision connection test failed: {e}")
            raise
    
    async def analyze_ui_semantically(self, screenshot: bytes, task_context: str) -> MultiModalAnalysisResult:
        """
        Analyze mobile UI with contextual understanding using Claude Vision
        
        Args:
            screenshot: Screenshot image as bytes
            task_context: Context about the task being performed
            
        Returns:
            MultiModalAnalysisResult with contextual analysis
        """
        
        start_time = time.time()
        
        try:
            # Convert screenshot to base64
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            
            # Create contextual analysis prompt
            prompt = self._create_contextual_prompt(task_context)
            
            # Call Claude Vision
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": screenshot_b64
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }]
            )
            
            # Parse response
            analysis_text = response.content[0].text
            parsed_result = await self._parse_claude_response(analysis_text, task_context)
            
            processing_time = time.time() - start_time
            parsed_result.processing_time = processing_time
            
            logger.debug(f"Claude Vision analysis completed in {processing_time:.2f}s")
            return parsed_result
            
        except Exception as e:
            logger.error(f"Claude Vision analysis failed: {e}")
            raise ThinkMeshException(f"Claude Vision analysis error: {e}", ErrorCode.API_ERROR)
    
    def _create_contextual_prompt(self, task_context: str) -> str:
        """Create contextual analysis prompt for Claude Vision"""
        
        return f"""
Analyze this mobile interface screenshot in the context of the task: "{task_context}"

I need you to understand the interface from a user workflow perspective. Please provide analysis in JSON format:

{{
    "workflow_analysis": {{
        "current_screen_purpose": "what this screen is for",
        "user_journey_stage": "where user is in their journey",
        "workflow_context": "broader context of what user is trying to accomplish",
        "previous_likely_actions": ["what user probably did to get here"],
        "next_logical_steps": ["what user would naturally do next"]
    }},
    "contextual_elements": [
        {{
            "element_id": "unique_id",
            "element_type": "button|input|text|navigation|content",
            "contextual_purpose": "why this element exists in this workflow",
            "user_intent_alignment": "how well this serves the user's goal",
            "interaction_priority": "high|medium|low priority for the task",
            "workflow_role": "primary_action|secondary_action|navigation|information",
            "coordinates": {{"x": 0, "y": 0, "width": 0, "height": 0}},
            "confidence": 0.0-1.0
        }}
    ],
    "reasoning_analysis": {{
        "task_feasibility": "how achievable is the task on this screen",
        "optimal_interaction_sequence": ["step 1", "step 2", "step 3"],
        "potential_user_confusion_points": ["areas where user might get confused"],
        "alternative_approaches": ["other ways to accomplish the same goal"],
        "context_dependent_factors": ["things that depend on app state or user history"]
    }},
    "workflow_optimization": {{
        "efficiency_assessment": "how efficient is this interface for the task",
        "user_experience_quality": "assessment of UX for this workflow",
        "suggested_improvements": ["how the interface could be better"],
        "accessibility_considerations": ["accessibility aspects relevant to the task"]
    }}
}}

Focus on understanding the USER'S PERSPECTIVE and WORKFLOW CONTEXT rather than just identifying elements.
Consider the broader user journey and how this screen fits into their goals.
"""
    
    async def _parse_claude_response(self, response_text: str, task_context: str) -> MultiModalAnalysisResult:
        """Parse Claude Vision response into structured result"""
        
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[json_start:json_end]
            analysis_data = json.loads(json_text)
            
            # Convert contextual elements to UIElement objects
            elements = []
            for elem_data in analysis_data.get("contextual_elements", []):
                element = UIElement(
                    id=elem_data.get("element_id", f"elem_{len(elements)}"),
                    type=elem_data.get("element_type", "unknown"),
                    purpose=elem_data.get("contextual_purpose", ""),
                    x=elem_data.get("coordinates", {}).get("x", 0),
                    y=elem_data.get("coordinates", {}).get("y", 0),
                    width=elem_data.get("coordinates", {}).get("width", 0),
                    height=elem_data.get("coordinates", {}).get("height", 0),
                    text=elem_data.get("text", ""),
                    confidence=elem_data.get("confidence", 0.8),
                    interaction_method="tap",  # Default for mobile
                    semantic_role=elem_data.get("workflow_role", "unknown")
                )
                elements.append(element)
            
            # Build comprehensive semantic context
            semantic_context = {
                "workflow_analysis": analysis_data.get("workflow_analysis", {}),
                "reasoning_analysis": analysis_data.get("reasoning_analysis", {}),
                "workflow_optimization": analysis_data.get("workflow_optimization", {}),
                "task_context": task_context,
                "provider": "claude_vision"
            }
            
            # Extract interaction strategy from reasoning
            reasoning = analysis_data.get("reasoning_analysis", {})
            interaction_strategy = {
                "optimal_sequence": reasoning.get("optimal_interaction_sequence", []),
                "alternative_approaches": reasoning.get("alternative_approaches", []),
                "potential_issues": reasoning.get("potential_user_confusion_points", []),
                "context_factors": reasoning.get("context_dependent_factors", []),
                "feasibility": reasoning.get("task_feasibility", "unknown")
            }
            
            # Calculate confidence based on reasoning quality
            confidence = self._calculate_contextual_confidence(analysis_data)
            
            return MultiModalAnalysisResult(
                provider=AIProvider.CLAUDE_VISION,
                elements=[elem.__dict__ for elem in elements],
                semantic_context=semantic_context,
                interaction_strategy=interaction_strategy,
                confidence=confidence,
                processing_time=0.0  # Will be set by caller
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse Claude response as JSON: {e}")
            
            # Fallback: create basic analysis from text
            return self._create_fallback_analysis(response_text, task_context)
    
    def _calculate_contextual_confidence(self, analysis_data: Dict[str, Any]) -> float:
        """Calculate confidence based on quality of contextual analysis"""
        
        confidence_factors = []
        
        # Check workflow analysis completeness
        workflow = analysis_data.get("workflow_analysis", {})
        if workflow.get("current_screen_purpose"):
            confidence_factors.append(0.2)
        if workflow.get("user_journey_stage"):
            confidence_factors.append(0.15)
        if workflow.get("next_logical_steps"):
            confidence_factors.append(0.15)
        
        # Check reasoning quality
        reasoning = analysis_data.get("reasoning_analysis", {})
        if reasoning.get("optimal_interaction_sequence"):
            confidence_factors.append(0.2)
        if reasoning.get("task_feasibility"):
            confidence_factors.append(0.1)
        
        # Check element analysis
        elements = analysis_data.get("contextual_elements", [])
        if len(elements) > 0:
            confidence_factors.append(0.2)
        
        return min(sum(confidence_factors), 1.0)
    
    def _create_fallback_analysis(self, response_text: str, task_context: str) -> MultiModalAnalysisResult:
        """Create fallback analysis when JSON parsing fails"""
        
        semantic_context = {
            "raw_analysis": response_text,
            "task_context": task_context,
            "parsing_method": "fallback_text_analysis",
            "provider": "claude_vision"
        }
        
        interaction_strategy = {
            "recommended_approach": "manual_analysis_required",
            "confidence": 0.4,
            "fallback": True
        }
        
        return MultiModalAnalysisResult(
            provider=AIProvider.CLAUDE_VISION,
            elements=[],
            semantic_context=semantic_context,
            interaction_strategy=interaction_strategy,
            confidence=0.4,
            processing_time=0.0
        )
    
    async def analyze_user_workflow(self, screenshot: bytes, user_goal: str, 
                                  previous_actions: List[str] = None) -> Dict[str, Any]:
        """
        Analyze user workflow and provide strategic guidance
        
        Args:
            screenshot: Current interface state
            user_goal: High-level user goal
            previous_actions: Actions user has taken so far
            
        Returns:
            Workflow analysis and strategic recommendations
        """
        
        previous_actions = previous_actions or []
        actions_context = f"Previous actions: {', '.join(previous_actions)}" if previous_actions else "Starting fresh"
        
        prompt = f"""
Analyze this interface in the context of the user's goal: "{user_goal}"
{actions_context}

Provide strategic workflow analysis:

1. Current position in user journey
2. Optimal path to goal completion
3. Potential roadblocks or complications
4. Alternative strategies if primary path fails
5. User experience assessment
6. Efficiency optimization opportunities

Focus on the strategic aspects of completing the user's goal.
"""
        
        try:
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": screenshot_b64
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }]
            )
            
            workflow_analysis = response.content[0].text
            
            # Try to parse as JSON, fallback to text
            try:
                return json.loads(workflow_analysis)
            except json.JSONDecodeError:
                return {
                    "workflow_analysis": workflow_analysis,
                    "parsed": False,
                    "user_goal": user_goal,
                    "previous_actions": previous_actions
                }
                
        except Exception as e:
            logger.error(f"Workflow analysis failed: {e}")
            return {"error": str(e), "analysis_available": False}
    
    async def reason_about_interface_context(self, screenshot: bytes, 
                                           context_questions: List[str]) -> Dict[str, Any]:
        """
        Answer specific questions about interface context using reasoning
        
        Args:
            screenshot: Interface to analyze
            context_questions: Specific questions to answer
            
        Returns:
            Reasoned answers to context questions
        """
        
        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(context_questions)])
        
        prompt = f"""
Analyze this interface and answer these specific questions using careful reasoning:

{questions_text}

For each question, provide:
- Your answer
- The reasoning behind your answer
- Confidence level (0.0-1.0)
- Evidence from the interface that supports your answer

Be thorough in your reasoning and cite specific visual elements.
"""
        
        try:
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1200,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": screenshot_b64
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }]
            )
            
            reasoning_response = response.content[0].text
            
            return {
                "questions": context_questions,
                "reasoning_response": reasoning_response,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Context reasoning failed: {e}")
            return {"error": str(e), "reasoning_available": False}
