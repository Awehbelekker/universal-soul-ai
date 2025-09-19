"""
SynergyCore™ Orchestration Platform
===================================

Enterprise-grade AI orchestration platform coordinating multiple specialized 
AI models and services in parallel for complex problem-solving workflows.

Key Features:
- Multi-agent coordination with collective intelligence
- CodeSwarm™ development agents for autonomous software development
- Enterprise scaling and load balancing
- Cost optimization and resource efficiency
- Compliance monitoring and audit trails
- Real-time collaboration between specialized agents

Copyright (c) 2025 SynergyCore™ AI Systems
"""

from .orchestrator import SynergyCoreOrchestrator
from .agent_manager import EnterpriseAgentManager
from .context_store import EnterpriseContextStore
from .codeswarm_agent import CodeSwarmAgent
from .enterprise_coordinator import EnterpriseCoordinator

# Backward compatibility aliases
from .orchestrator import SynergyCoreOrchestrator as MultiAgentOrchestrator
from .agent_manager import EnterpriseAgentManager as AgentManager
from .context_store import EnterpriseContextStore as ContextStore

__all__ = [
    # Enterprise SynergyCore™ components
    "SynergyCoreOrchestrator",
    "EnterpriseAgentManager",
    "EnterpriseContextStore",
    "CodeSwarmAgent",
    "EnterpriseCoordinator",
    
    # Backward compatibility aliases
    "MultiAgentOrchestrator",
    "AgentManager",
    "ContextStore"
]
