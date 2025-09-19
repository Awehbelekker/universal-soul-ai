"""
Multi-Agent Orchestration System
================================

Advanced multi-agent coordination system using crewAI framework for
collaborative AI agent coordination and collective intelligence.

Components:
- AgentOrchestrator: Main orchestration engine
- AgentManager: Agent lifecycle and coordination management
- CollectiveIntelligence: Multi-agent collaboration and consensus
- TaskDistributor: Intelligent task distribution and load balancing
- ContextStore: Shared context and knowledge management
"""

from .orchestrator import AgentOrchestrator, OrchestrationRequest, OrchestrationResult
from .agent_manager import AgentManager, AgentConfig, AgentStatus
from .collective_intelligence import CollectiveIntelligence, ConsensusResult
from .task_distributor import TaskDistributor, TaskAssignment
from .context_store import ContextStore, SharedContext

__all__ = [
    # Main orchestration
    "AgentOrchestrator",
    "OrchestrationRequest",
    "OrchestrationResult",
    
    # Agent management
    "AgentManager",
    "AgentConfig",
    "AgentStatus",
    
    # Collective intelligence
    "CollectiveIntelligence",
    "ConsensusResult",
    
    # Task distribution
    "TaskDistributor",
    "TaskAssignment",
    
    # Context management
    "ContextStore",
    "SharedContext"
]
