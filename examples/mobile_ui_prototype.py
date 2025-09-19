#!/usr/bin/env python3
"""
Mobile UI Prototype for Universal Soul AI
=========================================

A prototype implementation of the mobile interface design
using Python and tkinter for demonstration purposes.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
import time
from typing import Dict, Any, List
from enum import Enum


class UITheme:
    """Universal Soul AI design system colors and styles"""
    
    # Primary Colors
    PRIMARY = "#6366f1"      # Indigo - Intelligence
    SECONDARY = "#10b981"    # Emerald - Success/Privacy
    ACCENT = "#f59e0b"       # Amber - Attention/Warning
    
    # Neutral Colors
    DARK = "#1f2937"         # Dark Gray - Text
    MEDIUM = "#6b7280"       # Medium Gray - Secondary text
    LIGHT = "#f9fafb"        # Light Gray - Background
    WHITE = "#ffffff"        # Pure White - Cards/Surfaces
    
    # Status Colors
    SUCCESS = "#10b981"      # Green - Success states
    WARNING = "#f59e0b"      # Amber - Warning states
    ERROR = "#ef4444"        # Red - Error states
    INFO = "#3b82f6"         # Blue - Information
    
    # Privacy Colors
    PRIVACY = "#8b5cf6"      # Purple - Privacy indicators
    LOCAL = "#059669"        # Dark Green - Local processing
    SECURE = "#1e40af"       # Dark Blue - Security features


class VoiceState(Enum):
    """Voice interface states"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


class AutomationTask:
    """Represents an automation task"""
    
    def __init__(self, description: str, platform: str, status: str = "pending"):
        self.description = description
        self.platform = platform
        self.status = status  # pending, running, completed, failed
        self.progress = 0
        self.start_time = None
        self.duration = 0


