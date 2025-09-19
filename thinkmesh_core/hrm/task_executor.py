"""
Task Executor for HRM Engine
============================

Low-level tactical execution component that operates on seconds-to-minutes timescale
for specific task implementation and response generation.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from ..config import HRMConfig
from ..interfaces import UserContext
from ..exceptions import ThinkMeshException, ErrorCode

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Task execution result structure"""
    response: str
    confidence_score: float
    execution_steps: List[str]
    resources_used: Dict[str, Any]
    performance_metrics: Dict[str, float]
    learning_insights: Optional[str] = None


class TaskExecutor:
    """
    Task Execution Component
    
    Handles low-level, specific task execution and response generation.
    Operates on seconds-to-minutes timescale for immediate task completion.
    """
    
    def __init__(self, config: HRMConfig, mobile_optimizer=None):
        self.config = config
        self.mobile_optimizer = mobile_optimizer
        self.is_initialized = False
        
        # Execution patterns and templates
        self.execution_patterns: Dict[str, Any] = {}
        self.response_templates: Dict[str, List[str]] = {}
        self.task_handlers: Dict[str, Any] = {}
        
        # Performance tracking
        self.execution_history: List[Dict[str, Any]] = []
        self.pattern_performance: Dict[str, float] = {}
        
        # Resource management
        self.current_load = 0.0
        self.max_concurrent_tasks = 3
        self.active_tasks: List[str] = []
    
    async def initialize(self) -> None:
        """Initialize the task executor"""
        try:
            logger.info("Initializing Task Executor...")
            
            # Load execution patterns and templates
            await self._load_execution_patterns()
            await self._load_response_templates()
            await self._initialize_task_handlers()
            
            self.is_initialized = True
            logger.info("Task Executor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Task Executor: {e}")
            raise ThinkMeshException(
                f"Task Executor initialization failed: {e}",
                ErrorCode.HRM_INITIALIZATION_FAILED
            )
    
    async def execute_strategy(self, strategy: Dict[str, Any], 
                             context: UserContext) -> Dict[str, Any]:
        """Execute the strategic plan"""
        try:
            start_time = time.time()
            task_id = f"task_{int(time.time() * 1000)}"
            
            # Check resource availability
            if len(self.active_tasks) >= self.max_concurrent_tasks:
                await self._wait_for_available_slot()
            
            self.active_tasks.append(task_id)
            
            try:
                # Select execution approach based on strategy
                execution_approach = await self._select_execution_approach(strategy)
                
                # Execute the strategy step by step
                execution_result = await self._execute_strategic_steps(
                    strategy, execution_approach, context
                )
                
                # Apply mobile optimizations
                if self.mobile_optimizer:
                    execution_result = await self.mobile_optimizer.optimize_execution_result(
                        execution_result, strategy
                    )
                
                # Calculate performance metrics
                execution_time = time.time() - start_time
                execution_result["performance_metrics"] = {
                    "execution_time_ms": execution_time * 1000,
                    "approach_used": execution_approach,
                    "confidence_score": execution_result.get("confidence_score", 0.7)
                }
                
                # Store execution history
                await self._store_execution_history(strategy, execution_result, context)
                
                logger.debug(f"Task {task_id} executed in {execution_time:.3f}s")
                return execution_result
                
            finally:
                self.active_tasks.remove(task_id)
                
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            raise ThinkMeshException(
                f"Task execution failed: {e}",
                ErrorCode.HRM_PROCESSING_FAILED
            )
    
    async def _select_execution_approach(self, strategy: Dict[str, Any]) -> str:
        """Select execution approach based on strategy"""
        approach = strategy.get("approach", "contextual_reasoning")
        complexity = strategy.get("complexity", 0.5)
        domain = strategy.get("domain", "general")
        urgency = strategy.get("urgency", "medium")
        
        # Map strategic approaches to execution approaches
        execution_mapping = {
            "hierarchical_decomposition": "step_by_step_execution",
            "systematic_analysis": "analytical_execution",
            "generative_exploration": "creative_execution",
            "analytical_problem_solving": "problem_solving_execution",
            "knowledge_retrieval": "information_retrieval_execution",
            "direct_response": "immediate_execution",
            "contextual_reasoning": "contextual_execution"
        }
        
        base_approach = execution_mapping.get(approach, "contextual_execution")
        
        # Modify based on constraints
        if urgency == "high":
            return f"fast_{base_approach}"
        elif complexity > 0.7:
            return f"detailed_{base_approach}"
        else:
            return base_approach
    
    async def _execute_strategic_steps(self, strategy: Dict[str, Any], 
                                     execution_approach: str, 
                                     context: UserContext) -> Dict[str, Any]:
        """Execute the strategic steps"""
        key_steps = strategy.get("key_steps", [])
        execution_steps = []
        response_parts = []
        
        # Execute each strategic step
        for i, step in enumerate(key_steps):
            step_result = await self._execute_single_step(
                step, strategy, execution_approach, context, i
            )
            
            execution_steps.append(step_result["description"])
            if step_result.get("response_content"):
                response_parts.append(step_result["response_content"])
        
        # Synthesize final response
        final_response = await self._synthesize_response(
            response_parts, strategy, execution_approach
        )
        
        # Calculate confidence score
        confidence_score = await self._calculate_confidence_score(
            strategy, execution_steps, response_parts
        )
        
        # Generate learning insights
        learning_insights = await self._generate_learning_insights(
            strategy, execution_steps, confidence_score
        )
        
        return {
            "response": final_response,
            "confidence_score": confidence_score,
            "execution_steps": execution_steps,
            "learning_insights": learning_insights,
            "approach_used": execution_approach
        }
    
    async def _execute_single_step(self, step: str, strategy: Dict[str, Any],
                                 execution_approach: str, context: UserContext,
                                 step_index: int) -> Dict[str, Any]:
        """Execute a single strategic step"""
        try:
            # Get step handler based on execution approach
            handler = await self._get_step_handler(execution_approach, step)
            
            # Execute the step
            step_result = await handler(step, strategy, context, step_index)
            
            return {
                "description": f"Step {step_index + 1}: {step}",
                "response_content": step_result.get("content", ""),
                "metadata": step_result.get("metadata", {})
            }
            
        except Exception as e:
            logger.warning(f"Step execution failed: {e}")
            return {
                "description": f"Step {step_index + 1}: {step} (simplified)",
                "response_content": f"Addressed: {step}",
                "metadata": {"error": str(e)}
            }
    
    async def _get_step_handler(self, execution_approach: str, step: str):
        """Get appropriate handler for the step"""
        # Simplified handler selection
        if "information" in step.lower() or "search" in step.lower():
            return self._handle_information_step
        elif "analyze" in step.lower() or "evaluate" in step.lower():
            return self._handle_analysis_step
        elif "generate" in step.lower() or "create" in step.lower():
            return self._handle_generation_step
        elif "solve" in step.lower() or "fix" in step.lower():
            return self._handle_problem_solving_step
        else:
            return self._handle_general_step
    
    async def _handle_information_step(self, step: str, strategy: Dict[str, Any],
                                     context: UserContext, step_index: int) -> Dict[str, Any]:
        """Handle information retrieval steps"""
        # Simulate information retrieval
        content = f"Retrieved relevant information for: {step}"
        
        return {
            "content": content,
            "metadata": {"step_type": "information_retrieval", "confidence": 0.8}
        }
    
    async def _handle_analysis_step(self, step: str, strategy: Dict[str, Any],
                                  context: UserContext, step_index: int) -> Dict[str, Any]:
        """Handle analysis steps"""
        # Simulate analysis
        content = f"Analyzed and evaluated: {step}"
        
        return {
            "content": content,
            "metadata": {"step_type": "analysis", "confidence": 0.75}
        }
    
    async def _handle_generation_step(self, step: str, strategy: Dict[str, Any],
                                    context: UserContext, step_index: int) -> Dict[str, Any]:
        """Handle generation/creation steps"""
        # Simulate generation
        content = f"Generated solution for: {step}"
        
        return {
            "content": content,
            "metadata": {"step_type": "generation", "confidence": 0.7}
        }
    
    async def _handle_problem_solving_step(self, step: str, strategy: Dict[str, Any],
                                         context: UserContext, step_index: int) -> Dict[str, Any]:
        """Handle problem solving steps"""
        # Simulate problem solving
        content = f"Solved problem: {step}"
        
        return {
            "content": content,
            "metadata": {"step_type": "problem_solving", "confidence": 0.8}
        }
    
    async def _handle_general_step(self, step: str, strategy: Dict[str, Any],
                                 context: UserContext, step_index: int) -> Dict[str, Any]:
        """Handle general steps"""
        # Simulate general processing
        content = f"Processed: {step}"
        
        return {
            "content": content,
            "metadata": {"step_type": "general", "confidence": 0.6}
        }
    
    async def _synthesize_response(self, response_parts: List[str], 
                                 strategy: Dict[str, Any], 
                                 execution_approach: str) -> str:
        """Synthesize final response from execution parts"""
        if not response_parts:
            return "I've processed your request and completed the necessary steps."
        
        # Get response template based on strategy
        template = await self._get_response_template(strategy, execution_approach)
        
        # Combine response parts
        combined_content = " ".join(response_parts)
        
        # Apply template
        if "{content}" in template:
            final_response = template.format(content=combined_content)
        else:
            final_response = f"{template} {combined_content}"
        
        return final_response
    
    async def _get_response_template(self, strategy: Dict[str, Any], 
                                   execution_approach: str) -> str:
        """Get response template based on strategy and approach"""
        domain = strategy.get("domain", "general")
        intent = strategy.get("intent", "general_inquiry")
        
        templates = self.response_templates.get(domain, {})
        template = templates.get(intent, "Here's what I found: {content}")
        
        return template
    
    async def _calculate_confidence_score(self, strategy: Dict[str, Any],
                                        execution_steps: List[str],
                                        response_parts: List[str]) -> float:
        """Calculate confidence score for the execution"""
        base_confidence = 0.7
        
        # Adjust based on strategy complexity
        complexity = strategy.get("complexity", 0.5)
        complexity_adjustment = (1.0 - complexity) * 0.2
        
        # Adjust based on execution completeness
        steps_completed = len(execution_steps)
        expected_steps = len(strategy.get("key_steps", []))
        completeness = steps_completed / max(expected_steps, 1)
        completeness_adjustment = completeness * 0.15
        
        # Adjust based on response content quality
        content_quality = min(len(" ".join(response_parts)) / 100, 1.0) * 0.1
        
        confidence = base_confidence + complexity_adjustment + completeness_adjustment + content_quality
        return min(confidence, 1.0)
    
    async def _generate_learning_insights(self, strategy: Dict[str, Any],
                                        execution_steps: List[str],
                                        confidence_score: float) -> Optional[str]:
        """Generate learning insights from execution"""
        if confidence_score > 0.8:
            return "Execution completed successfully with high confidence."
        elif confidence_score > 0.6:
            return "Execution completed with moderate confidence. Some areas could be improved."
        else:
            return "Execution completed but with lower confidence. Consider alternative approaches."
    
    async def _store_execution_history(self, strategy: Dict[str, Any],
                                     execution_result: Dict[str, Any],
                                     context: UserContext) -> None:
        """Store execution history for learning"""
        history_record = {
            "timestamp": time.time(),
            "strategy_approach": strategy.get("approach"),
            "execution_approach": execution_result.get("approach_used"),
            "confidence_score": execution_result.get("confidence_score"),
            "execution_time": execution_result.get("performance_metrics", {}).get("execution_time_ms"),
            "user_id": context.user_id,
            "domain": strategy.get("domain"),
            "complexity": strategy.get("complexity")
        }
        
        self.execution_history.append(history_record)
        
        # Limit history size
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-500:]
    
    async def _wait_for_available_slot(self) -> None:
        """Wait for an available execution slot"""
        while len(self.active_tasks) >= self.max_concurrent_tasks:
            await asyncio.sleep(0.1)
    
    async def _load_execution_patterns(self) -> None:
        """Load execution patterns"""
        self.execution_patterns = {
            "step_by_step_execution": {
                "description": "Execute steps sequentially with full analysis",
                "confidence_factor": 0.9
            },
            "analytical_execution": {
                "description": "Focus on systematic analysis and evaluation",
                "confidence_factor": 0.85
            },
            "creative_execution": {
                "description": "Emphasize creative exploration and generation",
                "confidence_factor": 0.8
            },
            "problem_solving_execution": {
                "description": "Focus on problem identification and solution",
                "confidence_factor": 0.88
            },
            "information_retrieval_execution": {
                "description": "Optimize for information gathering and synthesis",
                "confidence_factor": 0.92
            },
            "immediate_execution": {
                "description": "Provide quick, direct responses",
                "confidence_factor": 0.75
            },
            "contextual_execution": {
                "description": "Consider context and provide appropriate responses",
                "confidence_factor": 0.82
            }
        }
    
    async def _load_response_templates(self) -> None:
        """Load response templates"""
        self.response_templates = {
            "technical": {
                "information_seeking": "Based on the technical analysis: {content}",
                "problem_solving": "Here's the technical solution: {content}",
                "task_completion": "I've completed the technical implementation: {content}"
            },
            "creative": {
                "creative": "Here's the creative solution I've developed: {content}",
                "task_completion": "I've created the following for you: {content}"
            },
            "analytical": {
                "information_seeking": "Based on my analysis: {content}",
                "decision_support": "Here's my analytical assessment: {content}"
            },
            "general": {
                "information_seeking": "Here's what I found: {content}",
                "problem_solving": "Here's how to address this: {content}",
                "task_completion": "I've completed this for you: {content}",
                "general_inquiry": "Based on your request: {content}"
            }
        }
    
    async def _initialize_task_handlers(self) -> None:
        """Initialize task handlers"""
        self.task_handlers = {
            "information_retrieval": self._handle_information_step,
            "analysis": self._handle_analysis_step,
            "generation": self._handle_generation_step,
            "problem_solving": self._handle_problem_solving_step,
            "general": self._handle_general_step
        }
    
    async def shutdown(self) -> None:
        """Shutdown the task executor"""
        try:
            # Wait for active tasks to complete
            while self.active_tasks:
                await asyncio.sleep(0.1)
            
            self.is_initialized = False
            logger.info("Task Executor shutdown complete")
        except Exception as e:
            logger.error(f"Error during Task Executor shutdown: {e}")
