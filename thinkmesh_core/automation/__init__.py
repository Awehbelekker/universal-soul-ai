"""
ThinkMesh Automation Module
==========================

Advanced cross-platform automation capabilities for Universal Soul AI.
Provides mobile navigation, GUI automation, and intelligent task execution
across all devices and platforms.

Key Features:
- Mobile interface navigation with computer vision
- Cross-platform GUI automation
- CoAct-1 hybrid automation (code + GUI)
- Privacy-first device synchronization
- Intelligent device adaptation
- Universal platform support

Copyright (c) 2025 ThinkMesh AI Systems
"""

from .mobile_navigator import MobileNavigator, MobileScreenAnalyzer, TouchSimulator
from .gui_automation import (
    GUIAutomationEngine,
    CrossPlatformAutomator,
    AutomationPlatform,
    ActionType,
    AutomationAction,
    AutomationResult
)
from .screen_analyzer import (
    ScreenAnalyzer,
    UIElementDetector,
    OCREngine,
    ScreenElement,
    ScreenAnalysisResult,
    LayoutAnalyzer
)
from .coact_integration import (
    CoAct1AutomationEngine,
    HybridTaskExecutor,
    ExecutionMethod,
    TaskAnalysis,
    HybridExecutionResult
)
from .device_adapter import (
    IntelligentDeviceAdapter,
    DeviceProfiler,
    DeviceType,
    OptimizationLevel,
    AdaptationResult
)

__all__ = [
    # Mobile Navigation
    'MobileNavigator',
    'MobileScreenAnalyzer',
    'TouchSimulator',

    # GUI Automation
    'GUIAutomationEngine',
    'CrossPlatformAutomator',
    'AutomationPlatform',
    'ActionType',
    'AutomationAction',
    'AutomationResult',

    # Screen Analysis
    'ScreenAnalyzer',
    'UIElementDetector',
    'OCREngine',
    'ScreenElement',
    'ScreenAnalysisResult',
    'LayoutAnalyzer',

    # CoAct-1 Integration
    'CoAct1AutomationEngine',
    'HybridTaskExecutor',
    'ExecutionMethod',
    'TaskAnalysis',
    'HybridExecutionResult',

    # Device Adaptation
    'IntelligentDeviceAdapter',
    'DeviceProfiler',
    'DeviceType',
    'OptimizationLevel',
    'AdaptationResult'
]

# Version information
__version__ = "1.0.0"
__author__ = "ThinkMesh AI Systems"
__description__ = "Advanced cross-platform automation for Universal Soul AI"
