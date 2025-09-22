#!/usr/bin/env python3
"""
Universal Soul AI - Minimal Android APK
=====================================

Ultra-minimal version to ensure build success.
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class UniversalSoulApp(App):
    def build(self):
        # Main container
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title = Label(
            text='Universal Soul AI',
            font_size='24sp',
            size_hint_y=0.3
        )
        layout.add_widget(title)
        
        # Status
        status = Label(
            text='AI Assistant Ready',
            font_size='16sp',
            size_hint_y=0.2
        )
        layout.add_widget(status)
        
        # Start button
        start_btn = Button(
            text='Activate AI',
            font_size='18sp',
            size_hint_y=0.3
        )
        start_btn.bind(on_press=self.activate_ai)
        layout.add_widget(start_btn)
        
        # Info button
        info_btn = Button(
            text='About',
            font_size='18sp',
            size_hint_y=0.2
        )
        info_btn.bind(on_press=self.show_info)
        layout.add_widget(info_btn)
        
        return layout
    
    def activate_ai(self, instance):
        instance.text = 'AI Activated!'
    
    def show_info(self, instance):
        instance.text = 'Universal Soul AI v1.0'

def main():
    UniversalSoulApp().run()

if __name__ == '__main__':
    main()