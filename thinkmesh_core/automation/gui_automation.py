"""
Cross-Platform GUI Automation Engine
===================================

Advanced GUI automation system supporting desktop, mobile, and web platforms.
Provides intelligent automation with safety checks and error recovery.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple, Union
import logging
from dataclasses import dataclass
from enum import Enum

from ..interfaces import UserContext
from ..exceptions import ThinkMeshException, ErrorCode
from ..logging import get_logger
from .screen_analyzer import ScreenAnalyzer, ScreenElement

logger = get_logger(__name__)


class AutomationPlatform(Enum):
    """Supported automation platforms"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    WEB = "web"
    SMART_TV = "smart_tv"


class ActionType(Enum):
    """Types of automation actions"""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE = "type"
    KEY_PRESS = "key_press"
    DRAG = "drag"
    SCROLL = "scroll"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    VERIFY = "verify"


@dataclass
class AutomationAction:
    """Represents a single automation action"""
    action_type: ActionType
    target: Optional[Union[ScreenElement, Tuple[int, int]]] = None
    text_input: Optional[str] = None
    key_combination: Optional[str] = None
    duration: float = 0.1
    timeout: float = 5.0
    retry_count: int = 3
    verification_text: Optional[str] = None


@dataclass
class AutomationResult:
    """Results of automation execution"""
    success: bool
    actions_executed: int
    total_actions: int
    execution_time: float
    error_message: Optional[str] = None
    screenshots: List[str] = None


