"""
Mobile Interface Navigation System
=================================

Advanced mobile interface interaction using computer vision,
touch simulation, and HRM reasoning for intelligent navigation.
Provides Warmwind-like capabilities with superior privacy and intelligence.
"""

import asyncio
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging
from PIL import Image
import time
from dataclasses import dataclass

from ..interfaces import UserContext
from ..exceptions import ThinkMeshException, ErrorCode
from ..logging import get_logger

logger = get_logger(__name__)


@dataclass
class NavigationStep:
    """Represents a single navigation step"""
    action_type: str  # 'tap', 'swipe', 'type', 'wait'
    coordinates: Optional[Tuple[int, int]] = None
    text_input: Optional[str] = None
    duration: float = 0.1
    confidence: float = 0.8


@dataclass
class MobileScreenAnalysis:
    """Results of mobile screen analysis"""
    ui_elements: List[Dict[str, Any]]
    text_elements: List[Dict[str, Any]]
    interactive_elements: List[Dict[str, Any]]
    app_context: str
    task_objective: str
    confidence_score: float


@dataclass
class NavigationExecutionResult:
    """Results of navigation execution"""
    task_completed: bool
    steps_executed: List[Dict[str, Any]]
    final_screen_state: Optional[np.ndarray]
    confidence_score: float
    execution_time: float


