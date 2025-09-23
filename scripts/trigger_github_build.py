#!/usr/bin/env python3
"""
Trigger GitHub Actions APK Build
===============================

Commits current changes and triggers GitHub Actions build for Universal Soul AI APK.
"""

import subprocess
import sys
import time
from datetime import datetime


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False


def main():
    """Main function to trigger GitHub build"""
    
    print("🚀 Universal Soul AI - GitHub Actions APK Build Trigger")
    print("=" * 60)
    
    # Check if we're in a git repository
    if not run_command("git status", "Checking git repository"):
        print("❌ Not in a git repository or git not available")
        return False
    
    # Check current status
    print("\n📋 Current repository status:")
    run_command("git status --short", "Checking file changes")
    
    # Add all changes
    if not run_command("git add .", "Adding all changes"):
        return False
    
    # Create commit message with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Multi-modal AI integration complete - APK build ready ({timestamp})"
    
    # Commit changes
    commit_cmd = f'git commit -m "{commit_message}"'
    if not run_command(commit_cmd, "Committing changes"):
        print("ℹ️ No changes to commit or commit failed")
    
    # Push to GitHub
    if not run_command("git push origin main", "Pushing to GitHub"):
        print("❌ Failed to push to GitHub")
        print("💡 Make sure you have push access to the repository")
        return False
    
    print("\n🎉 Code pushed to GitHub successfully!")
    print("\n🔗 Next steps:")
    print("1. Go to: https://github.com/Awehbelekker/universal-soul-ai/actions")
    print("2. Click on 'Universal Soul AI - Full Featured APK Build'")
    print("3. Click 'Run workflow' button")
    print("4. Select 'debug' for build type")
    print("5. Click 'Run workflow'")
    print("6. Wait 15-20 minutes for build to complete")
    print("7. Download APK from 'Artifacts' section")
    
    print("\n📱 APK will include:")
    print("  • Multi-modal AI integration (Google Gemini)")
    print("  • Advanced automation engine")
    print("  • Voice processing capabilities")
    print("  • Overlay interface system")
    print("  • Local processing fallbacks")
    
    print("\n⏱️ Build time: ~15-20 minutes")
    print("📊 Expected APK size: 50-100 MB")
    print("🎯 Target: Android API 23+ (Android 6.0+)")
    
    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ GitHub Actions build trigger completed!")
        print("🚀 Check GitHub Actions for build progress")
    else:
        print("\n❌ Failed to trigger GitHub Actions build")
        print("🔧 Check the errors above and try again")
    
    input("\nPress Enter to continue...")
    sys.exit(0 if success else 1)
