"""
Universal Soul AI Overlay Test Suite
===================================

Comprehensive testing framework for the Android overlay system.
Tests all components individually and as an integrated system.

Test Categories:
- Unit tests for individual components
- Integration tests for component interaction
- Performance tests for mobile optimization
- Privacy tests for data protection
- User experience tests for interface quality
"""

import asyncio
import unittest
import time
import json
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, AsyncMock
import logging

# Import test targets
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from android_overlay.universal_soul_overlay import UniversalSoulOverlay, OverlayConfig
from android_overlay.core.overlay_service import AndroidOverlayService, OverlayState
from android_overlay.core.gesture_handler import GestureHandler, GestureDirection, GestureEvent, GestureType
from android_overlay.core.context_analyzer import ContextAnalyzer, AppContext, AppCategory
from android_overlay.ui.overlay_view import OverlayView, OverlayTheme

# Configure test logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestOverlayService(unittest.IsolatedAsyncioTestCase):
    """Test cases for AndroidOverlayService"""
    
    async def asyncSetUp(self):
        """Set up test environment"""
        self.config = OverlayConfig(
            overlay_size=100,
            continuous_listening=False,  # Disable for testing
            local_processing_only=True
        )
        self.service = AndroidOverlayService(self.config)
    
    async def test_service_initialization(self):
        """Test overlay service initialization"""
        # Test initialization
        result = await self.service.initialize()
        self.assertTrue(result, "Service should initialize successfully")
        self.assertTrue(self.service.is_initialized, "Service should be marked as initialized")
    
    async def test_overlay_state_management(self):
        """Test overlay state transitions"""
        await self.service.initialize()
        
        # Test show overlay
        await self.service.show_overlay()
        self.assertEqual(self.service.state, OverlayState.MINIMIZED)
        
        # Test hide overlay
        await self.service.hide_overlay()
        self.assertEqual(self.service.state, OverlayState.HIDDEN)
    
    async def test_permission_handling(self):
        """Test Android permission management"""
        # Mock permission methods
        with patch.object(self.service, '_has_overlay_permission', return_value=True), \
             patch.object(self.service, '_has_microphone_permission', return_value=True), \
             patch.object(self.service, '_has_accessibility_permission', return_value=True):
            
            result = await self.service._request_permissions()
            self.assertTrue(result, "Permissions should be granted successfully")


class TestGestureHandler(unittest.IsolatedAsyncioTestCase):
    """Test cases for GestureHandler"""
    
    async def asyncSetUp(self):
        """Set up test environment"""
        self.handler = GestureHandler(sensitivity=0.8, timeout=2.0, haptic_enabled=False)
        await self.handler.initialize()
    
    def test_direction_calculation(self):
        """Test 8-direction gesture calculation"""
        test_cases = [
            ((50, 50), (100, 50), GestureDirection.EAST),      # Right
            ((50, 50), (50, 0), GestureDirection.NORTH),       # Up
            ((50, 50), (0, 50), GestureDirection.WEST),        # Left
            ((50, 50), (50, 100), GestureDirection.SOUTH),     # Down
            ((50, 50), (100, 0), GestureDirection.NORTHEAST),  # Up-Right
            ((50, 50), (0, 0), GestureDirection.NORTHWEST),    # Up-Left
            ((50, 50), (100, 100), GestureDirection.SOUTHEAST), # Down-Right
            ((50, 50), (0, 100), GestureDirection.SOUTHWEST)   # Down-Left
        ]
        
        for start, end, expected_direction in test_cases:
            direction = self.handler._calculate_direction(start, end)
            self.assertEqual(direction, expected_direction, 
                           f"Direction calculation failed for {start} -> {end}")
    
    def test_confidence_calculation(self):
        """Test gesture confidence scoring"""
        # Test optimal gesture
        confidence = self.handler._calculate_confidence(
            distance=100.0,  # Optimal distance
            velocity=500.0,  # Optimal velocity
            duration=0.5     # Good duration
        )
        self.assertGreater(confidence, 0.8, "Optimal gesture should have high confidence")
        
        # Test poor gesture
        confidence = self.handler._calculate_confidence(
            distance=10.0,   # Too short
            velocity=50.0,   # Too slow
            duration=2.0     # Too long
        )
        self.assertLess(confidence, 0.5, "Poor gesture should have low confidence")
    
    def test_gesture_recognition(self):
        """Test complete gesture recognition"""
        # Test swipe gesture
        gesture = self.handler._recognize_gesture(
            start=(50, 50),
            end=(150, 50),
            distance=100.0,
            velocity=300.0,
            duration=0.5,
            timestamp=time.time()
        )
        
        self.assertIsNotNone(gesture, "Valid gesture should be recognized")
        self.assertEqual(gesture.gesture_type, GestureType.SWIPE)
        self.assertEqual(gesture.direction, GestureDirection.EAST)
        self.assertGreater(gesture.confidence, 0.7)
    
    def test_gesture_mapping(self):
        """Test contextual gesture mappings"""
        # Test default mapping
        action = self.handler.get_gesture_mapping("default", GestureDirection.NORTH)
        self.assertEqual(action, "calendar", "North gesture should map to calendar")
        
        # Test custom mapping
        custom_mappings = {GestureDirection.NORTH: "custom_action"}
        self.handler.update_context_mappings("test_context", custom_mappings)
        
        action = self.handler.get_gesture_mapping("test_context", GestureDirection.NORTH)
        self.assertEqual(action, "custom_action", "Custom mapping should override default")


