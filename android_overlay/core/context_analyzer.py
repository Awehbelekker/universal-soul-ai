"""
Context Analyzer for Universal Soul AI Android Overlay
=====================================================

Provides contextual intelligence by analyzing current Android app context
and adapting overlay behavior accordingly. Maintains privacy-first approach
with local-only processing.

Features:
- Current app detection
- Activity context analysis
- Privacy-preserving screen content analysis
- Contextual gesture mapping adaptation
- Smart feature prioritization
"""

import asyncio
import time
import json
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
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


class AppCategory(Enum):
    """Categories of Android applications"""
    COMMUNICATION = "communication"  # WhatsApp, Telegram, Email
    PRODUCTIVITY = "productivity"    # Office, Notes, Calendar
    SOCIAL = "social"               # Facebook, Instagram, Twitter
    ENTERTAINMENT = "entertainment"  # YouTube, Netflix, Games
    SHOPPING = "shopping"           # Amazon, eBay, Shopping apps
    NAVIGATION = "navigation"       # Maps, GPS, Travel
    FINANCE = "finance"            # Banking, Payment, Investment
    HEALTH = "health"              # Fitness, Medical, Wellness
    EDUCATION = "education"        # Learning, Books, Courses
    UTILITIES = "utilities"        # Settings, File managers, Tools
    BROWSER = "browser"            # Chrome, Firefox, Safari
    UNKNOWN = "unknown"            # Unrecognized apps


@dataclass
class AppContext:
    """Current application context information"""
    package_name: str
    app_name: str
    category: AppCategory
    activity_name: str
    is_foreground: bool
    timestamp: float
    
    # Context-specific data
    text_input_active: bool = False
    keyboard_visible: bool = False
    media_playing: bool = False
    notification_count: int = 0
    
    # Privacy-safe content hints
    content_type: str = "unknown"  # text, media, form, list, etc.
    interaction_mode: str = "view"  # view, edit, input, navigate


@dataclass
class ContextualFeatures:
    """Features prioritized based on current context"""
    primary_actions: List[str]
    secondary_actions: List[str]
    gesture_mappings: Dict[str, str]
    voice_commands: List[str]
    automation_suggestions: List[str]


