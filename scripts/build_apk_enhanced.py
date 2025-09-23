#!/usr/bin/env python3
"""
Enhanced APK Build Script for Universal Soul AI
===============================================

Comprehensive APK build process with multi-modal AI integration,
dependency management, and build validation.
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ANDROID_OVERLAY_PATH = PROJECT_ROOT / "android_overlay"
THINKMESH_CORE_PATH = PROJECT_ROOT / "thinkmesh_core"


class APKBuilder:
    """Enhanced APK builder with comprehensive validation"""
    
    def __init__(self):
        self.build_timestamp = datetime.now()
        self.build_log = []
        self.errors = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log build messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.build_log.append(log_entry)
        print(log_entry)
        
        if level == "ERROR":
            self.errors.append(message)
    
    def validate_environment(self) -> bool:
        """Validate build environment"""
        
        self.log("🔍 Validating build environment...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            self.log(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}", "ERROR")
            return False
        
        self.log(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check if we're in the right directory
        if not ANDROID_OVERLAY_PATH.exists():
            self.log("android_overlay directory not found", "ERROR")
            return False
        
        # Check for main.py
        main_py = ANDROID_OVERLAY_PATH / "main.py"
        if not main_py.exists():
            self.log("main.py not found in android_overlay", "ERROR")
            return False
        
        # Check for buildozer.spec
        buildozer_spec = ANDROID_OVERLAY_PATH / "buildozer.spec"
        if not buildozer_spec.exists():
            self.log("buildozer.spec not found", "ERROR")
            return False
        
        # Check for API keys
        api_keys_file = ANDROID_OVERLAY_PATH / "api_keys.env"
        if not api_keys_file.exists():
            self.log("⚠️ api_keys.env not found - creating from template", "WARNING")
            template_file = ANDROID_OVERLAY_PATH / "api_keys_template.env"
            if template_file.exists():
                shutil.copy2(template_file, api_keys_file)
                self.log("✅ Created api_keys.env from template")
            else:
                self.log("api_keys_template.env not found", "ERROR")
                return False
        
        self.log("✅ Environment validation passed")
        return True
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are available"""
        
        self.log("📦 Checking dependencies...")
        
        # Check if buildozer is installed
        try:
            result = subprocess.run(["buildozer", "version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log("✅ Buildozer is installed")
            else:
                self.log("Buildozer not working properly", "ERROR")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("Buildozer not found - installing...", "WARNING")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "buildozer"], 
                             check=True, timeout=120)
                self.log("✅ Buildozer installed successfully")
            except Exception as e:
                self.log(f"Failed to install buildozer: {e}", "ERROR")
                return False
        
        # Check for Java (required for Android builds)
        try:
            result = subprocess.run(["java", "-version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log("✅ Java is available")
            else:
                self.log("⚠️ Java not found - may cause build issues", "WARNING")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("⚠️ Java not found - may cause build issues", "WARNING")
        
        return True
    
    def prepare_build_environment(self) -> bool:
        """Prepare the build environment"""
        
        self.log("⚙️ Preparing build environment...")
        
        # Change to android_overlay directory
        os.chdir(ANDROID_OVERLAY_PATH)
        self.log(f"📁 Changed to directory: {ANDROID_OVERLAY_PATH}")
        
        # Clean previous builds
        self.log("🧹 Cleaning previous builds...")
        
        # Remove .buildozer directory if it exists
        buildozer_dir = ANDROID_OVERLAY_PATH / ".buildozer"
        if buildozer_dir.exists():
            try:
                shutil.rmtree(buildozer_dir)
                self.log("✅ Removed previous .buildozer directory")
            except Exception as e:
                self.log(f"⚠️ Could not remove .buildozer directory: {e}", "WARNING")
        
        # Remove bin directory if it exists
        bin_dir = ANDROID_OVERLAY_PATH / "bin"
        if bin_dir.exists():
            try:
                shutil.rmtree(bin_dir)
                self.log("✅ Removed previous bin directory")
            except Exception as e:
                self.log(f"⚠️ Could not remove bin directory: {e}", "WARNING")
        
        return True
    
    def update_buildozer_spec(self) -> bool:
        """Update buildozer.spec with multi-modal AI requirements"""
        
        self.log("📝 Updating buildozer.spec for multi-modal AI...")
        
        buildozer_spec = ANDROID_OVERLAY_PATH / "buildozer.spec"
        
        try:
            # Read current spec
            with open(buildozer_spec, 'r') as f:
                content = f.read()
            
            # Update requirements to include multi-modal AI dependencies
            enhanced_requirements = (
                "kivy==2.1.0,kivymd==1.1.1,plyer,pyjnius,android,psutil,"
                "requests,websockets,python-dotenv,numpy,pillow,"
                "google-generativeai,openai,anthropic"
            )
            
            # Replace requirements line
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('requirements ='):
                    lines[i] = f"requirements = {enhanced_requirements}"
                    break
            
            # Update version with timestamp
            version_timestamp = self.build_timestamp.strftime("%Y%m%d.%H%M")
            for i, line in enumerate(lines):
                if line.startswith('version ='):
                    lines[i] = f"version = 1.0.{version_timestamp}"
                    break
            
            # Write updated spec
            with open(buildozer_spec, 'w') as f:
                f.write('\n'.join(lines))
            
            self.log("✅ Updated buildozer.spec with multi-modal AI requirements")
            return True
            
        except Exception as e:
            self.log(f"Failed to update buildozer.spec: {e}", "ERROR")
            return False
    
    def build_apk(self) -> bool:
        """Build the APK"""
        
        self.log("🔨 Starting APK build process...")
        self.log("⏱️ This may take 15-30 minutes for first build...")
        
        try:
            # Run buildozer android debug
            start_time = time.time()
            
            process = subprocess.Popen(
                ["buildozer", "android", "debug"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Filter out excessive noise but keep important messages
                    line = output.strip()
                    if any(keyword in line.lower() for keyword in [
                        'error', 'failed', 'exception', 'warning',
                        'building', 'compiling', 'installing', 'downloading',
                        'apk', 'success', 'complete'
                    ]):
                        self.log(f"📱 {line}")
            
            return_code = process.poll()
            build_time = time.time() - start_time
            
            if return_code == 0:
                self.log(f"✅ APK build completed successfully in {build_time:.1f} seconds")
                return True
            else:
                self.log(f"APK build failed with return code {return_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"APK build process failed: {e}", "ERROR")
            return False
    
    def validate_apk(self) -> bool:
        """Validate the built APK"""
        
        self.log("🔍 Validating built APK...")
        
        # Look for APK files in bin directory
        bin_dir = ANDROID_OVERLAY_PATH / "bin"
        if not bin_dir.exists():
            self.log("bin directory not found after build", "ERROR")
            return False
        
        apk_files = list(bin_dir.glob("*.apk"))
        if not apk_files:
            self.log("No APK files found in bin directory", "ERROR")
            return False
        
        # Get the most recent APK
        latest_apk = max(apk_files, key=lambda p: p.stat().st_mtime)
        apk_size = latest_apk.stat().st_size / (1024 * 1024)  # Size in MB
        
        self.log(f"✅ APK found: {latest_apk.name}")
        self.log(f"📊 APK size: {apk_size:.1f} MB")
        
        # Copy APK to deployment directory with timestamp
        deployment_dir = PROJECT_ROOT / "deployment" / "builds"
        deployment_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = self.build_timestamp.strftime("%Y%m%d_%H%M%S")
        deployment_apk = deployment_dir / f"universal_soul_ai_beta_{timestamp}.apk"
        
        try:
            shutil.copy2(latest_apk, deployment_apk)
            self.log(f"✅ APK copied to: {deployment_apk}")
        except Exception as e:
            self.log(f"⚠️ Could not copy APK to deployment directory: {e}", "WARNING")
        
        return True
    
    def generate_build_report(self) -> None:
        """Generate comprehensive build report"""
        
        self.log("📋 Generating build report...")
        
        # Create build report
        report = {
            "build_timestamp": self.build_timestamp.isoformat(),
            "build_duration": "N/A",  # Would need to track this
            "success": len(self.errors) == 0,
            "errors": self.errors,
            "log_entries": len(self.build_log),
            "apk_info": {
                "version": f"1.0.{self.build_timestamp.strftime('%Y%m%d.%H%M')}",
                "features": [
                    "Multi-modal AI integration (Google Gemini)",
                    "Advanced automation engine",
                    "Voice processing capabilities",
                    "Overlay interface system",
                    "Local processing fallbacks"
                ]
            }
        }
        
        # Save build report
        report_file = PROJECT_ROOT / "deployment" / f"build_report_{self.build_timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            import json
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            self.log(f"✅ Build report saved: {report_file}")
        except Exception as e:
            self.log(f"⚠️ Could not save build report: {e}", "WARNING")
        
        # Print summary
        print("\n" + "="*60)
        print("🎉 UNIVERSAL SOUL AI - APK BUILD COMPLETE!")
        print("="*60)
        
        if len(self.errors) == 0:
            print("✅ BUILD SUCCESSFUL!")
            print("\n📱 APK Features:")
            for feature in report["apk_info"]["features"]:
                print(f"  • {feature}")
            
            print(f"\n📊 Build Info:")
            print(f"  • Version: {report['apk_info']['version']}")
            print(f"  • Timestamp: {self.build_timestamp}")
            print(f"  • Log entries: {report['log_entries']}")
            
            print(f"\n📁 APK Location:")
            bin_dir = ANDROID_OVERLAY_PATH / "bin"
            if bin_dir.exists():
                apk_files = list(bin_dir.glob("*.apk"))
                if apk_files:
                    latest_apk = max(apk_files, key=lambda p: p.stat().st_mtime)
                    print(f"  • {latest_apk}")
            
            print(f"\n🚀 Next Steps:")
            print(f"  • Test APK on Android device")
            print(f"  • Distribute to beta testers")
            print(f"  • Collect feedback and metrics")
            print(f"  • Iterate based on results")
            
        else:
            print("❌ BUILD FAILED!")
            print(f"\n🔧 Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
            
            print(f"\n💡 Troubleshooting:")
            print(f"  • Check build log above for details")
            print(f"  • Ensure all dependencies are installed")
            print(f"  • Verify buildozer.spec configuration")
            print(f"  • Try cleaning build cache and rebuilding")
    
    def build(self) -> bool:
        """Run complete build process"""
        
        print("🚀 Universal Soul AI - Enhanced APK Build")
        print("=" * 60)
        
        try:
            # Step 1: Validate environment
            if not self.validate_environment():
                return False
            
            # Step 2: Check dependencies
            if not self.check_dependencies():
                return False
            
            # Step 3: Prepare build environment
            if not self.prepare_build_environment():
                return False
            
            # Step 4: Update buildozer spec
            if not self.update_buildozer_spec():
                return False
            
            # Step 5: Build APK
            if not self.build_apk():
                return False
            
            # Step 6: Validate APK
            if not self.validate_apk():
                return False
            
            return True
            
        except KeyboardInterrupt:
            self.log("Build cancelled by user", "ERROR")
            return False
        except Exception as e:
            self.log(f"Unexpected error during build: {e}", "ERROR")
            return False
        finally:
            # Always generate report
            self.generate_build_report()


def main():
    """Main build function"""
    
    builder = APKBuilder()
    success = builder.build()
    
    if success:
        print("\n🎉 APK build completed successfully!")
        print("Ready for beta testing deployment!")
        sys.exit(0)
    else:
        print("\n❌ APK build failed!")
        print("Check the error messages above for troubleshooting.")
        sys.exit(1)


if __name__ == "__main__":
    main()
