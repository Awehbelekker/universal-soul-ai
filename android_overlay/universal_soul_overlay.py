"""
Universal Soul AI Android Overlay Application
============================================

Main application that integrates all overlay components:
- Overlay service with voice recognition
- 360° gesture navigation system
- Contextual intelligence engine
- Privacy-first architecture

This creates the complete overlay experience for Android testing.
"""

import asyncio
import time
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging

# Core overlay components
from core.overlay_service import AndroidOverlayService, OverlayConfig, OverlayState
from core.gesture_handler import GestureHandler, GestureEvent, GestureDirection
from core.context_analyzer import ContextAnalyzer, AppContext, ContextualFeatures
from ui.overlay_view import MinimalistOverlayView, OverlayTheme, OverlayState as UIOverlayState, QuickAccessItem

# Universal Soul AI integration
from thinkmesh_core.voice import VoiceInterface, VoiceConfig
from thinkmesh_core.automation import CoAct1AutomationEngine
from thinkmesh_core.interfaces import UserContext

logger = logging.getLogger(__name__)


@dataclass
class OverlayStats:
    """Statistics for overlay usage"""
    session_start_time: float
    voice_commands_processed: int = 0
    gestures_recognized: int = 0
    context_switches: int = 0
    automation_tasks_executed: int = 0
    privacy_mode_active: bool = True


