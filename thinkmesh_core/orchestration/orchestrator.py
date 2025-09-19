"""
Agent Orchestrator
==================

Main orchestration engine that coordinates multiple AI agents for
collaborative problem solving and collective intelligence.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging

from ..interfaces import IAIEngine, IHealthCheck, ComponentStatus, HealthStatus, UserContext
from ..config import OrchestrationConfig
from ..exceptions import ThinkMeshException, ErrorCode
from ..logging import get_logger, log_function_call, log_component_lifecycle

logger = get_logger(__name__)


class OrchestrationStrategy(Enum):
    """Orchestration strategies for agent coordination"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    CONSENSUS = "consensus"
    COMPETITIVE = "competitive"
    COLLABORATIVE = "collaborative"


@dataclass
class OrchestrationRequest:
    """Request structure for agent orchestration"""
    task: str
    context: UserContext
    strategy: OrchestrationStrategy = OrchestrationStrategy.COLLABORATIVE
    max_agents: int = 3
    timeout_seconds: int = 30
    quality_threshold: float = 0.8
    require_consensus: bool = False
    agent_preferences: Optional[List[str]] = None


@dataclass
class OrchestrationResult:
    """Result structure from agent orchestration"""
    final_response: str
    confidence_score: float
    agents_used: List[str]
    execution_time_ms: float
    strategy_used: OrchestrationStrategy
    consensus_achieved: bool
    individual_responses: List[Dict[str, Any]]
    collective_insights: Dict[str, Any]


