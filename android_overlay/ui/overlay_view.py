"""
Android Overlay UI Components for Universal Soul AI
==================================================

Creates the visual overlay interface with voice button, gesture indicators,
privacy status, and contextual adaptations.

Features:
- Floating circular overlay with voice button
- 8-direction gesture visual indicators
- Privacy and status indicators
- Contextual color and icon adaptations
- Smooth animations and transitions
"""

import asyncio
import time
import math
from typing import Dict, Any, Optional, List, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Android-specific imports
try:
    from jnius import autoclass
    from android.runnable import run_on_ui_thread
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False

# Kivy imports for UI (fallback for testing)
try:
    from kivy.uix.widget import Widget
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.graphics import Color, Ellipse, Line, Rectangle
    from kivy.animation import Animation
    from kivy.clock import Clock
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False

logger = logging.getLogger(__name__)


class OverlayTheme:
    """Visual theme for Universal Soul AI minimalist overlay"""
    # Brand colors - Material Design 3 compliant
    PRIMARY = "#1976D2"      # Universal Soul AI blue
    SECONDARY = "#03DAC6"    # Teal accent
    ACCENT = "#FF6B35"       # Orange highlight
    SURFACE = "#FFFFFF"      # Surface color
    ON_SURFACE = "#1C1B1F"   # Text on surface

    # State colors with subtle variations
    LISTENING = "#4CAF50"    # Green for voice active
    PROCESSING = "#FF9800"   # Orange for processing
    GESTURE_ACTIVE = "#E3F2FD"  # Very light blue for gesture feedback
    ERROR = "#F44336"        # Red for errors
    PRIVACY = "#9C27B0"      # Purple for privacy mode

    # Transparency levels for minimalist design
    ALPHA_NORMAL = 0.95      # Slightly more opaque for premium feel
    ALPHA_MINIMIZED = 0.85   # Subtle presence when minimized
    ALPHA_GESTURE_GLOW = 0.3 # Gentle glow during gestures
    ALPHA_HIDDEN = 0.0       # Completely hidden

    # Minimalist sizes (dp) - Material Design 3 standards
    MINIMALIST_ICON_SIZE = 56    # Standard FAB size
    EXPANDED_PANEL_WIDTH = 280   # Quick access panel width
    EXPANDED_PANEL_HEIGHT = 200  # Quick access panel height
    GLOW_RADIUS = 8             # Subtle glow effect radius
    ELEVATION = 6               # Material elevation for depth
    CORNER_RADIUS = 28          # Perfect circle (half of icon size)

    # Animation durations (ms) for smooth interactions
    ANIMATION_FAST = 150        # Quick state changes
    ANIMATION_NORMAL = 250      # Standard transitions
    ANIMATION_SLOW = 350        # Expansion/collapse

    # Touch targets and spacing
    TOUCH_TARGET_SIZE = 48      # Minimum touch target (accessibility)
    PANEL_PADDING = 16          # Internal panel padding
    PANEL_ITEM_HEIGHT = 48      # Height of each panel item


class OverlayState(Enum):
    """Visual states of the minimalist overlay"""
    MINIMIZED = "minimized"          # Small floating icon only
    EXPANDED = "expanded"            # Quick access panel visible
    LISTENING = "listening"          # Voice recognition active
    PROCESSING = "processing"        # AI processing request
    GESTURE_FEEDBACK = "gesture_feedback"  # Subtle glow during gesture
    HIDDEN = "hidden"               # Completely hidden


@dataclass
class QuickAccessItem:
    """Item in the quick access panel"""
    title: str
    icon: str
    action: str
    context_relevant: bool = True

@dataclass
class MinimalistOverlayConfig:
    """Configuration for minimalist overlay appearance"""
    icon_size: int = OverlayTheme.MINIMALIST_ICON_SIZE
    auto_minimize_delay: float = 2.5
    gesture_feedback_duration: float = 0.3
    expansion_animation_duration: float = OverlayTheme.ANIMATION_NORMAL
    enable_subtle_animations: bool = True
    respect_system_theme: bool = True


