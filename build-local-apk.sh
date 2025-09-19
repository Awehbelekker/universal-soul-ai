#!/bin/bash
# Universal Soul AI - Local APK Build Script
# Run this on Ubuntu/WSL if GitHub Actions is delayed

set -e

echo "🚀 Universal Soul AI - Local APK Build"
echo "====================================="

# Check if we're in the right directory
if [ ! -f "android_overlay/main.py" ]; then
    echo "❌ Error: Please run this script from the repository root directory"
    echo "   Expected: android_overlay/main.py should exist"
    exit 1
fi

# Function to check command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        return 1
    fi
}

echo "🔍 Checking prerequisites..."

# Check Python
check_command python3
python_version=$(python3 --version)
echo "✅ Python: $python_version"

# Check Java
check_command java
java_version=$(java -version 2>&1 | head -n 1)
echo "✅ Java: $java_version"

# Install system dependencies if needed
echo "📦 Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y python3-pip python3-venv git zip unzip openjdk-8-jdk wget curl

# Set up Android SDK if not exists
if [ ! -d "$HOME/android-sdk" ]; then
    echo "📱 Setting up Android SDK..."
    mkdir -p $HOME/android-sdk
    cd $HOME/android-sdk
    
    # Download command line tools
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip
    unzip -q commandlinetools-linux-8512546_latest.zip
    mkdir -p cmdline-tools/latest
    mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true
    
    # Set environment
    export ANDROID_HOME=$HOME/android-sdk
    export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
    
    cd - # Return to original directory
else
    echo "✅ Android SDK already exists at $HOME/android-sdk"
    export ANDROID_HOME=$HOME/android-sdk
    export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
fi

# Go to build directory
cd android_overlay

echo "🏗️ Setting up Python virtual environment..."
# Create virtual environment
python3 -m venv buildenv
source buildenv/bin/activate

echo "📥 Installing Buildozer..."
pip install --upgrade pip
pip install buildozer==1.5.0 cython==0.29.33

echo "🔧 Building APK..."
echo "   This may take 10-20 minutes for first build..."
buildozer android debug --verbose

echo "📋 Checking build results..."
if find . -name "*.apk" -type f | grep -q .; then
    echo "🎉 SUCCESS! APK built successfully:"
    find . -name "*.apk" -type f -exec ls -lh {} \;
    echo ""
    echo "📦 APK locations:"
    find . -name "*.apk" -type f
else
    echo "❌ No APK files found. Check the build logs above for errors."
    exit 1
fi

echo ""
echo "✅ Build complete! Your Universal Soul AI APK is ready."