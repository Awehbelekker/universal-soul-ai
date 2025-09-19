"""
Intelligent Device Adaptation System
===================================

Automatically adapts AI behavior and interface based on device
capabilities, user context, and environmental constraints.
Provides device-specific optimization for maximum performance.
"""

import asyncio
import platform
import psutil
import time
from typing import Dict, Any, List, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

from ..interfaces import UserContext
from ..exceptions import ThinkMeshException, ErrorCode
from ..logging import get_logger

logger = get_logger(__name__)


class DeviceType(Enum):
    """Types of devices supported"""
    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    SMART_TV = "smart_tv"
    SMART_SPEAKER = "smart_speaker"
    UNKNOWN = "unknown"


class OptimizationLevel(Enum):
    """Levels of optimization"""
    MINIMAL = "minimal"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    MAXIMUM = "maximum"


@dataclass
class DeviceCapabilities:
    """Device capability information"""
    cpu_cores: int
    memory_gb: float
    storage_gb: float
    screen_resolution: Optional[Tuple[int, int]]
    has_touchscreen: bool
    has_keyboard: bool
    has_mouse: bool
    has_camera: bool
    has_microphone: bool
    has_speakers: bool
    battery_powered: bool
    network_capabilities: List[str]


@dataclass
class DeviceConstraints:
    """Current device constraints"""
    battery_level: float  # 0.0 to 1.0
    thermal_state: str    # "normal", "warm", "hot"
    memory_pressure: float  # 0.0 to 1.0
    cpu_usage: float      # 0.0 to 1.0
    network_quality: str  # "poor", "good", "excellent"
    storage_available: float  # GB available


@dataclass
class AdaptationResult:
    """Result of device adaptation"""
    optimization_level: OptimizationLevel
    interface_mode: str
    performance_profile: str
    battery_optimization: bool
    accessibility_features: List[str]
    recommended_settings: Dict[str, Any]


