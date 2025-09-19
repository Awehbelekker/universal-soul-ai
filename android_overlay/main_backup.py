#!/usr/bin/env python3
"""
Universal Soul AI - Android APK Main Entry Point
===============================================

Main entry point for the Android APK version of Universal Soul AI.
This creates a Kivy-based mobile app with the overlay functionality.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Kivy configuration (must be set before importing kivy)
os.environ['KIVY_WINDOW_ICON'] = str(project_root / 'assets' / 'icon.png')

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.utils import platform

# KivyMD for Material Design
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFloatingActionButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar

# Android-specific imports
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from jnius import autoclass, PythonJavaClass, java_method
    from android import activity
    
    # Android classes
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Settings = autoclass('android.provider.Settings')
    Uri = autoclass('android.net.Uri')

# Universal Soul AI components
try:
    from universal_soul_overlay import UniversalSoulOverlay, OverlayConfig
    from core.overlay_service import OverlayState
    from demo.overlay_demo import OverlayDemoRunner
except ImportError as e:
    Logger.warning(f"Could not import overlay components: {e}")
    UniversalSoulOverlay = None


class UniversalSoulAIScreen(MDScreen):
    """Main screen for Universal Soul AI mobile app"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.overlay_system = None
        self.is_overlay_active = False
        self.build_ui()
    
    def build_ui(self):
        """Build the main user interface"""
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
        self.status_card = MDCard(
            MDBoxLayout(
                MDLabel(
                    text="🔧 System Status",
                    theme_text_color="Primary",
                    font_style="H6"
                ),
                self.create_status_label("Overlay System", "Not Started", "🔴"),
                self.create_status_label("Voice Interface", "Not Started", "🔴"),
                self.create_status_label("Gesture Recognition", "Not Started", "🔴"),
                self.create_status_label("Context Intelligence", "Not Started", "🔴"),
                orientation='vertical',
                spacing='5dp',
                padding='20dp'
            ),
            elevation=3,
            size_hint_y=None,
            height='200dp'
        )
        main_layout.add_widget(self.status_card)
        
        # Control buttons
        button_layout = MDBoxLayout(
            orientation='vertical',
            spacing='10dp',
            size_hint_y=None,
            height='200dp'
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
            text="🎭 Run Demo",
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
        
        main_layout.add_widget(button_layout)
        
        # Floating action button for overlay toggle
        self.fab = MDFloatingActionButton(
            icon="gesture-tap",
            md_bg_color="#1976D2",
            pos_hint={'center_x': 0.9, 'center_y': 0.1},
            on_release=self.toggle_overlay
        )
        
        self.add_widget(main_layout)
        self.add_widget(self.fab)
    
    def create_status_label(self, component, status, icon):
        """Create a status label for system components"""
        return MDLabel(
            text=f"{icon} {component}: {status}",
            theme_text_color="Secondary",
            font_style="Body2"
        )
    
    def update_status(self, component, status, icon):
        """Update component status"""
        # Find and update the status label
        # This is a simplified version - in production you'd track labels properly
        Logger.info(f"Status Update: {component} -> {status} {icon}")
    
    def request_permissions(self, instance):
        """Request necessary Android permissions"""
        if platform == 'android':
            permissions = [
                Permission.RECORD_AUDIO,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.CAMERA,
                Permission.VIBRATE,
                Permission.WAKE_LOCK,
                Permission.SYSTEM_ALERT_WINDOW
            ]
            
            request_permissions(permissions)
            self.show_popup("Permissions", "✅ Permissions requested!\nPlease grant all permissions for full functionality.")
        else:
            self.show_popup("Permissions", "⚠️ Permission system only works on Android devices.")
    
    def open_system_settings(self, instance):
        """Open Android system settings for overlay permission"""
        if platform == 'android':
            try:
                # Open overlay permission settings
                intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)
                intent.setData(Uri.parse(f"package:{PythonActivity.mActivity.getPackageName()}"))
                PythonActivity.mActivity.startActivity(intent)
            except Exception as e:
                Logger.error(f"Failed to open settings: {e}")
                self.show_popup("Error", f"❌ Could not open settings: {e}")
        else:
            self.show_popup("Settings", "⚠️ System settings only available on Android devices.")
    
    def start_overlay_system(self, instance):
        """Start the Universal Soul AI overlay system"""
        if UniversalSoulOverlay is None:
            self.show_popup("Error", "❌ Overlay system not available.\nRunning in demo mode.")
            return
        
        try:
            # Update button state
            self.start_button.text = "🔄 Initializing..."
            self.start_button.disabled = True
            
            # Schedule async initialization
            Clock.schedule_once(self._async_start_overlay, 0.1)
            
        except Exception as e:
            Logger.error(f"Failed to start overlay: {e}")
            self.show_popup("Error", f"❌ Failed to start overlay: {e}")
            self.start_button.text = "🎪 Start Overlay System"
            self.start_button.disabled = False
    
    def _async_start_overlay(self, dt):
        """Async wrapper for starting overlay"""
        asyncio.create_task(self._initialize_overlay())
    
    async def _initialize_overlay(self):
        """Initialize the overlay system asynchronously"""
        try:
            # Create minimalist overlay configuration
            config = OverlayConfig(
                overlay_size=56,  # Minimalist 56dp floating icon
                continuous_listening=True,
                gesture_sensitivity=0.8,
                local_processing_only=True,
                battery_optimization=True
            )
            
            # Create overlay system
            self.overlay_system = UniversalSoulOverlay(config)
            
            # Initialize
            success = await self.overlay_system.initialize()
            
            if success:
                # Start overlay
                await self.overlay_system.start()
                self.is_overlay_active = True
                
                # Update UI
                Clock.schedule_once(self._update_ui_success, 0)
            else:
                Clock.schedule_once(self._update_ui_error, 0)
                
        except Exception as e:
            Logger.error(f"Overlay initialization failed: {e}")
            Clock.schedule_once(lambda dt: self._update_ui_error(str(e)), 0)
    
    def _update_ui_success(self, dt):
        """Update UI after successful overlay start"""
        self.start_button.text = "✅ Minimalist Overlay Active"
        self.start_button.md_bg_color = "#4CAF50"
        self.start_button.disabled = False
        self.show_popup("Success", "🎉 Minimalist Universal Soul AI is now active!\n\n🎯 Tap floating icon for quick access\n👆 Use invisible 360° gestures\n🎙️ Voice commands available")
    
    def _update_ui_error(self, error_msg=None):
        """Update UI after overlay start error"""
        self.start_button.text = "❌ Start Failed"
        self.start_button.md_bg_color = "#F44336"
        self.start_button.disabled = False
        error_text = f"❌ Failed to start overlay system.\n\nError: {error_msg}" if error_msg else "❌ Failed to start overlay system."
        self.show_popup("Error", error_text)
    
    def toggle_overlay(self, instance):
        """Toggle overlay visibility"""
        if self.overlay_system and self.is_overlay_active:
            # Toggle overlay state
            if self.overlay_system.current_state == OverlayState.HIDDEN:
                asyncio.create_task(self.overlay_system.overlay_service.show_overlay())
                self.fab.icon = "eye"
            else:
                asyncio.create_task(self.overlay_system.overlay_service.hide_overlay())
                self.fab.icon = "eye-off"
        else:
            self.show_popup("Info", "⚠️ Please start the overlay system first.")
    
    def run_demo(self, instance):
        """Run the overlay demonstration"""
        try:
            # Schedule async demo
            Clock.schedule_once(self._async_run_demo, 0.1)
        except Exception as e:
            Logger.error(f"Failed to run demo: {e}")
            self.show_popup("Error", f"❌ Demo failed: {e}")
    
    def _async_run_demo(self, dt):
        """Async wrapper for demo"""
        asyncio.create_task(self._run_demo_async())
    
    async def _run_demo_async(self):
        """Run demo asynchronously"""
        try:
            demo_runner = OverlayDemoRunner()
            await demo_runner.run_complete_demo()
            
            Clock.schedule_once(lambda dt: self.show_popup("Demo Complete", "🎉 Demo completed successfully!\nCheck the logs for detailed results."), 0)
            
        except Exception as e:
            Logger.error(f"Demo failed: {e}")
            Clock.schedule_once(lambda dt: self.show_popup("Demo Error", f"❌ Demo failed: {e}"), 0)
    
    def show_popup(self, title, message):
        """Show a popup message"""
        popup = Popup(
            title=title,
            content=Label(text=message, text_size=(300, None), halign='center'),
            size_hint=(0.8, 0.6),
            auto_dismiss=True
        )
        popup.open()


