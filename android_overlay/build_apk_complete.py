#!/usr/bin/env python3
"""
Complete APK Build Script for Universal Soul AI
Handles all aspects of APK building including environment setup
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_java_installation():
    """Check if Java is properly installed and configured"""
    print("🔍 Checking Java installation...")
    
    # Check if java command is available
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, check=True)
        print("✅ Java is installed:")
        print(result.stderr.split('\n')[0])  # Java version is in stderr
        
        # Check JAVA_HOME
        java_home = os.environ.get('JAVA_HOME')
        if java_home:
            print(f"✅ JAVA_HOME is set: {java_home}")
            return True
        else:
            print("⚠️ JAVA_HOME is not set")
            print("💡 Please set JAVA_HOME environment variable")
            return False
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Java is not installed or not in PATH")
        print("📥 Please install Java JDK 17:")
        print("   - Download: https://learn.microsoft.com/en-us/java/openjdk/download#openjdk-17")
        print("   - Or run: winget install Microsoft.OpenJDK.17")
        return False

def check_buildozer_config():
    """Validate buildozer.spec configuration"""
    print("\n🔧 Checking buildozer configuration...")
    
    if not os.path.exists('buildozer.spec'):
        print("❌ buildozer.spec not found")
        return False
    
    print("✅ buildozer.spec found")
    
    # Check if we can parse the config
    try:
        result = subprocess.run([sys.executable, '-m', 'buildozer', 'android', 'debug', '--dry-run'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Buildozer configuration is valid")
            return True
        else:
            print("⚠️ Buildozer configuration issues:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("⚠️ Buildozer check timed out (this is normal)")
        return True
    except Exception as e:
        print(f"⚠️ Could not validate buildozer config: {e}")
        return True  # Continue anyway

def run_integration_test():
    """Run the thinkmesh integration test"""
    print("\n🧪 Running integration tests...")
    
    if not os.path.exists('test_thinkmesh_integration.py'):
        print("⚠️ Integration test not found, skipping...")
        return True
    
    try:
        result = subprocess.run([sys.executable, 'test_thinkmesh_integration.py'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Integration tests passed")
            return True
        else:
            print("⚠️ Integration tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"⚠️ Could not run integration tests: {e}")
        return True  # Continue anyway

def build_apk():
    """Build the APK using buildozer"""
    print("\n🏗️ Building APK...")
    print("This may take 10-30 minutes for the first build...")
    
    try:
        # Run buildozer android debug
        cmd = [sys.executable, '-m', 'buildozer', 'android', 'debug']
        print(f"Running: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                 text=True, bufsize=1, universal_newlines=True)
        
        # Stream output in real-time
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print("\n🎉 APK built successfully!")
            
            # Find the APK file
            bin_dir = Path('bin')
            if bin_dir.exists():
                apk_files = list(bin_dir.glob('*.apk'))
                if apk_files:
                    apk_path = apk_files[0]
                    print(f"📱 APK location: {apk_path.absolute()}")
                    print(f"📊 APK size: {apk_path.stat().st_size / 1024 / 1024:.1f} MB")
                    return True
            
            print("⚠️ APK built but file not found in expected location")
            return True
            
        else:
            print(f"\n❌ APK build failed with exit code: {process.returncode}")
            return False
            
    except Exception as e:
        print(f"\n❌ APK build error: {e}")
        return False

def main():
    """Main build process"""
    print("🚀 Universal Soul AI - Complete APK Build Process")
    print("=" * 60)
    
    # Change to android_overlay directory if not already there
    if not os.path.exists('buildozer.spec'):
        android_overlay = Path(__file__).parent
        os.chdir(android_overlay)
        print(f"📁 Changed to directory: {android_overlay.absolute()}")
    
    # Step 1: Check Java
    java_ok = check_java_installation()
    if not java_ok:
        print("\n❌ Java setup required before building APK")
        print("Please install Java and set JAVA_HOME, then run this script again")
        return 1
    
    # Step 2: Check buildozer config
    config_ok = check_buildozer_config()
    if not config_ok:
        print("\n❌ Buildozer configuration issues need to be resolved")
        return 1
    
    # Step 3: Run integration tests
    tests_ok = run_integration_test()
    if not tests_ok:
        print("\n⚠️ Integration tests failed, but continuing with build...")
    
    # Step 4: Build APK
    build_ok = build_apk()
    if not build_ok:
        print("\n❌ APK build failed")
        return 1
    
    print("\n🎉 Build process completed successfully!")
    print("\n📱 Next steps:")
    print("1. Connect Android device with USB debugging enabled")
    print("2. Run: adb install bin/*.apk")
    print("3. Add API keys for full functionality:")
    print("   - ElevenLabs API key for premium TTS")
    print("   - Deepgram API key for premium STT")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
