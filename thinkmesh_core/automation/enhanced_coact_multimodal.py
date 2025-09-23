"""
Enhanced CoAct-1 with Multi-Modal Intelligence
==============================================

Enhanced CoAct-1 automation engine with multi-modal AI capabilities,
predictive automation, and adaptive learning from visual feedback.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from ..ai_providers import MultiModalAIProvider, AIProvider
from ..interfaces import UserContext
from ..exceptions import ThinkMeshException, ErrorCode
from .coact_integration import CoAct1AutomationEngine, AutomationPlatform, TaskAnalysis
from .multimodal_screen_analyzer import MultiModalScreenAnalyzer, TaskContext, MultiModalScreenAnalysis

logger = logging.getLogger(__name__)


class PredictionConfidence(Enum):
    """Confidence levels for predictions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class AutomationPlan:
    """Comprehensive automation plan with predictions"""
    primary_steps: List[Dict[str, Any]]
    alternative_steps: List[Dict[str, Any]]
    predicted_ui_changes: List[Dict[str, Any]]
    success_probability: float
    estimated_time: float
    risk_factors: List[str]
    success_indicators: List[str]
    fallback_strategies: List[str]


@dataclass
class ExecutionResult:
    """Enhanced execution result with learning data"""
    success: bool
    steps_completed: int
    total_steps: int
    execution_time: float
    confidence_achieved: float
    errors_encountered: List[str]
    learning_data: Dict[str, Any]
    multimodal_feedback: Dict[str, Any]