class TestContextAnalyzer(unittest.IsolatedAsyncioTestCase):
    """Test cases for ContextAnalyzer"""
    
    async def asyncSetUp(self):
        """Set up test environment"""
        self.analyzer = ContextAnalyzer(privacy_mode=True, update_interval=0.1)
        await self.analyzer.initialize()
    
    def test_app_categorization(self):
        """Test app category detection"""
        # Test known apps
        category = self.analyzer.app_categories.get("com.whatsapp")
        self.assertEqual(category, AppCategory.COMMUNICATION)
        
        category = self.analyzer.app_categories.get("com.google.android.apps.docs.editors.docs")
        self.assertEqual(category, AppCategory.PRODUCTIVITY)
        
        category = self.analyzer.app_categories.get("com.android.chrome")
        self.assertEqual(category, AppCategory.BROWSER)
    
    def test_contextual_features(self):
        """Test contextual feature mapping"""
        # Test communication features
        features = self.analyzer.context_features[AppCategory.COMMUNICATION]
        self.assertIn("transcribe_voice", features.primary_actions)
        self.assertIn("voice_transcription", features.gesture_mappings.values())
        
        # Test productivity features
        features = self.analyzer.context_features[AppCategory.PRODUCTIVITY]
        self.assertIn("voice_to_text", features.primary_actions)
        self.assertIn("create_task", features.primary_actions)
    
    async def test_context_monitoring(self):
        """Test context monitoring functionality"""
        # Mock context change callback
        callback_called = False
        test_context = None
        
        def mock_callback(context):
            nonlocal callback_called, test_context
            callback_called = True
            test_context = context
        
        self.analyzer.on_context_changed = mock_callback
        
        # Simulate context update
        await self.analyzer._update_context()
        
        # Wait for callback
        await asyncio.sleep(0.2)
        
        self.assertTrue(callback_called, "Context change callback should be called")
        self.assertIsNotNone(test_context, "Context should be provided to callback")
    
    def test_gesture_mapping_retrieval(self):
        """Test gesture mapping for current context"""
        # Set up mock context
        mock_context = AppContext(
            package_name="com.whatsapp",
            app_name="WhatsApp",
            category=AppCategory.COMMUNICATION,
            activity_name="com.whatsapp.MainActivity",
            is_foreground=True,
            timestamp=time.time()
        )
        
        self.analyzer.current_context = mock_context
        
        # Test gesture mapping
        action = self.analyzer.get_gesture_mapping("north")
        self.assertEqual(action, "voice_transcription")


