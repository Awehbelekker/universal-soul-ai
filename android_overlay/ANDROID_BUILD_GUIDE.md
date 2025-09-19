# 📱 Android APK Build Guide

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
