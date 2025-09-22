#!/usr/bin/env python3
"""
Universal Soul AI - Simplified Android APK Entry Point
====================================================

Simplified Android app focusing on core Kivy functionality for reliable builds.
"""

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

# Android-specific imports (conditional)
ANDROID_AVAILABLE = False
# Placeholders to avoid unresolved import errors when not on Android
request_permission = None
Permission = None
activity = None

if platform == 'android':
    try:
        import importlib
        android_permissions = importlib.import_module('android.permissions')
        request_permission = getattr(android_permissions, 'request_permission', None)
        Permission = getattr(android_permissions, 'Permission', None)
        android_mod = importlib.import_module('android')
        activity = getattr(android_mod, 'activity', None)
        if request_permission and Permission:
            ANDROID_AVAILABLE = True
            logger.info("Android platform detected and imports successful")
        else:
            logger.warning("Android modules loaded but expected attributes are missing")
    except Exception as e:
        logger.warning(f"Android imports failed: {e}")

class UniversalSoulApp(App):
    """Main Universal Soul AI Android Application"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Universal Soul AI"
        self.overlay_active = False
        
    def build(self):
        """Build the main application interface"""
        logger.info("Building Universal Soul AI interface...")
        
        # Main container
        main_layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=10
        )
        
        # Title
        title_label = Label(
            text='Universal Soul AI',
            font_size='24sp',
            size_hint_y=0.2,
            bold=True
        )
        main_layout.add_widget(title_label)
        
        # Status label
        self.status_label = Label(
            text='Ready to assist...',
            font_size='16sp',
            size_hint_y=0.15
        )
        main_layout.add_widget(self.status_label)
        
        # Buttons container
        buttons_layout = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=0.5
        )
        
        # Start Overlay button
        self.overlay_btn = Button(
            text='Start AI Overlay',
            font_size='18sp',
            size_hint_y=0.25
        )
        self.overlay_btn.bind(on_press=self.toggle_overlay)
        buttons_layout.add_widget(self.overlay_btn)
        
        # Voice Assistant button
        voice_btn = Button(
            text='Voice Assistant',
            font_size='18sp',
            size_hint_y=0.25
        )
        voice_btn.bind(on_press=self.start_voice_assistant)
        buttons_layout.add_widget(voice_btn)
        
        # Settings button
        settings_btn = Button(
            text='Settings',
            font_size='18sp',
            size_hint_y=0.25
        )
        settings_btn.bind(on_press=self.show_settings)
        buttons_layout.add_widget(settings_btn)
        
        # About button
        about_btn = Button(
            text='About',
            font_size='18sp',
            size_hint_y=0.25
        )
        about_btn.bind(on_press=self.show_about)
        buttons_layout.add_widget(about_btn)
        
        main_layout.add_widget(buttons_layout)
        
        # Progress bar
        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=0.1
        )
        main_layout.add_widget(self.progress)
        
        # Initialize Android permissions if available
        if ANDROID_AVAILABLE:
            Clock.schedule_once(self.request_android_permissions, 1)
        
        logger.info("Universal Soul AI interface built successfully")
        return main_layout
    
    def toggle_overlay(self, instance):
        """Toggle the AI overlay system"""
        if not self.overlay_active:
            self.start_overlay()
        else:
            self.stop_overlay()
    
    def start_overlay(self):
        """Start the AI overlay system"""
        logger.info("Starting AI overlay system...")
        self.overlay_active = True
        self.overlay_btn.text = 'Stop AI Overlay'
        self.status_label.text = 'AI Overlay Active'
        
        # Simulate overlay initialization
        self.progress.value = 0
        Clock.schedule_interval(self.update_progress, 0.1)
    
    def stop_overlay(self):
        """Stop the AI overlay system"""
        logger.info("Stopping AI overlay system...")
        self.overlay_active = False
        self.overlay_btn.text = 'Start AI Overlay'
        self.status_label.text = 'Ready to assist...'
        self.progress.value = 0
    
    def update_progress(self, dt):
        """Update progress bar"""
        self.progress.value += 2
        if self.progress.value >= 100:
            self.progress.value = 100
            self.status_label.text = 'AI Overlay Ready'
            return False  # Stop the scheduled interval
        return True
    
    def start_voice_assistant(self, instance):
        """Start voice assistant"""
        logger.info("Starting voice assistant...")
        self.show_popup("Voice Assistant", "Voice assistant activated!\nSay 'Hey Soul' to begin.")
    
    def show_settings(self, instance):
        """Show settings dialog"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(text='Universal Soul AI Settings', font_size='18sp'))
        content.add_widget(Label(text='• Privacy Mode: Enabled'))
        content.add_widget(Label(text='• Voice Recognition: Active'))
        content.add_widget(Label(text='• Gesture Control: Enabled'))
        content.add_widget(Label(text='• Local Processing: On'))
        
        close_btn = Button(text='Close', size_hint_y=0.3)
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Settings',
            content=content,
            size_hint=(0.8, 0.6)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_about(self, instance):
        """Show about dialog"""
        about_text = """Universal Soul AI

Privacy-first AI assistant with:
• Voice recognition
• Gesture navigation  
• Contextual intelligence
• Local processing
• Android overlay system

Version: 1.0.0
Built with Kivy & Python"""
        
        self.show_popup("About Universal Soul AI", about_text)
    
    def show_popup(self, title, message):
        """Show a popup with title and message"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message, text_size=(300, None), halign='center'))
        
        close_btn = Button(text='Close', size_hint_y=0.3)
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.5)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def request_android_permissions(self, dt):
        """Request Android permissions"""
        logger.info("Requesting Android permissions...")
        try:
            # Request overlay permission
            request_permission(Permission.SYSTEM_ALERT_WINDOW)
            # Request audio permission
            request_permission(Permission.RECORD_AUDIO)
            # Request storage permission
            request_permission(Permission.WRITE_EXTERNAL_STORAGE)
            
            self.status_label.text = 'Permissions requested'
            logger.info("Android permissions requested successfully")
        except Exception as e:
            logger.error(f"Permission request failed: {e}")
            self.status_label.text = 'Permission request failed'

def main():
    """Application entry point"""
    logger.info("Starting Universal Soul AI...")
    app = UniversalSoulApp()
    app.run()

if __name__ == '__main__':
    main()