class UniversalSoulOverlay:
    """
    Main Universal Soul AI overlay application for Android
    
    Integrates voice recognition, gesture navigation, contextual intelligence,
    and automation capabilities in a persistent floating interface.
    """
    
    def __init__(self, config: Optional[OverlayConfig] = None):
        self.config = config or OverlayConfig()
        self.is_running = False
        self.is_initialized = False
        
        # Core components
        self.overlay_service: Optional[AndroidOverlayService] = None
        self.gesture_handler: Optional[GestureHandler] = None
        self.context_analyzer: Optional[ContextAnalyzer] = None
        self.overlay_view: Optional[MinimalistOverlayView] = None
        
        # Integration components
        self.voice_interface: Optional[VoiceInterface] = None
        self.automation_engine: Optional[CoAct1AutomationEngine] = None
        
        # State tracking
        self.current_state = OverlayState.HIDDEN
        self.current_context: Optional[AppContext] = None
        self.current_features: Optional[ContextualFeatures] = None
        self.stats = OverlayStats(session_start_time=time.time())
        
        # User context for automation
        self.user_context = UserContext(
            user_id="overlay_user",
            preferences={"privacy_mode": True, "local_processing": True},
            device_info={"platform": "android", "overlay_enabled": True}
        )
    
    async def initialize(self) -> bool:
        """Initialize the complete overlay system"""
        try:
            logger.info("🚀 Initializing Universal Soul AI Overlay...")
            
            # Initialize core overlay service
            self.overlay_service = AndroidOverlayService(self.config)
            if not await self.overlay_service.initialize():
                raise Exception("Failed to initialize overlay service")
            
            # Initialize gesture handler
            self.gesture_handler = GestureHandler(
                sensitivity=self.config.gesture_sensitivity,
                timeout=self.config.gesture_timeout,
                haptic_enabled=self.config.haptic_feedback
            )
            if not await self.gesture_handler.initialize():
                raise Exception("Failed to initialize gesture handler")
            
            # Initialize context analyzer
            self.context_analyzer = ContextAnalyzer(
                privacy_mode=self.config.local_processing_only,
                update_interval=1.0
            )
            if not await self.context_analyzer.initialize():
                raise Exception("Failed to initialize context analyzer")
            
            # Initialize minimalist overlay UI
            from ui.overlay_view import MinimalistOverlayConfig
            ui_config = MinimalistOverlayConfig(
                icon_size=self.config.overlay_size,
                auto_minimize_delay=2.5,
                gesture_feedback_duration=0.3,
                enable_subtle_animations=True,
                respect_system_theme=True
            )
            self.overlay_view = MinimalistOverlayView(config=ui_config)
            if not await self.overlay_view.initialize():
                raise Exception("Failed to initialize minimalist overlay view")
            
            # Initialize voice interface
            await self._initialize_voice_interface()
            
            # Initialize automation engine
            await self._initialize_automation_engine()
            
            # Set up component callbacks
            self._setup_callbacks()
            
            self.is_initialized = True
            logger.info("✅ Universal Soul AI Overlay initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize overlay: {e}")
            return False
    
    async def _initialize_voice_interface(self) -> None:
        """Initialize voice recognition system"""
        voice_config = VoiceConfig(
            stt_provider="deepgram",
            tts_provider="elevenlabs",
            vad_provider="silero",
            sample_rate=16000,
            low_latency_mode=True,
            noise_suppression=True,
            echo_cancellation=True
        )
        
        self.voice_interface = VoiceInterface(voice_config)
        await self.voice_interface.initialize()
        logger.info("🎙️ Voice interface initialized")
    
    async def _initialize_automation_engine(self) -> None:
        """Initialize CoAct-1 automation engine"""
        self.automation_engine = CoAct1AutomationEngine()
        await self.automation_engine.initialize()
        logger.info("🤖 Automation engine initialized")
    
    def _setup_callbacks(self) -> None:
        """Set up callbacks between components"""
        
        # Gesture handler callbacks
        if self.gesture_handler:
            self.gesture_handler.on_gesture_detected = self._on_gesture_detected
            self.gesture_handler.on_gesture_started = self._on_gesture_started
            self.gesture_handler.on_gesture_ended = self._on_gesture_ended
        
        # Context analyzer callbacks
        if self.context_analyzer:
            self.context_analyzer.on_context_changed = self._on_context_changed
            self.context_analyzer.on_app_switched = self._on_app_switched
            self.context_analyzer.on_features_updated = self._on_features_updated
        
        # Minimalist overlay view callbacks
        if self.overlay_view:
            self.overlay_view.on_icon_tap = self._on_icon_tap
            self.overlay_view.on_quick_action_selected = self._on_quick_action_selected
            self.overlay_view.on_gesture_detected = self._on_gesture_feedback
            self.overlay_view.on_auto_minimize = self._on_auto_minimize
        
        logger.info("🔗 Component callbacks configured")
    
    async def start(self) -> bool:
        """Start the overlay system"""
        try:
            if not self.is_initialized:
                logger.error("Overlay not initialized - call initialize() first")
                return False
            
            logger.info("🎯 Starting Universal Soul AI Overlay...")
            
            # Show overlay
            if self.overlay_service:
                await self.overlay_service.show_overlay()
            
            # Update state
            self.current_state = OverlayState.MINIMIZED
            if self.overlay_view:
                self.overlay_view.update_state(self.current_state)
            
            # Start continuous voice monitoring if enabled
            if self.config.continuous_listening:
                await self._start_voice_monitoring()
            
            self.is_running = True
            logger.info("✅ Universal Soul AI Overlay is now active!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start overlay: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop the overlay system"""
        try:
            logger.info("🛑 Stopping Universal Soul AI Overlay...")
            
            self.is_running = False
            
            # Hide overlay
            if self.overlay_service:
                await self.overlay_service.hide_overlay()
            
            # Stop voice monitoring
            await self._stop_voice_monitoring()
            
            # Stop context monitoring
            if self.context_analyzer:
                self.context_analyzer.stop_monitoring()
            
            # Update state
            self.current_state = OverlayState.HIDDEN
            
            logger.info("✅ Universal Soul AI Overlay stopped")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop overlay: {e}")
    
    async def _start_voice_monitoring(self) -> None:
        """Start continuous voice monitoring"""
        if not self.voice_interface:
            return
        
        try:
            # Start voice activity detection
            await self.voice_interface.start_listening()
            logger.info("🎙️ Voice monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start voice monitoring: {e}")
    
    async def _stop_voice_monitoring(self) -> None:
        """Stop voice monitoring"""
        if not self.voice_interface:
            return
        
        try:
            await self.voice_interface.stop_listening()
            logger.info("🎙️ Voice monitoring stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop voice monitoring: {e}")
    
    # Event handlers
    
    async def _on_gesture_detected(self, gesture_event: GestureEvent) -> None:
        """Handle detected gesture"""
        try:
            logger.info(f"👆 Gesture detected: {gesture_event.gesture_type.value} {gesture_event.direction.value if gesture_event.direction else 'none'}")
            
            self.stats.gestures_recognized += 1
            
            # Get action for gesture in current context
            if gesture_event.direction and self.context_analyzer:
                action = self.context_analyzer.get_gesture_mapping(gesture_event.direction.value)
                
                if action:
                    await self._execute_gesture_action(action, gesture_event)
                else:
                    logger.warning(f"No action mapped for gesture: {gesture_event.direction.value}")
            
            # Update overlay state with gesture feedback
            if self.overlay_view:
                self.overlay_view.on_gesture_feedback(gesture_event.direction.value)

                # Auto-minimize after gesture feedback
                asyncio.create_task(self._auto_minimize_after_delay(1.5))
            
        except Exception as e:
            logger.error(f"Failed to handle gesture: {e}")
    
    async def _on_gesture_started(self, start_point: tuple) -> None:
        """Handle gesture start - minimalist approach"""
        logger.debug(f"👆 Gesture started at {start_point}")

        # No visible indicators in minimalist design - gestures are invisible
    
    async def _on_gesture_ended(self, gesture_event: GestureEvent) -> None:
        """Handle gesture end"""
        logger.debug(f"👆 Gesture ended: {gesture_event.confidence:.2f} confidence")
        
        # Hide gesture indicators
        if self.overlay_view:
            self.overlay_view.update_state(OverlayState.ACTIVE)
    
    async def _on_context_changed(self, context: AppContext) -> None:
        """Handle app context change"""
        logger.info(f"📱 Context changed: {context.app_name} ({context.category.value})")
        
        self.current_context = context
        self.stats.context_switches += 1
        
        # Update overlay appearance based on context
        if self.overlay_view:
            context_colors = {
                "communication": OverlayTheme.LISTENING,
                "productivity": OverlayTheme.PRIMARY,
                "social": OverlayTheme.ACCENT,
                "browser": OverlayTheme.SECONDARY,
                "entertainment": OverlayTheme.PROCESSING
            }
            
            context_icons = {
                "communication": "💬",
                "productivity": "📝",
                "social": "👥",
                "browser": "🌐",
                "entertainment": "🎵"
            }
            
            color = context_colors.get(context.category.value, OverlayTheme.PRIMARY)
            icon = context_icons.get(context.category.value, "🧠")
            
            self.overlay_view.update_context_appearance(context.category.value, color, icon)
    
    async def _on_app_switched(self, old_app: str, new_app: str) -> None:
        """Handle app switch"""
        logger.debug(f"📱 App switched: {old_app} -> {new_app}")
    
    async def _on_features_updated(self, features: ContextualFeatures) -> None:
        """Handle contextual features update"""
        self.current_features = features
        logger.debug(f"⚡ Features updated: {len(features.primary_actions)} primary actions")
    
    async def _on_voice_button_pressed(self) -> None:
        """Handle voice button press"""
        logger.info("🎙️ Voice button pressed")
        
        try:
            # Update state to listening
            if self.overlay_view:
                self.overlay_view.update_state(OverlayState.LISTENING)
            
            # Start voice recognition
            if self.voice_interface:
                result = await self.voice_interface.process_voice_input(self.user_context)
                
                if result and result.text:
                    await self._process_voice_command(result.text)
                    self.stats.voice_commands_processed += 1
            
            # Return to active state
            if self.overlay_view:
                self.overlay_view.update_state(OverlayState.ACTIVE)
                asyncio.create_task(self._auto_minimize_after_delay(3.0))
            
        except Exception as e:
            logger.error(f"Failed to process voice input: {e}")
            
            # Return to minimized state on error
            if self.overlay_view:
                self.overlay_view.update_state(OverlayState.MINIMIZED)
    
    async def _on_overlay_moved(self, x: float, y: float) -> None:
        """Handle overlay position change"""
        logger.debug(f"📍 Overlay moved to ({x}, {y})")
    
    async def _on_gesture_visual_feedback(self, direction: str) -> None:
        """Handle gesture visual feedback"""
        logger.debug(f"👆 Visual feedback for direction: {direction}")
    
    # Action execution
    
    async def _execute_gesture_action(self, action: str, gesture_event: GestureEvent) -> None:
        """Execute action triggered by gesture"""
        try:
            logger.info(f"⚡ Executing gesture action: {action}")
            
            # Update overlay state
            if self.overlay_view:
                self.overlay_view.update_state(OverlayState.PROCESSING)
            
            # Execute action based on type
            if action == "voice_transcription":
                await self._start_voice_transcription()
            elif action == "quick_reply":
                await self._show_quick_reply_interface()
            elif action == "create_task":
                await self._create_task_from_context()
            elif action == "save_content":
                await self._save_current_content()
            elif action == "translate_text":
                await self._translate_current_text()
            else:
                # Generic automation action
                await self._execute_automation_action(action)
            
            self.stats.automation_tasks_executed += 1
            
        except Exception as e:
            logger.error(f"Failed to execute gesture action: {e}")
        finally:
            # Return to active state
            if self.overlay_view:
                self.overlay_view.update_state(OverlayState.ACTIVE)
    
    async def _process_voice_command(self, command: str) -> None:
        """Process voice command"""
        logger.info(f"🎙️ Processing voice command: {command}")
        
        # Use automation engine to process command
        if self.automation_engine:
            result = await self.automation_engine.execute_voice_command(
                command, self.user_context, self.current_context
            )
            
            if result:
                logger.info(f"✅ Voice command executed successfully")
            else:
                logger.warning(f"❌ Voice command execution failed")
    
    async def _auto_minimize_after_delay(self, delay: float) -> None:
        """Auto-minimize overlay after delay"""
        await asyncio.sleep(delay)
        
        if self.overlay_view and self.current_state != OverlayState.HIDDEN:
            self.overlay_view.update_state(OverlayState.MINIMIZED)
            self.current_state = OverlayState.MINIMIZED
    
    # Minimalist overlay event handlers
    async def _on_icon_tap(self) -> None:
        """Handle floating icon tap - show quick access panel"""
        logger.debug("🎯 Floating icon tapped")

        # Update quick access items based on current context
        await self._update_contextual_quick_actions()

        # Icon tap is handled by the overlay view itself (expand/collapse)
        self.stats.total_interactions += 1

    async def _on_quick_action_selected(self, action: str) -> None:
        """Handle quick action selection from panel"""
        logger.debug(f"⚡ Quick action selected: {action}")

        self.stats.total_interactions += 1

        # Execute the selected action
        if action == "voice_assistant":
            await self._start_voice_assistant()
        elif action == "quick_note":
            await self._create_quick_note()
        elif action == "smart_actions":
            await self._show_smart_actions()
        elif action == "context_help":
            await self._show_context_help()
        else:
            logger.warning(f"Unknown quick action: {action}")

    async def _on_gesture_feedback(self, direction: str) -> None:
        """Handle gesture feedback from overlay view"""
        logger.debug(f"👆 Gesture feedback: {direction}")
        # This is called when the overlay view provides gesture feedback
        pass

    async def _on_auto_minimize(self) -> None:
        """Handle auto-minimize event"""
        logger.debug("⏰ Auto-minimize triggered")
        self.stats.total_interactions += 1

    async def _update_contextual_quick_actions(self) -> None:
        """Update quick access items based on current context"""
        if not self.current_context or not self.overlay_view:
            return

        # Create contextual quick access items
        context_items = []

        if self.current_context.category.value == "communication":
            context_items = [
                QuickAccessItem("Quick Reply", "💬", "quick_reply"),
                QuickAccessItem("Voice Message", "🎙️", "voice_message"),
                QuickAccessItem("Translate", "🌐", "translate"),
                QuickAccessItem("Smart Actions", "⚡", "smart_actions")
            ]
        elif self.current_context.category.value == "productivity":
            context_items = [
                QuickAccessItem("Quick Note", "📝", "quick_note"),
                QuickAccessItem("Create Task", "✅", "create_task"),
                QuickAccessItem("Voice Assistant", "🎙️", "voice_assistant"),
                QuickAccessItem("Context Help", "🧠", "context_help")
            ]
        else:
            # Default items
            context_items = [
                QuickAccessItem("Voice Assistant", "🎙️", "voice_assistant"),
                QuickAccessItem("Quick Note", "📝", "quick_note"),
                QuickAccessItem("Smart Actions", "⚡", "smart_actions"),
                QuickAccessItem("Context Help", "🧠", "context_help")
            ]

        # Update overlay view with new items
        self.overlay_view.update_quick_access_items(context_items)

    # Action method implementations
    async def _start_voice_assistant(self):
        """Start voice assistant"""
        if self.voice_interface:
            await self.voice_interface.start_listening()

    async def _create_quick_note(self):
        """Create a quick note"""
        # Implementation for quick note creation
        pass

    async def _show_smart_actions(self):
        """Show smart actions based on context"""
        # Implementation for smart actions
        pass

    async def _show_context_help(self):
        """Show context-specific help"""
        # Implementation for context help
        pass

    # Legacy placeholder methods (to be removed)
    async def _start_voice_transcription(self): pass
    async def _show_quick_reply_interface(self): pass
    async def _create_task_from_context(self): pass
    async def _save_current_content(self): pass
    async def _translate_current_text(self): pass
    async def _execute_automation_action(self, action: str): pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overlay usage statistics"""
        return asdict(self.stats)
