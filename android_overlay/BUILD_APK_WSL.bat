@echo off
echo 🚀 Universal Soul AI - WSL APK Builder
echo =====================================
echo.

REM Check if WSL is installed
wsl --version >nul 2>&1
if errorlevel 1 (
    echo ❌ WSL not detected. Please install WSL first:
    echo.
    echo 1. Right-click Start button
    echo 2. Select "Windows PowerShell (Admin)"
    echo 3. Run: wsl --install
    echo 4. Restart computer
    echo 5. Run this script again
    echo.
    pause
    exit /b 1
)

echo ✅ WSL detected - proceeding with APK build...
echo.

REM Install Python build dependencies in WSL
echo 📦 Installing system dependencies...
wsl sudo apt update
wsl sudo apt install -y python3 python3-pip python3-venv git
wsl sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
wsl sudo apt install -y openjdk-17-jdk
wsl sudo apt install -y autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5
wsl sudo apt install -y zip unzip

REM Install Android SDK dependencies
echo 📱 Installing Android build dependencies...
wsl sudo apt install -y wget curl

REM Create virtual environment
echo 🐍 Setting up Python environment...
wsl rm -rf /tmp/soul_build_env
wsl python3 -m venv /tmp/soul_build_env
wsl /tmp/soul_build_env/bin/pip install --upgrade pip setuptools wheel

REM Install requirements
echo 📋 Installing Python requirements...
wsl /tmp/soul_build_env/bin/pip install kivy kivymd buildozer cython plyer pyjnius
wsl /tmp/soul_build_env/bin/pip install numpy pillow requests aiohttp asyncio-mqtt

REM Run the build
echo 🔨 Building APK...
wsl cd "/mnt/c/Users/Richard.Downing/Documents/augment-projects/Soul/android_overlay" && /tmp/soul_build_env/bin/python build_apk.py

echo.
echo 🎉 APK build process completed!
echo 📱 Check your Desktop for UniversalSoulAI.apk
echo.
echo 🔧 Next steps:
echo   1. Connect Android device via USB
echo   2. Enable Developer Options and USB Debugging
echo   3. Install APK: adb install -r UniversalSoulAI.apk
echo   4. Grant overlay permissions when prompted
echo   5. Test the overlay system
echo.
echo 📋 Troubleshooting:
echo   - If build fails, check WSL Ubuntu installation
echo   - Ensure Java 17 is installed: wsl java -version
echo   - Check buildozer logs in .buildozer directory
echo   - For permission issues: Grant overlay permission manually
echo.
pause
