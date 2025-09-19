#!/usr/bin/env python3
"""
Simplified APK Builder for Windows
==================================
Direct buildozer execution without WSL dependency
"""

import subprocess
import sys
import os
from pathlib import Path

def simple_apk_build():
    """Simple APK build using buildozer directly"""
    print("🚀 Universal Soul AI - Simple APK Builder")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print(f"📁 Building in: {project_root}")
    
    # Check if buildozer.spec exists
    buildozer_spec = project_root / "buildozer.spec"
    if not buildozer_spec.exists():
        print("❌ buildozer.spec not found!")
        return False
    
    try:
        print("🔨 Starting buildozer android debug...")
        print("⏳ This will take 15-45 minutes on first build...")
        print("📋 Buildozer will download Android SDK, NDK, and dependencies...")
        print()
        
        # Run buildozer with verbose output
        result = subprocess.run([
            "buildozer", "android", "debug", "--verbose"
        ], cwd=project_root)
        
        if result.returncode == 0:
            print("\n🎉 APK BUILD SUCCESSFUL!")
            
            # Look for the APK file
            bin_dir = project_root / "bin"
            if bin_dir.exists():
                apk_files = list(bin_dir.glob("*.apk"))
                if apk_files:
                    apk_file = apk_files[0]
                    print(f"📱 APK Location: {apk_file}")
                    print(f"📊 APK Size: {apk_file.stat().st_size / (1024*1024):.1f} MB")
                    
                    # Try to copy to Desktop
                    try:
                        desktop = Path.home() / "Desktop"
                        if desktop.exists():
                            import shutil
                            dest = desktop / "UniversalSoulAI.apk"
                            shutil.copy2(apk_file, dest)
                            print(f"📋 APK copied to Desktop: {dest}")
                    except Exception as e:
                        print(f"⚠️ Could not copy to Desktop: {e}")
            
            print("\n📋 Installation Instructions:")
            print("1. Transfer APK to Android device")
            print("2. Enable 'Unknown Sources' in Android Settings")
            print("3. Install the APK")
            print("4. Grant overlay permissions")
            
            return True
        else:
            print(f"\n❌ Build failed with exit code: {result.returncode}")
            print("💡 Try checking the buildozer logs above for specific errors")
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️ Build interrupted by user")
        return False
    except FileNotFoundError:
        print("\n❌ Buildozer not found!")
        print("💡 Install with: pip install buildozer")
        return False
    except Exception as e:
        print(f"\n❌ Build error: {e}")
        return False

if __name__ == "__main__":
    success = simple_apk_build()
    input("\nPress Enter to continue...")
    sys.exit(0 if success else 1)