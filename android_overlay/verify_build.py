#!/usr/bin/env python3
"""
Universal Soul AI - Build Verification Test
==========================================
Comprehensive test to verify all build components work correctly
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    tests = [
        ("Kivy", "import kivy"),
        ("KivyMD", "import kivymd"),
        ("Main App", "import main"),
        ("Permissions", "from core.permissions import AndroidPermissions"),
        ("Device Tests", "from tests.device_test_suite import DeviceTestSuite"),
        ("Overlay System", "from universal_soul_overlay import UniversalSoulOverlay"),
        ("Build System", "import build_apk")
    ]
    
    results = {}
    
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"  ✅ {name}")
            results[name] = True
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            results[name] = False
    
    return results

def test_file_structure():
    """Test file structure completeness"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "main.py",
        "build_apk.py", 
        "buildozer.spec",
        "universal_soul_overlay.py",
        "core/permissions.py",
        "core/overlay_service.py",
        "core/gesture_handler.py",
        "core/context_analyzer.py",
        "tests/device_test_suite.py",
        "ui/overlay_view.py",
        "demo_minimalist_overlay.py",
        "BUILD_APK_WSL.bat"
    ]
    
    project_root = Path(__file__).parent
    results = {}
    
    for file_path in required_files:
        full_path = project_root / file_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
        results[file_path] = exists
    
    return results

def test_buildozer_config():
    """Test buildozer configuration"""
    print("\n⚙️ Testing buildozer configuration...")
    
    try:
        buildozer_spec = Path(__file__).parent / "buildozer.spec"
        
        if not buildozer_spec.exists():
            print("  ❌ buildozer.spec not found")
            return False
        
        content = buildozer_spec.read_text()
        
        required_sections = [
            "[app]",
            "title = Universal Soul AI",
            "package.name = universalsoulai",
            "package.domain = com.universalsoul",
            "source.dir = .",
            "requirements = ",
            "[buildozer]"
        ]
        
        missing = []
        for section in required_sections:
            if section not in content:
                missing.append(section)
        
        if missing:
            print(f"  ❌ Missing sections: {missing}")
            return False
        else:
            print("  ✅ Buildozer config is valid")
            return True
            
    except Exception as e:
        print(f"  ❌ Error reading buildozer.spec: {e}")
        return False

def test_permissions_system():
    """Test permissions system"""
    print("\n🔐 Testing permissions system...")
    
    try:
        from core.permissions import AndroidPermissions
        
        permissions = AndroidPermissions()
        
        # Test initialization
        if not hasattr(permissions, 'required_permissions'):
            print("  ❌ Missing required_permissions attribute")
            return False
        
        if not hasattr(permissions, 'request_permissions'):
            print("  ❌ Missing request_permissions method")
            return False
        
        if len(permissions.required_permissions) == 0:
            print("  ❌ No required permissions defined")
            return False
        
        print(f"  ✅ {len(permissions.required_permissions)} permissions defined")
        print("  ✅ Permission system initialized correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Permission system error: {e}")
        return False

def test_overlay_config():
    """Test overlay system configuration"""
    print("\n🔄 Testing overlay system...")
    
    try:
        from core.overlay_service import OverlayConfig
        
        # Test config creation
        config = OverlayConfig(
            overlay_size=56,
            local_processing_only=True
        )
        
        if not hasattr(config, 'overlay_size'):
            print("  ❌ Missing overlay_size attribute")
            return False
        
        if config.overlay_size != 56:
            print("  ❌ Overlay size not set correctly")
            return False
        
        print("  ✅ Overlay config system working")
        return True
        
    except Exception as e:
        print(f"  ❌ Overlay config error: {e}")
        return False

def run_verification_tests():
    """Run all verification tests"""
    print("🚀 Universal Soul AI - Build Verification")
    print("=" * 50)
    
    test_results = {}
    
    # Run all tests
    test_results['imports'] = test_imports()
    test_results['file_structure'] = test_file_structure()
    test_results['buildozer_config'] = test_buildozer_config()
    test_results['permissions'] = test_permissions_system()
    test_results['overlay_config'] = test_overlay_config()
    
    # Calculate overall results
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    
    overall_success = True
    
    for test_name, result in test_results.items():
        if isinstance(result, dict):
            # Count successes for dict results
            total = len(result)
            passed = sum(1 for v in result.values() if v)
            success = passed == total
            print(f"  {test_name}: {passed}/{total} ({'✅' if success else '❌'})")
            if not success:
                overall_success = False
        else:
            # Boolean results
            status = "✅" if result else "❌"
            print(f"  {test_name}: {status}")
            if not result:
                overall_success = False
    
    print("\n" + "=" * 50)
    if overall_success:
        print("🎉 ALL TESTS PASSED! Universal Soul AI is ready for user testing!")
        print("\n📋 Next Steps:")
        print("  1. Build APK: python build_apk.py")
        print("  2. Install on Android device")
        print("  3. Grant overlay permissions")
        print("  4. Test with real users")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    try:
        success = run_verification_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Verification failed with error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)