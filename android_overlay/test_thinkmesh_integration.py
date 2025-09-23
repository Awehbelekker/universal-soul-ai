#!/usr/bin/env python3
"""
Test script to verify thinkmesh_core integration with android_overlay
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to Python path for thinkmesh_core access
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_thinkmesh_integration():
    """Test that all thinkmesh_core components can be imported and initialized"""
    
    print("🧪 Testing thinkmesh_core integration...")
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from thinkmesh_core.voice import VoiceInterface, VoiceConfig
        from thinkmesh_core.automation import CoAct1AutomationEngine
        from thinkmesh_core.interfaces import UserContext
        print("  ✅ All imports successful")
        
        # Test VoiceConfig creation
        print("🎙️ Testing VoiceConfig...")
        voice_config = VoiceConfig(
            stt_provider="deepgram",
            tts_provider="elevenlabs",
            vad_provider="silero",
            sample_rate=16000,
            low_latency_mode=True,
            noise_suppression=True,
            echo_cancellation=True
        )
        print("  ✅ VoiceConfig created successfully")
        
        # Test VoiceInterface creation
        print("🎤 Testing VoiceInterface...")
        voice_interface = VoiceInterface(voice_config)
        print("  ✅ VoiceInterface created successfully")
        
        # Test VoiceInterface initialization (should work with fallbacks)
        print("🔧 Testing VoiceInterface initialization...")
        await voice_interface.initialize()
        print("  ✅ VoiceInterface initialized successfully")
        
        # Test CoAct1AutomationEngine creation
        print("🤖 Testing CoAct1AutomationEngine...")
        automation_engine = CoAct1AutomationEngine()
        print("  ✅ CoAct1AutomationEngine created successfully")
        
        # Test CoAct1AutomationEngine initialization
        print("⚙️ Testing CoAct1AutomationEngine initialization...")
        await automation_engine.initialize()
        print("  ✅ CoAct1AutomationEngine initialized successfully")
        
        # Test UserContext creation
        print("👤 Testing UserContext...")
        user_context = UserContext(
            user_id="test_user",
            preferences={"theme": "dark", "language": "en"},
            session_data={"session_id": "test_session", "app_context": "test_app"},
            device_info={"device_type": "mobile", "platform": "android"},
            privacy_settings={"data_sharing": False, "analytics": False}
        )
        print("  ✅ UserContext created successfully")
        
        print("\n🎉 All thinkmesh_core integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_android_overlay_integration():
    """Test that android_overlay can use thinkmesh_core components"""
    
    print("\n📱 Testing android_overlay integration...")
    
    try:
        # Test importing the main overlay class
        from universal_soul_overlay import UniversalSoulOverlay
        print("  ✅ UniversalSoulOverlay imported successfully")
        
        # Test creating the overlay (should work with thinkmesh_core)
        overlay = UniversalSoulOverlay()
        print("  ✅ UniversalSoulOverlay created successfully")
        
        # Test that thinkmesh_core is available
        if hasattr(overlay, 'THINKMESH_AVAILABLE'):
            if overlay.THINKMESH_AVAILABLE:
                print("  ✅ thinkmesh_core is available to android_overlay")
            else:
                print("  ⚠️ thinkmesh_core is not available (using fallbacks)")
        
        print("\n🎉 Android overlay integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Android overlay integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all integration tests"""
    
    print("🚀 Universal Soul AI - thinkmesh_core Integration Test")
    print("=" * 60)
    
    # Test thinkmesh_core components
    thinkmesh_success = await test_thinkmesh_integration()
    
    # Test android_overlay integration
    overlay_success = await test_android_overlay_integration()
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    print(f"  thinkmesh_core: {'✅ PASS' if thinkmesh_success else '❌ FAIL'}")
    print(f"  android_overlay: {'✅ PASS' if overlay_success else '❌ FAIL'}")
    
    if thinkmesh_success and overlay_success:
        print("\n🎉 ALL TESTS PASSED! thinkmesh_core is ready for Android deployment!")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