class GUIAutomationEngine:
    """Main GUI automation engine"""
    
    def __init__(self, platform: AutomationPlatform = AutomationPlatform.DESKTOP):
        self.platform = platform
        self.screen_analyzer = ScreenAnalyzer()
        self.automation_driver = self._create_automation_driver(platform)
        self.safety_checker = AutomationSafetyChecker()
        self.error_recovery = ErrorRecoverySystem()
        
    def _create_automation_driver(self, platform: AutomationPlatform):
        """Create platform-specific automation driver"""
        if platform == AutomationPlatform.DESKTOP:
            return DesktopAutomationDriver()
        elif platform == AutomationPlatform.MOBILE:
            return MobileAutomationDriver()
        elif platform == AutomationPlatform.WEB:
            return WebAutomationDriver()
        elif platform == AutomationPlatform.SMART_TV:
            return SmartTVAutomationDriver()
        else:
            raise ThinkMeshException(
                f"Unsupported platform: {platform}",
                ErrorCode.PLATFORM_NOT_SUPPORTED
            )
    
    async def execute_automation_sequence(self, actions: List[AutomationAction],
                                        context: UserContext,
                                        safety_checks: bool = True) -> AutomationResult:
        """Execute a sequence of automation actions"""
        start_time = time.time()
        executed_actions = 0
        screenshots = []
        
        try:
            logger.info(f"Starting automation sequence with {len(actions)} actions")
            
            # Pre-execution safety check
            if safety_checks:
                safety_result = await self.safety_checker.check_automation_safety(actions, context)
                if not safety_result.safe:
                    raise ThinkMeshException(
                        f"Automation safety check failed: {safety_result.reason}",
                        ErrorCode.AUTOMATION_SAFETY_VIOLATION
                    )
            
            # Execute actions sequentially
            for i, action in enumerate(actions):
                try:
                    # Take screenshot before action if needed
                    if action.action_type in [ActionType.CLICK, ActionType.TYPE]:
                        screenshot_path = await self._take_screenshot(f"before_action_{i}")
                        screenshots.append(screenshot_path)
                    
                    # Execute the action
                    action_result = await self._execute_single_action(action, context)
                    
                    if action_result.success:
                        executed_actions += 1
                        logger.debug(f"Action {i+1}/{len(actions)} completed successfully")
                    else:
                        # Attempt error recovery
                        recovery_result = await self.error_recovery.attempt_recovery(
                            action, action_result.error, context
                        )
                        
                        if recovery_result.recovered:
                            executed_actions += 1
                            logger.info(f"Action {i+1} recovered successfully")
                        else:
                            logger.error(f"Action {i+1} failed and could not be recovered")
                            break
                    
                    # Brief pause between actions
                    await asyncio.sleep(0.2)
                    
                except Exception as e:
                    logger.error(f"Action {i+1} execution failed: {e}")
                    break
            
            execution_time = time.time() - start_time
            success = executed_actions == len(actions)
            
            return AutomationResult(
                success=success,
                actions_executed=executed_actions,
                total_actions=len(actions),
                execution_time=execution_time,
                screenshots=screenshots
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Automation sequence failed: {e}")
            
            return AutomationResult(
                success=False,
                actions_executed=executed_actions,
                total_actions=len(actions),
                execution_time=execution_time,
                error_message=str(e),
                screenshots=screenshots
            )
    
    async def _execute_single_action(self, action: AutomationAction, 
                                   context: UserContext) -> 'ActionResult':
        """Execute a single automation action"""
        try:
            if action.action_type == ActionType.CLICK:
                return await self.automation_driver.click(action.target, action.duration)
            
            elif action.action_type == ActionType.DOUBLE_CLICK:
                return await self.automation_driver.double_click(action.target, action.duration)
            
            elif action.action_type == ActionType.RIGHT_CLICK:
                return await self.automation_driver.right_click(action.target, action.duration)
            
            elif action.action_type == ActionType.TYPE:
                return await self.automation_driver.type_text(action.text_input, action.duration)
            
            elif action.action_type == ActionType.KEY_PRESS:
                return await self.automation_driver.press_key(action.key_combination)
            
            elif action.action_type == ActionType.DRAG:
                return await self.automation_driver.drag(action.target, action.duration)
            
            elif action.action_type == ActionType.SCROLL:
                return await self.automation_driver.scroll(action.target, action.duration)
            
            elif action.action_type == ActionType.WAIT:
                await asyncio.sleep(action.duration)
                return ActionResult(success=True)
            
            elif action.action_type == ActionType.SCREENSHOT:
                screenshot_path = await self._take_screenshot("manual_screenshot")
                return ActionResult(success=True, data={"screenshot": screenshot_path})
            
            elif action.action_type == ActionType.VERIFY:
                return await self._verify_element_or_text(action.verification_text)
            
            else:
                return ActionResult(success=False, error=f"Unknown action type: {action.action_type}")
                
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return ActionResult(success=False, error=str(e))
    
    async def _take_screenshot(self, filename_prefix: str) -> str:
        """Take a screenshot and return the file path"""
        try:
            screenshot_path = f"screenshots/{filename_prefix}_{int(time.time())}.png"
            await self.automation_driver.take_screenshot(screenshot_path)
            return screenshot_path
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return ""
    
    async def _verify_element_or_text(self, verification_text: str) -> 'ActionResult':
        """Verify that an element or text is present on screen"""
        try:
            # Take current screenshot
            screenshot = await self.automation_driver.get_current_screenshot()
            
            # Analyze screen
            analysis_result = await self.screen_analyzer.analyze_screen(screenshot)
            
            # Check if verification text is found
            for text_region in analysis_result.text_regions:
                if verification_text.lower() in text_region['text'].lower():
                    return ActionResult(success=True, data={"found_text": text_region['text']})
            
            return ActionResult(success=False, error=f"Verification text '{verification_text}' not found")
            
        except Exception as e:
            return ActionResult(success=False, error=f"Verification failed: {e}")


@dataclass
class ActionResult:
    """Result of a single action execution"""
    success: bool
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class CrossPlatformAutomator:
    """High-level cross-platform automation orchestrator"""
    
    def __init__(self):
        self.automation_engines = {}
        self.current_platform = None
        
    async def initialize_platform(self, platform: AutomationPlatform) -> bool:
        """Initialize automation for a specific platform"""
        try:
            if platform not in self.automation_engines:
                self.automation_engines[platform] = GUIAutomationEngine(platform)
            
            self.current_platform = platform
            logger.info(f"Initialized automation for platform: {platform.value}")
            return True
            
        except Exception as e:
            logger.error(f"Platform initialization failed: {e}")
            return False
    
    async def automate_task(self, task_description: str, platform: AutomationPlatform,
                          context: UserContext) -> AutomationResult:
        """Automate a high-level task across platforms"""
        
        # Initialize platform if needed
        if platform not in self.automation_engines:
            await self.initialize_platform(platform)
        
        automation_engine = self.automation_engines[platform]
        
        # Convert task description to automation actions
        actions = await self._task_to_actions(task_description, platform, context)
        
        # Execute automation
        result = await automation_engine.execute_automation_sequence(actions, context)
        
        return result
    
    async def _task_to_actions(self, task_description: str, platform: AutomationPlatform,
                             context: UserContext) -> List[AutomationAction]:
        """Convert high-level task description to automation actions"""
        
        # This is a simplified implementation
        # In practice, this would use NLP and AI to parse the task
        
        actions = []
        
        # Basic task parsing
        if "click" in task_description.lower():
            actions.append(AutomationAction(
                action_type=ActionType.CLICK,
                target=(100, 100)  # Would be determined by screen analysis
            ))
        
        if "type" in task_description.lower():
            # Extract text to type (simplified)
            text_to_type = "example text"
            actions.append(AutomationAction(
                action_type=ActionType.TYPE,
                text_input=text_to_type
            ))
        
        # Add verification step
        actions.append(AutomationAction(
            action_type=ActionType.VERIFY,
            verification_text="success"
        ))
        
        return actions


class DesktopAutomationDriver:
    """Desktop-specific automation driver"""
    
    def __init__(self):
        self.pyautogui_available = self._check_pyautogui()
        
    def _check_pyautogui(self) -> bool:
        try:
            import pyautogui
            return True
        except ImportError:
            logger.warning("pyautogui not available for desktop automation")
            return False
    
    async def click(self, target: Union[ScreenElement, Tuple[int, int]], 
                   duration: float) -> ActionResult:
        """Perform click action"""
        if not self.pyautogui_available:
            return ActionResult(success=False, error="pyautogui not available")
        
        try:
            import pyautogui
            
            if isinstance(target, ScreenElement):
                x, y = target.center_point
            else:
                x, y = target
            
            pyautogui.click(x, y, duration=duration)
            return ActionResult(success=True)
            
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    async def double_click(self, target: Union[ScreenElement, Tuple[int, int]], 
                          duration: float) -> ActionResult:
        """Perform double-click action"""
        if not self.pyautogui_available:
            return ActionResult(success=False, error="pyautogui not available")
        
        try:
            import pyautogui
            
            if isinstance(target, ScreenElement):
                x, y = target.center_point
            else:
                x, y = target
            
            pyautogui.doubleClick(x, y)
            return ActionResult(success=True)
            
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    async def right_click(self, target: Union[ScreenElement, Tuple[int, int]], 
                         duration: float) -> ActionResult:
        """Perform right-click action"""
        if not self.pyautogui_available:
            return ActionResult(success=False, error="pyautogui not available")
        
        try:
            import pyautogui
            
            if isinstance(target, ScreenElement):
                x, y = target.center_point
            else:
                x, y = target
            
            pyautogui.rightClick(x, y)
            return ActionResult(success=True)
            
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    async def type_text(self, text: str, duration: float) -> ActionResult:
        """Type text"""
        if not self.pyautogui_available:
            return ActionResult(success=False, error="pyautogui not available")
        
        try:
            import pyautogui
            
            pyautogui.typewrite(text, interval=duration/len(text) if text else 0.1)
            return ActionResult(success=True)
            
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    async def press_key(self, key_combination: str) -> ActionResult:
        """Press key or key combination"""
        if not self.pyautogui_available:
            return ActionResult(success=False, error="pyautogui not available")
        
        try:
            import pyautogui
            
            if '+' in key_combination:
                # Handle key combinations like 'ctrl+c'
                keys = key_combination.split('+')
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(key_combination)
            
            return ActionResult(success=True)
            
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    async def drag(self, target: Union[ScreenElement, Tuple[int, int]], 
                  duration: float) -> ActionResult:
        """Perform drag action"""
        # Implementation would depend on start and end points
        return ActionResult(success=False, error="Drag action not fully implemented")
    
    async def scroll(self, target: Union[ScreenElement, Tuple[int, int]], 
                    duration: float) -> ActionResult:
        """Perform scroll action"""
        if not self.pyautogui_available:
            return ActionResult(success=False, error="pyautogui not available")
        
        try:
            import pyautogui
            
            if isinstance(target, ScreenElement):
                x, y = target.center_point
            else:
                x, y = target
            
            pyautogui.scroll(3, x=x, y=y)  # Scroll up 3 clicks
            return ActionResult(success=True)
            
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    async def take_screenshot(self, filepath: str) -> ActionResult:
        """Take screenshot"""
        if not self.pyautogui_available:
            return ActionResult(success=False, error="pyautogui not available")
        
        try:
            import pyautogui
            import os
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            return ActionResult(success=True, data={"filepath": filepath})
            
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    async def get_current_screenshot(self):
        """Get current screenshot as numpy array"""
        if not self.pyautogui_available:
            return None
        
        try:
            import pyautogui
            import numpy as np
            
            screenshot = pyautogui.screenshot()
            return np.array(screenshot)
            
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return None


class MobileAutomationDriver:
    """Mobile-specific automation driver"""
    
    async def click(self, target, duration) -> ActionResult:
        return ActionResult(success=False, error="Mobile automation not implemented")
    
    async def double_click(self, target, duration) -> ActionResult:
        return ActionResult(success=False, error="Mobile automation not implemented")
    
    async def right_click(self, target, duration) -> ActionResult:
        return ActionResult(success=False, error="Mobile automation not implemented")
    
    async def type_text(self, text, duration) -> ActionResult:
        return ActionResult(success=False, error="Mobile automation not implemented")
    
    async def press_key(self, key_combination) -> ActionResult:
        return ActionResult(success=False, error="Mobile automation not implemented")
    
    async def drag(self, target, duration) -> ActionResult:
        return ActionResult(success=False, error="Mobile automation not implemented")
    
    async def scroll(self, target, duration) -> ActionResult:
        return ActionResult(success=False, error="Mobile automation not implemented")
    
    async def take_screenshot(self, filepath) -> ActionResult:
        return ActionResult(success=False, error="Mobile automation not implemented")
    
    async def get_current_screenshot(self):
        return None


class WebAutomationDriver:
    """Web-specific automation driver using Selenium/Playwright"""
    
    def __init__(self):
        self.selenium_available = self._check_selenium()
        self.playwright_available = self._check_playwright()
        
    def _check_selenium(self) -> bool:
        try:
            import selenium
            return True
        except ImportError:
            return False
    
    def _check_playwright(self) -> bool:
        try:
            import playwright
            return True
        except ImportError:
            return False
    
    async def click(self, target, duration) -> ActionResult:
        return ActionResult(success=False, error="Web automation not fully implemented")
    
    async def double_click(self, target, duration) -> ActionResult:
        return ActionResult(success=False, error="Web automation not fully implemented")
    
    async def right_click(self, target, duration) -> ActionResult:
        return ActionResult(success=False, error="Web automation not fully implemented")
    
    async def type_text(self, text, duration) -> ActionResult:
        return ActionResult(success=False, error="Web automation not fully implemented")
    
    async def press_key(self, key_combination) -> ActionResult:
        return ActionResult(success=False, error="Web automation not fully implemented")
    
    async def drag(self, target, duration) -> ActionResult:
        return ActionResult(success=False, error="Web automation not fully implemented")
    
    async def scroll(self, target, duration) -> ActionResult:
        return ActionResult(success=False, error="Web automation not fully implemented")
    
    async def take_screenshot(self, filepath) -> ActionResult:
        return ActionResult(success=False, error="Web automation not fully implemented")
    
    async def get_current_screenshot(self):
        return None


class SmartTVAutomationDriver:
    """Smart TV automation driver"""
    
    async def click(self, target, duration) -> ActionResult:
        return ActionResult(success=False, error="Smart TV automation not implemented")
    
    async def double_click(self, target, duration) -> ActionResult:
        return ActionResult(success=False, error="Smart TV automation not implemented")
    
    async def right_click(self, target, duration) -> ActionResult:
        return ActionResult(success=False, error="Smart TV automation not implemented")
    
    async def type_text(self, text, duration) -> ActionResult:
        return ActionResult(success=False, error="Smart TV automation not implemented")
    
    async def press_key(self, key_combination) -> ActionResult:
        return ActionResult(success=False, error="Smart TV automation not implemented")
    
    async def drag(self, target, duration) -> ActionResult:
        return ActionResult(success=False, error="Smart TV automation not implemented")
    
    async def scroll(self, target, duration) -> ActionResult:
        return ActionResult(success=False, error="Smart TV automation not implemented")
    
    async def take_screenshot(self, filepath) -> ActionResult:
        return ActionResult(success=False, error="Smart TV automation not implemented")
    
    async def get_current_screenshot(self):
        return None


class AutomationSafetyChecker:
    """Checks automation safety before execution"""
    
    async def check_automation_safety(self, actions: List[AutomationAction], 
                                    context: UserContext) -> 'SafetyResult':
        """Check if automation sequence is safe to execute"""
        
        # Check for dangerous actions
        dangerous_actions = [ActionType.KEY_PRESS]  # Could include system keys
        
        for action in actions:
            if action.action_type in dangerous_actions:
                if action.key_combination and any(key in action.key_combination.lower() 
                                                for key in ['alt+f4', 'ctrl+alt+del', 'cmd+q']):
                    return SafetyResult(safe=False, reason="Dangerous key combination detected")
        
        # Check for excessive actions
        if len(actions) > 100:
            return SafetyResult(safe=False, reason="Too many actions in sequence")
        
        return SafetyResult(safe=True, reason="Automation sequence is safe")


@dataclass
class SafetyResult:
    """Result of safety check"""
    safe: bool
    reason: str


class ErrorRecoverySystem:
    """Handles error recovery during automation"""
    
    async def attempt_recovery(self, failed_action: AutomationAction, 
                             error: str, context: UserContext) -> 'RecoveryResult':
        """Attempt to recover from a failed action"""
        
        # Simple recovery strategies
        if "element not found" in error.lower():
            # Wait and retry
            await asyncio.sleep(2)
            return RecoveryResult(recovered=True, strategy="wait_and_retry")
        
        if "timeout" in error.lower():
            # Increase timeout and retry
            return RecoveryResult(recovered=True, strategy="increase_timeout")
        
        return RecoveryResult(recovered=False, strategy="no_recovery_available")


@dataclass
class RecoveryResult:
    """Result of error recovery attempt"""
    recovered: bool
    strategy: str
