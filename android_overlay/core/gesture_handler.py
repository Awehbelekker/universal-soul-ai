"""
Android Gesture Handler for Universal Soul AI Overlay
====================================================

Implements 8-direction 360° gesture recognition system based on the
360_gesture_integration_guide.md with Android-specific optimizations.

Features:
- 8-directional gesture detection (N, NE, E, SE, S, SW, W, NW)
- Haptic feedback integration
- Contextual gesture mappings
- Performance optimization for mobile
"""

import asyncio
import math
import time
from typing import Dict, Any, Optional, List, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Android-specific imports
try:
    from android.runnable import run_on_ui_thread
    from jnius import autoclass
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False

logger = logging.getLogger(__name__)


class GestureDirection(Enum):
    """8-direction gesture system"""
    NORTH = "north"          # ↑ - Calendar/Scheduling
    NORTHEAST = "northeast"  # ↗ - Quick Actions
    EAST = "east"           # → - AI Transcription
    SOUTHEAST = "southeast"  # ↘ - Settings
    SOUTH = "south"         # ↓ - Task Management
    SOUTHWEST = "southwest"  # ↙ - History
    WEST = "west"           # ← - Notes/Capture
    NORTHWEST = "northwest"  # ↖ - Voice Commands


class GestureType(Enum):
    """Types of gestures supported"""
    SWIPE = "swipe"
    TAP = "tap"
    LONG_PRESS = "long_press"
    DOUBLE_TAP = "double_tap"
    PINCH = "pinch"
    ROTATE = "rotate"


@dataclass
class GestureEvent:
    """Gesture event data structure"""
    gesture_type: GestureType
    direction: Optional[GestureDirection]
    start_point: Tuple[float, float]
    end_point: Tuple[float, float]
    velocity: float
    distance: float
    duration: float
    confidence: float
    timestamp: float


@dataclass
class GestureConfig:
    """Configuration for gesture recognition"""
    # Distance thresholds
    min_swipe_distance: float = 50.0  # dp
    max_swipe_distance: float = 300.0  # dp
    
    # Velocity thresholds
    min_swipe_velocity: float = 100.0  # dp/s
    max_swipe_velocity: float = 2000.0  # dp/s
    
    # Time thresholds
    max_swipe_duration: float = 1.0  # seconds
    long_press_duration: float = 0.5  # seconds
    double_tap_interval: float = 0.3  # seconds
    
    # Confidence thresholds
    min_confidence: float = 0.7
    direction_tolerance: float = 22.5  # degrees (45°/2)
    
    # Haptic feedback
    haptic_enabled: bool = True
    haptic_intensity: float = 0.8