class IntelligentDeviceAdapter:
    """Adapts AI system to device capabilities and constraints"""
    
    def __init__(self, hrm_engine=None, mobile_optimizer=None):
        self.hrm_engine = hrm_engine
        self.mobile_optimizer = mobile_optimizer
        self.device_profiler = DeviceProfiler()
        self.adaptation_strategies = AdaptationStrategies()
        self.performance_monitor = PerformanceMonitor()
        
    async def adapt_to_device(self, user_context: UserContext,
                             device_info: Optional[Dict[str, Any]] = None) -> AdaptationResult:
        """Adapt AI system to current device"""
        try:
            # Profile current device if not provided
            if not device_info:
                device_info = await self.device_profiler.profile_current_device()
            
            # Get current constraints
            current_constraints = await self._get_current_constraints()
            
            # Determine adaptation strategy
            if self.hrm_engine:
                adaptation_strategy = await self._create_hrm_adaptation_strategy(
                    device_info, current_constraints, user_context
                )
            else:
                adaptation_strategy = await self._create_heuristic_adaptation_strategy(
                    device_info, current_constraints, user_context
                )
            
            # Apply device-specific optimizations
            adaptation_result = await self._apply_device_optimizations(
                strategy=adaptation_strategy,
                device_info=device_info,
                constraints=current_constraints,
                user_context=user_context
            )
            
            # Update mobile optimizer if available
            if self.mobile_optimizer and device_info.get("device_type") in ["smartphone", "tablet"]:
                await self.mobile_optimizer.update_device_state(
                    battery_level=current_constraints.battery_level,
                    thermal_state=current_constraints.thermal_state,
                    memory_pressure=current_constraints.memory_pressure,
                    cpu_usage=current_constraints.cpu_usage,
                    network_quality=current_constraints.network_quality
                )
            
            logger.info(f"Device adaptation completed: {adaptation_result.optimization_level.value}")
            return adaptation_result
            
        except Exception as e:
            logger.error(f"Device adaptation failed: {e}")
            raise ThinkMeshException(
                f"Device adaptation error: {e}",
                ErrorCode.DEVICE_ADAPTATION_FAILED
            )
    
    async def _get_current_constraints(self) -> DeviceConstraints:
        """Get current device constraints"""
        
        # Get battery level (if available)
        battery_level = await self._get_battery_level()
        
        # Get thermal state
        thermal_state = await self._get_thermal_state()
        
        # Get memory pressure
        memory_info = psutil.virtual_memory()
        memory_pressure = memory_info.percent / 100.0
        
        # Get CPU usage
        cpu_usage = psutil.cpu_percent(interval=1) / 100.0
        
        # Get network quality
        network_quality = await self._assess_network_quality()
        
        # Get available storage
        disk_info = psutil.disk_usage('/')
        storage_available = disk_info.free / (1024**3)  # Convert to GB
        
        return DeviceConstraints(
            battery_level=battery_level,
            thermal_state=thermal_state,
            memory_pressure=memory_pressure,
            cpu_usage=cpu_usage,
            network_quality=network_quality,
            storage_available=storage_available
        )
    
    async def _get_battery_level(self) -> float:
        """Get battery level (0.0 to 1.0)"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return battery.percent / 100.0
            else:
                return 1.0  # Assume full if no battery (desktop)
        except:
            return 1.0  # Default to full battery
    
    async def _get_thermal_state(self) -> str:
        """Get thermal state of device"""
        try:
            # Try to get temperature sensors
            temps = psutil.sensors_temperatures()
            if temps:
                # Get average temperature
                all_temps = []
                for name, entries in temps.items():
                    for entry in entries:
                        if entry.current:
                            all_temps.append(entry.current)
                
                if all_temps:
                    avg_temp = sum(all_temps) / len(all_temps)
                    if avg_temp > 80:
                        return "hot"
                    elif avg_temp > 60:
                        return "warm"
                    else:
                        return "normal"
            
            return "normal"  # Default
        except:
            return "normal"
    
    async def _assess_network_quality(self) -> str:
        """Assess network quality"""
        try:
            # Simple network assessment based on interface stats
            net_io = psutil.net_io_counters()
            if net_io:
                # This is a simplified assessment
                # In practice, you'd measure latency, bandwidth, etc.
                return "good"  # Default
            else:
                return "poor"
        except:
            return "good"  # Default
    
    async def _create_hrm_adaptation_strategy(self, device_info: Dict[str, Any],
                                            constraints: DeviceConstraints,
                                            user_context: UserContext) -> Dict[str, Any]:
        """Create adaptation strategy using HRM reasoning"""
        try:
            # Create detailed prompt for HRM
            adaptation_prompt = (
                f"Create device adaptation strategy for:\n"
                f"Device Type: {device_info.get('device_type', 'unknown')}\n"
                f"CPU Cores: {device_info.get('hardware_info', {}).get('cpu_count', 'unknown')}\n"
                f"Memory: {device_info.get('hardware_info', {}).get('memory_total', 0) / (1024**3):.1f}GB\n"
                f"Battery Level: {constraints.battery_level * 100:.0f}%\n"
                f"Thermal State: {constraints.thermal_state}\n"
                f"Memory Pressure: {constraints.memory_pressure * 100:.0f}%\n"
                f"CPU Usage: {constraints.cpu_usage * 100:.0f}%\n"
                f"Network Quality: {constraints.network_quality}\n"
                f"Recommend optimization level, interface mode, and performance settings."
            )
            
            hrm_response = await self.hrm_engine.process_request(adaptation_prompt, user_context)
            
            # Parse HRM response into strategy
            strategy = await self._parse_hrm_adaptation_response(hrm_response, device_info, constraints)
            
            return strategy
            
        except Exception as e:
            logger.warning(f"HRM adaptation strategy failed, using fallback: {e}")
            return await self._create_heuristic_adaptation_strategy(device_info, constraints, user_context)
    
    async def _create_heuristic_adaptation_strategy(self, device_info: Dict[str, Any],
                                                  constraints: DeviceConstraints,
                                                  user_context: UserContext) -> Dict[str, Any]:
        """Create adaptation strategy using heuristic rules"""
        
        device_type = DeviceType(device_info.get('device_type', 'unknown'))
        
        # Determine optimization level based on constraints
        if constraints.battery_level < 0.2 or constraints.thermal_state == "hot":
            optimization_level = OptimizationLevel.AGGRESSIVE
        elif constraints.memory_pressure > 0.8 or constraints.cpu_usage > 0.8:
            optimization_level = OptimizationLevel.MODERATE
        else:
            optimization_level = OptimizationLevel.MINIMAL
        
        # Determine interface mode based on device type
        if device_type in [DeviceType.SMARTPHONE, DeviceType.TABLET]:
            interface_mode = "touch_primary"
        elif device_type == DeviceType.SMART_TV:
            interface_mode = "voice_remote_primary"
        elif device_type == DeviceType.SMART_SPEAKER:
            interface_mode = "voice_only"
        else:
            interface_mode = "keyboard_mouse_primary"
        
        # Determine performance profile
        if device_type in [DeviceType.SMARTPHONE, DeviceType.TABLET]:
            performance_profile = "battery_optimized"
        elif device_type == DeviceType.DESKTOP:
            performance_profile = "performance_optimized"
        else:
            performance_profile = "balanced"
        
        return {
            "optimization_level": optimization_level,
            "interface_mode": interface_mode,
            "performance_profile": performance_profile,
            "device_type": device_type,
            "constraints": constraints
        }
    
    async def _parse_hrm_adaptation_response(self, hrm_response: str,
                                           device_info: Dict[str, Any],
                                           constraints: DeviceConstraints) -> Dict[str, Any]:
        """Parse HRM response into adaptation strategy"""
        
        response_lower = hrm_response.lower()
        
        # Parse optimization level
        if 'aggressive' in response_lower or 'maximum' in response_lower:
            optimization_level = OptimizationLevel.AGGRESSIVE
        elif 'moderate' in response_lower:
            optimization_level = OptimizationLevel.MODERATE
        elif 'minimal' in response_lower:
            optimization_level = OptimizationLevel.MINIMAL
        else:
            optimization_level = OptimizationLevel.MODERATE  # Default
        
        # Parse interface mode
        if 'touch' in response_lower:
            interface_mode = "touch_primary"
        elif 'voice' in response_lower:
            interface_mode = "voice_primary"
        elif 'keyboard' in response_lower or 'mouse' in response_lower:
            interface_mode = "keyboard_mouse_primary"
        else:
            interface_mode = "adaptive"
        
        # Parse performance profile
        if 'battery' in response_lower:
            performance_profile = "battery_optimized"
        elif 'performance' in response_lower:
            performance_profile = "performance_optimized"
        else:
            performance_profile = "balanced"
        
        return {
            "optimization_level": optimization_level,
            "interface_mode": interface_mode,
            "performance_profile": performance_profile,
            "device_type": DeviceType(device_info.get('device_type', 'unknown')),
            "constraints": constraints,
            "hrm_reasoning": hrm_response[:200] + "..." if len(hrm_response) > 200 else hrm_response
        }
    
    async def _apply_device_optimizations(self, strategy: Dict[str, Any],
                                        device_info: Dict[str, Any],
                                        constraints: DeviceConstraints,
                                        user_context: UserContext) -> AdaptationResult:
        """Apply device-specific optimizations based on strategy"""
        
        device_type = strategy["device_type"]
        optimization_level = strategy["optimization_level"]
        
        if device_type in [DeviceType.SMARTPHONE, DeviceType.TABLET]:
            return await self._optimize_for_mobile(strategy, device_info, constraints, user_context)
        elif device_type in [DeviceType.DESKTOP, DeviceType.LAPTOP]:
            return await self._optimize_for_desktop(strategy, device_info, constraints, user_context)
        elif device_type == DeviceType.SMART_TV:
            return await self._optimize_for_tv(strategy, device_info, constraints, user_context)
        elif device_type == DeviceType.SMART_SPEAKER:
            return await self._optimize_for_voice_only(strategy, device_info, constraints, user_context)
        else:
            return await self._optimize_for_generic(strategy, device_info, constraints, user_context)
    
    async def _optimize_for_mobile(self, strategy: Dict[str, Any], device_info: Dict[str, Any],
                                 constraints: DeviceConstraints, user_context: UserContext) -> AdaptationResult:
        """Optimize for mobile devices"""
        
        accessibility_features = ["voice_control", "large_text", "haptic_feedback"]
        
        # Add accessibility features based on user preferences
        if user_context.preferences.get("high_contrast", False):
            accessibility_features.append("high_contrast")
        
        if user_context.preferences.get("voice_navigation", False):
            accessibility_features.append("voice_navigation")
        
        recommended_settings = {
            "animation_scale": 0.5 if strategy["optimization_level"] == OptimizationLevel.AGGRESSIVE else 1.0,
            "background_processing": "limited" if constraints.battery_level < 0.3 else "normal",
            "screen_brightness": "auto_adaptive",
            "notification_frequency": "reduced" if strategy["optimization_level"] == OptimizationLevel.AGGRESSIVE else "normal",
            "cache_size": "small" if constraints.memory_pressure > 0.7 else "normal"
        }
        
        return AdaptationResult(
            optimization_level=strategy["optimization_level"],
            interface_mode="touch_primary",
            performance_profile="battery_optimized",
            battery_optimization=True,
            accessibility_features=accessibility_features,
            recommended_settings=recommended_settings
        )
    
    async def _optimize_for_desktop(self, strategy: Dict[str, Any], device_info: Dict[str, Any],
                                  constraints: DeviceConstraints, user_context: UserContext) -> AdaptationResult:
        """Optimize for desktop/laptop devices"""
        
        accessibility_features = ["keyboard_shortcuts", "screen_reader_support", "zoom_controls"]
        
        # Add laptop-specific optimizations
        is_laptop = device_info.get('device_type') == 'laptop'
        battery_optimization = is_laptop and constraints.battery_level < 0.5
        
        recommended_settings = {
            "multi_window_support": True,
            "keyboard_shortcuts_enabled": True,
            "high_dpi_scaling": "auto",
            "performance_mode": "high" if not battery_optimization else "balanced",
            "background_tasks": "unlimited" if not battery_optimization else "limited"
        }
        
        return AdaptationResult(
            optimization_level=strategy["optimization_level"],
            interface_mode="keyboard_mouse_primary",
            performance_profile="performance_optimized" if not battery_optimization else "balanced",
            battery_optimization=battery_optimization,
            accessibility_features=accessibility_features,
            recommended_settings=recommended_settings
        )
    
    async def _optimize_for_tv(self, strategy: Dict[str, Any], device_info: Dict[str, Any],
                             constraints: DeviceConstraints, user_context: UserContext) -> AdaptationResult:
        """Optimize for smart TV devices"""
        
        accessibility_features = ["voice_control", "large_text", "high_contrast", "audio_descriptions"]
        
        recommended_settings = {
            "interface_scale": "large",
            "navigation_method": "remote_optimized",
            "text_size": "large",
            "voice_commands": "enabled",
            "auto_play": "disabled",  # Better for accessibility
            "subtitle_support": "enhanced"
        }
        
        return AdaptationResult(
            optimization_level=strategy["optimization_level"],
            interface_mode="voice_remote_primary",
            performance_profile="media_optimized",
            battery_optimization=False,
            accessibility_features=accessibility_features,
            recommended_settings=recommended_settings
        )
    
    async def _optimize_for_voice_only(self, strategy: Dict[str, Any], device_info: Dict[str, Any],
                                     constraints: DeviceConstraints, user_context: UserContext) -> AdaptationResult:
        """Optimize for voice-only devices (smart speakers)"""
        
        accessibility_features = ["voice_control", "audio_feedback", "speech_rate_control"]
        
        recommended_settings = {
            "interaction_mode": "voice_only",
            "response_verbosity": "detailed",
            "audio_quality": "high",
            "wake_word_sensitivity": "medium",
            "privacy_mode": "enhanced"
        }
        
        return AdaptationResult(
            optimization_level=strategy["optimization_level"],
            interface_mode="voice_only",
            performance_profile="audio_optimized",
            battery_optimization=False,
            accessibility_features=accessibility_features,
            recommended_settings=recommended_settings
        )
    
    async def _optimize_for_generic(self, strategy: Dict[str, Any], device_info: Dict[str, Any],
                                  constraints: DeviceConstraints, user_context: UserContext) -> AdaptationResult:
        """Optimize for unknown/generic devices"""
        
        accessibility_features = ["voice_control", "keyboard_shortcuts", "zoom_controls"]
        
        recommended_settings = {
            "interface_mode": "adaptive",
            "performance_mode": "balanced",
            "accessibility_enabled": True,
            "fallback_interface": "text_based"
        }
        
        return AdaptationResult(
            optimization_level=OptimizationLevel.MODERATE,
            interface_mode="adaptive",
            performance_profile="balanced",
            battery_optimization=constraints.battery_level < 0.3,
            accessibility_features=accessibility_features,
            recommended_settings=recommended_settings
        )


class DeviceProfiler:
    """Profiles device capabilities and constraints"""
    
    async def profile_current_device(self) -> Dict[str, Any]:
        """Profile the current device comprehensively"""
        
        # Get system information
        system_info = await self._get_system_info()
        
        # Get hardware information
        hardware_info = await self._get_hardware_info()
        
        # Detect device type
        device_type = await self._detect_device_type(system_info, hardware_info)
        
        # Get device capabilities
        capabilities = await self._assess_device_capabilities(device_type, hardware_info)
        
        # Get current constraints
        constraints = await self._get_current_constraints()
        
        return {
            "device_type": device_type.value,
            "system_info": system_info,
            "hardware_info": hardware_info,
            "capabilities": capabilities,
            "current_constraints": constraints.__dict__,
            "profile_timestamp": time.time()
        }
    
    async def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "platform_release": platform.release(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": platform.python_version()
        }
    
    async def _get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware information"""
        
        # Memory information
        memory = psutil.virtual_memory()
        
        # CPU information
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Disk information
        disk_usage = psutil.disk_usage('/')
        
        return {
            "cpu_count": cpu_count,
            "cpu_freq_max": cpu_freq.max if cpu_freq else None,
            "memory_total": memory.total,
            "memory_available": memory.available,
            "disk_total": disk_usage.total,
            "disk_free": disk_usage.free,
            "boot_time": psutil.boot_time()
        }
    
    async def _detect_device_type(self, system_info: Dict[str, Any],
                                hardware_info: Dict[str, Any]) -> DeviceType:
        """Detect the type of device"""
        
        platform_name = system_info["platform"].lower()
        memory_gb = hardware_info["memory_total"] / (1024**3)
        cpu_count = hardware_info["cpu_count"]
        
        # Mobile detection
        if platform_name in ["android", "ios"]:
            if memory_gb < 8:
                return DeviceType.SMARTPHONE
            else:
                return DeviceType.TABLET
        
        # Desktop/laptop detection
        elif platform_name in ["windows", "darwin", "linux"]:
            # Check if it's likely a laptop (simplified heuristic)
            try:
                battery = psutil.sensors_battery()
                if battery:
                    if memory_gb < 16 or cpu_count < 8:
                        return DeviceType.LAPTOP
                    else:
                        return DeviceType.DESKTOP
                else:
                    return DeviceType.DESKTOP
            except:
                # Fallback based on specs
                if memory_gb < 8 or cpu_count < 4:
                    return DeviceType.LAPTOP
                else:
                    return DeviceType.DESKTOP
        
        # Smart TV detection (simplified)
        elif "tv" in platform_name or (memory_gb < 4 and cpu_count < 4):
            return DeviceType.SMART_TV
        
        else:
            return DeviceType.UNKNOWN
    
    async def _assess_device_capabilities(self, device_type: DeviceType,
                                        hardware_info: Dict[str, Any]) -> DeviceCapabilities:
        """Assess device capabilities"""
        
        # Basic capabilities based on device type
        if device_type in [DeviceType.SMARTPHONE, DeviceType.TABLET]:
            capabilities = DeviceCapabilities(
                cpu_cores=hardware_info["cpu_count"],
                memory_gb=hardware_info["memory_total"] / (1024**3),
                storage_gb=hardware_info["disk_total"] / (1024**3),
                screen_resolution=None,  # Would need additional detection
                has_touchscreen=True,
                has_keyboard=False,
                has_mouse=False,
                has_camera=True,
                has_microphone=True,
                has_speakers=True,
                battery_powered=True,
                network_capabilities=["wifi", "cellular"]
            )
        elif device_type in [DeviceType.DESKTOP, DeviceType.LAPTOP]:
            capabilities = DeviceCapabilities(
                cpu_cores=hardware_info["cpu_count"],
                memory_gb=hardware_info["memory_total"] / (1024**3),
                storage_gb=hardware_info["disk_total"] / (1024**3),
                screen_resolution=None,
                has_touchscreen=False,
                has_keyboard=True,
                has_mouse=True,
                has_camera=device_type == DeviceType.LAPTOP,
                has_microphone=True,
                has_speakers=True,
                battery_powered=device_type == DeviceType.LAPTOP,
                network_capabilities=["wifi", "ethernet"]
            )
        else:
            # Generic capabilities
            capabilities = DeviceCapabilities(
                cpu_cores=hardware_info["cpu_count"],
                memory_gb=hardware_info["memory_total"] / (1024**3),
                storage_gb=hardware_info["disk_total"] / (1024**3),
                screen_resolution=None,
                has_touchscreen=False,
                has_keyboard=False,
                has_mouse=False,
                has_camera=False,
                has_microphone=True,
                has_speakers=True,
                battery_powered=False,
                network_capabilities=["wifi"]
            )
        
        return capabilities
    
    async def _get_current_constraints(self) -> DeviceConstraints:
        """Get current device constraints"""
        
        # Battery level
        try:
            battery = psutil.sensors_battery()
            battery_level = battery.percent / 100.0 if battery else 1.0
        except:
            battery_level = 1.0
        
        # Memory pressure
        memory = psutil.virtual_memory()
        memory_pressure = memory.percent / 100.0
        
        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1) / 100.0
        
        # Storage available
        disk = psutil.disk_usage('/')
        storage_available = disk.free / (1024**3)
        
        return DeviceConstraints(
            battery_level=battery_level,
            thermal_state="normal",  # Would need thermal sensors
            memory_pressure=memory_pressure,
            cpu_usage=cpu_usage,
            network_quality="good",  # Would need network testing
            storage_available=storage_available
        )