class TestOverlayView(unittest.IsolatedAsyncioTestCase):
    """Test cases for OverlayView"""
    
    async def asyncSetUp(self):
        """Set up test environment"""
        self.view = OverlayView(size=120)
        await self.view.initialize()
    
    def test_view_initialization(self):
        """Test overlay view initialization"""
        self.assertTrue(self.view.is_initialized, "View should be initialized")
        self.assertIsNotNone(self.view.root_view, "Root view should be created")
    
    def test_state_management(self):
        """Test overlay state transitions"""
        # Test state changes
        self.view.update_state(OverlayState.ACTIVE)
        self.assertEqual(self.view.state, OverlayState.ACTIVE)
        
        self.view.update_state(OverlayState.LISTENING)
        self.assertEqual(self.view.state, OverlayState.LISTENING)
    
    def test_context_appearance_update(self):
        """Test context-based appearance updates"""
        # Test appearance update
        self.view.update_context_appearance("communication", OverlayTheme.LISTENING, "💬")
        
        self.assertEqual(self.view.current_context_color, OverlayTheme.LISTENING)
        self.assertEqual(self.view.current_context_icon, "💬")
    
    def test_gesture_indicators(self):
        """Test gesture indicator management"""
        # Test showing indicators
        self.view._show_gesture_indicators()
        self.assertTrue(self.view.gesture_ring_visible)
        
        # Test hiding indicators
        self.view._hide_gesture_indicators()
        self.assertFalse(self.view.gesture_ring_visible)
    
    def test_color_conversion(self):
        """Test color utility functions"""
        # Test hex to RGBA conversion
        rgba = self.view._hex_to_rgba("#1976D2", 0.8)
        self.assertEqual(len(rgba), 4)
        self.assertAlmostEqual(rgba[3], 0.8)  # Alpha channel
        
        # Test color to int conversion
        color_int = self.view._color_to_int("#1976D2")
        self.assertIsInstance(color_int, int)


class TestIntegratedOverlay(unittest.IsolatedAsyncioTestCase):
    """Integration tests for complete overlay system"""
    
    async def asyncSetUp(self):
        """Set up test environment"""
        self.config = OverlayConfig(
            overlay_size=100,
            continuous_listening=False,
            local_processing_only=True
        )
        self.overlay = UniversalSoulOverlay(self.config)
    
    async def test_complete_initialization(self):
        """Test complete overlay system initialization"""
        result = await self.overlay.initialize()
        self.assertTrue(result, "Complete overlay system should initialize")
        self.assertTrue(self.overlay.is_initialized)
    
    async def test_start_stop_cycle(self):
        """Test overlay start/stop lifecycle"""
        await self.overlay.initialize()
        
        # Test start
        result = await self.overlay.start()
        self.assertTrue(result, "Overlay should start successfully")
        self.assertTrue(self.overlay.is_running)
        
        # Test stop
        await self.overlay.stop()
        self.assertFalse(self.overlay.is_running)
    
    async def test_gesture_to_action_flow(self):
        """Test complete gesture-to-action workflow"""
        await self.overlay.initialize()
        await self.overlay.start()
        
        # Create mock gesture event
        mock_gesture = GestureEvent(
            gesture_type=GestureType.SWIPE,
            direction=GestureDirection.NORTH,
            start_point=(50, 50),
            end_point=(50, 0),
            velocity=300.0,
            distance=50.0,
            duration=0.5,
            confidence=0.9,
            timestamp=time.time()
        )
        
        # Test gesture handling
        await self.overlay._on_gesture_detected(mock_gesture)
        
        # Verify stats updated
        self.assertGreater(self.overlay.stats.gestures_recognized, 0)
    
    async def test_context_adaptation_flow(self):
        """Test context change to UI adaptation workflow"""
        await self.overlay.initialize()
        await self.overlay.start()
        
        # Create mock context
        mock_context = AppContext(
            package_name="com.whatsapp",
            app_name="WhatsApp",
            category=AppCategory.COMMUNICATION,
            activity_name="com.whatsapp.MainActivity",
            is_foreground=True,
            timestamp=time.time()
        )
        
        # Test context handling
        await self.overlay._on_context_changed(mock_context)
        
        # Verify context updated
        self.assertEqual(self.overlay.current_context, mock_context)
        self.assertGreater(self.overlay.stats.context_switches, 0)


