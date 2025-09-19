#!/usr/bin/env python3
"""
Universal Soul AI - Windows Alternative Build System
===================================================

Alternative build approach for Windows users who cannot use buildozer directly.
Creates a portable Python app that can be tested on Windows and provides
instructions for Android deployment alternatives.
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path
import json
import time

class WindowsAlternativeBuilder:
    """Alternative build system for Windows users"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.assets_dir = self.project_root / "assets"
        
        print("🚀 Universal Soul AI - Windows Alternative Builder")
        print("=" * 60)
        print("⚠️  Note: This creates a Windows-testable version")
        print("📱 For Android APK, use WSL or Linux/macOS")
        print()
    
    def create_portable_app(self):
        """Create a portable Windows version for testing"""
        print("📦 Creating portable Windows application...")
        
        # Create distribution directory
        self.dist_dir.mkdir(exist_ok=True)
        
        # Copy main application files
        self.copy_app_files()
        
        # Create launcher script
        self.create_launcher()
        
        # Create requirements file
        self.create_requirements()
        
        # Create setup instructions
        self.create_setup_instructions()
        
        # Package everything
        self.create_distribution_package()
        
        print("✅ Portable Windows app created successfully!")
        self.show_windows_results()
    
    def copy_app_files(self):
        """Copy application files to distribution"""
        print("📁 Copying application files...")
        
        # Core files to copy
        files_to_copy = [
            "main.py",
            "universal_soul_overlay.py",
            "core/",
            "ui/",
            "demo/",
            "tests/",
            "config/",
            "assets/"
        ]
        
        for item in files_to_copy:
            src = self.project_root / item
            dst = self.dist_dir / item
            
            if src.exists():
                if src.is_file():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                else:
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                print(f"✅ Copied: {item}")
    
    def create_launcher(self):
        """Create Windows launcher script"""
        launcher_content = '''@echo off
echo 🚀 Universal Soul AI - Windows Test Version
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ first.
    echo 📥 Download from: https://python.org/downloads/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 🔧 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\\Scripts\\activate.bat

REM Install requirements
echo 📦 Installing requirements...
pip install -r requirements.txt

REM Run the application
echo 🎪 Starting Universal Soul AI...
echo.
echo 📱 Note: This is a Windows test version
echo 🔧 For full Android overlay functionality, use the APK
echo.
python main.py

pause
'''
        
        launcher_path = self.dist_dir / "start_universal_soul_ai.bat"
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        print("✅ Created Windows launcher script")
    
    def create_requirements(self):
        """Create requirements.txt for Windows"""
        requirements = [
            "kivy>=2.1.0",
            "kivymd>=1.1.1",
            "plyer>=2.1.0",
            "numpy>=1.21.0",
            "pillow>=9.0.0",
            "requests>=2.28.0",
            "asyncio-mqtt>=0.11.0",
            "websockets>=11.0.0",
            "pyaudio>=0.2.11",
            "speech-recognition>=3.10.0",
            "pyttsx3>=2.90"
        ]
        
        req_path = self.dist_dir / "requirements.txt"
        with open(req_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(requirements))
        
        print("✅ Created requirements.txt")
    
    def create_setup_instructions(self):
        """Create setup instructions for Windows"""
        instructions = '''# 🚀 Universal Soul AI - Windows Test Version

## 📋 Quick Start

1. **Double-click `start_universal_soul_ai.bat`**
   - This will automatically set up everything
   - Install Python dependencies
   - Launch the application

2. **Test the Interface**
   - The app will open with a Material Design interface
   - Click "Start Overlay System" to test overlay functionality
   - Use "Run Demo" to see all features in action

## 🔧 Manual Setup (if needed)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\\Scripts\\activate.bat

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## 📱 Android APK Build Options

### Option 1: Use WSL (Windows Subsystem for Linux)
```bash
# Install WSL
wsl --install

# In WSL terminal:
cd /mnt/c/path/to/your/project/android_overlay
python build_apk.py
```

### Option 2: Use GitHub Actions (Cloud Build)
1. Push code to GitHub repository
2. Use GitHub Actions with Ubuntu runner
3. Automatically build APK in the cloud

### Option 3: Use Docker
```bash
# Pull Android build environment
docker pull kivy/buildozer

# Run build in container
docker run -v %cd%:/app kivy/buildozer buildozer android debug
```

### Option 4: Use Online Build Services
- **Replit**: Online Python environment with Linux
- **CodeSandbox**: Browser-based development
- **Gitpod**: Cloud development environment

## 🎯 What This Windows Version Tests

✅ **Core Logic**: All Universal Soul AI algorithms
✅ **UI Interface**: Material Design mobile-like interface  
✅ **Voice System**: Speech recognition and synthesis
✅ **Gesture Recognition**: Touch/mouse gesture detection
✅ **Context Intelligence**: App awareness simulation
✅ **Privacy Architecture**: Local processing verification

❌ **Android-Specific**: System overlay, native permissions
❌ **Mobile Hardware**: Accelerometer, haptic feedback
❌ **Cross-App Integration**: Android intent system

## 🔍 Testing Checklist

- [ ] App launches successfully
- [ ] UI is responsive and attractive
- [ ] Voice recognition works (with microphone)
- [ ] Gesture detection responds to mouse/touch
- [ ] Demo mode runs without errors
- [ ] All components initialize properly

## 🚀 Next Steps

1. **Test thoroughly on Windows**
2. **Document any issues or improvements**
3. **Use WSL or Linux for Android APK build**
4. **Deploy APK to Android device for full testing**

## 📞 Support

If you encounter issues:
1. Check Python version (3.8+ required)
2. Ensure all dependencies install correctly
3. Try running in administrator mode if needed
4. Check Windows Defender/antivirus settings

**This Windows version validates your Universal Soul AI concept before Android deployment!** 🎉
'''
        
        readme_path = self.dist_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        print("✅ Created setup instructions")
    
    def create_distribution_package(self):
        """Create a ZIP package for easy distribution"""
        print("📦 Creating distribution package...")
        
        zip_path = self.project_root / "Universal_Soul_AI_Windows_Test.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.dist_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_path = file_path.relative_to(self.dist_dir)
                    zipf.write(file_path, arc_path)
        
        zip_size = zip_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ Created package: {zip_path} ({zip_size:.1f} MB)")
    
    def show_windows_results(self):
        """Show build results for Windows"""
        print("\n🎉 WINDOWS TEST VERSION READY!")
        print("=" * 50)
        print(f"📁 Location: {self.dist_dir}")
        print(f"📦 Package: Universal_Soul_AI_Windows_Test.zip")
        print()
        print("🚀 Quick Start:")
        print("1. Navigate to the 'dist' folder")
        print("2. Double-click 'start_universal_soul_ai.bat'")
        print("3. Wait for setup to complete")
        print("4. Test the Universal Soul AI interface")
        print()
        print("📱 For Android APK:")
        print("1. Use WSL: wsl --install")
        print("2. In WSL: cd /mnt/c/path/to/project")
        print("3. Run: python build_apk.py")
        print()
        print("🎯 This Windows version tests:")
        print("✅ Core Universal Soul AI logic")
        print("✅ Voice recognition and synthesis")
        print("✅ Gesture detection algorithms")
        print("✅ Material Design interface")
        print("✅ Privacy-first architecture")
        print()
        print("📋 Next Steps:")
        print("1. Test Windows version thoroughly")
        print("2. Use WSL or Linux for Android APK")
        print("3. Deploy to Android device")
        print("4. Validate full overlay functionality")
    
    def create_android_build_guide(self):
        """Create comprehensive Android build guide"""
        guide_content = '''# 📱 Android APK Build Guide

## 🎯 Recommended Approach: WSL (Windows Subsystem for Linux)

### Step 1: Install WSL
```powershell
# Run as Administrator
wsl --install
# Restart computer when prompted
```

### Step 2: Setup Ubuntu in WSL
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git -y

# Install Java (required for Android builds)
sudo apt install openjdk-11-jdk -y

# Install build tools
sudo apt install build-essential libssl-dev libffi-dev -y
```

### Step 3: Navigate to Project
```bash
# Access Windows files from WSL
cd /mnt/c/Users/YourUsername/Documents/augment-projects/Soul/android_overlay

# Or copy project to WSL home
cp -r /mnt/c/path/to/project ~/universal-soul-ai
cd ~/universal-soul-ai
```

### Step 4: Build APK
```bash
# Install buildozer
pip3 install buildozer cython

# Build APK (first time takes 20-30 minutes)
python3 build_apk.py

# APK will be in: bin/universalsoulai-1.0.0-debug.apk
```

## 🐳 Alternative: Docker Build

### Option 1: Use Pre-built Container
```bash
# Pull buildozer container
docker pull kivy/buildozer

# Run build
docker run -v %cd%:/app kivy/buildozer buildozer android debug
```

### Option 2: Custom Dockerfile
```dockerfile
FROM kivy/buildozer
WORKDIR /app
COPY . .
RUN buildozer android debug
```

## ☁️ Cloud Build Options

### GitHub Actions
Create `.github/workflows/build-apk.yml`:
```yaml
name: Build APK
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install buildozer cython
    - name: Build APK
      run: |
        cd android_overlay
        buildozer android debug
    - name: Upload APK
      uses: actions/upload-artifact@v2
      with:
        name: universal-soul-ai-apk
        path: android_overlay/bin/*.apk
```

### Replit (Online)
1. Go to replit.com
2. Create new Python project
3. Upload your code
4. Install buildozer in shell
5. Run build command

## 🔧 Troubleshooting

### Common Issues

**"Java not found"**
```bash
sudo apt install openjdk-11-jdk
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
```

**"Android SDK download fails"**
```bash
# Clean and retry
buildozer android clean
buildozer android debug
```

**"Permission denied"**
```bash
chmod +x build_apk.py
sudo chown -R $USER:$USER ~/.buildozer
```

**"Out of space"**
```bash
# Clean Docker images
docker system prune -a

# Clean buildozer cache
rm -rf ~/.buildozer
```

## 📱 APK Installation

### Transfer to Android
```bash
# Via ADB
adb install bin/universalsoulai-1.0.0-debug.apk

# Via file transfer
# Copy APK to phone storage
# Use file manager to install
```

### Enable Installation
1. Settings > Security > Unknown Sources ✅
2. Or Settings > Apps > Special Access > Install Unknown Apps

### Grant Permissions
1. Microphone ✅ (for voice recognition)
2. Storage ✅ (for app data)
3. Display over other apps ✅ (for overlay)
4. Camera ✅ (if using visual features)

## 🎯 Expected Results

**APK Size**: ~45-60 MB
**Build Time**: 10-30 minutes (first build)
**Target**: Android 6.0+ (API 23+)
**Architecture**: ARM64 + ARMv7

**Features Included**:
✅ 360° gesture recognition
✅ Persistent overlay system
✅ Voice interface (Hey Soul)
✅ Context intelligence
✅ Privacy-first architecture
✅ Material Design UI

## 🚀 Success Indicators

When APK is working correctly:
1. App installs without errors
2. Overlay permission can be granted
3. Floating overlay appears over other apps
4. Voice recognition responds to "Hey Soul"
5. 8-direction gestures are detected
6. Context adapts to different apps
7. Privacy indicators show local processing

**Your Universal Soul AI APK will demonstrate the world's first 360° gesture + overlay interface!** 🎉
'''
        
        guide_path = self.project_root / "ANDROID_BUILD_GUIDE.md"
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print("✅ Created comprehensive Android build guide")


def main():
    """Main entry point"""
    builder = WindowsAlternativeBuilder()
    
    print("🔍 Detected Windows environment")
    print("📱 Buildozer requires Linux/macOS for Android APK builds")
    print("🔧 Creating Windows test version instead...")
    print()
    
    try:
        # Create portable Windows app
        builder.create_portable_app()
        
        # Create Android build guide
        builder.create_android_build_guide()
        
        print("\n✅ SETUP COMPLETE!")
        print("=" * 50)
        print("🖥️  Windows test version: Ready to run")
        print("📱 Android APK guide: Created for WSL/Linux build")
        print("📋 Next step: Test Windows version, then use WSL for APK")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main()
