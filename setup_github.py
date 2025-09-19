#!/usr/bin/env python3
"""
Universal Soul AI - GitHub Setup Script
======================================
Automates GitHub repository setup and initial push
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and show progress"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def check_git_installed():
    """Check if git is installed"""
    return run_command("git --version", "Checking Git installation")

def initialize_repository():
    """Initialize git repository"""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("📁 Initializing Universal Soul AI repository...")
    
    # Check if already a git repo
    if (project_root / ".git").exists():
        print("✅ Git repository already exists")
        return True
    
    # Initialize git repo
    commands = [
        ("git init", "Initializing Git repository"),
        ("git add .", "Adding all files to Git"),
        ('git commit -m "Initial commit: Universal Soul AI complete implementation"', "Creating initial commit")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True

def setup_github_instructions():
    """Show GitHub setup instructions"""
    print("\n🚀 GitHub Repository Setup Instructions")
    print("=" * 50)
    print()
    print("1. Go to https://github.com and create a new repository")
    print("2. Name it: 'universal-soul-ai' (or your preferred name)")
    print("3. Make it Public (for free GitHub Actions)")
    print("4. Don't initialize with README (we already have one)")
    print()
    print("5. Copy the repository URL and run these commands:")
    print()
    print("   git remote add origin https://github.com/YOUR_USERNAME/universal-soul-ai.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    print()
    print("6. After pushing, GitHub Actions will automatically:")
    print("   ✅ Build your APK in the cloud")
    print("   ✅ Create releases with downloadable APK")
    print("   ✅ Run on every commit/push")
    print()
    print("🎉 Your Universal Soul AI will be live and building automatically!")

def main():
    """Main setup process"""
    print("🚀 Universal Soul AI - GitHub Setup")
    print("=" * 40)
    
    # Check prerequisites
    if not check_git_installed():
        print("❌ Git is not installed. Please install Git first:")
        print("   https://git-scm.com/downloads")
        return False
    
    # Initialize repository
    if not initialize_repository():
        print("❌ Failed to initialize repository")
        return False
    
    # Show setup instructions
    setup_github_instructions()
    
    print("\n📋 Next Steps:")
    print("1. Create GitHub repository")
    print("2. Push code using the commands above")
    print("3. Watch GitHub Actions build your APK")
    print("4. Download APK from Releases page")
    print("5. Install and test on Android device")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)