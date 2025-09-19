"""
Task Distributor
================

Intelligent task distribution and load balancing for multi-agent orchestration.
Distributes tasks optimally based on agent capabilities and current load.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from ..config import OrchestrationConfig
from ..interfaces import UserContext
from ..exceptions import ThinkMeshException, ErrorCode

logger = logging.getLogger(__name__)


class DistributionStrategy(Enum):
    """Task distribution strategies"""
    ROUND_ROBIN = "round_robin"
    LOAD_BALANCED = "load_balanced"
    CAPABILITY_MATCHED = "capability_matched"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    HYBRID = "hybrid"


@dataclass
class TaskAssignment:
    """Task assignment structure"""
    agent_id: str
    task: str
    context: UserContext
    priority: int
    estimated_duration: float
    additional_context: Dict[str, Any]
    assignment_timestamp: float


class TaskDistributor:
    """
    Task Distributor
    
    Intelligently distributes tasks to agents based on capabilities,
    current load, performance history, and optimization strategies.
    """
    
    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.is_initialized = False
        
        # Distribution state
        self.current_assignments: Dict[str, List[TaskAssignment]] = {}
        self.agent_loads: Dict[str, float] = {}
        self.distribution_history: List[Dict[str, Any]] = []
        
        # Load balancing
        self.round_robin_index = 0
        self.load_thresholds: Dict[str, float] = {}
        
        # Performance tracking
        self.distribution_metrics: Dict[str, Any] = {}
        self.strategy_performance: Dict[DistributionStrategy, Dict[str, float]] = {}
    
    async def initialize(self) -> None:
        """Initialize the task distributor"""
        try:
            logger.info("Initializing Task Distributor...")
            
            # Setup distribution strategies
            await self._setup_distribution_strategies()
            
            # Initialize load balancing
            await self._initialize_load_balancing()
            
            # Setup performance tracking
            await self._setup_performance_tracking()
            
            self.is_initialized = True
            logger.info("Task Distributor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Task Distributor: {e}")
            raise ThinkMeshException(
                f"Task Distributor initialization failed: {e}",
                ErrorCode.ORCHESTRATION_INITIALIZATION_FAILED
            )
    
    async def distribute_task(self, task: str, agents: List[Dict[str, Any]],
                            strategy: Any, context: UserContext) -> List[TaskAssignment]:
        """Distribute task among selected agents"""
        try:
            if not agents:
                raise ThinkMeshException(
                    "No agents available for task distribution",
                    ErrorCode.ORCHESTRATION_EXECUTION_FAILED
                )
            
            # Determine distribution strategy
            distribution_strategy = await self._determine_distribution_strategy(
                task, agents, strategy, context
            )
            
            # Create task assignments
            assignments = await self._create_task_assignments(
                task, agents, distribution_strategy, context
            )
            
            # Update load tracking
            await self._update_agent_loads(assignments)
            
            # Record distribution
            await self._record_distribution(task, assignments, distribution_strategy)
            
            logger.debug(f"Distributed task to {len(assignments)} agents using {distribution_strategy.value}")
            return assignments
            
        except Exception as e:
            logger.error(f"Task distribution failed: {e}")
            raise
    
    async def _determine_distribution_strategy(self, task: str, agents: List[Dict[str, Any]],
                                             orchestration_strategy: Any, 
                                             context: UserContext) -> DistributionStrategy:
        """Determine optimal distribution strategy"""
        # Analyze task characteristics
        task_complexity = await self._analyze_task_complexity(task)
        agent_diversity = await self._analyze_agent_diversity(agents)
        current_load = await self._analyze_current_load(agents)
        
        # Map orchestration strategy to distribution strategy
        if str(orchestration_strategy).endswith("SEQUENTIAL"):
            return DistributionStrategy.CAPABILITY_MATCHED
        elif str(orchestration_strategy).endswith("PARALLEL"):
            return DistributionStrategy.LOAD_BALANCED
        elif str(orchestration_strategy).endswith("CONSENSUS"):
            return DistributionStrategy.PERFORMANCE_OPTIMIZED
        elif str(orchestration_strategy).endswith("COMPETITIVE"):
            return DistributionStrategy.PERFORMANCE_OPTIMIZED
        else:
            # Default to hybrid for collaborative strategies
            return DistributionStrategy.HYBRID
    
    async def _create_task_assignments(self, task: str, agents: List[Dict[str, Any]],
                                     strategy: DistributionStrategy,
                                     context: UserContext) -> List[TaskAssignment]:
        """Create task assignments based on strategy"""
        if strategy == DistributionStrategy.ROUND_ROBIN:
            return await self._round_robin_assignment(task, agents, context)
        elif strategy == DistributionStrategy.LOAD_BALANCED:
            return await self._load_balanced_assignment(task, agents, context)
        elif strategy == DistributionStrategy.CAPABILITY_MATCHED:
            return await self._capability_matched_assignment(task, agents, context)
        elif strategy == DistributionStrategy.PERFORMANCE_OPTIMIZED:
            return await self._performance_optimized_assignment(task, agents, context)
        elif strategy == DistributionStrategy.HYBRID:
            return await self._hybrid_assignment(task, agents, context)
        else:
            # Fallback to capability matched
            return await self._capability_matched_assignment(task, agents, context)
    
    async def _round_robin_assignment(self, task: str, agents: List[Dict[str, Any]],
                                    context: UserContext) -> List[TaskAssignment]:
        """Round-robin task assignment"""
        assignments = []
        
        for i, agent in enumerate(agents):
            assignment = TaskAssignment(
                agent_id=agent["agent_id"],
                task=task,
                context=context,
                priority=1,
                estimated_duration=await self._estimate_task_duration(task, agent),
                additional_context={"assignment_method": "round_robin", "position": i},
                assignment_timestamp=time.time()
            )
            assignments.append(assignment)
        
        # Update round-robin index
        self.round_robin_index = (self.round_robin_index + len(agents)) % len(agents)
        
        return assignments
    
    async def _load_balanced_assignment(self, task: str, agents: List[Dict[str, Any]],
                                      context: UserContext) -> List[TaskAssignment]:
        """Load-balanced task assignment"""
        assignments = []
        
        # Sort agents by current load (ascending)
        sorted_agents = sorted(agents, key=lambda a: self.agent_loads.get(a["agent_id"], 0.0))
        
        for i, agent in enumerate(sorted_agents):
            # Adjust priority based on load
            current_load = self.agent_loads.get(agent["agent_id"], 0.0)
            priority = max(1, 5 - int(current_load * 4))  # Higher priority for lower load
            
            assignment = TaskAssignment(
                agent_id=agent["agent_id"],
                task=task,
                context=context,
                priority=priority,
                estimated_duration=await self._estimate_task_duration(task, agent),
                additional_context={
                    "assignment_method": "load_balanced",
                    "current_load": current_load,
                    "load_rank": i
                },
                assignment_timestamp=time.time()
            )
            assignments.append(assignment)
        
        return assignments
    
    async def _capability_matched_assignment(self, task: str, agents: List[Dict[str, Any]],
                                           context: UserContext) -> List[TaskAssignment]:
        """Capability-matched task assignment"""
        assignments = []
        
        # Analyze task requirements
        task_requirements = await self._analyze_task_requirements(task)
        
        for agent in agents:
            # Calculate capability match score
            match_score = await self._calculate_capability_match(agent, task_requirements)
            
            # Adjust priority based on capability match
            priority = max(1, int(match_score * 5))
            
            assignment = TaskAssignment(
                agent_id=agent["agent_id"],
                task=task,
                context=context,
                priority=priority,
                estimated_duration=await self._estimate_task_duration(task, agent),
                additional_context={
                    "assignment_method": "capability_matched",
                    "match_score": match_score,
                    "required_capabilities": task_requirements
                },
                assignment_timestamp=time.time()
            )
            assignments.append(assignment)
        
        # Sort by priority (highest first)
        assignments.sort(key=lambda a: a.priority, reverse=True)
        
        return assignments
    
    async def _performance_optimized_assignment(self, task: str, agents: List[Dict[str, Any]],
                                              context: UserContext) -> List[TaskAssignment]:
        """Performance-optimized task assignment"""
        assignments = []
        
        # Get performance metrics for each agent
        for agent in agents:
            performance_score = await self._get_agent_performance_score(agent["agent_id"])
            
            # Adjust priority based on performance
            priority = max(1, int(performance_score * 5))
            
            assignment = TaskAssignment(
                agent_id=agent["agent_id"],
                task=task,
                context=context,
                priority=priority,
                estimated_duration=await self._estimate_task_duration(task, agent),
                additional_context={
                    "assignment_method": "performance_optimized",
                    "performance_score": performance_score
                },
                assignment_timestamp=time.time()
            )
            assignments.append(assignment)
        
        # Sort by performance score (highest first)
        assignments.sort(key=lambda a: a.additional_context["performance_score"], reverse=True)
        
        return assignments
    
    async def _hybrid_assignment(self, task: str, agents: List[Dict[str, Any]],
                               context: UserContext) -> List[TaskAssignment]:
        """Hybrid task assignment combining multiple strategies"""
        assignments = []
        
        # Combine capability matching, load balancing, and performance optimization
        task_requirements = await self._analyze_task_requirements(task)
        
        for agent in agents:
            # Calculate composite score
            capability_score = await self._calculate_capability_match(agent, task_requirements)
            performance_score = await self._get_agent_performance_score(agent["agent_id"])
            load_factor = 1.0 - self.agent_loads.get(agent["agent_id"], 0.0)
            
            # Weighted combination
            composite_score = (
                0.4 * capability_score +
                0.3 * performance_score +
                0.3 * load_factor
            )
            
            priority = max(1, int(composite_score * 5))
            
            assignment = TaskAssignment(
                agent_id=agent["agent_id"],
                task=task,
                context=context,
                priority=priority,
                estimated_duration=await self._estimate_task_duration(task, agent),
                additional_context={
                    "assignment_method": "hybrid",
                    "composite_score": composite_score,
                    "capability_score": capability_score,
                    "performance_score": performance_score,
                    "load_factor": load_factor
                },
                assignment_timestamp=time.time()
            )
            assignments.append(assignment)
        
        # Sort by composite score (highest first)
        assignments.sort(key=lambda a: a.additional_context["composite_score"], reverse=True)
        
        return assignments
    
    async def _analyze_task_complexity(self, task: str) -> float:
        """Analyze task complexity (0.0 to 1.0)"""
        # Simple complexity analysis
        complexity_factors = []
        
        # Length factor
        length_factor = min(len(task.split()) / 50, 1.0)
        complexity_factors.append(length_factor)
        
        # Complexity keywords
        complex_keywords = ["analyze", "comprehensive", "detailed", "complex", "thorough"]
        keyword_count = sum(1 for keyword in complex_keywords if keyword in task.lower())
        keyword_factor = min(keyword_count / 3, 1.0)
        complexity_factors.append(keyword_factor)
        
        return sum(complexity_factors) / len(complexity_factors)
    
    async def _analyze_agent_diversity(self, agents: List[Dict[str, Any]]) -> float:
        """Analyze diversity of agent types"""
        if not agents:
            return 0.0
        
        agent_types = set(agent.get("agent_type", "general") for agent in agents)
        return len(agent_types) / len(agents)
    
    async def _analyze_current_load(self, agents: List[Dict[str, Any]]) -> float:
        """Analyze current load across agents"""
        if not agents:
            return 0.0
        
        total_load = sum(self.agent_loads.get(agent["agent_id"], 0.0) for agent in agents)
        return total_load / len(agents)
    
    async def _analyze_task_requirements(self, task: str) -> Dict[str, Any]:
        """Analyze task to determine requirements"""
        task_lower = task.lower()
        
        requirements = {
            "capabilities": [],
            "domain": "general",
            "complexity": await self._analyze_task_complexity(task),
            "urgency": "normal"
        }
        
        # Identify required capabilities
        if any(word in task_lower for word in ["analyze", "research", "study"]):
            requirements["capabilities"].extend(["analysis", "research"])
            requirements["domain"] = "analytical"
        
        if any(word in task_lower for word in ["create", "design", "write"]):
            requirements["capabilities"].extend(["creative_writing", "design"])
            requirements["domain"] = "creative"
        
        if any(word in task_lower for word in ["code", "program", "technical"]):
            requirements["capabilities"].extend(["programming", "system_design"])
            requirements["domain"] = "technical"
        
        if any(word in task_lower for word in ["solve", "fix", "troubleshoot"]):
            requirements["capabilities"].extend(["problem_solving", "debugging"])
            requirements["domain"] = "problem_solving"
        
        # Identify urgency
        if any(word in task_lower for word in ["urgent", "asap", "immediately"]):
            requirements["urgency"] = "high"
        elif any(word in task_lower for word in ["when possible", "eventually"]):
            requirements["urgency"] = "low"
        
        return requirements
    
    async def _calculate_capability_match(self, agent: Dict[str, Any], 
                                        requirements: Dict[str, Any]) -> float:
        """Calculate how well agent capabilities match task requirements"""
        agent_capabilities = set(agent.get("capabilities", []))
        required_capabilities = set(requirements.get("capabilities", []))
        
        if not required_capabilities:
            return 0.7  # Default match for general tasks
        
        # Calculate intersection over union
        intersection = agent_capabilities & required_capabilities
        union = agent_capabilities | required_capabilities
        
        if not union:
            return 0.5
        
        match_score = len(intersection) / len(required_capabilities)
        return min(match_score, 1.0)
    
    async def _get_agent_performance_score(self, agent_id: str) -> float:
        """Get performance score for an agent"""
        # This would integrate with agent performance tracking
        # For now, return a default score
        return 0.8
    
    async def _estimate_task_duration(self, task: str, agent: Dict[str, Any]) -> float:
        """Estimate task duration in seconds"""
        # Simple duration estimation
        base_duration = 5.0  # 5 seconds base
        
        # Adjust based on task complexity
        complexity = await self._analyze_task_complexity(task)
        duration = base_duration * (1 + complexity)
        
        # Adjust based on agent type
        agent_type = agent.get("agent_type", "general")
        type_modifiers = {
            "analytical": 1.2,
            "creative": 1.5,
            "technical": 0.8,
            "research": 2.0,
            "general": 1.0
        }
        
        duration *= type_modifiers.get(agent_type, 1.0)
        
        return duration
    
    async def _update_agent_loads(self, assignments: List[TaskAssignment]) -> None:
        """Update agent load tracking"""
        for assignment in assignments:
            agent_id = assignment.agent_id
            current_load = self.agent_loads.get(agent_id, 0.0)
            
            # Add estimated load (normalized by duration)
            additional_load = assignment.estimated_duration / 30.0  # Normalize to 30 seconds
            self.agent_loads[agent_id] = min(current_load + additional_load, 1.0)
    
    async def _record_distribution(self, task: str, assignments: List[TaskAssignment],
                                 strategy: DistributionStrategy) -> None:
        """Record distribution for analysis and learning"""
        distribution_record = {
            "timestamp": time.time(),
            "task": task,
            "strategy": strategy.value,
            "assignments": [
                {
                    "agent_id": a.agent_id,
                    "priority": a.priority,
                    "estimated_duration": a.estimated_duration
                }
                for a in assignments
            ],
            "total_agents": len(assignments)
        }
        
        self.distribution_history.append(distribution_record)
        
        # Limit history size
        if len(self.distribution_history) > 1000:
            self.distribution_history = self.distribution_history[-500:]
    
    async def _setup_distribution_strategies(self) -> None:
        """Setup distribution strategies"""
        # Initialize strategy performance tracking
        for strategy in DistributionStrategy:
            self.strategy_performance[strategy] = {
                "usage_count": 0,
                "success_rate": 0.0,
                "average_efficiency": 0.0
            }
    
    async def _initialize_load_balancing(self) -> None:
        """Initialize load balancing parameters"""
        self.load_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8,
            "critical": 0.95
        }
    
    async def _setup_performance_tracking(self) -> None:
        """Setup performance tracking"""
        self.distribution_metrics = {
            "total_distributions": 0,
            "successful_distributions": 0,
            "average_distribution_time": 0.0,
            "load_balance_efficiency": 0.0
        }
    
    async def get_distribution_metrics(self) -> Dict[str, Any]:
        """Get distribution performance metrics"""
        return {
            "total_distributions": len(self.distribution_history),
            "current_agent_loads": self.agent_loads.copy(),
            "strategy_performance": {
                strategy.value: metrics 
                for strategy, metrics in self.strategy_performance.items()
            },
            "load_balance_efficiency": await self._calculate_load_balance_efficiency()
        }
    
    async def _calculate_load_balance_efficiency(self) -> float:
        """Calculate load balancing efficiency"""
        if not self.agent_loads:
            return 1.0
        
        loads = list(self.agent_loads.values())
        if not loads:
            return 1.0
        
        # Calculate coefficient of variation (lower is better)
        mean_load = sum(loads) / len(loads)
        if mean_load == 0:
            return 1.0
        
        variance = sum((load - mean_load) ** 2 for load in loads) / len(loads)
        std_dev = variance ** 0.5
        cv = std_dev / mean_load
        
        # Convert to efficiency score (0-1, higher is better)
        efficiency = max(0.0, 1.0 - cv)
        return efficiency
    
    async def shutdown(self) -> None:
        """Shutdown the task distributor"""
        try:
            self.is_initialized = False
            logger.info("Task Distributor shutdown complete")
        except Exception as e:
            logger.error(f"Error during Task Distributor shutdown: {e}")