class UniversalSoulMobileUI:
    """Mobile UI prototype for Universal Soul AI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Universal Soul AI")
        self.root.geometry("375x812")  # iPhone 13 Pro dimensions
        self.root.configure(bg=UITheme.LIGHT)
        
        # State
        self.voice_state = VoiceState.IDLE
        self.current_tasks: List[AutomationTask] = []
        self.devices = [
            {"name": "iPhone", "location": "Living Room", "battery": 85, "signal": "Excellent"},
            {"name": "MacBook Pro", "location": "Office", "battery": 100, "signal": "Good"},
            {"name": "Apple TV", "location": "Bedroom", "battery": 100, "signal": "Excellent"}
        ]
        
        # Initialize UI
        self.setup_styles()
        self.create_main_interface()
        self.create_status_bar()
        self.create_voice_interface()
        self.create_task_list()
        self.create_quick_actions()
        self.create_privacy_footer()
        
        # Add sample tasks
        self.add_sample_tasks()
        
        # Start UI update loop
        self.start_ui_updates()
    
    def setup_styles(self):
        """Configure UI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Voice.TButton',
                       background=UITheme.PRIMARY,
                       foreground=UITheme.WHITE,
                       font=('Inter', 16, 'bold'),
                       padding=(20, 15))
        
        style.configure('Quick.TButton',
                       background=UITheme.WHITE,
                       foreground=UITheme.DARK,
                       font=('Inter', 12),
                       padding=(10, 8))
        
        style.configure('Privacy.TLabel',
                       background=UITheme.LIGHT,
                       foreground=UITheme.PRIVACY,
                       font=('Inter', 10))
    
    def create_main_interface(self):
        """Create the main interface container"""
        self.main_frame = tk.Frame(self.root, bg=UITheme.LIGHT)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)
    
    def create_status_bar(self):
        """Create the status bar"""
        status_frame = tk.Frame(self.main_frame, bg=UITheme.LIGHT, height=30)
        status_frame.pack(fill=tk.X, pady=(0, 16))
        status_frame.pack_propagate(False)
        
        # App title
        title_label = tk.Label(status_frame, 
                              text="Universal Soul AI",
                              bg=UITheme.LIGHT,
                              fg=UITheme.DARK,
                              font=('Inter', 20, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Status indicators
        status_indicators = tk.Frame(status_frame, bg=UITheme.LIGHT)
        status_indicators.pack(side=tk.RIGHT)
        
        privacy_icon = tk.Label(status_indicators,
                               text="🔒",
                               bg=UITheme.LIGHT,
                               font=('Arial', 16))
        privacy_icon.pack(side=tk.RIGHT, padx=(8, 0))
        
        signal_icon = tk.Label(status_indicators,
                              text="📶",
                              bg=UITheme.LIGHT,
                              font=('Arial', 16))
        signal_icon.pack(side=tk.RIGHT, padx=(8, 0))
    
    def create_voice_interface(self):
        """Create the voice interface section"""
        voice_frame = tk.Frame(self.main_frame, bg=UITheme.WHITE, relief=tk.RAISED, bd=1)
        voice_frame.pack(fill=tk.X, pady=(0, 24))
        
        # Voice button container
        voice_container = tk.Frame(voice_frame, bg=UITheme.WHITE)
        voice_container.pack(pady=32)
        
        # Main voice button
        self.voice_button = tk.Button(voice_container,
                                     text="🎙️",
                                     bg=UITheme.PRIMARY,
                                     fg=UITheme.WHITE,
                                     font=('Arial', 48),
                                     width=3,
                                     height=1,
                                     relief=tk.FLAT,
                                     command=self.toggle_voice)
        self.voice_button.pack()
        
        # Voice status label
        self.voice_status_label = tk.Label(voice_container,
                                          text="Tap to speak, or say 'Hey Soul'",
                                          bg=UITheme.WHITE,
                                          fg=UITheme.MEDIUM,
                                          font=('Inter', 14))
        self.voice_status_label.pack(pady=(16, 0))
        
        # Voice waveform (simulated)
        self.waveform_frame = tk.Frame(voice_container, bg=UITheme.WHITE, height=40)
        self.waveform_frame.pack(fill=tk.X, pady=(16, 0))
        self.waveform_frame.pack_propagate(False)
        
        self.waveform_canvas = tk.Canvas(self.waveform_frame,
                                        bg=UITheme.WHITE,
                                        height=40,
                                        highlightthickness=0)
        self.waveform_canvas.pack(fill=tk.BOTH)
    
    def create_task_list(self):
        """Create the recent tasks section"""
        tasks_frame = tk.Frame(self.main_frame, bg=UITheme.LIGHT)
        tasks_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
        
        # Tasks header
        tasks_header = tk.Label(tasks_frame,
                               text="Recent Tasks",
                               bg=UITheme.LIGHT,
                               fg=UITheme.DARK,
                               font=('Inter', 18, 'bold'))
        tasks_header.pack(anchor=tk.W, pady=(0, 12))
        
        # Tasks list container
        self.tasks_container = tk.Frame(tasks_frame, bg=UITheme.LIGHT)
        self.tasks_container.pack(fill=tk.BOTH, expand=True)
    
    def create_quick_actions(self):
        """Create the quick actions section"""
        actions_frame = tk.Frame(self.main_frame, bg=UITheme.LIGHT)
        actions_frame.pack(fill=tk.X, pady=(0, 16))
        
        # Quick action buttons
        actions_container = tk.Frame(actions_frame, bg=UITheme.LIGHT)
        actions_container.pack()
        
        actions = [
            ("📱", "Apps", self.show_mobile_automation),
            ("🖥️", "Desktop", self.show_desktop_automation),
            ("🔄", "Sync", self.show_device_sync),
            ("⚙️", "Settings", self.show_settings)
        ]
        
        for i, (icon, label, command) in enumerate(actions):
            action_frame = tk.Frame(actions_container, bg=UITheme.WHITE, relief=tk.RAISED, bd=1)
            action_frame.grid(row=0, column=i, padx=4, pady=4)
            
            action_button = tk.Button(action_frame,
                                     text=icon,
                                     bg=UITheme.WHITE,
                                     fg=UITheme.DARK,
                                     font=('Arial', 24),
                                     relief=tk.FLAT,
                                     command=command)
            action_button.pack(pady=(8, 4))
            
            action_label = tk.Label(action_frame,
                                   text=label,
                                   bg=UITheme.WHITE,
                                   fg=UITheme.DARK,
                                   font=('Inter', 10))
            action_label.pack(pady=(0, 8))
    
    def create_privacy_footer(self):
        """Create the privacy footer"""
        footer_frame = tk.Frame(self.main_frame, bg=UITheme.LIGHT)
        footer_frame.pack(fill=tk.X)
        
        privacy_text = tk.Label(footer_frame,
                               text="🔒 100% Private • 🚀 Zero Cost",
                               bg=UITheme.LIGHT,
                               fg=UITheme.PRIVACY,
                               font=('Inter', 12, 'bold'))
        privacy_text.pack()
    
    def add_sample_tasks(self):
        """Add sample tasks for demonstration"""
        sample_tasks = [
            AutomationTask("Booked flight to Paris", "mobile", "completed"),
            AutomationTask("Updated calendar events", "desktop", "completed"),
            AutomationTask("Processing emails", "web", "running"),
            AutomationTask("Sync devices", "sync", "pending")
        ]
        
        for task in sample_tasks:
            self.current_tasks.append(task)
            if task.status == "completed":
                task.progress = 100
            elif task.status == "running":
                task.progress = 65
        
        self.update_task_display()
    
    def update_task_display(self):
        """Update the task list display"""
        # Clear existing task widgets
        for widget in self.tasks_container.winfo_children():
            widget.destroy()
        
        # Add current tasks
        for task in self.current_tasks[-4:]:  # Show last 4 tasks
            task_frame = tk.Frame(self.tasks_container, bg=UITheme.WHITE, relief=tk.RAISED, bd=1)
            task_frame.pack(fill=tk.X, pady=2)
            
            # Task content
            content_frame = tk.Frame(task_frame, bg=UITheme.WHITE)
            content_frame.pack(fill=tk.X, padx=12, pady=8)
            
            # Task description and status
            desc_frame = tk.Frame(content_frame, bg=UITheme.WHITE)
            desc_frame.pack(fill=tk.X)
            
            # Status icon
            status_icons = {
                "completed": "✅",
                "running": "⚡",
                "pending": "⏳",
                "failed": "❌"
            }
            
            status_icon = tk.Label(desc_frame,
                                  text=status_icons.get(task.status, "⏳"),
                                  bg=UITheme.WHITE,
                                  font=('Arial', 14))
            status_icon.pack(side=tk.LEFT, padx=(0, 8))
            
            # Task description
            desc_label = tk.Label(desc_frame,
                                 text=task.description,
                                 bg=UITheme.WHITE,
                                 fg=UITheme.DARK,
                                 font=('Inter', 14))
            desc_label.pack(side=tk.LEFT)
            
            # Progress bar for running tasks
            if task.status == "running":
                progress_frame = tk.Frame(content_frame, bg=UITheme.WHITE)
                progress_frame.pack(fill=tk.X, pady=(4, 0))
                
                progress_canvas = tk.Canvas(progress_frame, bg=UITheme.LIGHT, height=4, highlightthickness=0)
                progress_canvas.pack(fill=tk.X)
                
                # Draw progress bar
                width = progress_canvas.winfo_reqwidth()
                if width > 1:
                    progress_width = int(width * task.progress / 100)
                    progress_canvas.create_rectangle(0, 0, progress_width, 4, fill=UITheme.PRIMARY, outline="")
    
    def toggle_voice(self):
        """Toggle voice interface state"""
        if self.voice_state == VoiceState.IDLE:
            self.start_voice_interaction()
        else:
            self.stop_voice_interaction()
    
    def start_voice_interaction(self):
        """Start voice interaction"""
        self.voice_state = VoiceState.LISTENING
        self.voice_button.configure(bg=UITheme.SUCCESS, text="🎙️")
        self.voice_status_label.configure(text="Listening... Speak now")
        self.animate_waveform()
        
        # Simulate voice processing
        self.root.after(3000, self.simulate_voice_processing)
    
    def simulate_voice_processing(self):
        """Simulate voice processing"""
        self.voice_state = VoiceState.PROCESSING
        self.voice_button.configure(bg=UITheme.WARNING, text="🧠")
        self.voice_status_label.configure(text="Processing your request...")
        
        # Simulate response
        self.root.after(2000, self.simulate_voice_response)
    
    def simulate_voice_response(self):
        """Simulate voice response"""
        self.voice_state = VoiceState.SPEAKING
        self.voice_button.configure(bg=UITheme.INFO, text="💬")
        self.voice_status_label.configure(text="I'll help you with that task")
        
        # Add new task
        new_task = AutomationTask("Book restaurant reservation", "mobile", "running")
        new_task.progress = 0
        self.current_tasks.append(new_task)
        self.update_task_display()
        
        # Return to idle
        self.root.after(3000, self.stop_voice_interaction)
    
    def stop_voice_interaction(self):
        """Stop voice interaction"""
        self.voice_state = VoiceState.IDLE
        self.voice_button.configure(bg=UITheme.PRIMARY, text="🎙️")
        self.voice_status_label.configure(text="Tap to speak, or say 'Hey Soul'")
        self.clear_waveform()
    
    def animate_waveform(self):
        """Animate the voice waveform"""
        if self.voice_state == VoiceState.LISTENING:
            self.waveform_canvas.delete("all")
            
            # Draw animated waveform bars
            width = self.waveform_canvas.winfo_width()
            if width > 1:
                import random
                bar_width = 3
                bar_spacing = 5
                num_bars = width // (bar_width + bar_spacing)
                
                for i in range(num_bars):
                    x = i * (bar_width + bar_spacing)
                    height = random.randint(5, 35)
                    y = 20 - height // 2
                    
                    self.waveform_canvas.create_rectangle(
                        x, y, x + bar_width, y + height,
                        fill=UITheme.PRIMARY, outline=""
                    )
            
            # Continue animation
            self.root.after(100, self.animate_waveform)
    
    def clear_waveform(self):
        """Clear the waveform display"""
        self.waveform_canvas.delete("all")
    
    def show_mobile_automation(self):
        """Show mobile automation interface"""
        messagebox.showinfo("Mobile Automation", 
                           "Mobile app automation interface\n\n"
                           "• Navigate mobile apps\n"
                           "• Touch gesture simulation\n"
                           "• Screen analysis\n"
                           "• Privacy-first processing")
    
    def show_desktop_automation(self):
        """Show desktop automation interface"""
        messagebox.showinfo("Desktop Automation",
                           "Desktop automation interface\n\n"
                           "• GUI automation\n"
                           "• Code execution\n"
                           "• Hybrid CoAct-1 approach\n"
                           "• Cross-platform support")
    
    def show_device_sync(self):
        """Show device synchronization interface"""
        sync_window = tk.Toplevel(self.root)
        sync_window.title("Device Synchronization")
        sync_window.geometry("350x400")
        sync_window.configure(bg=UITheme.LIGHT)
        
        # Header
        header = tk.Label(sync_window,
                         text="🔄 Transfer to Another Device",
                         bg=UITheme.LIGHT,
                         fg=UITheme.DARK,
                         font=('Inter', 16, 'bold'))
        header.pack(pady=16)
        
        # Available devices
        devices_label = tk.Label(sync_window,
                                text="Available Devices:",
                                bg=UITheme.LIGHT,
                                fg=UITheme.DARK,
                                font=('Inter', 14))
        devices_label.pack(anchor=tk.W, padx=16, pady=(0, 8))
        
        # Device list
        for device in self.devices:
            device_frame = tk.Frame(sync_window, bg=UITheme.WHITE, relief=tk.RAISED, bd=1)
            device_frame.pack(fill=tk.X, padx=16, pady=4)
            
            content = tk.Frame(device_frame, bg=UITheme.WHITE)
            content.pack(fill=tk.X, padx=12, pady=8)
            
            # Device info
            device_info = tk.Label(content,
                                  text=f"📱 {device['name']} ({device['location']})",
                                  bg=UITheme.WHITE,
                                  fg=UITheme.DARK,
                                  font=('Inter', 12, 'bold'))
            device_info.pack(anchor=tk.W)
            
            status_info = tk.Label(content,
                                  text=f"🔋 {device['battery']}% • 📶 {device['signal']}",
                                  bg=UITheme.WHITE,
                                  fg=UITheme.MEDIUM,
                                  font=('Inter', 10))
            status_info.pack(anchor=tk.W)
            
            transfer_btn = tk.Button(content,
                                    text="Transfer Session",
                                    bg=UITheme.PRIMARY,
                                    fg=UITheme.WHITE,
                                    font=('Inter', 10),
                                    relief=tk.FLAT,
                                    command=lambda d=device: self.transfer_session(d))
            transfer_btn.pack(anchor=tk.W, pady=(4, 0))
        
        # Privacy note
        privacy_note = tk.Label(sync_window,
                               text="🔒 All transfers encrypted\n⚡ Transfer time: ~0.4 seconds",
                               bg=UITheme.LIGHT,
                               fg=UITheme.PRIVACY,
                               font=('Inter', 10),
                               justify=tk.CENTER)
        privacy_note.pack(pady=16)
    
    def transfer_session(self, device):
        """Transfer session to device"""
        messagebox.showinfo("Session Transfer",
                           f"Transferring session to {device['name']}\n\n"
                           f"🔒 Encrypted transfer in progress...\n"
                           f"⚡ Estimated time: 0.4 seconds")
    
    def show_settings(self):
        """Show settings interface"""
        messagebox.showinfo("Settings",
                           "Universal Soul AI Settings\n\n"
                           "• Privacy & Security\n"
                           "• Voice Configuration\n"
                           "• Automation Preferences\n"
                           "• Device Management\n"
                           "• Performance Optimization")
    
    def start_ui_updates(self):
        """Start the UI update loop"""
        def update_loop():
            while True:
                # Update running tasks
                for task in self.current_tasks:
                    if task.status == "running" and task.progress < 100:
                        task.progress += 1
                        if task.progress >= 100:
                            task.status = "completed"
                
                # Schedule UI update
                self.root.after(0, self.update_task_display)
                time.sleep(0.1)
        
        # Start update thread
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    def run(self):
        """Run the mobile UI prototype"""
        self.root.mainloop()


def main():
    """Main function"""
    print("🚀 Universal Soul AI - Mobile UI Prototype")
    print("=" * 45)
    print("Demonstrating the mobile interface design")
    print("for the Universal Soul AI automation system\n")
    
    try:
        app = UniversalSoulMobileUI()
        app.run()
        
    except KeyboardInterrupt:
        print("\n⏹️  UI prototype stopped by user")
    except Exception as e:
        print(f"❌ UI prototype failed: {e}")


if __name__ == "__main__":
    main()
