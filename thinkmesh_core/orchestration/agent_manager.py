"""
Agent Manager
=============

Manages the lifecycle, coordination, and performance of AI agents
in the multi-agent orchestration system.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging

from ..config import OrchestrationConfig
from ..interfaces import UserContext
from ..exceptions import ThinkMeshException, ErrorCode

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Types of AI agents"""
    GENERAL = "general"
    SPECIALIST = "specialist"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    TECHNICAL = "technical"
    RESEARCH = "research"
    PROBLEM_SOLVER = "problem_solver"


class AgentStatus(Enum):
    """Agent status states"""
    IDLE = "idle"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    INITIALIZING = "initializing"


@dataclass
class AgentConfig:
    """Configuration for an AI agent"""
    agent_id: str
    agent_type: AgentType
    name: str
    description: str
    capabilities: List[str]
    specializations: List[str]
    max_concurrent_tasks: int = 1
    timeout_seconds: int = 30
    priority: int = 1  # 1-5, 5 being highest
    enabled: bool = True


@dataclass
class AgentMetrics:
    """Performance metrics for an agent"""
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_response_time: float = 0.0
    average_confidence: float = 0.0
    last_used: Optional[float] = None
    success_rate: float = 0.0


class AIAgent:
    """Individual AI agent implementation"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.status = AgentStatus.INITIALIZING
        self.current_tasks: Set[str] = set()
        self.metrics = AgentMetrics()
        self.last_error: Optional[str] = None
    
    async def initialize(self) -> None:
        """Initialize the agent"""
        try:
            # Agent-specific initialization
            await self._load_agent_model()
            await self._setup_capabilities()
            
            self.status = AgentStatus.IDLE
            logger.debug(f"Agent {self.config.agent_id} initialized")
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.last_error = str(e)
            logger.error(f"Agent {self.config.agent_id} initialization failed: {e}")
            raise
    
    async def process_task(self, task: str, context: UserContext, 
                         additional_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a task assigned to this agent"""
        if self.status != AgentStatus.IDLE:
            raise ThinkMeshException(
                f"Agent {self.config.agent_id} is not available (status: {self.status})",
                ErrorCode.AGENT_UNAVAILABLE
            )
        
        if len(self.current_tasks) >= self.config.max_concurrent_tasks:
            raise ThinkMeshException(
                f"Agent {self.config.agent_id} at maximum capacity",
                ErrorCode.AGENT_BUSY
            )
        
        task_id = f"task_{int(time.time() * 1000)}"
        start_time = time.time()
        
        try:
            self.status = AgentStatus.BUSY
            self.current_tasks.add(task_id)
            
            # Process the task based on agent type
            result = await self._execute_task(task, context, additional_context)
            
            # Update metrics
            execution_time = time.time() - start_time
            self._update_metrics(execution_time, True, result.get("confidence", 0.7))
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._update_metrics(execution_time, False, 0.0)
            self.last_error = str(e)
            
            logger.error(f"Agent {self.config.agent_id} task failed: {e}")
            raise
            
        finally:
            self.current_tasks.discard(task_id)
            if not self.current_tasks:
                self.status = AgentStatus.IDLE
    
    async def _execute_task(self, task: str, context: UserContext,
                          additional_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the task based on agent type and capabilities"""
        try:
            # Simulate agent processing based on type
            if self.config.agent_type == AgentType.ANALYTICAL:
                response = await self._analytical_processing(task, context)
            elif self.config.agent_type == AgentType.CREATIVE:
                response = await self._creative_processing(task, context)
            elif self.config.agent_type == AgentType.TECHNICAL:
                response = await self._technical_processing(task, context)
            elif self.config.agent_type == AgentType.RESEARCH:
                response = await self._research_processing(task, context)
            elif self.config.agent_type == AgentType.PROBLEM_SOLVER:
                response = await self._problem_solving_processing(task, context)
            else:
                response = await self._general_processing(task, context)
            
            return {
                "response": response,
                "confidence": await self._calculate_confidence(task, response),
                "agent_type": self.config.agent_type.value,
                "metadata": {
                    "agent_id": self.config.agent_id,
                    "specializations": self.config.specializations,
                    "processing_approach": self.config.agent_type.value
                }
            }
            
        except Exception as e:
            logger.error(f"Task execution failed for agent {self.config.agent_id}: {e}")
            raise
    
    async def _analytical_processing(self, task: str, context: UserContext) -> str:
        """Analytical agent processing"""
        # Simulate analytical processing
        await asyncio.sleep(0.1)  # Simulate processing time
        return f"Analytical analysis: {task} - Systematic evaluation completed with data-driven insights."
    
    async def _creative_processing(self, task: str, context: UserContext) -> str:
        """Creative agent processing"""
        await asyncio.sleep(0.15)  # Creative tasks take a bit longer
        return f"Creative solution: {task} - Innovative approach with original ideas and creative alternatives."
    
    async def _technical_processing(self, task: str, context: UserContext) -> str:
        """Technical agent processing"""
        await asyncio.sleep(0.08)  # Technical processing is efficient
        return f"Technical implementation: {task} - Detailed technical solution with implementation specifics."
    
    async def _research_processing(self, task: str, context: UserContext) -> str:
        """Research agent processing"""
        await asyncio.sleep(0.2)  # Research takes more time
        return f"Research findings: {task} - Comprehensive research with verified information and sources."
    
    async def _problem_solving_processing(self, task: str, context: UserContext) -> str:
        """Problem-solving agent processing"""
        await asyncio.sleep(0.12)
        return f"Problem solution: {task} - Systematic problem analysis with practical solution steps."
    
    async def _general_processing(self, task: str, context: UserContext) -> str:
        """General agent processing"""
        await asyncio.sleep(0.1)
        return f"General response: {task} - Balanced approach addressing the request comprehensively."
    
    async def _calculate_confidence(self, task: str, response: str) -> float:
        """Calculate confidence score for the response"""
        # Simple confidence calculation based on agent type and response quality
        base_confidence = 0.7
        
        # Agent type confidence modifiers
        type_modifiers = {
            AgentType.SPECIALIST: 0.1,
            AgentType.ANALYTICAL: 0.08,
            AgentType.TECHNICAL: 0.08,
            AgentType.RESEARCH: 0.05,
            AgentType.CREATIVE: 0.03,
            AgentType.PROBLEM_SOLVER: 0.06,
            AgentType.GENERAL: 0.0
        }
        
        confidence = base_confidence + type_modifiers.get(self.config.agent_type, 0.0)
        
        # Response quality modifier
        if len(response) > 50:
            confidence += 0.05
        if len(response) > 100:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _update_metrics(self, execution_time: float, success: bool, confidence: float) -> None:
        """Update agent performance metrics"""
        self.metrics.total_tasks += 1
        self.metrics.last_used = time.time()
        
        if success:
            self.metrics.successful_tasks += 1
        else:
            self.metrics.failed_tasks += 1
        
        # Update averages using exponential moving average
        alpha = 0.1
        self.metrics.average_response_time = (
            alpha * execution_time + (1 - alpha) * self.metrics.average_response_time
        )
        self.metrics.average_confidence = (
            alpha * confidence + (1 - alpha) * self.metrics.average_confidence
        )
        
        # Update success rate
        self.metrics.success_rate = self.metrics.successful_tasks / self.metrics.total_tasks
    
    async def _load_agent_model(self) -> None:
        """Load agent-specific model or configuration"""
        # Simulate model loading
        await asyncio.sleep(0.05)
    
    async def _setup_capabilities(self) -> None:
        """Setup agent capabilities"""
        # Initialize capabilities based on agent type
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.config.agent_id,
            "status": self.status.value,
            "current_tasks": len(self.current_tasks),
            "max_tasks": self.config.max_concurrent_tasks,
            "metrics": {
                "total_tasks": self.metrics.total_tasks,
                "success_rate": self.metrics.success_rate,
                "average_response_time": self.metrics.average_response_time,
                "average_confidence": self.metrics.average_confidence
            },
            "last_error": self.last_error
        }


class AgentManager:
    """
    Agent Manager
    
    Manages the lifecycle, selection, and coordination of AI agents
    in the multi-agent orchestration system.
    """
    
    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.is_initialized = False
        
        # Agent registry
        self.agents: Dict[str, AIAgent] = {}
        self.agent_configs: Dict[str, AgentConfig] = {}
        
        # Selection and load balancing
        self.agent_selection_history: List[Dict[str, Any]] = []
        self.load_balancer_state: Dict[str, Any] = {}
    
    async def initialize(self) -> None:
        """Initialize the agent manager"""
        try:
            logger.info("Initializing Agent Manager...")
            
            # Create default agents
            await self._create_default_agents()
            
            # Initialize all agents
            await self._initialize_agents()
            
            # Setup load balancing
            await self._setup_load_balancing()
            
            self.is_initialized = True
            logger.info("Agent Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Agent Manager: {e}")
            raise ThinkMeshException(
                f"Agent Manager initialization failed: {e}",
                ErrorCode.ORCHESTRATION_INITIALIZATION_FAILED
            )
    
    async def select_agents(self, task: str, context: UserContext, max_agents: int = 3,
                          preferences: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Select optimal agents for a task"""
        try:
            # Analyze task requirements
            task_analysis = await self._analyze_task_requirements(task, context)
            
            # Get available agents
            available_agents = await self._get_available_agents()
            
            # Score agents for this task
            agent_scores = await self._score_agents_for_task(
                available_agents, task_analysis, preferences
            )
            
            # Select top agents
            selected_agents = await self._select_top_agents(
                agent_scores, max_agents, task_analysis
            )
            
            # Record selection for learning
            await self._record_agent_selection(task, selected_agents, task_analysis)
            
            logger.debug(f"Selected {len(selected_agents)} agents for task")
            return selected_agents
            
        except Exception as e:
            logger.error(f"Agent selection failed: {e}")
            raise
    
    async def get_agent(self, agent_id: str) -> AIAgent:
        """Get agent by ID"""
        if agent_id not in self.agents:
            raise ThinkMeshException(
                f"Agent {agent_id} not found",
                ErrorCode.AGENT_NOT_FOUND
            )
        
        return self.agents[agent_id]
    
    async def get_agent_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get status of specific agent or all agents"""
        if agent_id:
            if agent_id not in self.agents:
                raise ThinkMeshException(
                    f"Agent {agent_id} not found",
                    ErrorCode.AGENT_NOT_FOUND
                )
            return self.agents[agent_id].get_status()
        else:
            return {
                agent_id: agent.get_status() 
                for agent_id, agent in self.agents.items()
            }
    
    async def _create_default_agents(self) -> None:
        """Create default set of agents"""
        default_agents = [
            AgentConfig(
                agent_id="analytical_agent",
                agent_type=AgentType.ANALYTICAL,
                name="Analytical Agent",
                description="Specializes in data analysis, research, and systematic evaluation",
                capabilities=["analysis", "research", "evaluation", "data_processing"],
                specializations=["statistical_analysis", "trend_analysis", "comparative_analysis"],
                priority=4
            ),
            AgentConfig(
                agent_id="creative_agent",
                agent_type=AgentType.CREATIVE,
                name="Creative Agent",
                description="Specializes in creative tasks, ideation, and innovative solutions",
                capabilities=["creative_writing", "ideation", "design", "innovation"],
                specializations=["content_creation", "brainstorming", "artistic_solutions"],
                priority=3
            ),
            AgentConfig(
                agent_id="technical_agent",
                agent_type=AgentType.TECHNICAL,
                name="Technical Agent",
                description="Specializes in technical implementation and problem-solving",
                capabilities=["programming", "system_design", "troubleshooting", "optimization"],
                specializations=["software_development", "architecture", "debugging"],
                priority=4
            ),
            AgentConfig(
                agent_id="research_agent",
                agent_type=AgentType.RESEARCH,
                name="Research Agent",
                description="Specializes in information gathering and knowledge synthesis",
                capabilities=["information_retrieval", "fact_checking", "synthesis", "verification"],
                specializations=["academic_research", "market_research", "fact_verification"],
                priority=3
            ),
            AgentConfig(
                agent_id="general_agent",
                agent_type=AgentType.GENERAL,
                name="General Agent",
                description="Handles general tasks and provides balanced responses",
                capabilities=["general_assistance", "conversation", "basic_analysis", "summarization"],
                specializations=["customer_service", "general_inquiry", "task_coordination"],
                priority=2
            )
        ]
        
        for agent_config in default_agents:
            self.agent_configs[agent_config.agent_id] = agent_config
    
    async def _initialize_agents(self) -> None:
        """Initialize all configured agents"""
        for agent_id, config in self.agent_configs.items():
            try:
                agent = AIAgent(config)
                await agent.initialize()
                self.agents[agent_id] = agent
                logger.debug(f"Agent {agent_id} initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize agent {agent_id}: {e}")
    
    async def _analyze_task_requirements(self, task: str, context: UserContext) -> Dict[str, Any]:
        """Analyze task to determine requirements"""
        task_lower = task.lower()
        
        requirements = {
            "complexity": "medium",
            "domain": "general",
            "required_capabilities": [],
            "preferred_agent_types": [],
            "urgency": "normal"
        }
        
        # Analyze complexity
        complexity_indicators = {
            "high": ["complex", "comprehensive", "detailed", "thorough", "extensive"],
            "low": ["simple", "quick", "basic", "brief", "straightforward"]
        }
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in task_lower for indicator in indicators):
                requirements["complexity"] = level
                break
        
        # Analyze domain and capabilities
        if any(word in task_lower for word in ["analyze", "research", "study", "evaluate"]):
            requirements["preferred_agent_types"].append(AgentType.ANALYTICAL)
            requirements["required_capabilities"].extend(["analysis", "research"])
        
        if any(word in task_lower for word in ["create", "design", "write", "generate"]):
            requirements["preferred_agent_types"].append(AgentType.CREATIVE)
            requirements["required_capabilities"].extend(["creative_writing", "design"])
        
        if any(word in task_lower for word in ["code", "program", "implement", "technical"]):
            requirements["preferred_agent_types"].append(AgentType.TECHNICAL)
            requirements["required_capabilities"].extend(["programming", "system_design"])
        
        if any(word in task_lower for word in ["find", "search", "information", "facts"]):
            requirements["preferred_agent_types"].append(AgentType.RESEARCH)
            requirements["required_capabilities"].extend(["information_retrieval", "research"])
        
        # Default to general if no specific type identified
        if not requirements["preferred_agent_types"]:
            requirements["preferred_agent_types"].append(AgentType.GENERAL)
        
        return requirements
    
    async def _get_available_agents(self) -> List[AIAgent]:
        """Get list of available agents"""
        available = []
        for agent in self.agents.values():
            if (agent.status == AgentStatus.IDLE and 
                agent.config.enabled and 
                len(agent.current_tasks) < agent.config.max_concurrent_tasks):
                available.append(agent)
        
        return available
    
    async def _score_agents_for_task(self, agents: List[AIAgent], 
                                   task_analysis: Dict[str, Any],
                                   preferences: Optional[List[str]]) -> List[Dict[str, Any]]:
        """Score agents based on task requirements"""
        scored_agents = []
        
        for agent in agents:
            score = await self._calculate_agent_score(agent, task_analysis, preferences)
            scored_agents.append({
                "agent": agent,
                "score": score,
                "agent_id": agent.config.agent_id
            })
        
        # Sort by score (highest first)
        scored_agents.sort(key=lambda x: x["score"], reverse=True)
        return scored_agents
    
    async def _calculate_agent_score(self, agent: AIAgent, task_analysis: Dict[str, Any],
                                   preferences: Optional[List[str]]) -> float:
        """Calculate score for an agent based on task requirements"""
        score = 0.0
        
        # Base score from agent priority
        score += agent.config.priority * 0.1
        
        # Type match bonus
        if agent.config.agent_type in task_analysis.get("preferred_agent_types", []):
            score += 0.4
        
        # Capability match bonus
        required_caps = task_analysis.get("required_capabilities", [])
        matching_caps = set(agent.config.capabilities) & set(required_caps)
        if required_caps:
            score += (len(matching_caps) / len(required_caps)) * 0.3
        
        # Performance bonus
        if agent.metrics.total_tasks > 0:
            score += agent.metrics.success_rate * 0.2
            score += min(agent.metrics.average_confidence, 1.0) * 0.1
        
        # Preference bonus
        if preferences and agent.config.agent_id in preferences:
            score += 0.2
        
        # Load balancing - prefer less recently used agents
        if agent.metrics.last_used:
            time_since_last_use = time.time() - agent.metrics.last_used
            score += min(time_since_last_use / 3600, 0.1)  # Max 0.1 bonus for 1+ hour
        
        return score
    
    async def _select_top_agents(self, scored_agents: List[Dict[str, Any]], 
                               max_agents: int, task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select top agents ensuring diversity"""
        selected = []
        used_types = set()
        
        for agent_data in scored_agents:
            if len(selected) >= max_agents:
                break
            
            agent = agent_data["agent"]
            agent_type = agent.config.agent_type
            
            # Ensure diversity in agent types
            if len(selected) < max_agents - 1 or agent_type not in used_types:
                selected.append({
                    "agent_id": agent.config.agent_id,
                    "agent_type": agent_type.value,
                    "score": agent_data["score"],
                    "capabilities": agent.config.capabilities,
                    "specializations": agent.config.specializations
                })
                used_types.add(agent_type)
        
        return selected
    
    async def _record_agent_selection(self, task: str, selected_agents: List[Dict[str, Any]],
                                    task_analysis: Dict[str, Any]) -> None:
        """Record agent selection for learning and optimization"""
        selection_record = {
            "timestamp": time.time(),
            "task": task,
            "task_analysis": task_analysis,
            "selected_agents": [agent["agent_id"] for agent in selected_agents],
            "selection_scores": {agent["agent_id"]: agent["score"] for agent in selected_agents}
        }
        
        self.agent_selection_history.append(selection_record)
        
        # Limit history size
        if len(self.agent_selection_history) > 1000:
            self.agent_selection_history = self.agent_selection_history[-500:]
    
    async def _setup_load_balancing(self) -> None:
        """Setup load balancing for agents"""
        self.load_balancer_state = {
            "round_robin_index": 0,
            "load_distribution": {},
            "performance_weights": {}
        }
    
    async def shutdown(self) -> None:
        """Shutdown the agent manager"""
        try:
            logger.info("Shutting down Agent Manager...")
            
            # Shutdown all agents
            for agent_id, agent in self.agents.items():
                try:
                    # Wait for current tasks to complete
                    while agent.current_tasks:
                        await asyncio.sleep(0.1)
                    
                    agent.status = AgentStatus.UNAVAILABLE
                    logger.debug(f"Agent {agent_id} shutdown")
                except Exception as e:
                    logger.error(f"Error shutting down agent {agent_id}: {e}")
            
            self.is_initialized = False
            logger.info("Agent Manager shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during Agent Manager shutdown: {e}")
