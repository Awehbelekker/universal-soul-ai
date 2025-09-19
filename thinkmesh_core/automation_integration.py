"""
Automation System Integration
============================

Integrates the cross-platform automation system with the existing
ThinkMesh AI infrastructure including HRM, orchestration, and voice systems.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
import logging

from .interfaces import UserContext
from .exceptions import ThinkMeshException, ErrorCode
from .logging import get_logger

# Import automation components
from .automation import (
    MobileNavigator,
    GUIAutomationEngine,
    CoAct1AutomationEngine,
    IntelligentDeviceAdapter,
    AutomationPlatform,
    ActionType,
    AutomationAction,
    DeviceType,
    ExecutionMethod
)

# Import sync components
from .sync import (
    SyncEngine,
    ContinuityManager,
    DeviceContext,
    SyncMethod
)

logger = get_logger(__name__)


class AutomationSystemIntegrator:
    """Integrates automation system with existing ThinkMesh infrastructure"""
    
    def __init__(self, hrm_engine=None, orchestrator=None, voice_interface=None, mobile_optimizer=None):
        self.hrm_engine = hrm_engine
        self.orchestrator = orchestrator
        self.voice_interface = voice_interface
        self.mobile_optimizer = mobile_optimizer
        
        # Initialize automation components with existing system integration
        self.device_adapter = IntelligentDeviceAdapter(hrm_engine, mobile_optimizer)
        self.coact_engine = CoAct1AutomationEngine(hrm_engine)
        self.mobile_navigator = MobileNavigator(hrm_engine)
        
        # Platform-specific engines
        self.automation_engines = {
            AutomationPlatform.DESKTOP: GUIAutomationEngine(AutomationPlatform.DESKTOP),
            AutomationPlatform.MOBILE: GUIAutomationEngine(AutomationPlatform.MOBILE),
            AutomationPlatform.WEB: GUIAutomationEngine(AutomationPlatform.WEB),
            AutomationPlatform.SMART_TV: GUIAutomationEngine(AutomationPlatform.SMART_TV)
        }
        
        # Sync and continuity
        self.device_id = self._generate_device_id()
        self.sync_engine = SyncEngine(self.device_id)
        self.continuity_manager = None  # Will be initialized with user_id
        
    def _generate_device_id(self) -> str:
        """Generate unique device ID"""
        import platform
        import hashlib
        
        device_info = f"{platform.node()}_{platform.system()}_{platform.machine()}"
        return hashlib.sha256(device_info.encode()).hexdigest()[:16]
    
    async def initialize_for_user(self, user_context: UserContext) -> bool:
        """Initialize automation system for specific user"""
        try:
            logger.info(f"Initializing automation system for user {user_context.user_id}")
            
            # Initialize continuity manager with user ID
            self.continuity_manager = ContinuityManager(self.device_id, user_context.user_id)
            
            # Adapt to current device
            adaptation_result = await self.device_adapter.adapt_to_device(user_context)
            logger.info(f"Device adapted: {adaptation_result.optimization_level.value}")
            
            # Start sync services if enabled
            if user_context.preferences.get("cross_platform_sync", True):
                await self._start_sync_services()
            
            # Register with orchestrator if available
            if self.orchestrator:
                await self._register_with_orchestrator(user_context)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize automation system: {e}")
            return False
    
    async def _start_sync_services(self):
        """Start synchronization services"""
        try:
            # Start local network sync
            from .sync.local_sync import LocalNetworkSync
            local_sync = LocalNetworkSync(self.device_id)
            await local_sync.start_services()
            
            logger.info("Sync services started successfully")
            
        except Exception as e:
            logger.warning(f"Failed to start sync services: {e}")
    
    async def _register_with_orchestrator(self, user_context: UserContext):
        """Register automation capabilities with orchestrator"""
        try:
            # Register automation agent with orchestrator
            automation_agent = AutomationAgent(
                agent_id=f"automation_{self.device_id}",
                capabilities=[
                    "mobile_navigation",
                    "gui_automation", 
                    "coact_hybrid_automation",
                    "cross_platform_sync",
                    "device_adaptation"
                ],
                integrator=self
            )
            
            await self.orchestrator.register_agent(automation_agent)
            logger.info("Automation agent registered with orchestrator")
            
        except Exception as e:
            logger.warning(f"Failed to register with orchestrator: {e}")
    
    async def execute_automation_task(self, task_description: str, 
                                    user_context: UserContext,
                                    platform: AutomationPlatform = AutomationPlatform.DESKTOP) -> Dict[str, Any]:
        """Execute automation task using integrated system"""
        
        try:
            logger.info(f"Executing automation task: {task_description}")
            
            # Use CoAct-1 hybrid automation for best results
            result = await self.coact_engine.execute_hybrid_task(
                task_description=task_description,
                context=user_context,
                platform=platform
            )
            
            # Add to sync if successful
            if result.success and self.sync_engine:
                await self.sync_engine.add_sync_item(
                    item_type="automation_task",
                    data={
                        "task_description": task_description,
                        "platform": platform.value,
                        "result": {
                            "success": result.success,
                            "method": result.method_used.value,
                            "execution_time": result.execution_time,
                            "confidence": result.confidence_score
                        },
                        "timestamp": time.time(),
                        "device_id": self.device_id
                    }
                )
            
            # Notify orchestrator if available
            if self.orchestrator and result.success:
                await self._notify_orchestrator_success(task_description, result)
            
            return {
                "success": result.success,
                "method_used": result.method_used.value,
                "execution_time": result.execution_time,
                "confidence_score": result.confidence_score,
                "error_message": result.error_message,
                "platform": platform.value
            }
            
        except Exception as e:
            logger.error(f"Automation task execution failed: {e}")
            return {
                "success": False,
                "error_message": str(e),
                "platform": platform.value
            }
    
    async def _notify_orchestrator_success(self, task_description: str, result):
        """Notify orchestrator of successful automation"""
        try:
            await self.orchestrator.notify_task_completion(
                task_id=f"automation_{int(time.time())}",
                agent_id=f"automation_{self.device_id}",
                result={
                    "task": task_description,
                    "success": True,
                    "method": result.method_used.value,
                    "confidence": result.confidence_score
                }
            )
        except Exception as e:
            logger.warning(f"Failed to notify orchestrator: {e}")
    
    async def navigate_mobile_app(self, app_name: str, task_description: str,
                                 user_context: UserContext) -> Dict[str, Any]:
        """Navigate mobile app using integrated system"""
        
        try:
            result = await self.mobile_navigator.navigate_mobile_app(
                app_name=app_name,
                task_description=task_description,
                context=user_context
            )
            
            return {
                "success": result.get("success", False),
                "navigation_steps": result.get("navigation_steps", []),
                "execution_time": result.get("execution_time", 0),
                "screenshots": result.get("screenshots", [])
            }
            
        except Exception as e:
            logger.error(f"Mobile navigation failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def transfer_session_to_device(self, target_device_id: str,
                                       user_context: UserContext) -> Dict[str, Any]:
        """Transfer current session to another device"""
        
        if not self.continuity_manager:
            return {
                "success": False,
                "error_message": "Continuity manager not initialized"
            }
        
        try:
            # Start session if not already active
            session_id = await self.continuity_manager.start_session(
                conversation_context={
                    "current_task": "automation_session",
                    "user_preferences": user_context.preferences,
                    "device_state": await self._get_current_device_state()
                },
                device_context=DeviceContext(
                    device_id=self.device_id,
                    device_type="desktop",  # Would be detected
                    device_name="Current Device",
                    capabilities=["automation", "sync", "voice"],
                    last_active=time.time(),
                    battery_level=1.0,
                    network_quality="good"
                )
            )
            
            # Transfer session
            transfer_result = await self.continuity_manager.transfer_session(
                session_id=session_id,
                target_device_id=target_device_id,
                user_context=user_context
            )
            
            return {
                "success": transfer_result.success,
                "transfer_id": transfer_result.transfer_id,
                "transfer_time": transfer_result.transfer_time,
                "error_message": transfer_result.error_message
            }
            
        except Exception as e:
            logger.error(f"Session transfer failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def _get_current_device_state(self) -> Dict[str, Any]:
        """Get current device state for session transfer"""
        
        return {
            "active_automations": [],  # Would track active automation tasks
            "device_adaptation": "optimized",
            "sync_status": "active",
            "timestamp": time.time()
        }
    
    async def get_automation_status(self) -> Dict[str, Any]:
        """Get comprehensive automation system status"""
        
        try:
            # Get sync status
            sync_status = await self.sync_engine.get_sync_status() if self.sync_engine else {}
            
            # Get device adaptation status
            device_status = {
                "device_id": self.device_id,
                "adaptation_active": True,
                "platforms_supported": [p.value for p in AutomationPlatform]
            }
            
            # Get continuity status
            continuity_status = {
                "manager_initialized": self.continuity_manager is not None,
                "active_sessions": 0  # Would count active sessions
            }
            
            return {
                "automation_system": "active",
                "device_status": device_status,
                "sync_status": sync_status,
                "continuity_status": continuity_status,
                "integrations": {
                    "hrm_engine": self.hrm_engine is not None,
                    "orchestrator": self.orchestrator is not None,
                    "voice_interface": self.voice_interface is not None,
                    "mobile_optimizer": self.mobile_optimizer is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get automation status: {e}")
            return {
                "automation_system": "error",
                "error_message": str(e)
            }


class AutomationAgent:
    """Automation agent for orchestrator integration"""
    
    def __init__(self, agent_id: str, capabilities: List[str], integrator: AutomationSystemIntegrator):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.integrator = integrator
        
    async def execute_task(self, task: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Execute automation task through orchestrator"""
        
        task_type = task.get("type", "automation")
        task_description = task.get("description", "")
        platform = AutomationPlatform(task.get("platform", "desktop"))
        
        if task_type == "automation":
            return await self.integrator.execute_automation_task(
                task_description, user_context, platform
            )
        elif task_type == "mobile_navigation":
            app_name = task.get("app_name", "")
            return await self.integrator.navigate_mobile_app(
                app_name, task_description, user_context
            )
        elif task_type == "session_transfer":
            target_device = task.get("target_device", "")
            return await self.integrator.transfer_session_to_device(
                target_device, user_context
            )
        else:
            return {
                "success": False,
                "error_message": f"Unknown task type: {task_type}"
            }
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return self.capabilities


# Global integrator instance
_automation_integrator: Optional[AutomationSystemIntegrator] = None


def get_automation_integrator() -> Optional[AutomationSystemIntegrator]:
    """Get global automation integrator instance"""
    return _automation_integrator


def initialize_automation_system(hrm_engine=None, orchestrator=None, 
                                voice_interface=None, mobile_optimizer=None) -> AutomationSystemIntegrator:
    """Initialize global automation system"""
    global _automation_integrator
    
    _automation_integrator = AutomationSystemIntegrator(
        hrm_engine=hrm_engine,
        orchestrator=orchestrator,
        voice_interface=voice_interface,
        mobile_optimizer=mobile_optimizer
    )
    
    logger.info("Automation system initialized successfully")
    return _automation_integrator


async def execute_automation_task(task_description: str, user_context: UserContext,
                                 platform: AutomationPlatform = AutomationPlatform.DESKTOP) -> Dict[str, Any]:
    """Execute automation task using global integrator"""
    
    integrator = get_automation_integrator()
    if not integrator:
        return {
            "success": False,
            "error_message": "Automation system not initialized"
        }
    
    return await integrator.execute_automation_task(task_description, user_context, platform)