@log_component_lifecycle("agent_orchestrator")
class AgentOrchestrator(IAIEngine, IHealthCheck):
    """
    Agent Orchestrator
    
    Coordinates multiple AI agents for collaborative problem solving,
    implementing collective intelligence and consensus mechanisms.
    """
    
    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.is_initialized = False
        
        # Core components
        self.agent_manager = None
        self.collective_intelligence = None
        self.task_distributor = None
        self.context_store = None
        
        # Performance tracking
        self.total_orchestrations = 0
        self.successful_orchestrations = 0
        self.average_response_time = 0.0
        self.agent_performance: Dict[str, Dict[str, float]] = {}
        
        # Active orchestrations
        self.active_orchestrations: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Agent Orchestrator created")
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the agent orchestrator"""
        if self.is_initialized:
            logger.warning("Agent Orchestrator already initialized")
            return
        
        try:
            logger.info("Initializing Agent Orchestrator...")
            
            # Update config if provided
            if config:
                for key, value in config.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
            
            # Initialize components
            await self._initialize_agent_manager()
            await self._initialize_collective_intelligence()
            await self._initialize_task_distributor()
            await self._initialize_context_store()
            
            self.is_initialized = True
            logger.info("Agent Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Agent Orchestrator: {e}")
            raise ThinkMeshException(
                f"Agent Orchestrator initialization failed: {str(e)}",
                ErrorCode.ORCHESTRATION_INITIALIZATION_FAILED,
                details={"error": str(e), "config": self.config.__dict__}
            )
    
    @log_function_call()
    async def process_request(self, request: str, context: UserContext) -> str:
        """Process request using multi-agent orchestration"""
        if not self.is_initialized:
            raise ThinkMeshException(
                "Agent Orchestrator not initialized",
                ErrorCode.ORCHESTRATION_NOT_INITIALIZED
            )
        
        start_time = time.time()
        orchestration_id = f"orch_{int(time.time() * 1000)}"
        self.total_orchestrations += 1
        
        try:
            # Create orchestration request
            orch_request = OrchestrationRequest(
                task=request,
                context=context,
                strategy=await self._determine_strategy(request, context),
                max_agents=self.config.max_agents,
                timeout_seconds=self.config.timeout_seconds
            )
            
            # Store active orchestration
            self.active_orchestrations[orchestration_id] = {
                "request": orch_request,
                "start_time": start_time,
                "status": "running"
            }
            
            try:
                # Execute orchestration
                result = await self._execute_orchestration(orch_request, orchestration_id)
                
                # Update performance metrics
                execution_time = (time.time() - start_time) * 1000
                self._update_performance_metrics(execution_time, True)
                
                self.successful_orchestrations += 1
                
                logger.info(f"Orchestration {orchestration_id} completed in {execution_time:.2f}ms")
                return result.final_response
                
            finally:
                # Clean up active orchestration
                if orchestration_id in self.active_orchestrations:
                    del self.active_orchestrations[orchestration_id]
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self._update_performance_metrics(execution_time, False)
            
            logger.error(f"Orchestration {orchestration_id} failed: {e}")
            raise ThinkMeshException(
                f"Agent orchestration failed: {str(e)}",
                ErrorCode.ORCHESTRATION_EXECUTION_FAILED,
                details={"request": request, "error": str(e)}
            )
    
    async def _execute_orchestration(self, request: OrchestrationRequest, 
                                   orchestration_id: str) -> OrchestrationResult:
        """Execute the orchestration strategy"""
        try:
            # Select and prepare agents
            selected_agents = await self.agent_manager.select_agents(
                task=request.task,
                context=request.context,
                max_agents=request.max_agents,
                preferences=request.agent_preferences
            )
            
            # Distribute task based on strategy
            task_assignments = await self.task_distributor.distribute_task(
                task=request.task,
                agents=selected_agents,
                strategy=request.strategy,
                context=request.context
            )
            
            # Execute tasks
            individual_results = await self._execute_agent_tasks(
                task_assignments, request.timeout_seconds
            )
            
            # Apply collective intelligence
            collective_result = await self.collective_intelligence.synthesize_responses(
                individual_results=individual_results,
                original_task=request.task,
                strategy=request.strategy,
                require_consensus=request.require_consensus
            )
            
            # Create final result
            result = OrchestrationResult(
                final_response=collective_result["final_response"],
                confidence_score=collective_result["confidence_score"],
                agents_used=[agent["agent_id"] for agent in selected_agents],
                execution_time_ms=(time.time() - time.time()) * 1000,  # Will be updated
                strategy_used=request.strategy,
                consensus_achieved=collective_result["consensus_achieved"],
                individual_responses=individual_results,
                collective_insights=collective_result["insights"]
            )
            
            # Update agent performance
            await self._update_agent_performance(selected_agents, individual_results)
            
            return result
            
        except Exception as e:
            logger.error(f"Orchestration execution failed: {e}")
            raise
    
    async def _execute_agent_tasks(self, task_assignments: List[Dict[str, Any]], 
                                 timeout_seconds: int) -> List[Dict[str, Any]]:
        """Execute tasks assigned to agents"""
        try:
            # Create tasks for each agent
            agent_tasks = []
            for assignment in task_assignments:
                task = self._create_agent_task(assignment, timeout_seconds)
                agent_tasks.append(task)
            
            # Execute tasks based on strategy
            if len(agent_tasks) == 1:
                # Single agent execution
                results = [await agent_tasks[0]]
            else:
                # Parallel execution with timeout
                try:
                    results = await asyncio.wait_for(
                        asyncio.gather(*agent_tasks, return_exceptions=True),
                        timeout=timeout_seconds
                    )
                except asyncio.TimeoutError:
                    logger.warning("Agent task execution timed out")
                    results = ["Task timed out"] * len(agent_tasks)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "agent_id": task_assignments[i]["agent_id"],
                        "response": f"Agent error: {str(result)}",
                        "confidence": 0.0,
                        "success": False,
                        "execution_time": timeout_seconds * 1000
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Agent task execution failed: {e}")
            raise
    
    async def _create_agent_task(self, assignment: Dict[str, Any], 
                               timeout_seconds: int) -> asyncio.Task:
        """Create an async task for agent execution"""
        async def execute_agent():
            try:
                start_time = time.time()
                
                # Get agent from manager
                agent = await self.agent_manager.get_agent(assignment["agent_id"])
                
                # Execute agent task
                response = await agent.process_task(
                    task=assignment["task"],
                    context=assignment["context"],
                    additional_context=assignment.get("additional_context", {})
                )
                
                execution_time = (time.time() - start_time) * 1000
                
                return {
                    "agent_id": assignment["agent_id"],
                    "response": response["response"],
                    "confidence": response.get("confidence", 0.7),
                    "success": True,
                    "execution_time": execution_time,
                    "metadata": response.get("metadata", {})
                }
                
            except Exception as e:
                logger.error(f"Agent {assignment['agent_id']} execution failed: {e}")
                return {
                    "agent_id": assignment["agent_id"],
                    "response": f"Agent execution failed: {str(e)}",
                    "confidence": 0.0,
                    "success": False,
                    "execution_time": timeout_seconds * 1000,
                    "error": str(e)
                }
        
        return asyncio.create_task(execute_agent())
    
    async def _determine_strategy(self, request: str, context: UserContext) -> OrchestrationStrategy:
        """Determine optimal orchestration strategy"""
        # Analyze request characteristics
        request_lower = request.lower()
        
        # Complex analysis or research tasks
        if any(word in request_lower for word in ["analyze", "research", "compare", "evaluate"]):
            return OrchestrationStrategy.COLLABORATIVE
        
        # Creative tasks benefit from multiple perspectives
        if any(word in request_lower for word in ["create", "design", "write", "generate"]):
            return OrchestrationStrategy.PARALLEL
        
        # Problem-solving tasks
        if any(word in request_lower for word in ["solve", "fix", "troubleshoot", "debug"]):
            return OrchestrationStrategy.CONSENSUS
        
        # Simple information requests
        if any(word in request_lower for word in ["what", "who", "when", "where"]):
            return OrchestrationStrategy.SEQUENTIAL
        
        # Default to collaborative
        return OrchestrationStrategy.COLLABORATIVE
    
    async def _update_agent_performance(self, agents: List[Dict[str, Any]], 
                                      results: List[Dict[str, Any]]) -> None:
        """Update agent performance metrics"""
        for agent, result in zip(agents, results):
            agent_id = agent["agent_id"]
            
            if agent_id not in self.agent_performance:
                self.agent_performance[agent_id] = {
                    "total_tasks": 0,
                    "successful_tasks": 0,
                    "average_confidence": 0.0,
                    "average_response_time": 0.0
                }
            
            metrics = self.agent_performance[agent_id]
            metrics["total_tasks"] += 1
            
            if result.get("success", False):
                metrics["successful_tasks"] += 1
            
            # Update averages
            alpha = 0.1  # Smoothing factor
            metrics["average_confidence"] = (
                alpha * result.get("confidence", 0.0) + 
                (1 - alpha) * metrics["average_confidence"]
            )
            metrics["average_response_time"] = (
                alpha * result.get("execution_time", 0.0) + 
                (1 - alpha) * metrics["average_response_time"]
            )
    
    def _update_performance_metrics(self, execution_time_ms: float, success: bool) -> None:
        """Update orchestrator performance metrics"""
        # Update average response time
        alpha = 0.1
        self.average_response_time = (
            alpha * execution_time_ms + 
            (1 - alpha) * self.average_response_time
        )
    
    async def get_capabilities(self) -> List[str]:
        """Get orchestrator capabilities"""
        return [
            "multi_agent_coordination",
            "collective_intelligence",
            "consensus_building",
            "task_distribution",
            "parallel_processing",
            "agent_performance_tracking",
            "context_sharing",
            "collaborative_problem_solving"
        ]
    
    async def check_health(self) -> HealthStatus:
        """Check orchestrator health status"""
        try:
            if not self.is_initialized:
                status = ComponentStatus.UNHEALTHY
                message = "Agent Orchestrator not initialized"
            elif len(self.active_orchestrations) > self.config.max_concurrent_orchestrations:
                status = ComponentStatus.DEGRADED
                message = "High orchestration load"
            elif self.average_response_time > 10000:  # 10 seconds
                status = ComponentStatus.DEGRADED
                message = "High response times"
            else:
                status = ComponentStatus.HEALTHY
                message = "Agent Orchestrator operating normally"
            
            return HealthStatus(
                status=status,
                message=message,
                details={
                    "initialized": self.is_initialized,
                    "total_orchestrations": self.total_orchestrations,
                    "success_rate": self.successful_orchestrations / max(self.total_orchestrations, 1),
                    "average_response_time_ms": self.average_response_time,
                    "active_orchestrations": len(self.active_orchestrations),
                    "agent_count": len(self.agent_performance)
                },
                timestamp=time.time(),
                component_name="agent_orchestrator"
            )
            
        except Exception as e:
            return HealthStatus(
                status=ComponentStatus.UNKNOWN,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=time.time(),
                component_name="agent_orchestrator"
            )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator performance metrics"""
        return {
            "total_orchestrations": self.total_orchestrations,
            "successful_orchestrations": self.successful_orchestrations,
            "success_rate": self.successful_orchestrations / max(self.total_orchestrations, 1),
            "average_response_time_ms": self.average_response_time,
            "active_orchestrations": len(self.active_orchestrations),
            "agent_performance": self.agent_performance
        }
    
    async def _initialize_agent_manager(self) -> None:
        """Initialize the agent manager"""
        from .agent_manager import AgentManager
        self.agent_manager = AgentManager(self.config)
        await self.agent_manager.initialize()
        logger.debug("Agent manager initialized")
    
    async def _initialize_collective_intelligence(self) -> None:
        """Initialize collective intelligence"""
        from .collective_intelligence import CollectiveIntelligence
        self.collective_intelligence = CollectiveIntelligence(self.config)
        await self.collective_intelligence.initialize()
        logger.debug("Collective intelligence initialized")
    
    async def _initialize_task_distributor(self) -> None:
        """Initialize task distributor"""
        from .task_distributor import TaskDistributor
        self.task_distributor = TaskDistributor(self.config)
        await self.task_distributor.initialize()
        logger.debug("Task distributor initialized")
    
    async def _initialize_context_store(self) -> None:
        """Initialize context store"""
        from .context_store import ContextStore
        self.context_store = ContextStore(self.config)
        await self.context_store.initialize()
        logger.debug("Context store initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the agent orchestrator"""
        logger.info("Shutting down Agent Orchestrator...")
        
        try:
            # Wait for active orchestrations to complete
            if self.active_orchestrations:
                logger.info(f"Waiting for {len(self.active_orchestrations)} active orchestrations to complete...")
                await asyncio.sleep(2)  # Give some time for completion
            
            # Shutdown components
            if self.context_store:
                await self.context_store.shutdown()
            
            if self.task_distributor:
                await self.task_distributor.shutdown()
            
            if self.collective_intelligence:
                await self.collective_intelligence.shutdown()
            
            if self.agent_manager:
                await self.agent_manager.shutdown()
            
            self.is_initialized = False
            logger.info("Agent Orchestrator shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during Agent Orchestrator shutdown: {e}")