class ContextAnalyzer:
    """
    Contextual intelligence engine for Universal Soul AI overlay
    
    Analyzes current Android app context to provide intelligent
    feature adaptation while maintaining complete privacy.
    """
    
    def __init__(self, privacy_mode: bool = True, update_interval: float = 1.0):
        self.privacy_mode = privacy_mode
        self.update_interval = update_interval
        self.is_initialized = False
        
        # Current context
        self.current_context: Optional[AppContext] = None
        self.context_history: List[AppContext] = []
        self.max_history_size = 100
        
        # App categorization database
        self.app_categories: Dict[str, AppCategory] = {}
        self._initialize_app_categories()
        
        # Context-specific feature mappings
        self.context_features: Dict[AppCategory, ContextualFeatures] = {}
        self._initialize_context_features()
        
        # Monitoring state
        self.monitoring_active = False
        self.last_update_time = 0.0
        
        # Callbacks
        self.on_context_changed: Optional[Callable[[AppContext], None]] = None
        self.on_app_switched: Optional[Callable[[str, str], None]] = None
        self.on_features_updated: Optional[Callable[[ContextualFeatures], None]] = None
        
        # Android components
        self.activity_manager = None
        self.accessibility_service = None
    
    async def initialize(self) -> bool:
        """Initialize context analysis system"""
        try:
            logger.info("Initializing context analyzer...")
            
            if ANDROID_AVAILABLE:
                await self._initialize_android_services()
            else:
                logger.info("Android not available - using simulation mode")
            
            # Start context monitoring
            await self._start_context_monitoring()
            
            self.is_initialized = True
            logger.info("Context analyzer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize context analyzer: {e}")
            return False
    
    async def _initialize_android_services(self) -> None:
        """Initialize Android system services for context analysis"""
        try:
            Context = autoclass('android.content.Context')
            ActivityManager = autoclass('android.app.ActivityManager')
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            
            # Get activity manager for app detection
            self.activity_manager = activity.getSystemService(Context.ACTIVITY_SERVICE)
            
            logger.info("Android services initialized for context analysis")
            
        except Exception as e:
            logger.error(f"Failed to initialize Android services: {e}")
    
    def _initialize_app_categories(self) -> None:
        """Initialize app categorization database"""
        # Communication apps
        comm_apps = [
            "com.whatsapp", "org.telegram.messenger", "com.google.android.gm",
            "com.microsoft.office.outlook", "com.slack", "com.discord",
            "com.skype.raider", "us.zoom.videomeetings"
        ]
        
        # Productivity apps
        prod_apps = [
            "com.microsoft.office.word", "com.google.android.apps.docs.editors.docs",
            "com.microsoft.office.excel", "com.google.android.calendar",
            "com.todoist", "com.any.do", "com.evernote", "com.notion.id"
        ]
        
        # Social apps
        social_apps = [
            "com.facebook.katana", "com.instagram.android", "com.twitter.android",
            "com.linkedin.android", "com.snapchat.android", "com.tiktok.musically"
        ]
        
        # Entertainment apps
        entertainment_apps = [
            "com.google.android.youtube", "com.netflix.mediaclient",
            "com.spotify.music", "com.amazon.avod.thirdpartyclient"
        ]
        
        # Browser apps
        browser_apps = [
            "com.android.chrome", "org.mozilla.firefox", "com.microsoft.emmx",
            "com.opera.browser", "com.brave.browser"
        ]
        
        # Map categories
        for app in comm_apps:
            self.app_categories[app] = AppCategory.COMMUNICATION
        for app in prod_apps:
            self.app_categories[app] = AppCategory.PRODUCTIVITY
        for app in social_apps:
            self.app_categories[app] = AppCategory.SOCIAL
        for app in entertainment_apps:
            self.app_categories[app] = AppCategory.ENTERTAINMENT
        for app in browser_apps:
            self.app_categories[app] = AppCategory.BROWSER
    
    def _initialize_context_features(self) -> None:
        """Initialize context-specific feature mappings"""
        
        # Communication context features
        self.context_features[AppCategory.COMMUNICATION] = ContextualFeatures(
            primary_actions=["transcribe_voice", "quick_reply", "translate_text"],
            secondary_actions=["schedule_message", "save_contact", "create_reminder"],
            gesture_mappings={
                "north": "voice_transcription",
                "east": "quick_reply",
                "south": "save_conversation",
                "west": "translate_text"
            },
            voice_commands=["transcribe this", "reply with", "translate", "save contact"],
            automation_suggestions=["Auto-reply setup", "Message scheduling", "Contact organization"]
        )
        
        # Productivity context features
        self.context_features[AppCategory.PRODUCTIVITY] = ContextualFeatures(
            primary_actions=["voice_to_text", "create_task", "schedule_event"],
            secondary_actions=["format_document", "share_content", "backup_work"],
            gesture_mappings={
                "north": "create_calendar_event",
                "east": "voice_to_text",
                "south": "create_task",
                "west": "save_notes"
            },
            voice_commands=["create task", "schedule meeting", "take notes", "format text"],
            automation_suggestions=["Document formatting", "Task automation", "Calendar integration"]
        )
        
        # Social context features
        self.context_features[AppCategory.SOCIAL] = ContextualFeatures(
            primary_actions=["quick_post", "save_content", "share_external"],
            secondary_actions=["analyze_sentiment", "schedule_post", "backup_media"],
            gesture_mappings={
                "north": "quick_post",
                "east": "share_external",
                "south": "save_content",
                "west": "analyze_post"
            },
            voice_commands=["post this", "save image", "share to", "analyze sentiment"],
            automation_suggestions=["Post scheduling", "Content curation", "Engagement tracking"]
        )
        
        # Browser context features
        self.context_features[AppCategory.BROWSER] = ContextualFeatures(
            primary_actions=["save_page", "extract_text", "translate_page"],
            secondary_actions=["bookmark_page", "share_link", "read_aloud"],
            gesture_mappings={
                "north": "bookmark_page",
                "east": "translate_page",
                "south": "save_article",
                "west": "extract_text"
            },
            voice_commands=["save this page", "translate", "read aloud", "extract text"],
            automation_suggestions=["Auto-bookmark", "Reading list", "Translation automation"]
        )
        
        # Default features for unknown contexts
        self.context_features[AppCategory.UNKNOWN] = ContextualFeatures(
            primary_actions=["voice_command", "quick_note", "screenshot"],
            secondary_actions=["app_automation", "system_control", "help"],
            gesture_mappings={
                "north": "voice_command",
                "east": "app_automation",
                "south": "quick_note",
                "west": "screenshot"
            },
            voice_commands=["help", "automate this", "take note", "screenshot"],
            automation_suggestions=["App automation", "System shortcuts", "Custom workflows"]
        )
    
    async def _start_context_monitoring(self) -> None:
        """Start continuous context monitoring"""
        self.monitoring_active = True
        asyncio.create_task(self._context_monitoring_loop())
        logger.info("Context monitoring started")
    
    async def _context_monitoring_loop(self) -> None:
        """Main context monitoring loop"""
        while self.monitoring_active:
            try:
                current_time = time.time()
                
                # Check if update is needed
                if current_time - self.last_update_time >= self.update_interval:
                    await self._update_context()
                    self.last_update_time = current_time
                
                # Sleep for a short interval
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Context monitoring error: {e}")
                await asyncio.sleep(1.0)  # Longer sleep on error
    
    async def _update_context(self) -> None:
        """Update current application context"""
        try:
            if ANDROID_AVAILABLE:
                new_context = await self._get_android_context()
            else:
                new_context = await self._get_simulated_context()
            
            if new_context and self._context_changed(new_context):
                # Update current context
                old_context = self.current_context
                self.current_context = new_context
                
                # Add to history
                self._add_to_history(new_context)
                
                # Get contextual features
                features = self._get_contextual_features(new_context)
                
                # Trigger callbacks
                if self.on_context_changed:
                    self.on_context_changed(new_context)
                
                if self.on_app_switched and old_context:
                    if old_context.package_name != new_context.package_name:
                        self.on_app_switched(old_context.package_name, new_context.package_name)
                
                if self.on_features_updated:
                    self.on_features_updated(features)
                
                logger.debug(f"Context updated: {new_context.app_name} ({new_context.category.value})")
                
        except Exception as e:
            logger.error(f"Context update failed: {e}")
    
    async def _get_android_context(self) -> Optional[AppContext]:
        """Get current context from Android system"""
        try:
            if not self.activity_manager:
                return None
            
            # Get running tasks (requires permission)
            running_tasks = self.activity_manager.getRunningTasks(1)
            if not running_tasks or len(running_tasks) == 0:
                return None
            
            # Get foreground task
            task = running_tasks[0]
            component_name = task.topActivity
            package_name = component_name.getPackageName()
            activity_name = component_name.getClassName()
            
            # Get app name
            package_manager = autoclass('org.kivy.android.PythonActivity').mActivity.getPackageManager()
            app_info = package_manager.getApplicationInfo(package_name, 0)
            app_name = package_manager.getApplicationLabel(app_info).toString()
            
            # Determine category
            category = self.app_categories.get(package_name, AppCategory.UNKNOWN)
            
            return AppContext(
                package_name=package_name,
                app_name=app_name,
                category=category,
                activity_name=activity_name,
                is_foreground=True,
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"Failed to get Android context: {e}")
            return None
    
    async def _get_simulated_context(self) -> AppContext:
        """Get simulated context for testing"""
        # Simulate different apps for testing
        simulated_apps = [
            ("com.whatsapp", "WhatsApp", AppCategory.COMMUNICATION),
            ("com.google.android.gm", "Gmail", AppCategory.COMMUNICATION),
            ("com.google.android.apps.docs.editors.docs", "Google Docs", AppCategory.PRODUCTIVITY),
            ("com.android.chrome", "Chrome", AppCategory.BROWSER),
            ("com.spotify.music", "Spotify", AppCategory.ENTERTAINMENT)
        ]
        
        # Cycle through apps every 30 seconds
        app_index = int(time.time() / 30) % len(simulated_apps)
        package_name, app_name, category = simulated_apps[app_index]
        
        return AppContext(
            package_name=package_name,
            app_name=app_name,
            category=category,
            activity_name=f"{package_name}.MainActivity",
            is_foreground=True,
            timestamp=time.time()
        )
    
    def _context_changed(self, new_context: AppContext) -> bool:
        """Check if context has significantly changed"""
        if not self.current_context:
            return True
        
        return (self.current_context.package_name != new_context.package_name or
                self.current_context.activity_name != new_context.activity_name)
    
    def _get_contextual_features(self, context: AppContext) -> ContextualFeatures:
        """Get contextual features for current app context"""
        return self.context_features.get(context.category, self.context_features[AppCategory.UNKNOWN])
    
    def _add_to_history(self, context: AppContext) -> None:
        """Add context to history"""
        self.context_history.append(context)
        
        # Maintain history size limit
        if len(self.context_history) > self.max_history_size:
            self.context_history.pop(0)
    
    def get_current_features(self) -> Optional[ContextualFeatures]:
        """Get features for current context"""
        if not self.current_context:
            return None
        
        return self._get_contextual_features(self.current_context)
    
    def get_gesture_mapping(self, gesture_direction: str) -> Optional[str]:
        """Get action mapping for gesture in current context"""
        features = self.get_current_features()
        if not features:
            return None
        
        return features.gesture_mappings.get(gesture_direction)
    
    def stop_monitoring(self) -> None:
        """Stop context monitoring"""
        self.monitoring_active = False
        logger.info("Context monitoring stopped")
