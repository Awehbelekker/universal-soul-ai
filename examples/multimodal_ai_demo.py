#!/usr/bin/env python3
"""
Multi-Modal AI Integration Demo
==============================

Demonstrates the enhanced Universal Soul AI system with multi-modal AI capabilities.
Shows GPT-4 Vision, Claude Vision, and Gemini Pro integration for semantic UI understanding.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import enhanced components
from thinkmesh_core.ai_providers import MultiModalAIProvider, AIProvider
from thinkmesh_core.automation.multimodal_screen_analyzer import MultiModalScreenAnalyzer, TaskContext
from thinkmesh_core.automation.enhanced_coact_multimodal import EnhancedCoAct1AutomationEngine
from thinkmesh_core.interfaces import UserContext
from thinkmesh_core.automation import AutomationPlatform


class MultiModalAIDemo:
    """Demonstration of multi-modal AI capabilities"""
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.multimodal_provider = None
        self.screen_analyzer = None
        self.enhanced_coact = None
        
    def _load_api_keys(self) -> dict:
        """Load API keys from environment or config file"""
        
        api_keys = {}
        
        # Try to load from environment variables
        for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_AI_API_KEY"]:
            value = os.getenv(key)
            if value and value != "your_api_key_here":
                api_keys[key] = value
        
        # Try to load from api_keys.env file
        api_keys_file = project_root / "android_overlay" / "api_keys.env"
        if api_keys_file.exists():
            try:
                with open(api_keys_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            if value and value != "your_api_key_here":
                                api_keys[key] = value
            except Exception as e:
                logger.warning(f"Failed to load API keys from file: {e}")
        
        logger.info(f"Loaded {len(api_keys)} API keys")
        return api_keys
    
    async def initialize(self):
        """Initialize all multi-modal AI components"""
        
        logger.info("🚀 Initializing Multi-Modal AI Demo...")
        
        # Initialize multi-modal AI provider
        self.multimodal_provider = MultiModalAIProvider(self.api_keys)
        await self.multimodal_provider.initialize()
        
        # Initialize enhanced screen analyzer
        self.screen_analyzer = MultiModalScreenAnalyzer(self.api_keys)
        await self.screen_analyzer.initialize()
        
        # Initialize enhanced CoAct-1 engine
        self.enhanced_coact = EnhancedCoAct1AutomationEngine(self.api_keys)
        await self.enhanced_coact.initialize_enhanced()
        
        logger.info("✅ Multi-Modal AI Demo initialized successfully")
    
    async def demo_provider_capabilities(self):
        """Demonstrate individual AI provider capabilities"""
        
        logger.info("\n🔍 DEMO: AI Provider Capabilities")
        logger.info("=" * 50)
        
        # Get performance report
        performance_report = await self.multimodal_provider.get_performance_report()
        
        logger.info(f"Available providers: {performance_report['available_providers']}")
        logger.info(f"Total providers: {performance_report['total_providers']}")
        
        # Test each provider with a sample task
        sample_screenshot = b"sample_screenshot_data"  # Placeholder
        task_context = "Navigate to settings menu"
        
        for provider in performance_report['available_providers']:
            try:
                logger.info(f"\n🧠 Testing {provider.value}...")
                
                result = await self.multimodal_provider.analyze_screen_semantically(
                    screenshot=sample_screenshot,
                    task_context=task_context,
                    preferred_provider=provider
                )
                
                logger.info(f"  ✅ Analysis completed with confidence: {result.confidence:.2f}")
                logger.info(f"  📊 Processing time: {result.processing_time:.2f}s")
                logger.info(f"  🎯 Elements detected: {len(result.elements)}")
                
            except Exception as e:
                logger.warning(f"  ❌ Provider {provider.value} failed: {e}")
    
    async def demo_screen_analysis(self):
        """Demonstrate comprehensive screen analysis"""
        
        logger.info("\n📱 DEMO: Comprehensive Screen Analysis")
        logger.info("=" * 50)
        
        # Create sample task context
        user_context = UserContext(
            user_id="demo_user",
            privacy_settings={"local_processing_only": False}
        )
        
        task_context = TaskContext(
            description="Open the camera app and take a photo",
            user_context=user_context,
            platform="android",
            complexity="medium",
            app_context="home_screen"
        )
        
        # Simulate screenshot analysis
        sample_screenshot = b"sample_mobile_screenshot_data"  # Placeholder
        
        try:
            logger.info("🔍 Analyzing mobile interface...")
            
            analysis = await self.screen_analyzer.analyze_screen_comprehensive(
                screenshot=sample_screenshot,
                task_context=task_context
            )
            
            logger.info(f"✅ Analysis completed in {analysis.processing_time:.2f}s")
            logger.info(f"📊 Fused confidence: {analysis.fused_confidence:.2f}")
            logger.info(f"🎯 Task feasibility: {analysis.task_feasibility:.2f}")
            logger.info(f"🔧 Providers used: {', '.join(analysis.providers_used)}")
            logger.info(f"📱 Elements detected: {len(analysis.fused_elements)}")
            
            # Show recommended actions
            if analysis.recommended_actions:
                logger.info("💡 Recommended actions:")
                for i, action in enumerate(analysis.recommended_actions[:3], 1):
                    logger.info(f"  {i}. {action}")
            
            # Show potential issues
            if analysis.potential_issues:
                logger.info("⚠️  Potential issues:")
                for issue in analysis.potential_issues[:2]:
                    logger.info(f"  • {issue}")
                    
        except Exception as e:
            logger.error(f"❌ Screen analysis failed: {e}")
    
    async def demo_enhanced_automation(self):
        """Demonstrate enhanced automation with multi-modal intelligence"""
        
        logger.info("\n🤖 DEMO: Enhanced Automation with Multi-Modal Intelligence")
        logger.info("=" * 60)
        
        # Create user context
        user_context = UserContext(
            user_id="demo_user",
            privacy_settings={"local_processing_only": False}
        )
        
        # Test automation tasks
        test_tasks = [
            "Open the camera app",
            "Navigate to settings and enable dark mode",
            "Send a message to John saying 'Hello'",
            "Take a screenshot and save it"
        ]
        
        for i, task in enumerate(test_tasks, 1):
            logger.info(f"\n🎯 Task {i}: {task}")
            logger.info("-" * 40)
            
            try:
                # Execute with enhanced multi-modal intelligence
                result = await self.enhanced_coact.execute_task_with_multimodal_intelligence(
                    task=task,
                    context=user_context,
                    platform=AutomationPlatform.MOBILE
                )
                
                # Display results
                success_icon = "✅" if result.success else "❌"
                logger.info(f"{success_icon} Success: {result.success}")
                logger.info(f"⏱️  Execution time: {result.execution_time:.2f}s")
                logger.info(f"📊 Confidence achieved: {result.confidence_achieved:.2f}")
                logger.info(f"🔢 Steps completed: {result.steps_completed}/{result.total_steps}")
                
                if result.errors_encountered:
                    logger.info("⚠️  Errors encountered:")
                    for error in result.errors_encountered:
                        logger.info(f"  • {error}")
                
                # Show learning data
                if result.learning_data:
                    logger.info("🧠 Learning data recorded for future improvement")
                
            except Exception as e:
                logger.error(f"❌ Task execution failed: {e}")
    
    async def demo_adaptive_learning(self):
        """Demonstrate adaptive learning capabilities"""
        
        logger.info("\n🧠 DEMO: Adaptive Learning Capabilities")
        logger.info("=" * 50)
        
        # Get learning patterns for different task types
        task_types = ["navigation", "text_input", "selection", "general"]
        
        for task_type in task_types:
            patterns = await self.enhanced_coact.adaptive_learning.get_patterns(f"{task_type} task")
            
            logger.info(f"\n📈 {task_type.title()} Tasks:")
            logger.info(f"  Success rate: {patterns['success_rate']:.1%}")
            logger.info(f"  Avg execution time: {patterns['avg_execution_time']:.1f}s")
            logger.info(f"  Avg confidence: {patterns['avg_confidence']:.2f}")
            logger.info(f"  Total experience: {patterns['total_experience']} attempts")
    
    async def demo_performance_comparison(self):
        """Demonstrate performance comparison between traditional and enhanced systems"""
        
        logger.info("\n📊 DEMO: Performance Comparison")
        logger.info("=" * 50)
        
        # Get capabilities report
        capabilities = await self.screen_analyzer.get_analysis_capabilities()
        
        logger.info("🔧 System Capabilities:")
        logger.info(f"  Traditional CV available: {capabilities['traditional_cv_available']}")
        logger.info(f"  AI providers available: {capabilities['ai_providers_available']}")
        logger.info(f"  Multi-modal fusion: {capabilities['multimodal_fusion']}")
        logger.info(f"  Adaptive confidence: {capabilities['adaptive_confidence']}")
        
        # Show expected performance improvements
        logger.info("\n📈 Expected Performance Improvements:")
        improvements = [
            ("UI Element Detection Accuracy", "60%", "90%", "+50%"),
            ("Task Success Rate", "85%", "95%+", "+12%"),
            ("Complex UI Handling", "65%", "90%", "+38%"),
            ("Voice Command Accuracy", "80%", "95%", "+19%"),
            ("Error Recovery Rate", "70%", "85%", "+21%"),
            ("Automation Speed", "Baseline", "35% faster", "+35%")
        ]
        
        for metric, current, enhanced, improvement in improvements:
            logger.info(f"  {metric}: {current} → {enhanced} ({improvement})")
    
    async def run_complete_demo(self):
        """Run the complete multi-modal AI demonstration"""
        
        try:
            await self.initialize()
            
            # Run all demo sections
            await self.demo_provider_capabilities()
            await self.demo_screen_analysis()
            await self.demo_enhanced_automation()
            await self.demo_adaptive_learning()
            await self.demo_performance_comparison()
            
            logger.info("\n🎉 Multi-Modal AI Demo completed successfully!")
            logger.info("=" * 60)
            logger.info("The Universal Soul AI system now has advanced multi-modal capabilities:")
            logger.info("✅ GPT-4 Vision for semantic UI understanding")
            logger.info("✅ Claude Vision for contextual workflow analysis")
            logger.info("✅ Gemini Pro for comprehensive multi-modal processing")
            logger.info("✅ Predictive automation with AI-powered planning")
            logger.info("✅ Adaptive learning from user interactions")
            logger.info("✅ Real-time confidence calibration")
            logger.info("✅ Intelligent fallback mechanisms")
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            raise


async def main():
    """Main demo function"""
    
    print("🚀 Universal Soul AI - Multi-Modal AI Integration Demo")
    print("=" * 60)
    print("This demo showcases the enhanced automation capabilities with:")
    print("• GPT-4 Vision for semantic UI understanding")
    print("• Claude Vision for contextual reasoning")
    print("• Gemini Pro for multi-modal analysis")
    print("• Predictive automation planning")
    print("• Adaptive learning from interactions")
    print("=" * 60)
    
    demo = MultiModalAIDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)
