#!/bin/bash
# Universal Soul AI - WSL Setup and APK Build Script
# ==================================================
# Run this script in WSL after installation to build your APK

echo "🚀 Universal Soul AI - WSL APK Builder"
echo "======================================"
echo "🎯 Building the world's first 360° gesture + overlay AI interface"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}🔧 $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in WSL
if ! grep -q Microsoft /proc/version; then
    print_error "This script must be run in WSL (Windows Subsystem for Linux)"
    exit 1
fi

print_info "Detected WSL environment - proceeding with setup..."

# Update system
print_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_status "System updated"

# Install Python and dependencies
print_info "Installing Python and build dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    openjdk-11-jdk \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    unzip \
    zip

print_status "Dependencies installed"

# Set JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
echo 'export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64' >> ~/.bashrc

print_status "Java environment configured"

# Install Python packages
print_info "Installing Python packages for Android development..."
pip3 install --user --upgrade pip
pip3 install --user \
    buildozer \
    cython \
    kivy \
    kivymd \
    plyer \
    pyjnius \
    numpy \
    pillow \
    requests

print_status "Python packages installed"

# Add pip user bin to PATH
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
export PATH=$PATH:~/.local/bin

# Navigate to project directory
PROJECT_PATH="/mnt/c/Users/Richard.Downing/Documents/augment-projects/Soul/android_overlay"

if [ ! -d "$PROJECT_PATH" ]; then
    print_error "Project directory not found: $PROJECT_PATH"
    print_info "Please ensure your project is in the correct location"
    exit 1
fi

cd "$PROJECT_PATH"
print_status "Navigated to project directory: $PROJECT_PATH"

# Check if buildozer.spec exists
if [ ! -f "buildozer.spec" ]; then
    print_error "buildozer.spec not found in project directory"
    exit 1
fi

print_status "Found buildozer.spec configuration"

# Clean any previous builds
print_info "Cleaning previous build artifacts..."
if [ -d ".buildozer" ]; then
    rm -rf .buildozer
fi
if [ -d "bin" ]; then
    rm -rf bin
fi

print_status "Build directory cleaned"

# Initialize buildozer
print_info "Initializing buildozer (this may take a while)..."
buildozer init

# Start APK build
print_info "Starting APK build process..."
print_warning "This will take 10-30 minutes for the first build"
print_info "Downloading Android SDK, NDK, and dependencies..."
echo ""

# Build the APK
buildozer android debug

# Check if build was successful
if [ $? -eq 0 ]; then
    print_status "APK BUILD SUCCESSFUL!"
    echo ""
    echo "🎉 UNIVERSAL SOUL AI APK READY!"
    echo "================================"
    
    # Find the APK file
    APK_FILE=$(find bin -name "*.apk" | head -1)
    
    if [ -n "$APK_FILE" ]; then
        APK_SIZE=$(du -h "$APK_FILE" | cut -f1)
        print_status "APK Location: $APK_FILE"
        print_status "APK Size: $APK_SIZE"
        echo ""
        echo "📱 INSTALLATION INSTRUCTIONS:"
        echo "1. Copy APK to your Android device:"
        echo "   - Via USB cable"
        echo "   - Email to yourself"
        echo "   - Upload to cloud storage"
        echo ""
        echo "2. On Android device:"
        echo "   - Enable 'Unknown Sources' in Settings"
        echo "   - Tap the APK file to install"
        echo "   - Grant all requested permissions"
        echo ""
        echo "3. Launch Universal Soul AI:"
        echo "   - Tap 'Request Permissions'"
        echo "   - Enable 'Display over other apps'"
        echo "   - Tap 'Start Overlay System'"
        echo "   - Test 360° gestures and 'Hey Soul' voice commands"
        echo ""
        echo "🎯 TESTING FEATURES:"
        echo "✅ Persistent overlay across all apps"
        echo "✅ 8-direction 360° gesture navigation"
        echo "✅ 'Hey Soul' voice activation"
        echo "✅ Context-aware app adaptation"
        echo "✅ 100% local privacy processing"
        echo ""
        echo "🏆 ACHIEVEMENT UNLOCKED:"
        echo "World's First 360° Gesture + Overlay AI Interface!"
        
        # Copy APK to Windows accessible location
        WINDOWS_PATH="/mnt/c/Users/Richard.Downing/Desktop/UniversalSoulAI.apk"
        cp "$APK_FILE" "$WINDOWS_PATH"
        print_status "APK copied to Desktop: UniversalSoulAI.apk"
        
    else
        print_warning "APK file not found in bin directory"
    fi
    
else
    print_error "APK build failed"
    echo ""
    echo "🔧 TROUBLESHOOTING:"
    echo "1. Check internet connection"
    echo "2. Ensure sufficient disk space (5GB+)"
    echo "3. Try running: buildozer android clean"
    echo "4. Then run this script again"
    exit 1
fi

echo ""
echo "🚀 Universal Soul AI APK build complete!"
echo "Ready to revolutionize mobile AI interaction!"
