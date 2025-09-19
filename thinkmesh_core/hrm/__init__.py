"""
ThinkMesh HRM (Hierarchical Reasoning Model) Engine
==================================================

Revolutionary 27M parameter AI engine optimized for mobile devices.
Combines strategic planning with tactical execution for human-like reasoning.

Key Features:
- 27M parameters vs 175B+ in traditional models
- Single forward pass reasoning (no iterative prompting)
- Hierarchical brain-like architecture
- Mobile-optimized with battery awareness
- Local processing with complete privacy
"""

from .engine import HRMEngine
from .strategic_planner import StrategicPlanner
from .task_executor import TaskExecutor
from .learning_engine import LearningEngine
from .mobile_optimizer import HRMMobileOptimizer

__all__ = [
    "HRMEngine",
    "StrategicPlanner", 
    "TaskExecutor",
    "LearningEngine",
    "HRMMobileOptimizer"
]