class UniversalSoulAIApp(MDApp):
    """Main Universal Soul AI Android Application"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Universal Soul AI"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
    
    def build(self):
        """Build the application"""
        Logger.info("🚀 Starting Universal Soul AI Android App")
        
        # Create main screen
        screen = UniversalSoulAIScreen()
        
        return screen
    
    def on_start(self):
        """Called when the app starts"""
        Logger.info("✅ Universal Soul AI App started successfully")
        
        # Request permissions on startup if Android
        if platform == 'android':
            Clock.schedule_once(self._request_initial_permissions, 2.0)
    
    def _request_initial_permissions(self, dt):
        """Request initial permissions"""
        try:
            permissions = [
                Permission.RECORD_AUDIO,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.VIBRATE
            ]
            request_permissions(permissions)
        except Exception as e:
            Logger.warning(f"Could not request initial permissions: {e}")
    
    def on_pause(self):
        """Called when app is paused"""
        Logger.info("⏸️ Universal Soul AI App paused")
        return True
    
    def on_resume(self):
        """Called when app is resumed"""
        Logger.info("▶️ Universal Soul AI App resumed")


def main():
    """Main entry point for the Android APK"""
    try:
        # Set up asyncio for Android
        if platform == 'android':
            # Android-specific asyncio setup
            import asyncio
            if hasattr(asyncio, 'set_event_loop_policy'):
                asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
        
        # Create and run the app
        app = UniversalSoulAIApp()
        app.run()
        
    except Exception as e:
        Logger.error(f"❌ App startup failed: {e}")
        print(f"❌ Universal Soul AI startup failed: {e}")


if __name__ == '__main__':
    main()