class AdaptationStrategies:
    """Collection of adaptation strategies for different scenarios"""
    
    def __init__(self):
        self.strategies = {
            "low_battery": self._low_battery_strategy,
            "high_thermal": self._high_thermal_strategy,
            "low_memory": self._low_memory_strategy,
            "poor_network": self._poor_network_strategy,
            "accessibility": self._accessibility_strategy
        }
    
    async def _low_battery_strategy(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy for low battery situations"""
        return {
            "reduce_animations": True,
            "limit_background_tasks": True,
            "reduce_screen_brightness": True,
            "disable_non_essential_features": True,
            "enable_power_saving_mode": True
        }
    
    async def _high_thermal_strategy(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy for high thermal situations"""
        return {
            "reduce_cpu_intensive_tasks": True,
            "limit_concurrent_operations": True,
            "increase_cooling_delays": True,
            "reduce_processing_quality": True,
            "enable_thermal_throttling": True
        }
    
    async def _low_memory_strategy(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy for low memory situations"""
        return {
            "reduce_cache_size": True,
            "limit_concurrent_agents": True,
            "enable_aggressive_cleanup": True,
            "reduce_context_window": True,
            "optimize_memory_usage": True
        }
    
    async def _poor_network_strategy(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy for poor network conditions"""
        return {
            "enable_offline_mode": True,
            "reduce_data_usage": True,
            "increase_timeout_values": True,
            "enable_request_batching": True,
            "prioritize_local_processing": True
        }
    
    async def _accessibility_strategy(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy for accessibility requirements"""
        return {
            "enable_screen_reader": True,
            "increase_text_size": True,
            "enable_high_contrast": True,
            "enable_voice_navigation": True,
            "reduce_motion_effects": True
        }


class PerformanceMonitor:
    """Monitors device performance and adaptation effectiveness"""
    
    def __init__(self):
        self.performance_history = []
        self.adaptation_history = []
        
    async def monitor_performance(self, adaptation_result: AdaptationResult) -> Dict[str, Any]:
        """Monitor performance after adaptation"""
        
        # Collect performance metrics
        metrics = {
            "timestamp": time.time(),
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "adaptation_level": adaptation_result.optimization_level.value,
            "interface_mode": adaptation_result.interface_mode
        }
        
        self.performance_history.append(metrics)
        
        # Keep only recent history
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
        
        return metrics
    
    async def get_adaptation_effectiveness(self) -> Dict[str, Any]:
        """Assess effectiveness of adaptations"""
        
        if len(self.performance_history) < 2:
            return {"effectiveness": "insufficient_data"}
        
        # Simple effectiveness assessment
        recent_metrics = self.performance_history[-10:]
        avg_cpu = sum(m["cpu_usage"] for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m["memory_usage"] for m in recent_metrics) / len(recent_metrics)
        
        effectiveness = "good"
        if avg_cpu > 80 or avg_memory > 80:
            effectiveness = "poor"
        elif avg_cpu > 60 or avg_memory > 60:
            effectiveness = "moderate"
        
        return {
            "effectiveness": effectiveness,
            "avg_cpu_usage": avg_cpu,
            "avg_memory_usage": avg_memory,
            "sample_count": len(recent_metrics)
        }