class PerformanceTestSuite:
    """Performance testing for mobile optimization"""
    
    def __init__(self):
        self.results = {}
    
    async def test_gesture_recognition_performance(self):
        """Test gesture recognition speed"""
        handler = GestureHandler()
        await handler.initialize()
        
        # Test multiple gesture recognitions
        start_time = time.time()
        iterations = 100
        
        for _ in range(iterations):
            handler._recognize_gesture(
                start=(50, 50),
                end=(100, 50),
                distance=50.0,
                velocity=200.0,
                duration=0.5,
                timestamp=time.time()
            )
        
        end_time = time.time()
        avg_time = (end_time - start_time) / iterations * 1000  # ms
        
        self.results['gesture_recognition_ms'] = avg_time
        return avg_time < 10  # Should be under 10ms
    
    async def test_context_analysis_performance(self):
        """Test context analysis speed"""
        analyzer = ContextAnalyzer()
        await analyzer.initialize()
        
        # Test context updates
        start_time = time.time()
        iterations = 50
        
        for _ in range(iterations):
            await analyzer._get_simulated_context()
        
        end_time = time.time()
        avg_time = (end_time - start_time) / iterations * 1000  # ms
        
        self.results['context_analysis_ms'] = avg_time
        return avg_time < 50  # Should be under 50ms
    
    async def test_memory_usage(self):
        """Test memory footprint"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create overlay system
        overlay = UniversalSoulOverlay()
        await overlay.initialize()
        await overlay.start()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_usage = final_memory - initial_memory
        
        await overlay.stop()
        
        self.results['memory_usage_mb'] = memory_usage
        return memory_usage < 100  # Should be under 100MB
    
    def get_results(self) -> Dict[str, Any]:
        """Get performance test results"""
        return self.results


async def run_all_tests():
    """Run complete test suite"""
    print("🧪 Universal Soul AI Overlay - Test Suite")
    print("=" * 50)
    
    # Unit tests
    print("📋 Running unit tests...")
    unittest_loader = unittest.TestLoader()
    unittest_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestOverlayService,
        TestGestureHandler,
        TestContextAnalyzer,
        TestOverlayView,
        TestIntegratedOverlay
    ]
    
    for test_class in test_classes:
        tests = unittest_loader.loadTestsFromTestCase(test_class)
        unittest_suite.addTests(tests)
    
    # Run unit tests
    runner = unittest.TextTestRunner(verbosity=2)
    unit_result = runner.run(unittest_suite)
    
    # Performance tests
    print("\n⚡ Running performance tests...")
    perf_suite = PerformanceTestSuite()
    
    gesture_perf = await perf_suite.test_gesture_recognition_performance()
    context_perf = await perf_suite.test_context_analysis_performance()
    memory_perf = await perf_suite.test_memory_usage()
    
    perf_results = perf_suite.get_results()
    
    # Results summary
    print("\n📊 Test Results Summary")
    print("-" * 30)
    print(f"Unit Tests: {unit_result.testsRun} run, {len(unit_result.failures)} failed, {len(unit_result.errors)} errors")
    print(f"Performance Tests: {'✅ PASS' if all([gesture_perf, context_perf, memory_perf]) else '❌ FAIL'}")
    
    print("\n⚡ Performance Metrics:")
    for metric, value in perf_results.items():
        print(f"   {metric}: {value:.2f}")
    
    # Overall result
    overall_success = (unit_result.wasSuccessful() and 
                      gesture_perf and context_perf and memory_perf)
    
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success


if __name__ == "__main__":
    asyncio.run(run_all_tests())
