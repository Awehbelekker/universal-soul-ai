@echo off
setlocal enabledelayedexpansion

echo 🚀 Universal Soul AI - Build Manager
echo ===================================

set "command=%~1"
if "%command%"=="" set "command=status"

goto :main

:enable_workflow
set "workflow_name=%~1"
set "disabled_name=%workflow_name%.disabled"

if exist ".github\workflows\%disabled_name%" (
    move ".github\workflows\%disabled_name%" ".github\workflows\%workflow_name%" >nul
    echo ✅ Enabled: %workflow_name%
) else if exist ".github\workflows\%workflow_name%" (
    echo ℹ️  Already enabled: %workflow_name%
) else (
    echo ❌ Workflow not found: %workflow_name%
    exit /b 1
)
goto :eof

:disable_workflow
set "workflow_name=%~1"
set "disabled_name=%workflow_name%.disabled"

if exist ".github\workflows\%workflow_name%" (
    move ".github\workflows\%workflow_name%" ".github\workflows\%disabled_name%" >nul
    echo 🔇 Disabled: %workflow_name%
) else if exist ".github\workflows\%disabled_name%" (
    echo ℹ️  Already disabled: %workflow_name%
) else (
    echo ❌ Workflow not found: %workflow_name%
    exit /b 1
)
goto :eof

:show_status
echo.
echo 📊 Current Workflow Status:
echo ==========================

for %%w in (build-minimal.yml build-full.yml build-apk.yml build-apk-simple.yml) do (
    if exist ".github\workflows\%%w" (
        echo ✅ ACTIVE:   %%w
    ) else if exist ".github\workflows\%%w.disabled" (
        echo 🔇 DISABLED: %%w
    ) else (
        echo ❓ MISSING:  %%w
    )
)
echo.
goto :eof

:enable_minimal
echo 🔄 Switching to MINIMAL build mode...
call :enable_workflow "build-minimal.yml"
call :disable_workflow "build-full.yml"
call :disable_workflow "build-apk.yml"
call :disable_workflow "build-apk-simple.yml"
echo ✅ Minimal build mode activated
goto :eof

:enable_full
echo 🔄 Switching to FULL build mode...
call :enable_workflow "build-full.yml"
call :disable_workflow "build-minimal.yml"
call :disable_workflow "build-apk.yml"
call :disable_workflow "build-apk-simple.yml"
echo ✅ Full build mode activated
goto :eof

:enable_all
echo 🔄 Enabling ALL workflows...
call :enable_workflow "build-minimal.yml"
call :enable_workflow "build-full.yml"
call :enable_workflow "build-apk.yml"
call :enable_workflow "build-apk-simple.yml"
echo ✅ All workflows activated
goto :eof

:disable_all
echo 🔄 Disabling ALL workflows...
call :disable_workflow "build-minimal.yml"
call :disable_workflow "build-full.yml"
call :disable_workflow "build-apk.yml"
call :disable_workflow "build-apk-simple.yml"
echo ✅ All workflows disabled
goto :eof

:show_help
echo.
echo 📚 Usage: %~nx0 [command]
echo.
echo Commands:
echo   minimal     Enable only minimal build workflow
echo   full        Enable only full-featured build workflow
echo   all         Enable all build workflows
echo   none        Disable all build workflows
echo   status      Show current workflow status (default)
echo   help        Show this help message
echo.
echo Examples:
echo   %~nx0 minimal    # Switch to minimal APK builds
echo   %~nx0 full       # Switch to full-featured APK builds
echo   %~nx0 status     # Check which workflows are active
echo.
goto :eof

:main
if /i "%command%"=="minimal" goto :enable_minimal
if /i "%command%"=="min" goto :enable_minimal
if /i "%command%"=="full" goto :enable_full
if /i "%command%"=="complete" goto :enable_full
if /i "%command%"=="all" goto :enable_all
if /i "%command%"=="enable-all" goto :enable_all
if /i "%command%"=="none" goto :disable_all
if /i "%command%"=="disable-all" goto :disable_all
if /i "%command%"=="status" goto :show_status
if /i "%command%"=="show" goto :show_status
if /i "%command%"=="help" goto :show_help
if /i "%command%"=="-h" goto :show_help
if /i "%command%"=="--help" goto :show_help

echo ❌ Unknown command: %command%
echo Run '%~nx0 help' for usage information
exit /b 1

:show_status
call :show_status

where git >nul 2>&1
if %errorlevel%==0 (
    git status --porcelain >nul 2>&1
    if not errorlevel 1 (
        for /f %%i in ('git status --porcelain 2^>nul') do (
            echo 💡 Don't forget to commit and push your workflow changes!
            echo    git add .github/workflows/
            echo    git commit -m "Switch build workflow configuration"
            echo    git push
            goto :end
        )
    )
)

:end
pause