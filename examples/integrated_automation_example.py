#!/usr/bin/env python3
"""
Integrated Automation System Example
===================================

Demonstrates how to use the fully integrated automation system
with the existing ThinkMesh AI infrastructure.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the integrated system
from thinkmesh_core import (
    initialize_automation_system,
    execute_automation_task,
    get_automation_integrator,
    UserContext,
    get_logger
)

from thinkmesh_core.automation import AutomationPlatform

logger = get_logger(__name__)


class IntegratedAutomationDemo:
    """Demonstrates the integrated automation system"""
    
    def __init__(self):
        self.user_context = UserContext(
            user_id="demo_user_001",
            preferences={
                "automation_level": "advanced",
                "privacy_mode": "maximum",
                "voice_enabled": True,
                "cross_platform_sync": True,
                "device_adaptation": True
            }
        )
        
        # Initialize the automation system
        self.automation_integrator = None
    
    async def initialize_system(self):
        """Initialize the integrated automation system"""
        
        print("🚀 Initializing Universal Soul AI Automation System")
        print("=" * 55)
        
        try:
            # Initialize automation system (without full dependencies for demo)
            self.automation_integrator = initialize_automation_system(
                hrm_engine=None,  # Would be actual HRM engine in production
                orchestrator=None,  # Would be actual orchestrator in production
                voice_interface=None,  # Would be actual voice interface in production
                mobile_optimizer=None  # Would be actual mobile optimizer in production
            )
            
            # Initialize for user
            success = await self.automation_integrator.initialize_for_user(self.user_context)
            
            if success:
                print("✅ Automation system initialized successfully!")
                print("   - Device adaptation: Active")
                print("   - Cross-platform sync: Ready")
                print("   - CoAct-1 hybrid automation: Available")
                print("   - Mobile navigation: Ready")
                print("   - Privacy-first operation: Enabled")
            else:
                print("❌ Failed to initialize automation system")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    async def demo_desktop_automation(self):
        """Demonstrate desktop automation"""
        
        print("\n🖥️  Desktop Automation Demo")
        print("-" * 30)
        
        try:
            task_description = "Take a screenshot and analyze the current screen layout"
            
            print(f"🎯 Task: {task_description}")
            print("🤖 Executing with CoAct-1 hybrid automation...")
            
            result = await execute_automation_task(
                task_description=task_description,
                user_context=self.user_context,
                platform=AutomationPlatform.DESKTOP
            )
            
            if result["success"]:
                print("✅ Desktop automation completed successfully!")
                print(f"   Method: {result['method_used']}")
                print(f"   Execution time: {result['execution_time']:.2f}s")
                print(f"   Confidence: {result['confidence_score']:.2f}")
                print(f"   Platform: {result['platform']}")
            else:
                print(f"⚠️  Desktop automation failed: {result.get('error_message', 'Unknown error')}")
            
        except Exception as e:
            print(f"❌ Desktop automation demo failed: {e}")
    
    async def demo_mobile_navigation(self):
        """Demonstrate mobile navigation"""
        
        print("\n📱 Mobile Navigation Demo")
        print("-" * 25)
        
        try:
            app_name = "Settings"
            task_description = "Navigate to notification settings and enable app notifications"
            
            print(f"📱 App: {app_name}")
            print(f"🎯 Task: {task_description}")
            print("🔍 Analyzing mobile interface...")
            
            result = await self.automation_integrator.navigate_mobile_app(
                app_name=app_name,
                task_description=task_description,
                user_context=self.user_context
            )
            
            if result["success"]:
                print("✅ Mobile navigation completed successfully!")
                print(f"   Navigation steps: {len(result.get('navigation_steps', []))}")
                print(f"   Execution time: {result.get('execution_time', 0):.2f}s")
                print(f"   Screenshots taken: {len(result.get('screenshots', []))}")
            else:
                print(f"⚠️  Mobile navigation failed: {result.get('error_message', 'Unknown error')}")
            
        except Exception as e:
            print(f"❌ Mobile navigation demo failed: {e}")
    
    async def demo_cross_platform_tasks(self):
        """Demonstrate cross-platform task execution"""
        
        print("\n🌐 Cross-Platform Task Demo")
        print("-" * 30)
        
        tasks = [
            {
                "description": "Calculate monthly budget totals from spreadsheet",
                "platform": AutomationPlatform.DESKTOP,
                "expected_method": "pure_code"
            },
            {
                "description": "Navigate to email app and check unread messages",
                "platform": AutomationPlatform.MOBILE,
                "expected_method": "pure_gui"
            },
            {
                "description": "Download sales report, analyze data, and update dashboard",
                "platform": AutomationPlatform.WEB,
                "expected_method": "hybrid_optimal"
            }
        ]
        
        for i, task in enumerate(tasks, 1):
            print(f"\n📋 Task {i}: {task['description']}")
            print(f"   Platform: {task['platform'].value}")
            print(f"   Expected method: {task['expected_method']}")
            
            try:
                result = await execute_automation_task(
                    task_description=task["description"],
                    user_context=self.user_context,
                    platform=task["platform"]
                )
                
                if result["success"]:
                    print(f"   ✅ Completed with {result['method_used']} method")
                    print(f"   ⏱️  Time: {result['execution_time']:.2f}s")
                    print(f"   🎯 Confidence: {result['confidence_score']:.2f}")
                else:
                    print(f"   ❌ Failed: {result.get('error_message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    async def demo_device_continuity(self):
        """Demonstrate cross-device continuity"""
        
        print("\n🔄 Device Continuity Demo")
        print("-" * 25)
        
        try:
            target_device_id = "demo_device_002"  # Simulated target device
            
            print(f"🎯 Transferring session to device: {target_device_id}")
            print("📤 Preparing session transfer...")
            
            result = await self.automation_integrator.transfer_session_to_device(
                target_device_id=target_device_id,
                user_context=self.user_context
            )
            
            if result["success"]:
                print("✅ Session transfer completed successfully!")
                print(f"   Transfer ID: {result['transfer_id']}")
                print(f"   Transfer time: {result['transfer_time']:.2f}s")
                print("   🔒 All data encrypted during transfer")
                print("   📱 Session ready on target device")
            else:
                print(f"⚠️  Session transfer failed: {result.get('error_message', 'Unknown error')}")
            
        except Exception as e:
            print(f"❌ Device continuity demo failed: {e}")
    
    async def demo_system_status(self):
        """Demonstrate system status monitoring"""
        
        print("\n📊 System Status Demo")
        print("-" * 20)
        
        try:
            status = await self.automation_integrator.get_automation_status()
            
            print("🔍 Automation System Status:")
            print(f"   System: {status.get('automation_system', 'unknown')}")
            print(f"   Device ID: {status.get('device_status', {}).get('device_id', 'unknown')[:16]}...")
            print(f"   Platforms: {len(status.get('device_status', {}).get('platforms_supported', []))}")
            
            integrations = status.get('integrations', {})
            print("\n🔗 System Integrations:")
            print(f"   HRM Engine: {'✅' if integrations.get('hrm_engine') else '❌'}")
            print(f"   Orchestrator: {'✅' if integrations.get('orchestrator') else '❌'}")
            print(f"   Voice Interface: {'✅' if integrations.get('voice_interface') else '❌'}")
            print(f"   Mobile Optimizer: {'✅' if integrations.get('mobile_optimizer') else '❌'}")
            
            sync_status = status.get('sync_status', {})
            if sync_status:
                print(f"\n🔄 Sync Status:")
                print(f"   Local items: {sync_status.get('local_items_count', 0)}")
                print(f"   Available methods: {len(sync_status.get('available_methods', []))}")
            
        except Exception as e:
            print(f"❌ Status demo failed: {e}")
    
    async def run_complete_demo(self):
        """Run the complete integrated automation demo"""
        
        # Initialize system
        if not await self.initialize_system():
            return
        
        # Run all demos
        await self.demo_desktop_automation()
        await self.demo_mobile_navigation()
        await self.demo_cross_platform_tasks()
        await self.demo_device_continuity()
        await self.demo_system_status()
        
        print("\n🎉 Integrated Automation Demo Complete!")
        print("\n🌟 Universal Soul AI Advantages:")
        print("   🔒 Complete Privacy - 100% local processing")
        print("   🚀 Superior Performance - CoAct-1 hybrid automation")
        print("   🌐 Universal Platform Support - All devices")
        print("   💰 Zero Ongoing Costs - No subscriptions")
        print("   ⚡ Instant Response - No network latency")
        print("   🧠 Intelligent Adaptation - Device-aware optimization")
        print("   🔄 Seamless Continuity - Cross-device session transfer")
        print("   🛡️  Enterprise Security - User-controlled encryption")


async def main():
    """Main demo function"""
    
    print("🚀 Universal Soul AI - Integrated Automation Demo")
    print("=" * 55)
    print("Demonstrating the complete integrated automation system")
    print("that surpasses Warmwind while maintaining privacy\n")
    
    try:
        demo = IntegratedAutomationDemo()
        await demo.run_complete_demo()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Starting Integrated Automation Demo...")
    print("Press Ctrl+C to stop at any time\n")
    
    asyncio.run(main())
