#!/usr/bin/env python3
"""
Universal Soul AI Android Overlay - Main Entry Point
===================================================

Launch script for the complete Android overlay system.
Provides command-line interface for configuration and execution.

Usage:
    python run_overlay.py                    # Run with default settings
    python run_overlay.py --demo             # Run demonstration mode
    python run_overlay.py --test             # Run test suite
    python run_overlay.py --config custom    # Use custom configuration
"""

import asyncio
import argparse
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import overlay components
from android_overlay.universal_soul_overlay import UniversalSoulOverlay, OverlayConfig
from android_overlay.demo.overlay_demo import OverlayDemoRunner
from android_overlay.tests.overlay_test_suite import run_all_tests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('overlay.log')
    ]
)
logger = logging.getLogger(__name__)


class OverlayLauncher:
    """
    Main launcher for Universal Soul AI overlay system
    
    Handles configuration, initialization, and execution of the overlay
    with support for different modes (production, demo, testing).
    """
    
    def __init__(self):
        self.overlay: Optional[UniversalSoulOverlay] = None
        self.config: Optional[OverlayConfig] = None
        self.mode = "production"
    
    def load_config(self, config_name: str = "default") -> OverlayConfig:
        """Load configuration from file or create default"""
        config_file = Path(__file__).parent / "config" / f"{config_name}.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                return OverlayConfig(**config_data)
                
            except Exception as e:
                logger.warning(f"Failed to load config {config_name}: {e}")
                logger.info("Using default configuration")
        
        # Return default configuration
        return self._get_default_config()
    
    def _get_default_config(self) -> OverlayConfig:
        """Get default overlay configuration"""
        return OverlayConfig(
            # Overlay appearance
            overlay_size=120,
            overlay_alpha=0.9,
            overlay_color="#1976D2",
            
            # Voice settings
            continuous_listening=True,
            wake_word="Hey Soul",
            voice_timeout=5.0,
            
            # Gesture settings
            gesture_sensitivity=0.8,
            gesture_timeout=2.0,
            haptic_feedback=True,
            
            # Privacy settings
            local_processing_only=True,
            show_privacy_indicators=True,
            data_retention="session-only",
            
            # Performance settings
            battery_optimization=True,
            low_power_mode_threshold=20.0
        )
    
    def save_config(self, config: OverlayConfig, config_name: str = "default") -> None:
        """Save configuration to file"""
        config_dir = Path(__file__).parent / "config"
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / f"{config_name}.json"
        
        try:
            config_dict = {
                "overlay_size": config.overlay_size,
                "overlay_alpha": config.overlay_alpha,
                "overlay_color": config.overlay_color,
                "continuous_listening": config.continuous_listening,
                "wake_word": config.wake_word,
                "voice_timeout": config.voice_timeout,
                "gesture_sensitivity": config.gesture_sensitivity,
                "gesture_timeout": config.gesture_timeout,
                "haptic_feedback": config.haptic_feedback,
                "local_processing_only": config.local_processing_only,
                "show_privacy_indicators": config.show_privacy_indicators,
                "data_retention": config.data_retention,
                "battery_optimization": config.battery_optimization,
                "low_power_mode_threshold": config.low_power_mode_threshold
            }
            
            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Configuration saved to {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    async def run_production_mode(self, config_name: str = "default") -> None:
        """Run overlay in production mode"""
        print("🚀 Universal Soul AI - Android Overlay System")
        print("=" * 60)
        print("🎯 Starting in Production Mode")
        print("🔒 Privacy-First • 🧠 AI-Powered • 📱 Cross-Platform")
        print()
        
        try:
            # Load configuration
            self.config = self.load_config(config_name)
            logger.info(f"Loaded configuration: {config_name}")
            
            # Create overlay system
            self.overlay = UniversalSoulOverlay(self.config)
            
            # Initialize system
            print("🔧 Initializing overlay system...")
            success = await self.overlay.initialize()
            
            if not success:
                raise Exception("Failed to initialize overlay system")
            
            print("✅ Overlay system initialized successfully!")
            
            # Start overlay
            print("🎪 Starting overlay interface...")
            success = await self.overlay.start()
            
            if not success:
                raise Exception("Failed to start overlay")
            
            print("✅ Universal Soul AI Overlay is now active!")
            print()
            print("📱 Overlay Controls:")
            print("   👆 Swipe in 8 directions for different actions")
            print("   🎙️ Tap overlay or say 'Hey Soul' for voice commands")
            print("   🔒 All processing happens locally on your device")
            print()
            print("⌨️  Press Ctrl+C to stop the overlay")
            
            # Keep running until interrupted
            try:
                while True:
                    await asyncio.sleep(1)
                    
                    # Check if overlay is still running
                    if not self.overlay.is_running:
                        break
            
            except KeyboardInterrupt:
                print("\n🛑 Stopping overlay...")
            
        except Exception as e:
            logger.error(f"Production mode failed: {e}")
            print(f"❌ Error: {e}")
        
        finally:
            # Cleanup
            if self.overlay:
                await self.overlay.stop()
                print("✅ Overlay stopped successfully")
    
    async def run_demo_mode(self) -> None:
        """Run overlay in demonstration mode"""
        print("🎪 Universal Soul AI - Overlay Demonstration Mode")
        print("=" * 60)
        
        try:
            demo_runner = OverlayDemoRunner()
            await demo_runner.run_complete_demo()
            
        except Exception as e:
            logger.error(f"Demo mode failed: {e}")
            print(f"❌ Demo failed: {e}")
    
    async def run_test_mode(self) -> None:
        """Run overlay test suite"""
        print("🧪 Universal Soul AI - Test Suite Mode")
        print("=" * 60)
        
        try:
            success = await run_all_tests()
            
            if success:
                print("\n🎉 All tests passed! Overlay system is ready for deployment.")
            else:
                print("\n❌ Some tests failed. Please check the output above.")
                sys.exit(1)
            
        except Exception as e:
            logger.error(f"Test mode failed: {e}")
            print(f"❌ Test suite failed: {e}")
            sys.exit(1)
    
    def interactive_config(self) -> OverlayConfig:
        """Interactive configuration setup"""
        print("⚙️  Interactive Configuration Setup")
        print("-" * 40)
        
        config = self._get_default_config()
        
        # Overlay settings
        print("\n📱 Overlay Settings:")
        size = input(f"Overlay size in dp (default: {config.overlay_size}): ").strip()
        if size:
            config.overlay_size = int(size)
        
        # Voice settings
        print("\n🎙️ Voice Settings:")
        continuous = input(f"Continuous listening (default: {config.continuous_listening}): ").strip().lower()
        if continuous in ['false', 'no', 'n', '0']:
            config.continuous_listening = False
        
        wake_word = input(f"Wake word (default: '{config.wake_word}'): ").strip()
        if wake_word:
            config.wake_word = wake_word
        
        # Gesture settings
        print("\n👆 Gesture Settings:")
        sensitivity = input(f"Gesture sensitivity 0.0-1.0 (default: {config.gesture_sensitivity}): ").strip()
        if sensitivity:
            config.gesture_sensitivity = float(sensitivity)
        
        haptic = input(f"Haptic feedback (default: {config.haptic_feedback}): ").strip().lower()
        if haptic in ['false', 'no', 'n', '0']:
            config.haptic_feedback = False
        
        # Privacy settings
        print("\n🔒 Privacy Settings:")
        local_only = input(f"Local processing only (default: {config.local_processing_only}): ").strip().lower()
        if local_only in ['false', 'no', 'n', '0']:
            config.local_processing_only = False
        
        # Save configuration
        save_config = input("\n💾 Save this configuration? (y/n): ").strip().lower()
        if save_config in ['yes', 'y', '1']:
            config_name = input("Configuration name (default: 'custom'): ").strip() or 'custom'
            self.save_config(config, config_name)
        
        return config
    
    def print_help(self) -> None:
        """Print help information"""
        print("🚀 Universal Soul AI - Android Overlay System")
        print("=" * 60)
        print()
        print("📋 Available Commands:")
        print("   python run_overlay.py                    # Run in production mode")
        print("   python run_overlay.py --demo             # Run demonstration")
        print("   python run_overlay.py --test             # Run test suite")
        print("   python run_overlay.py --config custom    # Use custom config")
        print("   python run_overlay.py --interactive      # Interactive setup")
        print("   python run_overlay.py --help             # Show this help")
        print()
        print("🔧 Configuration:")
        print("   Configurations are stored in config/ directory")
        print("   Default configuration is automatically created")
        print("   Use --interactive for guided setup")
        print()
        print("📱 System Requirements:")
        print("   - Android 6.0+ (API level 23+)")
        print("   - System alert window permission")
        print("   - Microphone permission (for voice)")
        print("   - 50MB+ available storage")
        print()
        print("🔒 Privacy:")
        print("   - 100% local processing by default")
        print("   - No data transmitted to cloud")
        print("   - User-controlled encryption")
        print("   - Session-only data retention")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Universal Soul AI Android Overlay System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--demo', action='store_true',
                       help='Run in demonstration mode')
    parser.add_argument('--test', action='store_true',
                       help='Run test suite')
    parser.add_argument('--config', type=str, default='default',
                       help='Configuration name to use')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive configuration setup')
    parser.add_argument('--help-extended', action='store_true',
                       help='Show extended help information')
    
    args = parser.parse_args()
    
    launcher = OverlayLauncher()
    
    # Handle help
    if args.help_extended:
        launcher.print_help()
        return
    
    # Handle different modes
    try:
        if args.test:
            await launcher.run_test_mode()
        elif args.demo:
            await launcher.run_demo_mode()
        elif args.interactive:
            config = launcher.interactive_config()
            launcher.overlay = UniversalSoulOverlay(config)
            await launcher.run_production_mode()
        else:
            await launcher.run_production_mode(args.config)
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
