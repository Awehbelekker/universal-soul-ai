"""
CogniFlow™ Reasoning Engine
==========================

Advanced hierarchical reasoning system mimicking human cognitive patterns
for strategic planning and tactical execution in enterprise environments.

Key Features:
- 27M parameters optimized for enterprise deployment
- Hierarchical brain-like architecture
- Single forward pass reasoning (no iterative prompting)
- Enterprise compliance and audit capabilities
- Mobile and edge optimization
- Complete privacy with local processing

Copyright (c) 2025 SynergyCore™ AI Systems
"""

from .engine import CogniFlowEngine
from .strategic_planner import EnterpriseStrategicPlanner
from .task_executor import EnterpriseTaskExecutor
from .learning_engine import EnterpriseLearningEngine
from .mobile_optimizer import CogniFlowMobileOptimizer

# Backward compatibility aliases
from .engine import CogniFlowEngine as HRMEngine
from .strategic_planner import EnterpriseStrategicPlanner as StrategicPlanner
from .task_executor import EnterpriseTaskExecutor as TaskExecutor
from .learning_engine import EnterpriseLearningEngine as LearningEngine
from .mobile_optimizer import CogniFlowMobileOptimizer as HRMMobileOptimizer

__all__ = [
    # Enterprise CogniFlow™ components
    "CogniFlowEngine",
    "EnterpriseStrategicPlanner", 
    "EnterpriseTaskExecutor",
    "EnterpriseLearningEngine",
    "CogniFlowMobileOptimizer",
    
    # Backward compatibility aliases
    "HRMEngine",
    "StrategicPlanner",
    "TaskExecutor", 
    "LearningEngine",
    "HRMMobileOptimizer"
]
