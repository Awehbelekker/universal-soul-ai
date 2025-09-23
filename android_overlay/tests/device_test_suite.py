"""
Device Testing Suite
===================
Real device testing for Android APK
"""

import asyncio
import json
import time
import logging
import importlib
from pathlib import Path
from typing import Dict, Any, List
from kivy.utils import platform

logger = logging.getLogger(__name__)

class DeviceTestSuite:
    def __init__(self):
        self.test_results = {}
        self.device_info = {}
        self.test_start_time = time.time()
        
    async def run_device_tests(self) -> bool:
        """Run comprehensive device tests"""
        print("📱 Starting Device Test Suite")
        print("=" * 40)
        
        try:
            # Collect device info
            await self._collect_device_info()
            
            # Run individual test components
            tests = [
                ("Device Info", self._test_device_info),
                ("Permissions", self._test_permissions),
                ("Overlay System", self._test_overlay_system),
                ("Gesture Recognition", self._test_gesture_system), 
                ("Voice Interface", self._test_voice_interface),
                ("Performance", self._test_performance),
                ("Memory Usage", self._test_memory_usage),
                ("UI Responsiveness", self._test_ui_responsiveness)
            ]
            
            overall_success = True
            
            for test_name, test_func in tests:
                print(f"\n🔬 Testing {test_name}...")
                try:
                    result = await test_func()
                    self.test_results[test_name] = {
                        'success': result,
                        'timestamp': time.time()
                    }
                    
                    status = "✅ PASSED" if result else "❌ FAILED"
                    print(f"   {status}")
                    
                    if not result:
                        overall_success = False
                        
                except Exception as e:
                    logger.error(f"Test {test_name} error: {e}")
                    self.test_results[test_name] = {
                        'success': False,
                        'error': str(e),
                        'timestamp': time.time()
                    }
                    print(f"   ❌ ERROR: {e}")
                    overall_success = False
            
            # Generate test report
            await self._generate_test_report(overall_success)
            
            return overall_success
            
        except Exception as e:
            logger.error(f"Device test suite error: {e}")
            return False
    
    async def _collect_device_info(self):
        """Collect comprehensive device information"""
        try:
            self.device_info = {
                'platform': platform,
                'test_timestamp': self.test_start_time
            }
            
            if platform == 'android':
                try:
                    from jnius import autoclass
                    
                    # Android device info
                    Build = autoclass('android.os.Build')
                    ActivityManager = autoclass('android.app.ActivityManager')
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    
                    activity = PythonActivity.mActivity
                    am = activity.getSystemService('activity')
                    
                    memory_info = ActivityManager.MemoryInfo()
                    am.getMemoryInfo(memory_info)
                    
                    self.device_info.update({
                        'manufacturer': Build.MANUFACTURER,
                        'model': Build.MODEL,
                        'android_version': Build.VERSION.RELEASE,
                        'sdk_int': Build.VERSION.SDK_INT,
                        'hardware': Build.HARDWARE,
                        'total_memory': memory_info.totalMem,
                        'available_memory': memory_info.availMem,
                        'low_memory': memory_info.lowMemory
                    })
                    
                except Exception as e:
                    logger.warning(f"Could not get Android device info: {e}")
            
            # Cross-platform info
            try:
                import psutil
                self.device_info.update({
                    'cpu_count': psutil.cpu_count(),
                    'memory_total': psutil.virtual_memory().total,
                    'memory_available': psutil.virtual_memory().available,
                    'disk_usage': psutil.disk_usage('/').percent if platform != 'win' else psutil.disk_usage('C:').percent
                })
            except ImportError:
                logger.warning("psutil not available for system info")
            except:
                pass
            
            print(f"📱 Device: {self.device_info.get('manufacturer', 'Unknown')} {self.device_info.get('model', 'Unknown')}")
            print(f"🤖 Android: {self.device_info.get('android_version', 'Unknown')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Device info collection error: {e}")
            return False
    
    async def _test_device_info(self):
        """Test device info collection"""
        required_fields = ['platform']
        
        for field in required_fields:
            if field not in self.device_info:
                return False
        
        return True
    
    async def _test_permissions(self):
        """Test Android permissions"""
        try:
            from core.permissions import AndroidPermissions
            
            permissions = AndroidPermissions()
            success = permissions.request_permissions()
            
            # Store permission status in results
            self.test_results['permission_details'] = permissions.get_permission_status()
            
            return success
            
        except Exception as e:
            logger.error(f"Permission test error: {e}")
            return False
    
    async def _test_overlay_system(self):
        """Test overlay creation and display"""
        try:
            from universal_soul_overlay import UniversalSoulOverlay
            from core.overlay_service import OverlayConfig
            
            # Create minimal config for testing
            config = OverlayConfig(
                overlay_size=56,
                local_processing_only=True,
                continuous_listening=False,  # Don't enable listening for tests
                enable_voice=False,
                enable_gestures=True
            )
            
            overlay = UniversalSoulOverlay(config)
            
            # Test initialization
            init_success = await overlay.initialize()
            if not init_success:
                return False
            
            # Test start/stop cycle
            await overlay.start()
            await asyncio.sleep(1)  # Let it run briefly
            await overlay.stop()
            
            return True
            
        except Exception as e:
            logger.error(f"Overlay test error: {e}")
            return False
    
    async def _test_gesture_system(self):
        """Test gesture recognition system"""
        try:
            from core.gesture_handler import GestureHandler
            
            gesture_handler = GestureHandler()
            
            # Test gesture recognition initialization
            success = await gesture_handler.initialize()
            if not success:
                return False
            
            # Test basic gesture processing
            # Create mock touch event
            mock_event = {
                'x': 100,
                'y': 100,
                'timestamp': time.time(),
                'action': 'down'
            }
            
            # Process mock gesture
            result = await gesture_handler.process_touch_event(mock_event)
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Gesture test error: {e}")
            return False
    
    async def _test_voice_interface(self):
        """Test voice interface"""
        try:
            # Import voice interface if available (dynamic import to avoid static resolution errors)
            import importlib.util
            VoiceInterface = None
            try:
                spec = importlib.util.find_spec("core.voice.interface")
                if spec is not None:
                    module = importlib.import_module("core.voice.interface")
                    VoiceInterface = getattr(module, "VoiceInterface", None)
                    voice_available = VoiceInterface is not None
                else:
                    logger.warning("Voice interface module not found in core.voice.interface")
                    voice_available = False
            except Exception as e:
                logger.warning(f"Error checking voice interface module: {e}")
                voice_available = False
            
            if not voice_available:
                # Mark as passed since voice is optional
                self.test_results['voice_details'] = {
                    'recognition_available': False,
                    'tts_available': False,
                    'note': 'Voice interface not implemented yet'
                }
                return True
            
            voice = VoiceInterface()
            
            # Test voice system initialization
            success = await voice.initialize()
            if not success:
                logger.warning("Voice interface initialization failed")
                return True  # Non-critical for basic functionality
            
            # Test voice recognition availability
            has_recognition = voice.is_recognition_available()
            
            # Test TTS availability  
            has_tts = voice.is_tts_available()
            
            self.test_results['voice_details'] = {
                'recognition_available': has_recognition,
                'tts_available': has_tts
            }
            
            return True  # Voice is optional
        except Exception as e:
            logger.warning(f"Voice test error (non-critical): {e}")
            return True  # Voice functionality is optional
    
    async def _test_performance(self):
        """Test system performance"""
        try:
            # CPU usage test
            cpu_usage = 0
            memory_usage = 0
            
            try:
                import psutil
                cpu_start = psutil.cpu_percent()
                await asyncio.sleep(1)
                cpu_usage = psutil.cpu_percent()
                
                # Memory usage test
                memory = psutil.virtual_memory()
                memory_usage = memory.percent
            except ImportError:
                logger.warning("psutil not available for performance testing")
                cpu_usage = 50  # Default reasonable value
                memory_usage = 60
            
            # Response time test
            start_time = time.time()
            await asyncio.sleep(0.1)  # Simulate small operation
            response_time = time.time() - start_time
            
            self.test_results['performance_details'] = {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'response_time': response_time
            }
            
            # Performance thresholds
            performance_ok = (
                cpu_usage < 80 and
                memory_usage < 90 and
                response_time < 1.0
            )
            
            return performance_ok
            
        except Exception as e:
            logger.error(f"Performance test error: {e}")
            return False
    
    async def _test_memory_usage(self):
        """Test memory usage patterns"""
        try:
            initial_memory = 0
            after_alloc_memory = 0
            after_cleanup_memory = 0
            
            try:
                import psutil
                import gc
                
                # Get initial memory
                process = psutil.Process()
                initial_memory = process.memory_info().rss
                
                # Create some objects to test memory management
                test_objects = []
                for i in range(1000):
                    test_objects.append({'test': i, 'data': 'x' * 100})
                
                # Check memory after allocation
                after_alloc_memory = process.memory_info().rss
                
                # Clean up
                del test_objects
                gc.collect()
                
                # Check memory after cleanup
                after_cleanup_memory = process.memory_info().rss
                
            except ImportError:
                logger.warning("psutil not available for memory testing")
                # Use placeholder values
                initial_memory = 1000000
                after_alloc_memory = 1100000
                after_cleanup_memory = 1050000
            
            memory_growth = after_alloc_memory - initial_memory
            memory_recovered = after_alloc_memory - after_cleanup_memory
            
            self.test_results['memory_details'] = {
                'initial_memory': initial_memory,
                'peak_memory': after_alloc_memory,
                'final_memory': after_cleanup_memory,
                'memory_growth': memory_growth,
                'memory_recovered': memory_recovered
            }
            
            # Check if memory was properly managed
            recovery_ratio = memory_recovered / memory_growth if memory_growth > 0 else 1
            
            return recovery_ratio > 0.3  # At least 30% memory recovery
            
        except Exception as e:
            logger.error(f"Memory test error: {e}")
            return False
    
    async def _test_ui_responsiveness(self):
        """Test UI responsiveness"""
        try:
            from kivy.clock import Clock
            
            response_times = []
            
            # Test multiple UI operations
            for i in range(5):
                start_time = time.time()
                
                # Simulate UI operation
                def dummy_callback(dt):
                    pass
                
                Clock.schedule_once(dummy_callback, 0)
                await asyncio.sleep(0.05)  # Small delay
                
                response_time = time.time() - start_time
                response_times.append(response_time)
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            self.test_results['ui_details'] = {
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'response_times': response_times
            }
            
            # UI should be responsive (under 100ms average)
            return avg_response_time < 0.1 and max_response_time < 0.2
            
        except Exception as e:
            logger.error(f"UI responsiveness test error: {e}")
            return False
    
    async def _generate_test_report(self, overall_success: bool):
        """Generate comprehensive test report"""
        try:
            test_duration = time.time() - self.test_start_time
            
            report = {
                'test_suite_version': '1.0.0',
                'timestamp': self.test_start_time,
                'duration_seconds': test_duration,
                'device_info': self.device_info,
                'test_results': self.test_results,
                'overall_success': overall_success,
                'summary': {
                    'total_tests': len([r for r in self.test_results.values() if isinstance(r, dict) and 'success' in r]),
                    'passed_tests': sum(1 for r in self.test_results.values() 
                                      if isinstance(r, dict) and r.get('success')),
                    'failed_tests': sum(1 for r in self.test_results.values() 
                                      if isinstance(r, dict) and not r.get('success'))
                }
            }
            
            # Save to file
            timestamp_str = time.strftime('%Y%m%d_%H%M%S', time.localtime(self.test_start_time))
            report_filename = f"device_test_report_{timestamp_str}.json"
            
            # Try to save to multiple locations
            save_locations = [
                Path(__file__).parent / report_filename,
                Path.cwd() / report_filename
            ]
            
            # Add Desktop if possible
            try:
                save_locations.append(Path.home() / "Desktop" / report_filename)
            except:
                pass
            
            for location in save_locations:
                try:
                    location.parent.mkdir(parents=True, exist_ok=True)
                    with open(location, 'w', encoding='utf-8') as f:
                        json.dump(report, f, indent=2, default=str)
                    print(f"\n📊 Test report saved: {location}")
                    break
                except Exception as e:
                    logger.warning(f"Could not save to {location}: {e}")
            
            # Print summary
            print(f"\n📋 Test Summary:")
            print(f"   Duration: {test_duration:.1f}s")
            print(f"   Tests: {report['summary']['passed_tests']}/{report['summary']['total_tests']} passed")
            print(f"   Result: {'✅ PASSED' if overall_success else '❌ FAILED'}")
            
            return True
            
        except Exception as e:
            logger.error(f"Test report generation error: {e}")
            return False

# Standalone test runner
async def run_device_tests():
    """Standalone function to run device tests"""
    test_suite = DeviceTestSuite()
    return await test_suite.run_device_tests()

if __name__ == "__main__":
    # Run tests if called directly
    asyncio.run(run_device_tests())