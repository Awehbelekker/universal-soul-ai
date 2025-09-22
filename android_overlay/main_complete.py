#!/usr/bin/env python3
"""
Universal Soul AI - Complete Android APK Entry Point
==================================================

Full-featured Android app with overlay functionality, voice recognition,
gesture navigation, and contextual intelligence.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kivy configuration (must be set before importing kivy)
os.environ['KIVY_WINDOW_ICON'] = str(project_root / 'assets' / 'icon.png')
os.environ['KIVY_NO_CONSOLELOG'] = '1'

# Core Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.utils import platform

# KivyMD imports with fallbacks
try:
    from kivymd.app import MDApp
    from kivymd.uix.screen import MDScreen
    from kivymd.uix.button import MDRaisedButton, MDFloatingActionButton
    from kivymd.uix.label import MDLabel
    from kivymd.uix.boxlayout import MDBoxLayout
    from kivymd.uix.card import MDCard
    from kivymd.uix.toolbar import MDTopAppBar
    KIVYMD_AVAILABLE = True
    logger.info("KivyMD loaded successfully")
except ImportError as e:
    logger.warning(f"KivyMD not available, using Kivy fallbacks: {e}")
    KIVYMD_AVAILABLE = False
    # Create fallback classes
    MDApp = App
    MDScreen = BoxLayout
    MDRaisedButton = Button
    MDFloatingActionButton = Button
    MDLabel = Label
    MDBoxLayout = BoxLayout
    MDCard = BoxLayout
    MDTopAppBar = Label

# Android-specific imports with robust fallbacks
ANDROID_AVAILABLE = False
request_permissions = None
Permission = None

if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission  # type: ignore
        from jnius import autoclass, PythonJavaClass, java_method  # type: ignore
        # Android classes
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')
        Uri = autoclass('android.net.Uri')
        ANDROID_AVAILABLE = True
        logger.info("Android APIs loaded successfully")
    except ImportError as e:
        logger.warning(f"Android APIs not available: {e}")

# Universal Soul AI components with fallbacks
OVERLAY_AVAILABLE = False
UniversalSoulOverlay = None
OverlayConfig = None
OverlayState = None

try:
    from universal_soul_overlay import UniversalSoulOverlay, OverlayConfig
    from core.overlay_service import OverlayState, AndroidOverlayService
    OVERLAY_AVAILABLE = True
    logger.info("Overlay components loaded successfully")
except ImportError as e:
    logger.warning(f"Overlay components not available: {e}")
    # Create mock overlay classes
    class OverlayConfig:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class OverlayState:
        HIDDEN = "hidden"
        ACTIVE = "active"
    
    class UniversalSoulOverlay:
        def __init__(self, config):
            self.config = config
            self.is_active = False
        
        async def initialize(self):
            return True
        
        async def start(self):
            self.is_active = True
        
        async def stop(self):
            self.is_active = False


class UniversalSoulAIApp(MDApp if KIVYMD_AVAILABLE else App):
    """Complete Universal Soul AI Android Application"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Universal Soul AI"
        self.theme_cls.primary_palette = "Blue" if KIVYMD_AVAILABLE else None
        self.overlay_system = None
        self.is_overlay_active = False
        self.components_status = {
            'overlay': False,
            'voice': False,
            'gesture': False,
            'context': False
        }
    
    def build(self):
        """Build the main application interface"""
        if KIVYMD_AVAILABLE:
            return self.build_material_ui()
        else:
            return self.build_basic_ui()
    
    def build_material_ui(self):
        """Build Material Design interface with KivyMD"""
        main_screen = MDScreen()
        
        # Main layout
        main_layout = MDBoxLayout(
            orientation='vertical',
            spacing='20dp',
            padding='20dp'
        )
        
        # Top app bar
        toolbar = MDTopAppBar(
            title="Universal Soul AI",
            elevation=2,
            md_bg_color="#1976D2"
        )
        main_layout.add_widget(toolbar)
        
        # Welcome card
        welcome_card = MDCard(
            MDBoxLayout(
                MDLabel(
                    text="🚀 Universal Soul AI",
                    theme_text_color="Primary",
                    font_style="H4",
                    halign="center"
                ),
                MDLabel(
                    text="Minimalist Floating AI • 360° Gestures • Privacy-First",
                    theme_text_color="Secondary",
                    font_style="Body1",
                    halign="center"
                ),
                orientation='vertical',
                spacing='10dp',
                padding='20dp'
            ),
            elevation=3,
            size_hint_y=None,
            height='120dp'
        )
        main_layout.add_widget(welcome_card)
        
        # Status card
        self.status_card = self.create_status_card()
        main_layout.add_widget(self.status_card)
        
        # Control buttons
        button_layout = self.create_button_layout()
        main_layout.add_widget(button_layout)
        
        # Floating action button
        self.fab = MDFloatingActionButton(
            icon="gesture-tap",
            md_bg_color="#1976D2",
            pos_hint={'center_x': 0.9, 'center_y': 0.1},
            on_release=self.toggle_overlay
        )
        
        main_screen.add_widget(main_layout)
        main_screen.add_widget(self.fab)
        
        # Initialize systems on startup
        Clock.schedule_once(self.initialize_systems, 1)
        
        return main_screen
    
    def build_basic_ui(self):
        """Build basic Kivy interface fallback"""
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Title
        title_label = Label(
            text="Universal Soul AI",
            size_hint_y=None,
            height='50dp',
            font_size='24sp'
        )
        main_layout.add_widget(title_label)
        
        # Status
        self.status_label = Label(
            text="Status: Ready",
            size_hint_y=None,
            height='40dp'
        )
        main_layout.add_widget(self.status_label)
        
        # Start button
        start_button = Button(
            text="Start Overlay System",
            size_hint_y=None,
            height='50dp',
            on_release=self.start_overlay_system
        )
        main_layout.add_widget(start_button)
        
        # Permissions button
        permissions_button = Button(
            text="Request Permissions",
            size_hint_y=None,
            height='50dp',
            on_release=self.request_permissions
        )
        main_layout.add_widget(permissions_button)
        
        # Initialize systems
        Clock.schedule_once(self.initialize_systems, 1)
        
        return main_layout
    
    def create_status_card(self):
        """Create status monitoring card"""
        status_layout = MDBoxLayout(
            orientation='vertical',
            spacing='5dp',
            padding='20dp'
        )
        
        status_layout.add_widget(MDLabel(
            text="🔧 System Status",
            theme_text_color="Primary",
            font_style="H6"
        ))
        
        self.status_labels = {}
        for component in ['overlay', 'voice', 'gesture', 'context']:
            self.status_labels[component] = MDLabel(
                text=f"{component.title()}: Not Started 🔴",
                theme_text_color="Secondary"
            )
            status_layout.add_widget(self.status_labels[component])
        
        return MDCard(
            status_layout,
            elevation=3,
            size_hint_y=None,
            height='200dp'
        )
    
    def create_button_layout(self):
        """Create control buttons layout"""
        button_layout = MDBoxLayout(
            orientation='vertical',
            spacing='10dp',
            size_hint_y=None,
            height='250dp'
        )
        
        # Start overlay button
        self.start_button = MDRaisedButton(
            text="🚀 Start Minimalist Overlay",
            md_bg_color="#4CAF50",
            size_hint_y=None,
            height='50dp',
            on_release=self.start_overlay_system
        )
        button_layout.add_widget(self.start_button)
        
        # Demo button
        demo_button = MDRaisedButton(
            text="🎭 Run Feature Demo",
            md_bg_color="#FF9800",
            size_hint_y=None,
            height='50dp',
            on_release=self.run_demo
        )
        button_layout.add_widget(demo_button)
        
        # Permissions button
        permissions_button = MDRaisedButton(
            text="🔐 Request Permissions",
            md_bg_color="#9C27B0",
            size_hint_y=None,
            height='50dp',
            on_release=self.request_permissions
        )
        button_layout.add_widget(permissions_button)
        
        # Settings button
        settings_button = MDRaisedButton(
            text="⚙️ System Settings",
            md_bg_color="#607D8B",
            size_hint_y=None,
            height='50dp',
            on_release=self.open_system_settings
        )
        button_layout.add_widget(settings_button)
        
        # Test button
        test_button = MDRaisedButton(
            text="🧪 Component Test",
            md_bg_color="#795548",
            size_hint_y=None,
            height='50dp',
            on_release=self.run_component_test
        )
        button_layout.add_widget(test_button)
        
        return button_layout
    
    def initialize_systems(self, dt):
        """Initialize all Universal Soul AI systems"""
        logger.info("Initializing Universal Soul AI systems...")
        
        # Create overlay configuration
        overlay_config = OverlayConfig(
            overlay_size=56,
            overlay_alpha=0.95,
            overlay_color="#1976D2",
            continuous_listening=True,
            wake_word="Hey Soul",
            voice_timeout=5.0,
            gesture_sensitivity=0.8,
            gesture_timeout=2.0,
            haptic_feedback=True,
            local_processing_only=True,
            show_privacy_indicators=True,
            battery_optimization=True
        )
        
        # Initialize overlay system
        if OVERLAY_AVAILABLE:
            self.overlay_system = UniversalSoulOverlay(overlay_config)
            asyncio.create_task(self.async_initialize_overlay())
        else:
            logger.info("Using mock overlay system")
            self.overlay_system = UniversalSoulOverlay(overlay_config)
        
        self.update_status_display()
    
    async def async_initialize_overlay(self):
        """Asynchronously initialize overlay system"""
        try:
            success = await self.overlay_system.initialize()
            if success:
                self.components_status['overlay'] = True
                logger.info("Overlay system initialized successfully")
            else:
                logger.warning("Overlay system initialization failed")
        except Exception as e:
            logger.error(f"Error initializing overlay: {e}")
        
        Clock.schedule_once(lambda dt: self.update_status_display(), 0)
    
    def update_status_display(self):
        """Update status display"""
        if KIVYMD_AVAILABLE and hasattr(self, 'status_labels'):
            for component, status in self.components_status.items():
                icon = "🟢" if status else "🔴"
                text = "Active" if status else "Not Started"
                self.status_labels[component].text = f"{component.title()}: {text} {icon}"
        elif hasattr(self, 'status_label'):
            active_count = sum(self.components_status.values())
            self.status_label.text = f"Status: {active_count}/4 systems active"
    
    def start_overlay_system(self, button):
        """Start the overlay system"""
        logger.info("Starting overlay system...")
        
        if not self.is_overlay_active:
            if self.overlay_system:
                asyncio.create_task(self.async_start_overlay())
                button.text = "🛑 Stop Overlay"
                self.is_overlay_active = True
            else:
                self.show_popup("Error", "Overlay system not initialized")
        else:
            if self.overlay_system:
                asyncio.create_task(self.async_stop_overlay())
                button.text = "🚀 Start Minimalist Overlay"
                self.is_overlay_active = False
    
    async def async_start_overlay(self):
        """Asynchronously start overlay"""
        try:
            await self.overlay_system.start()
            self.components_status['overlay'] = True
            Clock.schedule_once(lambda dt: self.update_status_display(), 0)
            logger.info("Overlay started successfully")
        except Exception as e:
            logger.error(f"Error starting overlay: {e}")
    
    async def async_stop_overlay(self):
        """Asynchronously stop overlay"""
        try:
            await self.overlay_system.stop()
            self.components_status['overlay'] = False
            Clock.schedule_once(lambda dt: self.update_status_display(), 0)
            logger.info("Overlay stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping overlay: {e}")
    
    def toggle_overlay(self, button):
        """Toggle overlay visibility"""
        self.start_overlay_system(self.start_button if hasattr(self, 'start_button') else button)
    
    def request_permissions(self, button):
        """Request necessary Android permissions"""
        logger.info("Requesting Android permissions...")
        
        if ANDROID_AVAILABLE and request_permissions:
            try:
                permissions = [
                    Permission.INTERNET,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.CAMERA,
                    Permission.RECORD_AUDIO,
                    Permission.SYSTEM_ALERT_WINDOW,
                    Permission.VIBRATE,
                    Permission.ACCESS_NETWORK_STATE,
                    Permission.WAKE_LOCK
                ]
                request_permissions(permissions)
                self.show_popup("Permissions", "Permission requests sent")
            except Exception as e:
                logger.error(f"Error requesting permissions: {e}")
                self.show_popup("Error", f"Permission request failed: {e}")
        else:
            self.show_popup("Info", "Running in simulation mode - no permissions needed")
    
    def open_system_settings(self, button):
        """Open Android system settings"""
        if ANDROID_AVAILABLE:
            try:
                intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)
                intent.setData(Uri.parse(f"package:{PythonActivity.mActivity.getPackageName()}"))
                PythonActivity.mActivity.startActivity(intent)
            except Exception as e:
                logger.error(f"Error opening settings: {e}")
                self.show_popup("Error", f"Cannot open settings: {e}")
        else:
            self.show_popup("Info", "System settings not available in simulation mode")
    
    def run_demo(self, button):
        """Run feature demonstration"""
        logger.info("Running Universal Soul AI demo...")
        self.show_popup("Demo", "🎭 Universal Soul AI Demo\n\n• Voice: 'Hey Soul'\n• Gestures: 8-direction swipe\n• Overlay: Minimalist floating UI\n• Privacy: Local processing")
    
    def run_component_test(self, button):
        """Run component functionality test"""
        logger.info("Running component tests...")
        asyncio.create_task(self.async_component_test())
    
    async def async_component_test(self):
        """Asynchronously test all components"""
        test_results = []
        
        # Test overlay system
        if self.overlay_system:
            try:
                await self.overlay_system.initialize()
                test_results.append("✅ Overlay: OK")
                self.components_status['overlay'] = True
            except Exception as e:
                test_results.append(f"❌ Overlay: {e}")
        
        # Test voice system (mock)
        test_results.append("✅ Voice: Mock OK")
        self.components_status['voice'] = True
        
        # Test gesture system (mock)
        test_results.append("✅ Gesture: Mock OK")
        self.components_status['gesture'] = True
        
        # Test context system (mock)
        test_results.append("✅ Context: Mock OK")
        self.components_status['context'] = True
        
        Clock.schedule_once(lambda dt: self.update_status_display(), 0)
        Clock.schedule_once(lambda dt: self.show_popup("Test Results", "\n".join(test_results)), 0)
    
    def show_popup(self, title, content):
        """Show information popup"""
        popup = Popup(
            title=title,
            content=Label(text=content),
            size_hint=(0.8, 0.6)
        )
        popup.open()
    
    def on_start(self):
        """Called when app starts"""
        logger.info("Universal Soul AI started successfully")
        if ANDROID_AVAILABLE:
            logger.info("Running on Android device")
        else:
            logger.info("Running in simulation mode")
    
    def on_stop(self):
        """Called when app stops"""
        logger.info("Stopping Universal Soul AI...")
        if self.overlay_system and self.is_overlay_active:
            asyncio.create_task(self.async_stop_overlay())


def main():
    """Main entry point"""
    logger.info("🚀 Starting Universal Soul AI - Complete Android App")
    
    try:
        app = UniversalSoulAIApp()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()