class GestureHandler:
    """
    Android gesture recognition handler for Universal Soul AI overlay
    
    Implements the 360° gesture system with contextual mappings and
    haptic feedback for optimal mobile experience.
    """
    
    def __init__(self, sensitivity: float = 0.8, timeout: float = 2.0, haptic_enabled: bool = True):
        self.config = GestureConfig(
            min_confidence=sensitivity,
            max_swipe_duration=timeout,
            haptic_enabled=haptic_enabled
        )
        
        # State tracking
        self.is_initialized = False
        self.gesture_in_progress = False
        self.last_touch_time = 0.0
        self.touch_start_point: Optional[Tuple[float, float]] = None
        self.touch_current_point: Optional[Tuple[float, float]] = None
        
        # Gesture history for pattern recognition
        self.gesture_history: List[GestureEvent] = []
        self.max_history_size = 50
        
        # Contextual mappings
        self.context_mappings: Dict[str, Dict[GestureDirection, str]] = {
            "default": {
                GestureDirection.NORTH: "calendar",
                GestureDirection.NORTHEAST: "quick_actions",
                GestureDirection.EAST: "transcription",
                GestureDirection.SOUTHEAST: "settings",
                GestureDirection.SOUTH: "tasks",
                GestureDirection.SOUTHWEST: "history",
                GestureDirection.WEST: "notes",
                GestureDirection.NORTHWEST: "voice_commands"
            }
        }
        
        # Callbacks
        self.on_gesture_detected: Optional[Callable[[GestureEvent], None]] = None
        self.on_gesture_started: Optional[Callable[[Tuple[float, float]], None]] = None
        self.on_gesture_ended: Optional[Callable[[GestureEvent], None]] = None
        
        # Android components
        self.vibrator = None
        self.haptic_feedback = None
    
    async def initialize(self) -> bool:
        """Initialize gesture recognition system"""
        try:
            logger.info("Initializing gesture handler...")
            
            if ANDROID_AVAILABLE:
                await self._initialize_android_components()
            else:
                logger.info("Android not available - using simulation mode")
            
            self.is_initialized = True
            logger.info("Gesture handler initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize gesture handler: {e}")
            return False
    
    async def _initialize_android_components(self) -> None:
        """Initialize Android-specific gesture components"""
        try:
            # Get vibrator service for haptic feedback
            Context = autoclass('android.content.Context')
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            
            self.vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
            
            # Initialize haptic feedback
            if hasattr(self.vibrator, 'hasVibrator') and self.vibrator.hasVibrator():
                self.haptic_feedback = self.vibrator
                logger.info("Haptic feedback initialized")
            else:
                logger.warning("Haptic feedback not available")
                
        except Exception as e:
            logger.error(f"Failed to initialize Android components: {e}")
    
    def register_touch_events(self, overlay_view) -> None:
        """Register touch event handlers on overlay view"""
        if not ANDROID_AVAILABLE:
            return
        
        # Set up touch listener
        overlay_view.setOnTouchListener(self._on_touch_event)
        logger.info("Touch events registered on overlay")
    
    def _on_touch_event(self, view, motion_event) -> bool:
        """Handle Android touch events"""
        try:
            action = motion_event.getAction()
            x = motion_event.getX()
            y = motion_event.getY()
            current_time = time.time()
            
            if action == 0:  # ACTION_DOWN
                return self._handle_touch_down(x, y, current_time)
            elif action == 1:  # ACTION_UP
                return self._handle_touch_up(x, y, current_time)
            elif action == 2:  # ACTION_MOVE
                return self._handle_touch_move(x, y, current_time)
            
            return False
            
        except Exception as e:
            logger.error(f"Touch event handling failed: {e}")
            return False
    
    def _handle_touch_down(self, x: float, y: float, timestamp: float) -> bool:
        """Handle touch down event"""
        self.touch_start_point = (x, y)
        self.touch_current_point = (x, y)
        self.last_touch_time = timestamp
        self.gesture_in_progress = True
        
        # Trigger gesture started callback
        if self.on_gesture_started:
            self.on_gesture_started((x, y))
        
        logger.debug(f"Touch down at ({x}, {y})")
        return True
    
    def _handle_touch_move(self, x: float, y: float, timestamp: float) -> bool:
        """Handle touch move event"""
        if not self.gesture_in_progress or not self.touch_start_point:
            return False
        
        self.touch_current_point = (x, y)
        
        # Calculate current gesture metrics
        distance = self._calculate_distance(self.touch_start_point, (x, y))
        duration = timestamp - self.last_touch_time
        
        # Check if this could be a valid swipe
        if distance > self.config.min_swipe_distance:
            direction = self._calculate_direction(self.touch_start_point, (x, y))
            velocity = distance / max(duration, 0.001)  # Avoid division by zero
            
            logger.debug(f"Gesture in progress: distance={distance:.1f}, direction={direction}, velocity={velocity:.1f}")
        
        return True
    
    def _handle_touch_up(self, x: float, y: float, timestamp: float) -> bool:
        """Handle touch up event and recognize gesture"""
        if not self.gesture_in_progress or not self.touch_start_point:
            return False
        
        try:
            # Calculate gesture metrics
            distance = self._calculate_distance(self.touch_start_point, (x, y))
            duration = timestamp - self.last_touch_time
            velocity = distance / max(duration, 0.001)
            
            # Determine gesture type and direction
            gesture_event = self._recognize_gesture(
                self.touch_start_point, (x, y), distance, velocity, duration, timestamp
            )
            
            if gesture_event and gesture_event.confidence >= self.config.min_confidence:
                # Add to history
                self._add_to_history(gesture_event)
                
                # Trigger haptic feedback
                if self.config.haptic_enabled:
                    # Schedule haptic feedback as a task instead of awaiting
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            loop.create_task(self._trigger_haptic_feedback(gesture_event))
                        else:
                            # If no loop running, skip haptic feedback
                            pass
                    except:
                        # Fallback: skip haptic feedback if asyncio not available
                        pass
                
                # Trigger gesture detected callback
                if self.on_gesture_detected:
                    self.on_gesture_detected(gesture_event)
                
                # Trigger gesture ended callback
                if self.on_gesture_ended:
                    self.on_gesture_ended(gesture_event)
                
                logger.info(f"Gesture recognized: {gesture_event.gesture_type.value} {gesture_event.direction.value if gesture_event.direction else 'none'} (confidence: {gesture_event.confidence:.2f})")
            
            return True
            
        finally:
            # Reset gesture state
            self.gesture_in_progress = False
            self.touch_start_point = None
            self.touch_current_point = None
    
    def _recognize_gesture(self, start: Tuple[float, float], end: Tuple[float, float],
                          distance: float, velocity: float, duration: float, timestamp: float) -> Optional[GestureEvent]:
        """Recognize gesture type and direction"""
        
        # Determine gesture type based on metrics
        if distance < 10.0 and duration < self.config.long_press_duration:
            gesture_type = GestureType.TAP
            direction = None
            confidence = 0.9
            
        elif distance < 10.0 and duration >= self.config.long_press_duration:
            gesture_type = GestureType.LONG_PRESS
            direction = None
            confidence = 0.9
            
        elif (distance >= self.config.min_swipe_distance and 
              distance <= self.config.max_swipe_distance and
              velocity >= self.config.min_swipe_velocity and
              duration <= self.config.max_swipe_duration):
            
            gesture_type = GestureType.SWIPE
            direction = self._calculate_direction(start, end)
            confidence = self._calculate_confidence(distance, velocity, duration)
            
        else:
            # Gesture doesn't meet criteria
            return None
        
        return GestureEvent(
            gesture_type=gesture_type,
            direction=direction,
            start_point=start,
            end_point=end,
            velocity=velocity,
            distance=distance,
            duration=duration,
            confidence=confidence,
            timestamp=timestamp
        )
    
    def _calculate_direction(self, start: Tuple[float, float], end: Tuple[float, float]) -> GestureDirection:
        """Calculate 8-direction gesture direction"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        # Calculate angle in degrees (0° = East, 90° = North)
        angle = math.degrees(math.atan2(-dy, dx))  # Negative dy for screen coordinates
        
        # Normalize to 0-360°
        if angle < 0:
            angle += 360
        
        # Map to 8 directions (45° sectors)
        if 337.5 <= angle or angle < 22.5:
            return GestureDirection.EAST
        elif 22.5 <= angle < 67.5:
            return GestureDirection.NORTHEAST
        elif 67.5 <= angle < 112.5:
            return GestureDirection.NORTH
        elif 112.5 <= angle < 157.5:
            return GestureDirection.NORTHWEST
        elif 157.5 <= angle < 202.5:
            return GestureDirection.WEST
        elif 202.5 <= angle < 247.5:
            return GestureDirection.SOUTHWEST
        elif 247.5 <= angle < 292.5:
            return GestureDirection.SOUTH
        else:  # 292.5 <= angle < 337.5
            return GestureDirection.SOUTHEAST
    
    def _calculate_distance(self, start: Tuple[float, float], end: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def _calculate_confidence(self, distance: float, velocity: float, duration: float) -> float:
        """Calculate gesture recognition confidence score"""
        # Base confidence from distance (optimal range: 50-150 dp)
        distance_score = 1.0 - abs(distance - 100) / 100
        distance_score = max(0.0, min(1.0, distance_score))
        
        # Velocity score (optimal range: 200-800 dp/s)
        velocity_score = 1.0 - abs(velocity - 500) / 500
        velocity_score = max(0.0, min(1.0, velocity_score))
        
        # Duration score (optimal: quick gestures)
        duration_score = max(0.0, 1.0 - duration / self.config.max_swipe_duration)
        
        # Weighted average
        confidence = (distance_score * 0.4 + velocity_score * 0.4 + duration_score * 0.2)
        
        return max(0.0, min(1.0, confidence))
    
    async def _trigger_haptic_feedback(self, gesture_event: GestureEvent) -> None:
        """Trigger haptic feedback for gesture"""
        if not self.haptic_feedback or not self.config.haptic_enabled:
            return
        
        try:
            # Different patterns for different gestures
            if gesture_event.gesture_type == GestureType.TAP:
                duration = 50  # Short tap
            elif gesture_event.gesture_type == GestureType.LONG_PRESS:
                duration = 100  # Medium press
            elif gesture_event.gesture_type == GestureType.SWIPE:
                duration = 75  # Swipe feedback
            else:
                duration = 50  # Default
            
            # Trigger vibration
            self.haptic_feedback.vibrate(duration)
            
        except Exception as e:
            logger.error(f"Haptic feedback failed: {e}")
    
    def _add_to_history(self, gesture_event: GestureEvent) -> None:
        """Add gesture to history for pattern analysis"""
        self.gesture_history.append(gesture_event)
        
        # Maintain history size limit
        if len(self.gesture_history) > self.max_history_size:
            self.gesture_history.pop(0)
    
    def get_gesture_mapping(self, context: str, direction: GestureDirection) -> Optional[str]:
        """Get action mapping for gesture in given context"""
        context_map = self.context_mappings.get(context, self.context_mappings["default"])
        return context_map.get(direction)
    
    def update_context_mappings(self, context: str, mappings: Dict[GestureDirection, str]) -> None:
        """Update gesture mappings for specific context"""
        self.context_mappings[context] = mappings
        logger.info(f"Updated gesture mappings for context: {context}")
