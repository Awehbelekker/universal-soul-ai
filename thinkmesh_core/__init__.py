"""
SynergyCore™ Enterprise AI Platform - Core Module
================================================

Revolutionary enterprise AI platform that combines mobile-first design
with enterprise-grade capabilities, eliminating AI costs while maintaining
complete privacy and compliance.

Key Features:
- CogniFlow™ 27M Parameter Reasoning Engine optimized for enterprise
- SynergyCore™ Orchestration Platform with collective intelligence
- EdgeMind™ Local AI Service for on-premise deployment
- OptiCore™ Resource Optimizer reducing AI costs by up to 70%
- CodeSwarm™ Development Agents for autonomous software development
- Complete Privacy with all processing happening on-premise
- Zero AI Costs with no API fees or cloud dependencies
- Enterprise Compliance and Governance built-in

Copyright (c) 2025 SynergyCore™ AI Systems
"""

__version__ = "1.0.0"
__author__ = "SynergyCore™ AI Systems"
__license__ = "Proprietary"

# Enterprise system components
from .neuralmesh_system import (
    NeuralMeshSystem, neuralmesh_enterprise_system,
    get_enterprise_system, set_enterprise_system
)
from .enterprise_config import (
    NeuralMeshConfig, get_enterprise_config, set_enterprise_config
)
from .enterprise_interfaces import *

# Core infrastructure (with backward compatibility)
from .system import ThinkMeshSystem, thinkmesh_system, get_system, set_system
from .config import ThinkMeshConfig, get_config, set_config
from .interfaces import *
from .container import get_container, register, register_instance, resolve
from .health import HealthChecker
from .logging import get_logger
from .exceptions import ThinkMeshException, ErrorCode

# Enterprise component modules (to be implemented)
# from . import cogniflow
# from . import synergycore
# from . import edgemind
# from . import opticore

# Legacy component modules (backward compatibility)
from . import hrm
from . import orchestration
from . import voice
from . import localai
from . import automation
from . import sync
from .automation_integration import (
    AutomationSystemIntegrator,
    initialize_automation_system,
    get_automation_integrator,
    execute_automation_task
)
# from . import data
# from . import mobile

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",

    # Enterprise system
    "NeuralMeshSystem",
    "neuralmesh_enterprise_system",
    "get_enterprise_system",
    "set_enterprise_system",

    # Enterprise configuration
    "NeuralMeshConfig",
    "get_enterprise_config",
    "set_enterprise_config",

    # Legacy system (backward compatibility)
    "ThinkMeshSystem",
    "thinkmesh_system",
    "get_system",
    "set_system",

    # Legacy configuration (backward compatibility)
    "ThinkMeshConfig",
    "get_config",
    "set_config",

    # Infrastructure
    "get_container",
    "register",
    "register_instance",
    "resolve",
    "HealthChecker",
    "get_logger",
    "ThinkMeshException",
    "ErrorCode",

    # Enterprise interfaces
    "ICogniFlowEngine",
    "ISynergyCoreOrchestrator",
    "IEdgeMindService",
    "IOptiCoreOptimizer",
    "INeuralMeshDataManager",
    "ICodeSwarmAgent",
    "IEnterpriseCompliance",
    "IEnterpriseCostOptimizer",

    # Legacy interfaces (backward compatibility)
    "IAIEngine",
    "IAgentOrchestrator",
    "IVoiceInterface",
    "IDataManager",
    "IHealthCheck",
    "ILocalAIService",
    "IMobileOptimizer",

    # Core data structures
    "UserContext",
    "VoiceInput",
    "VoiceOutput",
    "HealthStatus",
    "ComponentStatus",
    "TaskPriority",
    "AgentRole",

    # Automation system
    "AutomationSystemIntegrator",
    "initialize_automation_system",
    "get_automation_integrator",
    "execute_automation_task",
]