class MobileNavigator:
    """Advanced mobile interface navigation system"""
    
    def __init__(self, hrm_engine=None):
        self.hrm_engine = hrm_engine
        self.screen_analyzer = MobileScreenAnalyzer()
        self.touch_simulator = TouchSimulator()
        self.element_detector = UIElementDetector()
        self.navigation_history = []
        
    async def navigate_mobile_app(self, app_name: str, task_description: str,
                                 context: UserContext) -> Dict[str, Any]:
        """Navigate any mobile app to complete a task"""
        try:
            start_time = time.time()
            logger.info(f"Starting mobile navigation for app: {app_name}, task: {task_description}")
            
            # Capture current screen
            screenshot = await self._capture_mobile_screen()
            
            # Analyze screen with computer vision
            screen_analysis = await self.screen_analyzer.analyze_interface(
                screenshot=screenshot,
                app_context=app_name,
                task_objective=task_description
            )
            
            # Create navigation plan (with or without HRM)
            if self.hrm_engine:
                navigation_plan = await self._create_hrm_navigation_plan(
                    screen_analysis, task_description, app_name, context
                )
            else:
                navigation_plan = await self._create_basic_navigation_plan(
                    screen_analysis, task_description
                )
            
            # Execute navigation steps
            execution_result = await self._execute_navigation_plan(
                navigation_plan=navigation_plan,
                screen_analysis=screen_analysis
            )
            
            execution_time = time.time() - start_time
            
            # Store in navigation history
            self.navigation_history.append({
                "app_name": app_name,
                "task_description": task_description,
                "execution_time": execution_time,
                "success": execution_result.task_completed,
                "timestamp": time.time()
            })
            
            return {
                "success": True,
                "task_completed": execution_result.task_completed,
                "steps_executed": execution_result.steps_executed,
                "final_screen_state": execution_result.final_screen_state is not None,
                "confidence_score": execution_result.confidence_score,
                "execution_time": execution_time,
                "navigation_method": "hrm_enhanced" if self.hrm_engine else "basic_cv"
            }
            
        except Exception as e:
            logger.error(f"Mobile navigation failed: {e}")
            raise ThinkMeshException(
                f"Mobile navigation error: {e}",
                ErrorCode.AUTOMATION_EXECUTION_FAILED
            )
    
    async def _capture_mobile_screen(self) -> np.ndarray:
        """Capture mobile device screen"""
        try:
            # Try to import mss for screen capture
            import mss
            
            with mss.mss() as sct:
                # Capture primary monitor (mobile device screen)
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array
                img_array = np.array(screenshot)
                
                # Convert BGRA to RGB
                img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGRA2RGB)
                
                return img_rgb
                
        except ImportError:
            logger.warning("mss not available, using fallback screen capture")
            # Fallback to basic screen capture
            return await self._fallback_screen_capture()
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            raise ThinkMeshException(
                f"Screen capture error: {e}",
                ErrorCode.SCREEN_CAPTURE_FAILED
            )
    
    async def _fallback_screen_capture(self) -> np.ndarray:
        """Fallback screen capture method"""
        try:
            import pyautogui
            
            # Capture screenshot
            screenshot = pyautogui.screenshot()
            
            # Convert to numpy array
            img_array = np.array(screenshot)
            
            # Convert RGB to BGR for OpenCV
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            return img_bgr
            
        except Exception as e:
            logger.error(f"Fallback screen capture failed: {e}")
            # Return a dummy image if all else fails
            return np.zeros((800, 600, 3), dtype=np.uint8)
    
    async def _create_hrm_navigation_plan(self, screen_analysis: MobileScreenAnalysis,
                                         task_description: str, app_name: str,
                                         context: UserContext) -> List[NavigationStep]:
        """Create navigation plan using HRM reasoning"""
        try:
            # Use HRM for intelligent navigation planning
            hrm_response = await self.hrm_engine.process_request(
                f"Create mobile navigation plan for app '{app_name}' to complete task: '{task_description}'. "
                f"Available UI elements: {len(screen_analysis.ui_elements)} elements detected. "
                f"Interactive elements: {len(screen_analysis.interactive_elements)} found.",
                context
            )
            
            # Parse HRM response into navigation steps
            navigation_steps = await self._parse_hrm_navigation_response(
                hrm_response, screen_analysis
            )
            
            return navigation_steps
            
        except Exception as e:
            logger.warning(f"HRM navigation planning failed, using fallback: {e}")
            return await self._create_basic_navigation_plan(screen_analysis, task_description)
    
    async def _create_basic_navigation_plan(self, screen_analysis: MobileScreenAnalysis,
                                           task_description: str) -> List[NavigationStep]:
        """Create basic navigation plan using computer vision"""
        
        navigation_steps = []
        
        # Simple heuristic-based navigation
        for element in screen_analysis.interactive_elements:
            if element.get('type') == 'button' and 'submit' in element.get('text', '').lower():
                navigation_steps.append(NavigationStep(
                    action_type='tap',
                    coordinates=(element['x'], element['y']),
                    confidence=0.7
                ))
                break
        
        # Add a wait step for UI response
        navigation_steps.append(NavigationStep(
            action_type='wait',
            duration=1.0,
            confidence=0.9
        ))
        
        return navigation_steps
    
    async def _execute_navigation_plan(self, navigation_plan: List[NavigationStep],
                                     screen_analysis: MobileScreenAnalysis) -> NavigationExecutionResult:
        """Execute the navigation plan step by step"""
        
        execution_steps = []
        start_time = time.time()
        
        for i, step in enumerate(navigation_plan):
            try:
                step_result = await self._execute_navigation_step(step, i)
                execution_steps.append(step_result)
                
                # Brief pause between steps for UI responsiveness
                await asyncio.sleep(0.3)
                
            except Exception as e:
                logger.error(f"Navigation step {i} failed: {e}")
                execution_steps.append({
                    "step_index": i,
                    "success": False,
                    "error": str(e),
                    "action_type": step.action_type
                })
        
        execution_time = time.time() - start_time
        
        # Capture final screen state
        try:
            final_screen = await self._capture_mobile_screen()
        except:
            final_screen = None
        
        return NavigationExecutionResult(
            task_completed=all(step.get("success", False) for step in execution_steps),
            steps_executed=execution_steps,
            final_screen_state=final_screen,
            confidence_score=sum(step.get("confidence", 0.5) for step in execution_steps) / len(execution_steps) if execution_steps else 0.0,
            execution_time=execution_time
        )
    
    async def _execute_navigation_step(self, step: NavigationStep, step_index: int) -> Dict[str, Any]:
        """Execute a single navigation step"""
        try:
            if step.action_type == 'tap' and step.coordinates:
                success = await self.touch_simulator.tap(
                    step.coordinates[0], step.coordinates[1], step.duration
                )
                
            elif step.action_type == 'swipe' and step.coordinates:
                # For swipe, coordinates should be (start_x, start_y, end_x, end_y)
                if len(step.coordinates) == 4:
                    success = await self.touch_simulator.swipe(
                        step.coordinates[0], step.coordinates[1],
                        step.coordinates[2], step.coordinates[3],
                        step.duration
                    )
                else:
                    success = False
                    
            elif step.action_type == 'type' and step.text_input:
                success = await self.touch_simulator.type_text(step.text_input)
                
            elif step.action_type == 'wait':
                await asyncio.sleep(step.duration)
                success = True
                
            else:
                success = False
            
            return {
                "step_index": step_index,
                "action_type": step.action_type,
                "success": success,
                "confidence": step.confidence,
                "coordinates": step.coordinates,
                "duration": step.duration
            }
            
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            return {
                "step_index": step_index,
                "action_type": step.action_type,
                "success": False,
                "error": str(e),
                "confidence": 0.0
            }


