#!/usr/bin/env python3
"""
Universal Soul AI - APK Build Script
===================================

Automated script to build the Universal Soul AI Android APK.
Handles dependencies, asset generation, and buildozer compilation.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
import time

# Build configuration
BUILD_CONFIG = {
    "app_name": "Universal Soul AI",
    "package_name": "com.universalsoul.ai",
    "version": "1.0.0",
    "build_mode": "debug",  # or "release"
    "target_arch": "arm64-v8a,armeabi-v7a"
}

class APKBuilder:
    """Automated APK builder for Universal Soul AI"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / ".buildozer"
        self.bin_dir = self.project_root / "bin"
        self.assets_dir = self.project_root / "assets"
        
        print("🚀 Universal Soul AI - APK Builder")
        print("=" * 50)
    
    def check_prerequisites(self) -> bool:
        """Check if all build prerequisites are met"""
        print("🔍 Checking build prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
        
        # Check if buildozer is installed
        try:
            result = subprocess.run(['buildozer', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Buildozer found: {result.stdout.strip()}")
            else:
                print("❌ Buildozer not found. Installing...")
                self.install_buildozer()
        except FileNotFoundError:
            print("❌ Buildozer not found. Installing...")
            self.install_buildozer()
        
        # Check Android SDK/NDK (buildozer will handle this)
        print("✅ Prerequisites check completed")
        return True
    
    def install_buildozer(self):
        """Install buildozer and dependencies"""
        print("📦 Installing buildozer...")
        
        try:
            # Install buildozer
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "buildozer", "cython", "kivy", "kivymd"
            ], check=True)
            
            print("✅ Buildozer installed successfully")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install buildozer: {e}")
            sys.exit(1)
    
    def prepare_assets(self):
        """Prepare app assets (icons, splash screens, etc.)"""
        print("🎨 Preparing app assets...")
        
        # Create assets directory
        self.assets_dir.mkdir(exist_ok=True)
        
        # Generate app icon (placeholder)
        self.generate_app_icon()
        
        # Generate splash screen
        self.generate_splash_screen()
        
        print("✅ Assets prepared")
    
    def generate_app_icon(self):
        """Generate app icon programmatically"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create 512x512 icon
            size = 512
            icon = Image.new('RGBA', (size, size), (25, 118, 210, 255))  # Universal Soul AI blue
            draw = ImageDraw.Draw(icon)
            
            # Draw simple icon design
            # Outer circle
            margin = 50
            draw.ellipse([margin, margin, size-margin, size-margin], 
                        fill=(255, 255, 255, 255), outline=(25, 118, 210, 255), width=10)
            
            # Inner design - brain/soul symbol
            center = size // 2
            # Draw stylized "S" for Soul
            try:
                font = ImageFont.truetype("arial.ttf", 200)
            except:
                font = ImageFont.load_default()
            
            # Draw "S" in center
            text = "🧠"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            draw.text((x, y), text, fill=(25, 118, 210, 255), font=font)
            
            # Save icon
            icon_path = self.assets_dir / "icon.png"
            icon.save(icon_path, "PNG")
            print(f"✅ Generated app icon: {icon_path}")
            
        except ImportError:
            print("⚠️ PIL not available, creating placeholder icon")
            # Create placeholder
            icon_path = self.assets_dir / "icon.png"
            with open(icon_path, 'w') as f:
                f.write("# Placeholder icon - replace with actual PNG")
    
    def generate_splash_screen(self):
        """Generate splash screen"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create 1080x1920 splash screen (portrait)
            width, height = 1080, 1920
            splash = Image.new('RGB', (width, height), (25, 118, 210))  # Universal Soul AI blue
            draw = ImageDraw.Draw(splash)
            
            # Draw app name
            try:
                title_font = ImageFont.truetype("arial.ttf", 80)
                subtitle_font = ImageFont.truetype("arial.ttf", 40)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
            
            # Title
            title = "Universal Soul AI"
            bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = bbox[2] - bbox[0]
            x = (width - title_width) // 2
            y = height // 2 - 100
            draw.text((x, y), title, fill=(255, 255, 255), font=title_font)
            
            # Subtitle
            subtitle = "360° Gesture + Overlay Interface"
            bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            subtitle_width = bbox[2] - bbox[0]
            x = (width - subtitle_width) // 2
            y = height // 2 + 50
            draw.text((x, y), subtitle, fill=(255, 255, 255, 200), font=subtitle_font)
            
            # Save splash screen
            splash_path = self.assets_dir / "presplash.png"
            splash.save(splash_path, "PNG")
            print(f"✅ Generated splash screen: {splash_path}")
            
        except ImportError:
            print("⚠️ PIL not available, creating placeholder splash")
            # Create placeholder
            splash_path = self.assets_dir / "presplash.png"
            with open(splash_path, 'w') as f:
                f.write("# Placeholder splash - replace with actual PNG")
    
    def clean_build(self):
        """Clean previous build artifacts"""
        print("🧹 Cleaning previous build...")
        
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            print("✅ Cleaned .buildozer directory")
        
        if self.bin_dir.exists():
            shutil.rmtree(self.bin_dir)
            print("✅ Cleaned bin directory")
    
    def build_apk(self):
        """Build the APK using buildozer"""
        print("🔨 Building APK...")
        print("⏳ This may take 10-30 minutes for first build...")
        
        start_time = time.time()
        
        try:
            # Change to project directory
            os.chdir(self.project_root)
            
            # Build command
            build_cmd = ["buildozer", "android", BUILD_CONFIG["build_mode"]]
            
            print(f"🔧 Running: {' '.join(build_cmd)}")
            
            # Run buildozer
            process = subprocess.Popen(
                build_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output
            for line in process.stdout:
                print(line.rstrip())
            
            process.wait()
            
            if process.returncode == 0:
                build_time = time.time() - start_time
                print(f"✅ APK built successfully in {build_time:.1f} seconds!")
                self.show_build_results()
            else:
                print(f"❌ Build failed with return code {process.returncode}")
                return False
                
        except Exception as e:
            print(f"❌ Build error: {e}")
            return False
        
        return True
    
    def show_build_results(self):
        """Show build results and APK location"""
        print("\n🎉 BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
        # Find APK file
        apk_files = list(self.bin_dir.glob("*.apk"))
        
        if apk_files:
            apk_path = apk_files[0]
            apk_size = apk_path.stat().st_size / (1024 * 1024)  # MB
            
            print(f"📱 APK Location: {apk_path}")
            print(f"📊 APK Size: {apk_size:.1f} MB")
            print(f"📦 Package: {BUILD_CONFIG['package_name']}")
            print(f"🔢 Version: {BUILD_CONFIG['version']}")
            print()
            print("📋 Installation Instructions:")
            print("1. Transfer APK to your Android device")
            print("2. Enable 'Install from Unknown Sources' in Settings")
            print("3. Tap the APK file to install")
            print("4. Grant all requested permissions")
            print("5. Launch 'Universal Soul AI' app")
            print()
            print("🎯 Testing Instructions:")
            print("1. Tap 'Request Permissions' first")
            print("2. Grant overlay permission in system settings")
            print("3. Tap 'Start Overlay System'")
            print("4. Use 360° gestures and voice commands")
            print()
            print("🔧 Troubleshooting:")
            print("- If overlay doesn't appear, check overlay permissions")
            print("- If voice doesn't work, check microphone permissions")
            print("- For gesture issues, try adjusting sensitivity in settings")
            
        else:
            print("⚠️ APK file not found in bin directory")
    
    def install_dependencies(self):
        """Install Python dependencies for the build"""
        print("📦 Installing Python dependencies...")
        
        requirements = [
            "kivy>=2.1.0",
            "kivymd>=1.1.1",
            "plyer>=2.1.0",
            "pyjnius>=1.4.2",
            "numpy>=1.21.0",
            "pillow>=9.0.0",
            "requests>=2.28.0"
        ]
        
        for req in requirements:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", req], 
                             check=True, capture_output=True)
                print(f"✅ Installed: {req}")
            except subprocess.CalledProcessError:
                print(f"⚠️ Failed to install: {req}")
    
    def run_full_build(self):
        """Run the complete build process"""
        print("🚀 Starting full APK build process...")
        print()
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites check failed")
            return False
        
        # Step 2: Install dependencies
        self.install_dependencies()
        
        # Step 3: Prepare assets
        self.prepare_assets()
        
        # Step 4: Clean previous build
        self.clean_build()
        
        # Step 5: Build APK
        success = self.build_apk()
        
        if success:
            print("\n🎉 UNIVERSAL SOUL AI APK BUILD COMPLETED!")
            print("Your APK is ready for testing on Android devices.")
        else:
            print("\n❌ Build failed. Check the output above for errors.")
        
        return success


def main():
    """Main entry point for APK builder"""
    builder = APKBuilder()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "clean":
            builder.clean_build()
        elif command == "assets":
            builder.prepare_assets()
        elif command == "deps":
            builder.install_dependencies()
        elif command == "build":
            builder.build_apk()
        elif command == "full":
            builder.run_full_build()
        else:
            print("Usage: python build_apk.py [clean|assets|deps|build|full]")
    else:
        # Default: run full build
        builder.run_full_build()


if __name__ == "__main__":
    main()