class PredictiveAutomationEngine:
    """Predicts UI changes and pre-plans automation sequences"""
    
    def __init__(self, multimodal_ai: MultiModalAIProvider):
        self.multimodal_ai = multimodal_ai
        self.prediction_cache = {}
        self.pattern_database = {}
        
    async def create_automation_plan(self, task: str, screen_analysis: MultiModalScreenAnalysis,
                                   historical_patterns: Dict[str, Any]) -> AutomationPlan:
        """Create comprehensive automation plan with predictions"""
        
        # Analyze task complexity and requirements
        task_analysis = await self._analyze_task_requirements(task, screen_analysis)
        
        # Generate primary automation sequence
        primary_steps = await self._generate_primary_steps(task, screen_analysis, task_analysis)
        
        # Generate alternative approaches
        alternative_steps = await self._generate_alternative_steps(task, screen_analysis)
        
        # Predict UI changes for each step
        predicted_changes = await self._predict_ui_changes_sequence(primary_steps, screen_analysis)
        
        # Calculate success probability
        success_probability = await self._calculate_success_probability(
            primary_steps, screen_analysis, historical_patterns
        )
        
        # Estimate execution time
        estimated_time = await self._estimate_execution_time(primary_steps, task_analysis)
        
        # Identify risk factors
        risk_factors = await self._identify_risk_factors(primary_steps, screen_analysis)
        
        # Define success indicators
        success_indicators = await self._define_success_indicators(task, primary_steps)
        
        # Create fallback strategies
        fallback_strategies = await self._create_fallback_strategies(primary_steps, alternative_steps)
        
        return AutomationPlan(
            primary_steps=primary_steps,
            alternative_steps=alternative_steps,
            predicted_ui_changes=predicted_changes,
            success_probability=success_probability,
            estimated_time=estimated_time,
            risk_factors=risk_factors,
            success_indicators=success_indicators,
            fallback_strategies=fallback_strategies
        )
    
    async def _analyze_task_requirements(self, task: str, screen_analysis: MultiModalScreenAnalysis) -> Dict[str, Any]:
        """Analyze task requirements and complexity"""
        
        # Extract task type and complexity from AI analysis
        ai_context = screen_analysis.ai_semantic_context
        
        task_type = "unknown"
        complexity = "medium"
        
        if ai_context:
            # Determine task type from semantic context
            workflow_analysis = ai_context.get("workflow_analysis", {})
            task_type = workflow_analysis.get("current_screen_purpose", "unknown")
            
            # Determine complexity from interaction strategy
            interaction_strategy = screen_analysis.ai_interaction_strategy
            if interaction_strategy:
                steps = interaction_strategy.get("step_by_step", [])
                if len(steps) <= 2:
                    complexity = "simple"
                elif len(steps) <= 5:
                    complexity = "medium"
                else:
                    complexity = "complex"
        
        return {
            "task_type": task_type,
            "complexity": complexity,
            "requires_text_input": "type" in task.lower() or "enter" in task.lower(),
            "requires_navigation": "go to" in task.lower() or "navigate" in task.lower(),
            "requires_selection": "select" in task.lower() or "choose" in task.lower(),
            "estimated_steps": len(screen_analysis.ai_interaction_strategy.get("step_by_step", [])) if screen_analysis.ai_interaction_strategy else 3
        }
    
    async def _generate_primary_steps(self, task: str, screen_analysis: MultiModalScreenAnalysis,
                                    task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate primary automation steps"""
        
        steps = []
        
        # Use AI interaction strategy if available
        if screen_analysis.ai_interaction_strategy:
            ai_steps = screen_analysis.ai_interaction_strategy.get("step_by_step", [])
            
            for i, step_description in enumerate(ai_steps):
                # Find relevant UI element for this step
                relevant_element = await self._find_relevant_element(step_description, screen_analysis)
                
                step = {
                    "step_id": f"step_{i+1}",
                    "description": step_description,
                    "action_type": self._determine_action_type(step_description),
                    "target_element": relevant_element,
                    "confidence": relevant_element.get("confidence", 0.7) if relevant_element else 0.5,
                    "estimated_time": self._estimate_step_time(step_description),
                    "prerequisites": [],
                    "success_criteria": self._define_step_success_criteria(step_description)
                }
                steps.append(step)
        
        # Fallback: create basic steps from task description
        if not steps:
            steps = await self._create_fallback_steps(task, screen_analysis)
        
        return steps
    
    async def _find_relevant_element(self, step_description: str, 
                                   screen_analysis: MultiModalScreenAnalysis) -> Optional[Dict[str, Any]]:
        """Find UI element most relevant to the step"""
        
        # Combine AI and CV elements
        all_elements = screen_analysis.fused_elements
        
        if not all_elements:
            return None
        
        # Simple keyword matching for now
        step_lower = step_description.lower()
        best_element = None
        best_score = 0.0
        
        for element in all_elements:
            score = 0.0
            
            # Check element text
            if element.get("text"):
                text_lower = element["text"].lower()
                if any(word in text_lower for word in step_lower.split()):
                    score += 0.5
            
            # Check element purpose
            if element.get("purpose"):
                purpose_lower = element["purpose"].lower()
                if any(word in purpose_lower for word in step_lower.split()):
                    score += 0.3
            
            # Check element type
            if element.get("type"):
                type_lower = element["type"].lower()
                if "button" in step_lower and "button" in type_lower:
                    score += 0.4
                elif "input" in step_lower and "input" in type_lower:
                    score += 0.4
            
            if score > best_score:
                best_score = score
                best_element = element
        
        return best_element
    
    def _determine_action_type(self, step_description: str) -> str:
        """Determine action type from step description"""
        
        step_lower = step_description.lower()
        
        if any(word in step_lower for word in ["tap", "click", "press", "touch"]):
            return "tap"
        elif any(word in step_lower for word in ["type", "enter", "input"]):
            return "type"
        elif any(word in step_lower for word in ["swipe", "scroll"]):
            return "swipe"
        elif any(word in step_lower for word in ["wait", "pause"]):
            return "wait"
        else:
            return "tap"  # Default action
    
    def _estimate_step_time(self, step_description: str) -> float:
        """Estimate time required for step"""
        
        step_lower = step_description.lower()
        
        if "type" in step_lower or "enter" in step_lower:
            return 3.0  # Typing takes longer
        elif "wait" in step_lower:
            return 2.0  # Wait for UI changes
        else:
            return 1.0  # Simple tap/swipe
    
    def _define_step_success_criteria(self, step_description: str) -> List[str]:
        """Define success criteria for step"""
        
        return [
            "Action completed without error",
            "UI responded to action",
            "Expected element state change occurred"
        ]
    
    async def _create_fallback_steps(self, task: str, screen_analysis: MultiModalScreenAnalysis) -> List[Dict[str, Any]]:
        """Create basic fallback steps when AI analysis unavailable"""
        
        return [{
            "step_id": "step_1",
            "description": f"Complete task: {task}",
            "action_type": "tap",
            "target_element": None,
            "confidence": 0.5,
            "estimated_time": 2.0,
            "prerequisites": [],
            "success_criteria": ["Task completed successfully"]
        }]
    
    async def _predict_ui_changes_sequence(self, steps: List[Dict[str, Any]], 
                                         screen_analysis: MultiModalScreenAnalysis) -> List[Dict[str, Any]]:
        """Predict UI changes for each step in sequence"""
        
        predictions = []
        
        for step in steps:
            prediction = {
                "step_id": step["step_id"],
                "predicted_changes": [
                    "UI will respond to action",
                    "Screen may transition to new state"
                ],
                "confidence": PredictionConfidence.MEDIUM,
                "expected_elements": [],
                "potential_issues": []
            }
            predictions.append(prediction)
        
        return predictions
    
    async def _calculate_success_probability(self, steps: List[Dict[str, Any]], 
                                           screen_analysis: MultiModalScreenAnalysis,
                                           historical_patterns: Dict[str, Any]) -> float:
        """Calculate overall success probability"""
        
        if not steps:
            return 0.3
        
        # Base probability from screen analysis confidence
        base_probability = screen_analysis.fused_confidence
        
        # Adjust based on step complexity
        step_confidences = [step.get("confidence", 0.5) for step in steps]
        avg_step_confidence = sum(step_confidences) / len(step_confidences)
        
        # Adjust based on historical patterns
        historical_success = historical_patterns.get("success_rate", 0.7)
        
        # Combine factors
        success_probability = (base_probability * 0.4 + avg_step_confidence * 0.4 + historical_success * 0.2)
        
        return min(0.95, max(0.1, success_probability))
    
    async def _estimate_execution_time(self, steps: List[Dict[str, Any]], 
                                     task_analysis: Dict[str, Any]) -> float:
        """Estimate total execution time"""
        
        if not steps:
            return 5.0
        
        total_time = sum(step.get("estimated_time", 1.0) for step in steps)
        
        # Add overhead for UI transitions
        ui_transition_overhead = len(steps) * 0.5
        
        # Add complexity overhead
        complexity_multiplier = {
            "simple": 1.0,
            "medium": 1.2,
            "complex": 1.5
        }
        
        complexity = task_analysis.get("complexity", "medium")
        total_time *= complexity_multiplier.get(complexity, 1.2)
        
        return total_time + ui_transition_overhead
    
    async def _identify_risk_factors(self, steps: List[Dict[str, Any]], 
                                   screen_analysis: MultiModalScreenAnalysis) -> List[str]:
        """Identify potential risk factors"""
        
        risks = []
        
        # Check for low confidence elements
        for step in steps:
            if step.get("confidence", 1.0) < 0.6:
                risks.append(f"Low confidence in step: {step['description']}")
        
        # Check for missing target elements
        missing_targets = [step for step in steps if not step.get("target_element")]
        if missing_targets:
            risks.append(f"{len(missing_targets)} steps have no clear target element")
        
        # Check AI-identified risks
        if screen_analysis.potential_issues:
            risks.extend(screen_analysis.potential_issues)
        
        return risks
    
    async def _define_success_indicators(self, task: str, steps: List[Dict[str, Any]]) -> List[str]:
        """Define indicators of successful task completion"""
        
        return [
            "All automation steps completed without errors",
            "Final UI state matches expected outcome",
            "Task objective achieved as specified",
            "No unexpected error dialogs or states encountered"
        ]
    
    async def _create_fallback_strategies(self, primary_steps: List[Dict[str, Any]], 
                                        alternative_steps: List[Dict[str, Any]]) -> List[str]:
        """Create fallback strategies if primary approach fails"""
        
        strategies = [
            "Retry failed step with increased wait time",
            "Use alternative UI element if primary target fails",
            "Break complex steps into smaller sub-steps",
            "Request user intervention for manual completion"
        ]
        
        if alternative_steps:
            strategies.append("Switch to alternative automation approach")
        
        return strategies
    
    async def _generate_alternative_steps(self, task: str, screen_analysis: MultiModalScreenAnalysis) -> List[Dict[str, Any]]:
        """Generate alternative automation approaches"""
        
        # For now, return empty - will be enhanced in future iterations
        return []


class AdaptiveLearningEngine:
    """Learns from automation outcomes to improve future performance"""
    
    def __init__(self):
        self.learning_database = {}
        self.pattern_recognition = {}
        self.performance_metrics = {}
        
    async def learn_from_execution(self, task: str, plan: AutomationPlan, 
                                 result: ExecutionResult, 
                                 multimodal_analysis: MultiModalScreenAnalysis) -> None:
        """Learn from automation execution outcome"""
        
        # Extract learning patterns
        learning_data = {
            "task_type": self._categorize_task(task),
            "success": result.success,
            "execution_time": result.execution_time,
            "confidence_achieved": result.confidence_achieved,
            "steps_completed_ratio": result.steps_completed / result.total_steps,
            "multimodal_confidence": multimodal_analysis.fused_confidence,
            "ai_provider_used": multimodal_analysis.providers_used,
            "timestamp": time.time()
        }
        
        # Update learning database
        task_category = learning_data["task_type"]
        if task_category not in self.learning_database:
            self.learning_database[task_category] = []
        
        self.learning_database[task_category].append(learning_data)
        
        # Update performance metrics
        await self._update_performance_metrics(task_category, learning_data)
        
        logger.info(f"Learning data recorded for task category: {task_category}")
    
    def _categorize_task(self, task: str) -> str:
        """Categorize task for learning purposes"""
        
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["navigate", "go to", "open"]):
            return "navigation"
        elif any(word in task_lower for word in ["type", "enter", "input"]):
            return "text_input"
        elif any(word in task_lower for word in ["select", "choose", "pick"]):
            return "selection"
        elif any(word in task_lower for word in ["scroll", "swipe"]):
            return "scrolling"
        else:
            return "general"
    
    async def _update_performance_metrics(self, task_category: str, learning_data: Dict[str, Any]) -> None:
        """Update performance metrics for task category"""
        
        if task_category not in self.performance_metrics:
            self.performance_metrics[task_category] = {
                "total_attempts": 0,
                "successful_attempts": 0,
                "avg_execution_time": 0.0,
                "avg_confidence": 0.0
            }
        
        metrics = self.performance_metrics[task_category]
        metrics["total_attempts"] += 1
        
        if learning_data["success"]:
            metrics["successful_attempts"] += 1
        
        # Update averages
        total = metrics["total_attempts"]
        metrics["avg_execution_time"] = (
            (metrics["avg_execution_time"] * (total - 1) + learning_data["execution_time"]) / total
        )
        metrics["avg_confidence"] = (
            (metrics["avg_confidence"] * (total - 1) + learning_data["confidence_achieved"]) / total
        )
    
    async def get_patterns(self, task: str) -> Dict[str, Any]:
        """Get learned patterns for similar tasks"""
        
        task_category = self._categorize_task(task)
        
        if task_category in self.performance_metrics:
            metrics = self.performance_metrics[task_category]
            return {
                "success_rate": metrics["successful_attempts"] / metrics["total_attempts"],
                "avg_execution_time": metrics["avg_execution_time"],
                "avg_confidence": metrics["avg_confidence"],
                "total_experience": metrics["total_attempts"]
            }
        
        return {"success_rate": 0.7, "avg_execution_time": 3.0, "avg_confidence": 0.7, "total_experience": 0}


class EnhancedCoAct1AutomationEngine(CoAct1AutomationEngine):
    """
    Enhanced CoAct-1 automation engine with multi-modal intelligence
    Integrates predictive capabilities and adaptive learning
    """
    
    def __init__(self, api_keys: Dict[str, str] = None):
        super().__init__()
        self.multimodal_analyzer = MultiModalScreenAnalyzer(api_keys)
        self.predictive_engine = PredictiveAutomationEngine(self.multimodal_analyzer.multimodal_ai)
        self.adaptive_learning = AdaptiveLearningEngine()
        self.is_enhanced_initialized = False
        
    async def initialize_enhanced(self) -> None:
        """Initialize enhanced multi-modal capabilities"""
        if self.is_enhanced_initialized:
            return
            
        logger.info("Initializing Enhanced CoAct-1 with Multi-Modal Intelligence...")
        
        # Initialize parent class
        await super().initialize()
        
        # Initialize multi-modal components
        await self.multimodal_analyzer.initialize()
        
        self.is_enhanced_initialized = True
        logger.info("Enhanced CoAct-1 initialization complete")
    
    async def execute_task_with_multimodal_intelligence(self, task: str, context: UserContext, 
                                                      platform: AutomationPlatform) -> ExecutionResult:
        """Execute automation with full multi-modal intelligence"""
        
        if not self.is_enhanced_initialized:
            await self.initialize_enhanced()
        
        start_time = time.time()
        
        try:
            # 1. Capture current screen state
            screenshot = await self._capture_screen_state()
            
            # 2. Multi-modal task analysis
            task_context = TaskContext(
                description=task,
                user_context=context,
                platform=platform.value,
                complexity=self._assess_task_complexity(task)
            )
            
            multimodal_analysis = await self.multimodal_analyzer.analyze_screen_comprehensive(
                screenshot=screenshot,
                task_context=task_context
            )
            
            # 3. Predictive automation planning
            historical_patterns = await self.adaptive_learning.get_patterns(task)
            automation_plan = await self.predictive_engine.create_automation_plan(
                task=task,
                screen_analysis=multimodal_analysis,
                historical_patterns=historical_patterns
            )
            
            # 4. Enhanced execution with real-time adaptation
            execution_result = await self._execute_with_realtime_adaptation(
                plan=automation_plan,
                multimodal_analysis=multimodal_analysis,
                context=context
            )
            
            # 5. Learn from outcome
            await self.adaptive_learning.learn_from_execution(
                task=task,
                plan=automation_plan,
                result=execution_result,
                multimodal_analysis=multimodal_analysis
            )
            
            execution_time = time.time() - start_time
            execution_result.execution_time = execution_time
            
            logger.info(f"Enhanced automation completed in {execution_time:.2f}s with success: {execution_result.success}")
            return execution_result
            
        except Exception as e:
            logger.error(f"Enhanced automation failed: {e}")
            return ExecutionResult(
                success=False,
                steps_completed=0,
                total_steps=1,
                execution_time=time.time() - start_time,
                confidence_achieved=0.0,
                errors_encountered=[str(e)],
                learning_data={},
                multimodal_feedback={}
            )
    
    async def _capture_screen_state(self) -> bytes:
        """Capture current screen state for analysis"""
        # Implementation depends on platform
        # For now, return placeholder
        return b"placeholder_screenshot_data"
    
    def _assess_task_complexity(self, task: str) -> str:
        """Assess task complexity for analysis"""
        
        task_lower = task.lower()
        word_count = len(task.split())
        
        if word_count <= 3 and any(word in task_lower for word in ["tap", "click", "open"]):
            return "simple"
        elif word_count <= 6:
            return "medium"
        else:
            return "complex"
    
    async def _execute_with_realtime_adaptation(self, plan: AutomationPlan, 
                                              multimodal_analysis: MultiModalScreenAnalysis,
                                              context: UserContext) -> ExecutionResult:
        """Execute automation plan with real-time adaptation"""
        
        steps_completed = 0
        total_steps = len(plan.primary_steps)
        errors_encountered = []
        learning_data = {}
        
        try:
            for i, step in enumerate(plan.primary_steps):
                # Execute step
                step_success = await self._execute_automation_step(step, context)
                
                if step_success:
                    steps_completed += 1
                else:
                    errors_encountered.append(f"Step {i+1} failed: {step['description']}")
                    
                    # Try fallback strategies
                    fallback_success = await self._try_fallback_strategies(step, plan.fallback_strategies)
                    if fallback_success:
                        steps_completed += 1
                    else:
                        break  # Stop execution on failure
            
            success = steps_completed == total_steps
            
            return ExecutionResult(
                success=success,
                steps_completed=steps_completed,
                total_steps=total_steps,
                execution_time=0.0,  # Will be set by caller
                confidence_achieved=multimodal_analysis.fused_confidence,
                errors_encountered=errors_encountered,
                learning_data=learning_data,
                multimodal_feedback={"analysis_quality": "high", "provider_performance": "good"}
            )
            
        except Exception as e:
            logger.error(f"Execution with adaptation failed: {e}")
            return ExecutionResult(
                success=False,
                steps_completed=steps_completed,
                total_steps=total_steps,
                execution_time=0.0,
                confidence_achieved=0.0,
                errors_encountered=[str(e)],
                learning_data={},
                multimodal_feedback={}
            )
    
    async def _execute_automation_step(self, step: Dict[str, Any], context: UserContext) -> bool:
        """Execute individual automation step"""
        
        try:
            action_type = step.get("action_type", "tap")
            target_element = step.get("target_element")
            
            if not target_element:
                logger.warning(f"No target element for step: {step['description']}")
                return False
            
            # Execute based on action type
            if action_type == "tap":
                return await self._execute_tap_action(target_element)
            elif action_type == "type":
                return await self._execute_type_action(target_element, step.get("text", ""))
            elif action_type == "swipe":
                return await self._execute_swipe_action(target_element)
            elif action_type == "wait":
                await asyncio.sleep(step.get("wait_time", 1.0))
                return True
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            return False
    
    async def _execute_tap_action(self, target_element: Dict[str, Any]) -> bool:
        """Execute tap action on target element"""
        # Implementation depends on platform
        logger.info(f"Executing tap on element: {target_element.get('id', 'unknown')}")
        return True  # Placeholder
    
    async def _execute_type_action(self, target_element: Dict[str, Any], text: str) -> bool:
        """Execute type action on target element"""
        # Implementation depends on platform
        logger.info(f"Typing '{text}' in element: {target_element.get('id', 'unknown')}")
        return True  # Placeholder
    
    async def _execute_swipe_action(self, target_element: Dict[str, Any]) -> bool:
        """Execute swipe action on target element"""
        # Implementation depends on platform
        logger.info(f"Swiping on element: {target_element.get('id', 'unknown')}")
        return True  # Placeholder
    
    async def _try_fallback_strategies(self, failed_step: Dict[str, Any], 
                                     fallback_strategies: List[str]) -> bool:
        """Try fallback strategies for failed step"""
        
        for strategy in fallback_strategies:
            logger.info(f"Trying fallback strategy: {strategy}")
            
            if "retry" in strategy.lower():
                # Retry the step with delay
                await asyncio.sleep(1.0)
                return await self._execute_automation_step(failed_step, None)
            elif "alternative" in strategy.lower():
                # Try alternative approach (placeholder)
                return False
            elif "manual" in strategy.lower():
                # Request manual intervention
                logger.info("Requesting manual user intervention")
                return False
        
        return False