class MinimalistOverlayView:
    """
    Minimalist floating overlay for Universal Soul AI

    Creates a small, elegant floating icon that expands to show
    contextual AI features when tapped. Gestures work invisibly
    on the icon with subtle visual feedback only.
    """

    def __init__(self, config: Optional[MinimalistOverlayConfig] = None):
        self.config = config or MinimalistOverlayConfig()
        self.size = self.config.icon_size
        self.state = OverlayState.MINIMIZED
        self.is_initialized = False

        # Core UI components
        self.root_view = None
        self.floating_icon = None
        self.quick_access_panel = None
        self.glow_effect = None

        # Animation controllers
        self.glow_animation = None
        self.pulse_animation = None
        self.expansion_animation = None
        self.auto_minimize_timer = None

        # State management
        self.is_expanded = False
        self.is_gesture_active = False
        self.last_interaction_time = 0

        # Context adaptation
        self.current_context_color = OverlayTheme.PRIMARY
        self.current_context_icon = "🧠"
        self.quick_access_items: List[QuickAccessItem] = []
        
        # Event callbacks
        self.on_icon_tap: Optional[Callable] = None
        self.on_gesture_detected: Optional[Callable] = None
        self.on_quick_action_selected: Optional[Callable] = None
        self.on_context_change: Optional[Callable] = None
        self.on_auto_minimize: Optional[Callable] = None

        # Initialize minimalist interface
        self._initialize_minimalist_interface()

    def _initialize_minimalist_interface(self) -> None:
        """Initialize the minimalist overlay interface"""
        # Set up default quick access items (will be updated based on context)
        self.quick_access_items = [
            QuickAccessItem("Voice Assistant", "🎙️", "voice_assistant"),
            QuickAccessItem("Quick Note", "📝", "quick_note"),
            QuickAccessItem("Smart Actions", "⚡", "smart_actions"),
            QuickAccessItem("Context Help", "🧠", "context_help")
        ]

        # Initialize animation timers
        self.auto_minimize_timer = None

        logger.debug("Minimalist overlay interface initialized")

    async def initialize(self) -> bool:
        """Initialize overlay UI components"""
        try:
            logger.info("Initializing overlay view...")
            
            if ANDROID_AVAILABLE:
                await self._create_android_view()
            elif KIVY_AVAILABLE:
                await self._create_kivy_view()
            else:
                logger.warning("No UI framework available - using mock view")
                await self._create_mock_view()
            
            self.is_initialized = True
            logger.info("Overlay view initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize overlay view: {e}")
            return False
    
    def _initialize_gesture_indicators(self) -> None:
        """Initialize 8-direction gesture indicators"""
        directions = [
            ("north", 90, "📅", "Calendar"),
            ("northeast", 45, "⚡", "Quick Actions"),
            ("east", 0, "🎤", "Transcription"),
            ("southeast", 315, "⚙️", "Settings"),
            ("south", 270, "✅", "Tasks"),
            ("southwest", 225, "📚", "History"),
            ("west", 180, "📝", "Notes"),
            ("northwest", 135, "🎙️", "Voice Commands")
        ]
        
        for direction, angle, icon, label in directions:
            self.gesture_indicators[direction] = GestureIndicator(
                direction=direction,
                angle=angle,
                icon=icon,
                color=OverlayTheme.SECONDARY
            )
    
    async def _create_android_view(self) -> None:
        """Create native Android overlay view"""
        try:
            # Create custom Android view
            View = autoclass('android.view.View')
            LinearLayout = autoclass('android.widget.LinearLayout')
            Button = autoclass('android.widget.Button')
            ImageView = autoclass('android.widget.ImageView')
            
            # Create root layout
            self.root_view = LinearLayout(autoclass('org.kivy.android.PythonActivity').mActivity)
            self.root_view.setOrientation(LinearLayout.VERTICAL)
            self.root_view.setGravity(0x11)  # CENTER
            
            # Create voice button
            self.voice_button = Button(autoclass('org.kivy.android.PythonActivity').mActivity)
            self.voice_button.setText("🧠")
            self.voice_button.setTextSize(32)
            self.voice_button.setBackgroundColor(self._color_to_int(OverlayTheme.PRIMARY))
            
            # Set button click listener
            self.voice_button.setOnClickListener(self._on_voice_button_click)
            
            # Add to layout
            self.root_view.addView(self.voice_button)
            
            logger.info("Android overlay view created")
            
        except Exception as e:
            logger.error(f"Failed to create Android view: {e}")
            raise
    
    async def _create_kivy_view(self) -> None:
        """Create minimalist Kivy-based overlay view"""
        try:
            from kivy.uix.floatlayout import FloatLayout
            from kivy.uix.button import Button
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.label import Label
            from kivy.graphics import Color, Ellipse, Rectangle
            from kivy.animation import Animation
            from kivy.metrics import dp

            # Create root layout for floating icon
            self.root_view = FloatLayout(
                size=(dp(self.size), dp(self.size)),
                size_hint=(None, None)
            )

            # Create minimalist floating icon
            self.floating_icon = Button(
                text="🧠",  # Soul AI symbol
                size=(dp(self.size), dp(self.size)),
                size_hint=(None, None),
                pos=(0, 0),
                background_normal='',  # Remove default background
                background_color=(0, 0, 0, 0),  # Transparent
                font_size=dp(24),
                color=(1, 1, 1, 1)  # White text
            )

            # Draw minimalist icon background with elevation
            with self.floating_icon.canvas.before:
                # Shadow for elevation
                Color(0, 0, 0, 0.15)
                self.icon_shadow = Ellipse(
                    pos=(dp(2), dp(-2)),
                    size=(dp(self.size), dp(self.size))
                )

                # Main icon background
                Color(*self._hex_to_rgba(OverlayTheme.PRIMARY, OverlayTheme.ALPHA_NORMAL))
                self.icon_background = Ellipse(
                    pos=(0, 0),
                    size=(dp(self.size), dp(self.size))
                )

            # Bind touch events
            self.floating_icon.bind(on_press=self._on_icon_tap)

            # Add to root
            self.root_view.add_widget(self.floating_icon)

            # Create quick access panel (initially hidden)
            self._create_quick_access_panel()

            logger.info("Minimalist Kivy overlay view created")

        except Exception as e:
            logger.error(f"Failed to create minimalist Kivy view: {e}")
            raise
    
    def _create_quick_access_panel(self) -> None:
        """Create the quick access panel for contextual AI features"""
        try:
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.button import Button
            from kivy.uix.label import Label
            from kivy.graphics import Color, RoundedRectangle
            from kivy.metrics import dp

            # Create panel container (initially hidden)
            self.quick_access_panel = BoxLayout(
                orientation='vertical',
                size=(dp(OverlayTheme.EXPANDED_PANEL_WIDTH), dp(OverlayTheme.EXPANDED_PANEL_HEIGHT)),
                size_hint=(None, None),
                pos=(dp(self.size + 10), 0),  # Position to the right of icon
                spacing=dp(8),
                padding=dp(OverlayTheme.PANEL_PADDING),
                opacity=0  # Initially hidden
            )

            # Draw panel background
            with self.quick_access_panel.canvas.before:
                Color(*self._hex_to_rgba(OverlayTheme.SURFACE, 0.95))
                self.panel_background = RoundedRectangle(
                    pos=self.quick_access_panel.pos,
                    size=self.quick_access_panel.size,
                    radius=[dp(12)]
                )

                # Panel shadow
                Color(0, 0, 0, 0.1)
                self.panel_shadow = RoundedRectangle(
                    pos=(self.quick_access_panel.x + dp(2), self.quick_access_panel.y - dp(2)),
                    size=self.quick_access_panel.size,
                    radius=[dp(12)]
                )

            # Add quick access items
            for item in self.quick_access_items:
                item_button = Button(
                    text=f"{item.icon} {item.title}",
                    size_hint_y=None,
                    height=dp(OverlayTheme.PANEL_ITEM_HEIGHT),
                    background_normal='',
                    background_color=self._hex_to_rgba(OverlayTheme.PRIMARY, 0.1),
                    color=self._hex_to_rgba(OverlayTheme.ON_SURFACE),
                    halign='left'
                )
                item_button.bind(on_press=lambda x, action=item.action: self._on_quick_action_selected(action))
                self.quick_access_panel.add_widget(item_button)

            # Add to root (but hidden)
            self.root_view.add_widget(self.quick_access_panel)

        except Exception as e:
            logger.error(f"Failed to create quick access panel: {e}")

    async def _create_mock_view(self) -> None:
        """Create mock view for testing without UI framework"""
        self.root_view = {"type": "mock_minimalist_overlay", "size": self.size}
        self.floating_icon = {"type": "mock_icon", "text": "🧠"}
        self.quick_access_panel = {"type": "mock_panel", "items": len(self.quick_access_items)}
        logger.info("Mock minimalist overlay view created")
    
    def update_state(self, new_state: OverlayState) -> None:
        """Update minimalist overlay visual state"""
        if self.state == new_state:
            return

        old_state = self.state
        self.state = new_state
        self.last_interaction_time = time.time()

        # Update visual appearance with minimalist approach
        self._update_minimalist_visual_state(old_state, new_state)

        # Handle auto-minimize timing
        if new_state in [OverlayState.EXPANDED, OverlayState.LISTENING, OverlayState.PROCESSING]:
            self._schedule_auto_minimize()

        logger.debug(f"Minimalist overlay state changed: {old_state.value} -> {new_state.value}")
    
    def _update_minimalist_visual_state(self, old_state: OverlayState, new_state: OverlayState) -> None:
        """Update minimalist visual appearance for state change"""
        try:
            if new_state == OverlayState.LISTENING:
                self._start_subtle_pulse_animation()
                self._update_icon_color(OverlayTheme.LISTENING)

            elif new_state == OverlayState.PROCESSING:
                self._start_gentle_glow_animation()
                self._update_icon_color(OverlayTheme.PROCESSING)

            elif new_state == OverlayState.GESTURE_FEEDBACK:
                self._start_gesture_glow_effect()
                # Keep current color, just add subtle glow

            elif new_state == OverlayState.EXPANDED:
                self._show_quick_access_panel()
                self._stop_all_animations()

            elif new_state == OverlayState.MINIMIZED:
                self._hide_quick_access_panel()
                self._stop_all_animations()
                self._update_icon_color(self.current_context_color)

            elif new_state == OverlayState.HIDDEN:
                self._hide_overlay_completely()

        except Exception as e:
            logger.error(f"Failed to update minimalist visual state: {e}")
    
    def _start_subtle_pulse_animation(self) -> None:
        """Start subtle pulsing animation for listening state"""
        if not KIVY_AVAILABLE or not self.floating_icon:
            return

        try:
            from kivy.animation import Animation

            # Stop existing animations
            self._stop_all_animations()

            # Create very subtle pulse animation
            self.pulse_animation = Animation(
                opacity=0.85, duration=1.2
            ) + Animation(
                opacity=1.0, duration=1.2
            )
            self.pulse_animation.repeat = True
            self.pulse_animation.start(self.floating_icon)

        except Exception as e:
            logger.error(f"Failed to start subtle pulse animation: {e}")

    def _start_gentle_glow_animation(self) -> None:
        """Start gentle glow animation for processing state"""
        if not KIVY_AVAILABLE or not self.floating_icon:
            return

        try:
            from kivy.animation import Animation

            # Stop existing animations
            self._stop_all_animations()

            # Create gentle glow effect (very subtle)
            self.glow_animation = Animation(
                opacity=0.9, duration=0.8
            ) + Animation(
                opacity=1.0, duration=0.8
            )
            self.glow_animation.repeat = True
            self.glow_animation.start(self.floating_icon)

        except Exception as e:
            logger.error(f"Failed to start gentle glow animation: {e}")

    def _start_gesture_glow_effect(self) -> None:
        """Start very subtle glow effect during gesture recognition"""
        if not KIVY_AVAILABLE or not self.floating_icon:
            return

        try:
            from kivy.animation import Animation

            # Very brief, subtle glow
            gesture_glow = Animation(
                opacity=0.95, duration=self.config.gesture_feedback_duration
            ) + Animation(
                opacity=1.0, duration=self.config.gesture_feedback_duration
            )
            gesture_glow.start(self.floating_icon)

        except Exception as e:
            logger.error(f"Failed to start gesture glow effect: {e}")
    
    def _show_quick_access_panel(self) -> None:
        """Show the quick access panel with smooth animation"""
        if not KIVY_AVAILABLE or not self.quick_access_panel:
            return

        try:
            from kivy.animation import Animation

            self.is_expanded = True

            # Animate panel appearance
            self.expansion_animation = Animation(
                opacity=1.0,
                duration=self.config.expansion_animation_duration / 1000.0
            )
            self.expansion_animation.start(self.quick_access_panel)

        except Exception as e:
            logger.error(f"Failed to show quick access panel: {e}")

    def _hide_quick_access_panel(self) -> None:
        """Hide the quick access panel with smooth animation"""
        if not KIVY_AVAILABLE or not self.quick_access_panel:
            return

        try:
            from kivy.animation import Animation

            self.is_expanded = False

            # Animate panel disappearance
            hide_animation = Animation(
                opacity=0.0,
                duration=self.config.expansion_animation_duration / 1000.0
            )
            hide_animation.start(self.quick_access_panel)

        except Exception as e:
            logger.error(f"Failed to hide quick access panel: {e}")
    
    def _stop_animations(self) -> None:
        """Stop all running animations"""
        if not KIVY_AVAILABLE:
            return
        
        try:
            if self.current_animation:
                self.current_animation.stop(self.voice_button)
                self.current_animation = None
            
            if self.pulse_animation:
                self.pulse_animation.stop(self.voice_button)
                self.pulse_animation = None
            
            # Reset button properties
            self.voice_button.opacity = 1.0
            self.voice_button.rotation = 0
            
        except Exception as e:
            logger.error(f"Failed to stop animations: {e}")

    def _schedule_auto_minimize(self) -> None:
        """Schedule auto-minimize after configured delay"""
        try:
            # Cancel existing timer
            if self.auto_minimize_timer:
                self.auto_minimize_timer.cancel()

            # Calculate intelligent delay based on interaction type
            delay = self._calculate_auto_minimize_delay()

            # Schedule new timer
            import threading
            self.auto_minimize_timer = threading.Timer(delay, self._auto_minimize)
            self.auto_minimize_timer.start()

        except Exception as e:
            logger.error(f"Failed to schedule auto-minimize: {e}")

    def _calculate_auto_minimize_delay(self) -> float:
        """Calculate intelligent auto-minimize delay based on current state"""
        if self.state == OverlayState.EXPANDED:
            return 4.0  # Longer for panel interactions
        elif self.state == OverlayState.LISTENING:
            return 5.0  # Longer for voice interactions
        elif self.state == OverlayState.PROCESSING:
            return 3.0  # Medium for processing
        else:
            return self.config.auto_minimize_delay  # Default

    def _auto_minimize(self) -> None:
        """Auto-minimize the overlay to icon state"""
        try:
            if self.state != OverlayState.MINIMIZED:
                self.update_state(OverlayState.MINIMIZED)

                if self.on_auto_minimize:
                    self.on_auto_minimize()

        except Exception as e:
            logger.error(f"Failed to auto-minimize: {e}")

    def _show_gesture_indicators(self) -> None:
        """Show 8-direction gesture indicators"""
        self.gesture_ring_visible = True
        
        if KIVY_AVAILABLE and self.root_view:
            try:
                # Draw gesture ring
                with self.root_view.canvas:
                    Color(*self._hex_to_rgba(OverlayTheme.SECONDARY, 0.5))
                    
                    # Draw indicators for each direction
                    center_x = self.size / 2
                    center_y = self.size / 2
                    radius = self.size / 2 - 20
                    
                    for direction, indicator in self.gesture_indicators.items():
                        angle_rad = math.radians(indicator.angle)
                        x = center_x + radius * math.cos(angle_rad)
                        y = center_y + radius * math.sin(angle_rad)
                        
                        # Draw indicator circle
                        Ellipse(
                            pos=(x - OverlayTheme.INDICATOR_SIZE/2, y - OverlayTheme.INDICATOR_SIZE/2),
                            size=(OverlayTheme.INDICATOR_SIZE, OverlayTheme.INDICATOR_SIZE)
                        )
                
            except Exception as e:
                logger.error(f"Failed to show gesture indicators: {e}")
    
    def _hide_gesture_indicators(self) -> None:
        """Hide gesture indicators"""
        self.gesture_ring_visible = False
        
        if KIVY_AVAILABLE and self.root_view:
            try:
                # Clear gesture indicators from canvas
                self.root_view.canvas.clear()
                
                # Redraw base overlay
                with self.root_view.canvas.before:
                    Color(*self._hex_to_rgba(self.current_context_color, OverlayTheme.ALPHA_NORMAL))
                    self.overlay_circle = Ellipse(
                        pos=(0, 0),
                        size=(self.size, self.size)
                    )
                
            except Exception as e:
                logger.error(f"Failed to hide gesture indicators: {e}")
    
    def highlight_gesture_direction(self, direction: str) -> None:
        """Highlight specific gesture direction"""
        self.gesture_highlight_direction = direction
        
        if self.on_gesture_visual_feedback:
            self.on_gesture_visual_feedback(direction)
        
        logger.debug(f"Highlighted gesture direction: {direction}")
    
    def update_context_appearance(self, context_type: str, color: str, icon: str) -> None:
        """Update overlay appearance based on app context"""
        self.current_context_color = color
        self.current_context_icon = icon
        
        # Update voice button icon
        if self.voice_button:
            if ANDROID_AVAILABLE:
                self.voice_button.setText(icon)
            elif KIVY_AVAILABLE:
                self.voice_button.text = icon
        
        # Update overlay color if not in special state
        if self.state in [OverlayState.MINIMIZED, OverlayState.ACTIVE]:
            self._update_overlay_color(color)
        
        logger.debug(f"Updated context appearance: {context_type} ({icon})")
    
    def _update_overlay_color(self, color: str) -> None:
        """Update overlay background color"""
        if KIVY_AVAILABLE and hasattr(self, 'overlay_circle'):
            try:
                with self.root_view.canvas.before:
                    Color(*self._hex_to_rgba(color, OverlayTheme.ALPHA_NORMAL))
                    self.overlay_circle = Ellipse(
                        pos=(0, 0),
                        size=(self.size, self.size)
                    )
            except Exception as e:
                logger.error(f"Failed to update overlay color: {e}")
    
    def _set_overlay_alpha(self, alpha: float) -> None:
        """Set overlay transparency"""
        if KIVY_AVAILABLE and self.root_view:
            self.root_view.opacity = alpha
    
    def _on_icon_tap(self, button) -> None:
        """Handle floating icon tap - expand to show quick access panel"""
        logger.debug("Floating icon tapped")

        if self.state == OverlayState.MINIMIZED:
            # Expand to show quick access panel
            self.update_state(OverlayState.EXPANDED)
        elif self.state == OverlayState.EXPANDED:
            # Collapse back to minimized
            self.update_state(OverlayState.MINIMIZED)

        if self.on_icon_tap:
            self.on_icon_tap()

    def _on_quick_action_selected(self, action: str) -> None:
        """Handle quick action selection from panel"""
        logger.debug(f"Quick action selected: {action}")

        # Trigger callback
        if self.on_quick_action_selected:
            self.on_quick_action_selected(action)

        # Auto-minimize after action
        self.update_state(OverlayState.MINIMIZED)

    def on_gesture_feedback(self, direction: str) -> None:
        """Handle gesture feedback - show subtle visual response"""
        logger.debug(f"Gesture feedback for direction: {direction}")

        # Show subtle gesture feedback
        self.update_state(OverlayState.GESTURE_FEEDBACK)

        # Trigger callback
        if self.on_gesture_detected:
            self.on_gesture_detected(direction)

        # Return to minimized state after brief feedback
        import threading
        threading.Timer(self.config.gesture_feedback_duration,
                       lambda: self.update_state(OverlayState.MINIMIZED)).start()
    
    def _update_icon_color(self, color: str) -> None:
        """Update the floating icon color"""
        if not KIVY_AVAILABLE or not self.floating_icon:
            return

        try:
            from kivy.graphics import Color

            # Update icon background color
            with self.floating_icon.canvas.before:
                Color(*self._hex_to_rgba(color, OverlayTheme.ALPHA_NORMAL))

        except Exception as e:
            logger.error(f"Failed to update icon color: {e}")

    def _hide_overlay_completely(self) -> None:
        """Hide the overlay completely"""
        if KIVY_AVAILABLE and self.root_view:
            self.root_view.opacity = 0

    def update_quick_access_items(self, items: List[QuickAccessItem]) -> None:
        """Update the quick access panel items based on context"""
        self.quick_access_items = items

        # Recreate panel if it exists
        if self.quick_access_panel:
            self._create_quick_access_panel()

    def _hex_to_rgba(self, hex_color: str, alpha: float = 1.0) -> Tuple[float, float, float, float]:
        """Convert hex color to RGBA tuple"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b, alpha)
    
    def _color_to_int(self, hex_color: str) -> int:
        """Convert hex color to Android color int"""
        hex_color = hex_color.lstrip('#')
        return int(f"FF{hex_color}", 16)  # Add alpha channel
    
    def get_view(self):
        """Get the root view for adding to window manager"""
        return self.root_view
    
    def cleanup(self) -> None:
        """Clean up minimalist overlay resources"""
        try:
            # Stop all animations
            self._stop_all_animations()

            # Cancel auto-minimize timer
            if self.auto_minimize_timer:
                self.auto_minimize_timer.cancel()
                self.auto_minimize_timer = None

            # Clean up UI components
            if self.root_view and ANDROID_AVAILABLE:
                # Remove from parent if attached
                parent = self.root_view.getParent()
                if parent:
                    parent.removeView(self.root_view)

            logger.info("Minimalist overlay view cleaned up")

        except Exception as e:
            logger.error(f"Failed to cleanup minimalist overlay view: {e}")


# Compatibility alias for existing code
OverlayView = MinimalistOverlayView
