@echo off
echo 🚀 Universal Soul AI - GitHub Setup Automation
echo =============================================
echo.

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git not found. Please install Git first:
    echo.
    echo 1. Go to: https://git-scm.com/downloads
    echo 2. Download and install Git for Windows
    echo 3. Use default settings during installation
    echo 4. Restart this script after installation
    echo.
    echo 💡 Tip: You can also install Git via winget:
    echo    winget install --id Git.Git -e --source winget
    echo.
    pause
    exit /b 1
)

echo ✅ Git is installed - proceeding with repository setup...
echo.

REM Initialize Git repository
echo 📁 Initializing Git repository...
git init

REM Add all files
echo 📦 Adding all files to Git...
git add .

REM Create initial commit
echo 💾 Creating initial commit...
git commit -m "Universal Soul AI - Complete implementation ready for user testing"

echo.
echo 🎉 Local Git repository initialized successfully!
echo.
echo 📋 Next steps:
echo.
echo 1. Go to: https://github.com/new
echo 2. Repository name: universal-soul-ai
echo 3. Make it PUBLIC (for free GitHub Actions)
echo 4. DON'T initialize with README
echo 5. Click "Create repository"
echo.
echo 6. Then run these commands in PowerShell:
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/universal-soul-ai.git
echo    git branch -M main  
echo    git push -u origin main
echo.
echo 🔗 Replace YOUR_USERNAME with your actual GitHub username
echo.
echo ⚡ After pushing, GitHub Actions will automatically build your APK!
echo.
pause