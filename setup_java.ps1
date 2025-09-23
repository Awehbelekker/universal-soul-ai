# PowerShell script to set up Java for Android development
# Run this script as Administrator

Write-Host "Setting up Java JDK for Android Development" -ForegroundColor Green

# Check if Java is already installed
$javaVersion = try { java -version 2>&1 } catch { $null }
if ($javaVersion) {
    Write-Host "Java is already installed:" -ForegroundColor Green
    Write-Host $javaVersion
    
    # Check JAVA_HOME
    $javaHome = $env:JAVA_HOME
    if ($javaHome) {
        Write-Host "JAVA_HOME is set to: $javaHome" -ForegroundColor Green
    } else {
        Write-Host "JAVA_HOME is not set" -ForegroundColor Yellow
        
        # Try to find Java installation
        $javaPaths = @(
            "C:\Program Files\Microsoft\jdk-*",
            "C:\Program Files\Java\jdk-*",
            "C:\Program Files\OpenJDK\*",
            "C:\Program Files (x86)\Java\jdk-*"
        )
        
        foreach ($path in $javaPaths) {
            $found = Get-ChildItem $path -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($found) {
                Write-Host "Found Java at: $($found.FullName)" -ForegroundColor Cyan
                Write-Host "Set JAVA_HOME manually to: $($found.FullName)" -ForegroundColor Yellow
                break
            }
        }
    }
} else {
    Write-Host "Java is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installation Options:" -ForegroundColor Cyan
    Write-Host "1. Download from: https://learn.microsoft.com/en-us/java/openjdk/download#openjdk-17"
    Write-Host "2. Or run: winget install Microsoft.OpenJDK.17"
    Write-Host ""
    Write-Host "After installation, set environment variables:" -ForegroundColor Yellow
    Write-Host "   JAVA_HOME = C:\Program Files\Microsoft\jdk-17.x.x-hotspot"
    Write-Host "   PATH += %JAVA_HOME%\bin"
}

Write-Host ""
Write-Host "Current Environment:" -ForegroundColor Cyan
Write-Host "   JAVA_HOME: $env:JAVA_HOME"
Write-Host "   PATH contains Java: $($env:PATH -like '*java*')"

Write-Host ""
Write-Host "Next Steps for Android Development:" -ForegroundColor Green
Write-Host "1. Install Java JDK (this script)"
Write-Host "2. Set JAVA_HOME environment variable"
Write-Host "3. Run 'buildozer android debug' to build APK"
Write-Host "4. Deploy APK to Android device"
Write-Host "5. Add API keys for voice functionality"