class MobileScreenAnalyzer:
    """Analyzes mobile screen interfaces using computer vision"""
    
    def __init__(self):
        self.ocr_available = self._check_ocr_availability()
        
    def _check_ocr_availability(self) -> bool:
        """Check if OCR capabilities are available"""
        try:
            import pytesseract
            return True
        except ImportError:
            logger.warning("pytesseract not available, OCR features disabled")
            return False
    
    async def analyze_interface(self, screenshot: np.ndarray, 
                               app_context: str, task_objective: str) -> MobileScreenAnalysis:
        """Analyze mobile interface elements"""
        
        # Detect UI elements using computer vision
        ui_elements = await self._detect_ui_elements(screenshot)
        
        # Extract text using OCR if available
        text_elements = await self._extract_text_elements(screenshot) if self.ocr_available else []
        
        # Identify interactive elements
        interactive_elements = await self._identify_interactive_elements(screenshot, ui_elements)
        
        # Calculate confidence score
        confidence_score = self._calculate_analysis_confidence(ui_elements, text_elements, interactive_elements)
        
        return MobileScreenAnalysis(
            ui_elements=ui_elements,
            text_elements=text_elements,
            interactive_elements=interactive_elements,
            app_context=app_context,
            task_objective=task_objective,
            confidence_score=confidence_score
        )
    
    async def _detect_ui_elements(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Detect UI elements using computer vision"""
        elements = []
        
        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter out very small elements
                if w > 20 and h > 20:
                    elements.append({
                        'id': f'element_{i}',
                        'type': 'unknown',
                        'x': int(x + w/2),  # Center point
                        'y': int(y + h/2),
                        'width': int(w),
                        'height': int(h),
                        'area': int(w * h),
                        'confidence': 0.6
                    })
            
        except Exception as e:
            logger.error(f"UI element detection failed: {e}")
        
        return elements
    
    async def _extract_text_elements(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Extract text using OCR"""
        text_elements = []
        
        if not self.ocr_available:
            return text_elements
        
        try:
            import pytesseract
            
            # Convert to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))
            
            # Extract text with bounding boxes
            data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
            
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if text and len(text) > 1:
                    text_elements.append({
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'confidence': data['conf'][i] / 100.0
                    })
                    
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
        
        return text_elements
    
    async def _identify_interactive_elements(self, screenshot: np.ndarray, 
                                           ui_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify interactive elements from UI elements"""
        interactive_elements = []
        
        for element in ui_elements:
            # Simple heuristics for identifying interactive elements
            width, height = element['width'], element['height']
            area = element['area']
            
            # Likely button if rectangular and medium-sized
            if 50 < width < 300 and 30 < height < 100 and 1500 < area < 30000:
                element_copy = element.copy()
                element_copy['type'] = 'button'
                element_copy['interactive'] = True
                interactive_elements.append(element_copy)
            
            # Likely input field if wide and short
            elif width > 100 and 20 < height < 60:
                element_copy = element.copy()
                element_copy['type'] = 'input'
                element_copy['interactive'] = True
                interactive_elements.append(element_copy)
        
        return interactive_elements
    
    def _calculate_analysis_confidence(self, ui_elements: List[Dict[str, Any]], 
                                     text_elements: List[Dict[str, Any]],
                                     interactive_elements: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for the analysis"""
        
        # Base confidence on number of elements detected
        element_score = min(1.0, len(ui_elements) / 10.0)
        text_score = min(1.0, len(text_elements) / 5.0) if self.ocr_available else 0.5
        interactive_score = min(1.0, len(interactive_elements) / 3.0)
        
        # Weighted average
        confidence = (element_score * 0.4 + text_score * 0.3 + interactive_score * 0.3)
        
        return max(0.1, min(1.0, confidence))


class TouchSimulator:
    """Simulates touch interactions on mobile devices"""
    
    def __init__(self):
        self.touch_precision = 0.95  # 95% accuracy for touch targets
        self.pyautogui_available = self._check_pyautogui_availability()
        
    def _check_pyautogui_availability(self) -> bool:
        """Check if pyautogui is available"""
        try:
            import pyautogui
            return True
        except ImportError:
            logger.warning("pyautogui not available, touch simulation disabled")
            return False
    
    async def tap(self, x: int, y: int, duration: float = 0.1) -> bool:
        """Simulate tap gesture"""
        if not self.pyautogui_available:
            logger.warning("Touch simulation not available")
            return False
            
        try:
            import pyautogui
            
            # Add small random offset for more natural interaction
            import random
            offset_x = random.randint(-2, 2)
            offset_y = random.randint(-2, 2)
            
            pyautogui.click(x + offset_x, y + offset_y, duration=duration)
            logger.debug(f"Tapped at ({x + offset_x}, {y + offset_y})")
            return True
            
        except Exception as e:
            logger.error(f"Touch simulation failed: {e}")
            return False
    
    async def swipe(self, start_x: int, start_y: int, 
                   end_x: int, end_y: int, duration: float = 0.5) -> bool:
        """Simulate swipe gesture"""
        if not self.pyautogui_available:
            logger.warning("Swipe simulation not available")
            return False
            
        try:
            import pyautogui
            
            pyautogui.drag(start_x, start_y, end_x, end_y, duration=duration)
            logger.debug(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            return True
            
        except Exception as e:
            logger.error(f"Swipe simulation failed: {e}")
            return False
    
    async def type_text(self, text: str) -> bool:
        """Simulate text input"""
        if not self.pyautogui_available:
            logger.warning("Text input simulation not available")
            return False
            
        try:
            import pyautogui
            
            pyautogui.typewrite(text, interval=0.05)  # Small delay between characters
            logger.debug(f"Typed text: {text[:20]}...")
            return True
            
        except Exception as e:
            logger.error(f"Text input simulation failed: {e}")
            return False


class UIElementDetector:
    """Detects and classifies UI elements"""
    
    def __init__(self):
        self.detection_confidence_threshold = 0.5
        
    async def detect_elements(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Detect UI elements in screenshot"""
        
        # This is a simplified implementation
        # In production, you might use more advanced computer vision models
        
        elements = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get binary image
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter based on size
                if w > 10 and h > 10:
                    element_type = self._classify_element(w, h, contour)
                    
                    elements.append({
                        'id': f'ui_element_{i}',
                        'type': element_type,
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'center_x': x + w // 2,
                        'center_y': y + h // 2,
                        'area': w * h,
                        'confidence': 0.7
                    })
                    
        except Exception as e:
            logger.error(f"Element detection failed: {e}")
        
        return elements
    
    def _classify_element(self, width: int, height: int, contour) -> str:
        """Classify UI element based on dimensions and shape"""
        
        aspect_ratio = width / height if height > 0 else 1
        area = width * height
        
        # Simple classification heuristics
        if 0.8 <= aspect_ratio <= 1.2 and 1000 < area < 10000:
            return 'button'
        elif aspect_ratio > 2 and height < 60:
            return 'input_field'
        elif aspect_ratio > 3 and height < 40:
            return 'text_label'
        elif width > 200 and height > 200:
            return 'container'
        else:
            return 'unknown'
