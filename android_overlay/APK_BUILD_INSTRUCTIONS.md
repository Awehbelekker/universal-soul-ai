# 📱 Universal Soul AI - APK Build Instructions

## 🚀 **Quick Start - Build Your APK**

### **Option 1: Automated Build (Recommended)**

```bash
cd android_overlay
python build_apk.py
```

This will automatically:
- ✅ Install all dependencies
- ✅ Generate app assets (icon, splash screen)
- ✅ Build the APK using buildozer
- ✅ Show installation instructions

### **Option 2: Manual Step-by-Step Build**

```bash
# 1. Install dependencies
python build_apk.py deps

# 2. Generate assets
python build_apk.py assets

# 3. Build APK
python build_apk.py build
```

## 🔧 **Prerequisites**

### **System Requirements**
- **Python 3.8+** (required)
- **Git** (required)
- **Java 8 or 11** (buildozer will install if needed)
- **Android SDK/NDK** (buildozer will install automatically)
- **Linux/macOS/WSL** (Windows requires WSL)

### **Python Dependencies**
```bash
pip install buildozer cython kivy kivymd plyer pyjnius numpy pillow
```

## 📋 **Build Process Details**

### **What the Build Script Does**

1. **Prerequisites Check**
   - Verifies Python version
   - Installs buildozer if missing
   - Checks system dependencies

2. **Asset Generation**
   - Creates app icon (512x512 PNG)
   - Generates splash screen (1080x1920 PNG)
   - Prepares app resources

3. **APK Compilation**
   - Uses buildozer to compile Python to APK
   - Includes all Universal Soul AI components
   - Optimizes for Android deployment

4. **Result Packaging**
   - Creates installable APK file
   - Provides installation instructions
   - Shows testing guidelines

### **Build Configuration**

The build is configured in `buildozer.spec`:

```ini
[app]
title = Universal Soul AI
package.name = universalsoulai
package.domain = com.universalsoul.ai
version = 1.0.0

# Key permissions for overlay functionality
android.permissions = SYSTEM_ALERT_WINDOW,RECORD_AUDIO,VIBRATE,CAMERA

# Target modern Android versions
android.api = 33
android.minapi = 23
```

## 📱 **APK Installation & Testing**

### **Installation Steps**

1. **Transfer APK to Android device**
   ```bash
   # APK will be in: android_overlay/bin/universalsoulai-1.0.0-debug.apk
   adb install bin/universalsoulai-1.0.0-debug.apk
   ```

2. **Enable Unknown Sources**
   - Go to Settings > Security
   - Enable "Install from Unknown Sources"
   - Or enable for specific app (Android 8+)

3. **Install APK**
   - Tap the APK file in file manager
   - Follow installation prompts
   - Grant all requested permissions

### **First Launch Setup**

1. **Launch Universal Soul AI app**
2. **Tap "Request Permissions"**
   - Grant microphone permission
   - Grant storage permissions
   - Grant camera permission (if needed)

3. **Enable Overlay Permission**
   - Tap "System Settings"
   - Enable "Display over other apps"
   - Return to Universal Soul AI

4. **Start Overlay System**
   - Tap "Start Overlay System"
   - Wait for initialization
   - Look for floating overlay icon

### **Testing the Overlay**

1. **360° Gesture Testing**
   - Swipe in 8 directions from overlay
   - North (↑): Calendar/scheduling
   - East (→): Transcription/notes
   - South (↓): Tasks/reminders
   - West (←): Quick actions

2. **Voice Command Testing**
   - Say "Hey Soul" near device
   - Try commands like:
     - "Take a note"
     - "Set a reminder"
     - "What's my schedule?"
     - "Help me with this app"

3. **Context Intelligence Testing**
   - Open different apps (WhatsApp, Chrome, etc.)
   - Notice overlay adapts colors/features
   - Test contextual gestures and commands

## 🔧 **Troubleshooting**

### **Build Issues**

**"Buildozer not found"**
```bash
pip install buildozer cython
```

**"Java not found"**
```bash
# Ubuntu/Debian
sudo apt install openjdk-11-jdk

# macOS
brew install openjdk@11
```

**"Android SDK download fails"**
```bash
# Clean and retry
python build_apk.py clean
python build_apk.py build
```

### **Runtime Issues**

**"Overlay not appearing"**
- Check overlay permission in Android settings
- Ensure "Display over other apps" is enabled
- Try restarting the app

**"Voice recognition not working"**
- Check microphone permission
- Test in quiet environment
- Ensure internet connection for initial setup

**"Gestures not detected"**
- Adjust gesture sensitivity in app settings
- Ensure overlay is visible and active
- Try slower, more deliberate gestures

**"App crashes on startup"**
- Check Android version (requires API 23+)
- Ensure all permissions are granted
- Check device logs with `adb logcat`

### **Performance Issues**

**"App is slow"**
- Close other apps to free memory
- Disable battery optimization for the app
- Reduce overlay size in settings

**"Battery drain"**
- Enable battery optimization in app
- Reduce continuous listening sensitivity
- Use gesture-only mode when possible

## 📊 **Build Output**

### **Successful Build Results**

```
🎉 BUILD COMPLETED SUCCESSFULLY!
==================================================
📱 APK Location: bin/universalsoulai-1.0.0-debug.apk
📊 APK Size: 45.2 MB
📦 Package: com.universalsoul.ai
🔢 Version: 1.0.0
```

### **APK Contents**

The APK includes:
- ✅ Universal Soul AI overlay system
- ✅ 360° gesture recognition engine
- ✅ Voice interface (ElevenLabs + Deepgram + Silero)
- ✅ Context intelligence system
- ✅ CoAct-1 automation engine
- ✅ Privacy-first architecture
- ✅ Mobile-optimized performance

## 🚀 **Next Steps After Testing**

### **Feedback Collection**
1. Test all overlay features
2. Document any issues or bugs
3. Note performance on your device
4. Test battery impact over time

### **Feature Validation**
1. Verify 360° gestures work smoothly
2. Test voice recognition accuracy
3. Check context adaptation across apps
4. Validate privacy indicators

### **Production Preparation**
1. Optimize performance based on testing
2. Refine gesture sensitivity
3. Improve voice recognition
4. Enhance UI/UX based on feedback

## 📞 **Support**

If you encounter issues:

1. **Check logs**: `adb logcat | grep UniversalSoul`
2. **Review permissions**: Ensure all required permissions granted
3. **Test environment**: Try in different apps and contexts
4. **Device compatibility**: Verify Android version and hardware

**The APK build system is ready to create your testable Universal Soul AI overlay app!** 🎉

Build time: ~10-30 minutes (first build)
APK size: ~45-60 MB
Supported devices: Android 6.0+ (API 23+)
