"""
ThinkMesh Health Monitoring System
=================================

Comprehensive health checks, performance monitoring, and system diagnostics
for all ThinkMesh components with mobile-optimized resource tracking.
"""

import asyncio
import time
import psutil
import platform
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

from .interfaces import IHealthCheck, ComponentStatus, HealthStatus
from .config import get_config
from .logging import get_logger, log_system_event
from .exceptions import ThinkMeshException, ErrorCode

logger = get_logger(__name__)


@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_usage_percent: float
    memory_usage_percent: float
    memory_available_mb: int
    disk_usage_percent: float
    disk_available_gb: float
    battery_level: Optional[float] = None
    temperature_celsius: Optional[float] = None
    network_connected: bool = True
    network_type: Optional[str] = None


@dataclass
class ComponentMetrics:
    """Individual component metrics"""
    component_name: str
    status: ComponentStatus
    response_time_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    error_count: int
    last_error: Optional[str] = None
    uptime_seconds: float = 0.0
    custom_metrics: Dict[str, Any] = None


class SystemMonitor:
    """System-level monitoring and metrics collection"""
    
    def __init__(self):
        self.start_time = time.time()
        self._last_metrics = None
        self._metrics_cache_duration = 5.0  # Cache for 5 seconds
        self._last_metrics_time = 0
    
    async def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics"""
        current_time = time.time()
        
        # Return cached metrics if recent
        if (self._last_metrics and 
            current_time - self._last_metrics_time < self._metrics_cache_duration):
            return self._last_metrics
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_mb = memory.available / (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_available_gb = disk.free / (1024 * 1024 * 1024)
            
            # Battery (mobile devices)
            battery_level = None
            try:
                battery = psutil.sensors_battery()
                if battery:
                    battery_level = battery.percent
            except (AttributeError, NotImplementedError):
                pass
            
            # Temperature (if available)
            temperature = None
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get first available temperature sensor
                    for sensor_name, sensor_list in temps.items():
                        if sensor_list:
                            temperature = sensor_list[0].current
                            break
            except (AttributeError, NotImplementedError):
                pass
            
            # Network connectivity
            network_connected = True
            network_type = None
            try:
                network_stats = psutil.net_if_stats()
                active_interfaces = [
                    name for name, stats in network_stats.items() 
                    if stats.isup and name != 'lo'
                ]
                network_connected = len(active_interfaces) > 0
                
                if network_connected:
                    # Determine network type (simplified)
                    if any('wifi' in iface.lower() or 'wlan' in iface.lower() 
                          for iface in active_interfaces):
                        network_type = 'wifi'
                    elif any('eth' in iface.lower() or 'en' in iface.lower() 
                            for iface in active_interfaces):
                        network_type = 'ethernet'
                    else:
                        network_type = 'cellular'
                        
            except Exception:
                pass
            
            metrics = SystemMetrics(
                cpu_usage_percent=cpu_percent,
                memory_usage_percent=memory_percent,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_percent,
                disk_available_gb=disk_available_gb,
                battery_level=battery_level,
                temperature_celsius=temperature,
                network_connected=network_connected,
                network_type=network_type
            )
            
            # Cache metrics
            self._last_metrics = metrics
            self._last_metrics_time = current_time
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            # Return minimal metrics on error
            return SystemMetrics(
                cpu_usage_percent=0.0,
                memory_usage_percent=0.0,
                memory_available_mb=0,
                disk_usage_percent=0.0,
                disk_available_gb=0.0
            )
    
    def get_uptime_seconds(self) -> float:
        """Get system uptime in seconds"""
        return time.time() - self.start_time
    
    async def check_resource_constraints(self) -> List[str]:
        """Check for resource constraints that might affect performance"""
        constraints = []
        metrics = await self.get_system_metrics()
        
        # Memory constraints
        if metrics.memory_usage_percent > 90:
            constraints.append("Critical memory usage")
        elif metrics.memory_usage_percent > 80:
            constraints.append("High memory usage")
        
        # CPU constraints
        if metrics.cpu_usage_percent > 90:
            constraints.append("Critical CPU usage")
        elif metrics.cpu_usage_percent > 80:
            constraints.append("High CPU usage")
        
        # Disk constraints
        if metrics.disk_usage_percent > 95:
            constraints.append("Critical disk usage")
        elif metrics.disk_usage_percent > 90:
            constraints.append("High disk usage")
        
        # Battery constraints (mobile)
        if metrics.battery_level is not None:
            if metrics.battery_level < 10:
                constraints.append("Critical battery level")
            elif metrics.battery_level < 20:
                constraints.append("Low battery level")
        
        # Temperature constraints
        if metrics.temperature_celsius is not None:
            if metrics.temperature_celsius > 80:
                constraints.append("High device temperature")
        
        # Network constraints
        if not metrics.network_connected:
            constraints.append("No network connectivity")
        
        return constraints


class ComponentHealthTracker:
    """Track health status of individual components"""
    
    def __init__(self):
        self.components: Dict[str, ComponentMetrics] = {}
        self.error_counts: Dict[str, int] = {}
        self.last_errors: Dict[str, str] = {}
        self.start_times: Dict[str, float] = {}
    
    def register_component(self, component_name: str) -> None:
        """Register a component for health tracking"""
        self.start_times[component_name] = time.time()
        self.error_counts[component_name] = 0
        logger.info(f"Registered component for health tracking: {component_name}")
    
    def record_error(self, component_name: str, error_message: str) -> None:
        """Record an error for a component"""
        self.error_counts[component_name] = self.error_counts.get(component_name, 0) + 1
        self.last_errors[component_name] = error_message
        
        log_system_event(
            logger, "component_error", component_name,
            {"error_message": error_message, "error_count": self.error_counts[component_name]}
        )
    
    async def update_component_metrics(self, component_name: str, 
                                     custom_metrics: Dict[str, Any]) -> None:
        """Update metrics for a component"""
        try:
            # Get component-specific resource usage (simplified)
            memory_usage_mb = custom_metrics.get('memory_usage_mb', 0)
            cpu_usage_percent = custom_metrics.get('cpu_usage_percent', 0)
            response_time_ms = custom_metrics.get('response_time_ms', 0)
            
            # Determine status based on metrics and errors
            status = self._determine_component_status(
                component_name, response_time_ms, memory_usage_mb
            )
            
            uptime = time.time() - self.start_times.get(component_name, time.time())
            
            metrics = ComponentMetrics(
                component_name=component_name,
                status=status,
                response_time_ms=response_time_ms,
                memory_usage_mb=memory_usage_mb,
                cpu_usage_percent=cpu_usage_percent,
                error_count=self.error_counts.get(component_name, 0),
                last_error=self.last_errors.get(component_name),
                uptime_seconds=uptime,
                custom_metrics=custom_metrics
            )
            
            self.components[component_name] = metrics
            
        except Exception as e:
            logger.error(f"Failed to update metrics for {component_name}: {e}")
    
    def _determine_component_status(self, component_name: str, 
                                  response_time_ms: float, 
                                  memory_usage_mb: float) -> ComponentStatus:
        """Determine component health status based on metrics"""
        error_count = self.error_counts.get(component_name, 0)
        
        # Critical conditions
        if error_count > 10:
            return ComponentStatus.UNHEALTHY
        if response_time_ms > 5000:  # 5 second response time
            return ComponentStatus.UNHEALTHY
        if memory_usage_mb > 1000:  # 1GB memory usage
            return ComponentStatus.UNHEALTHY
        
        # Degraded conditions
        if error_count > 5:
            return ComponentStatus.DEGRADED
        if response_time_ms > 2000:  # 2 second response time
            return ComponentStatus.DEGRADED
        if memory_usage_mb > 500:  # 500MB memory usage
            return ComponentStatus.DEGRADED
        
        return ComponentStatus.HEALTHY
    
    def get_component_metrics(self, component_name: str) -> Optional[ComponentMetrics]:
        """Get metrics for a specific component"""
        return self.components.get(component_name)
    
    def get_all_components(self) -> Dict[str, ComponentMetrics]:
        """Get metrics for all components"""
        return self.components.copy()


class HealthChecker:
    """Main health checking coordinator"""
    
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.component_tracker = ComponentHealthTracker()
        self.registered_health_checks: Dict[str, IHealthCheck] = {}
        self.config = get_config()
        self._health_check_task: Optional[asyncio.Task] = None
    
    def register_health_check(self, component_name: str, 
                            health_check: IHealthCheck) -> None:
        """Register a component for health checking"""
        self.registered_health_checks[component_name] = health_check
        self.component_tracker.register_component(component_name)
        logger.info(f"Registered health check for: {component_name}")
    
    async def start_monitoring(self) -> None:
        """Start continuous health monitoring"""
        if self._health_check_task is not None:
            return
        
        self._health_check_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started health monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop health monitoring"""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None
        
        logger.info("Stopped health monitoring")
    
    async def _monitoring_loop(self) -> None:
        """Continuous monitoring loop"""
        interval = self.config.monitoring.health_check_interval_seconds
        
        while True:
            try:
                await self.check_all_components()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    async def check_all_components(self) -> Dict[str, HealthStatus]:
        """Check health of all registered components"""
        results = {}
        
        # Check system health
        system_status = await self._check_system_health()
        results["system"] = system_status
        
        # Check individual components
        for component_name, health_check in self.registered_health_checks.items():
            try:
                start_time = time.time()
                status = await health_check.check_health()
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                # Get component metrics
                metrics = await health_check.get_metrics()
                metrics['response_time_ms'] = response_time
                
                # Update component tracker
                await self.component_tracker.update_component_metrics(
                    component_name, metrics
                )
                
                results[component_name] = status
                
            except Exception as e:
                # Record error and create unhealthy status
                error_msg = f"Health check failed: {str(e)}"
                self.component_tracker.record_error(component_name, error_msg)
                
                results[component_name] = HealthStatus(
                    status=ComponentStatus.UNHEALTHY,
                    message=error_msg,
                    details={"exception": str(e)},
                    timestamp=time.time(),
                    component_name=component_name
                )
        
        return results
    
    async def _check_system_health(self) -> HealthStatus:
        """Check overall system health"""
        try:
            metrics = await self.system_monitor.get_system_metrics()
            constraints = await self.system_monitor.check_resource_constraints()
            
            # Determine overall system status
            if any("Critical" in constraint for constraint in constraints):
                status = ComponentStatus.UNHEALTHY
                message = f"Critical system issues: {', '.join(constraints)}"
            elif constraints:
                status = ComponentStatus.DEGRADED
                message = f"System constraints: {', '.join(constraints)}"
            else:
                status = ComponentStatus.HEALTHY
                message = "System operating normally"
            
            return HealthStatus(
                status=status,
                message=message,
                details=asdict(metrics),
                timestamp=time.time(),
                component_name="system"
            )
            
        except Exception as e:
            return HealthStatus(
                status=ComponentStatus.UNKNOWN,
                message=f"Unable to check system health: {str(e)}",
                details={"exception": str(e)},
                timestamp=time.time(),
                component_name="system"
            )
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary"""
        health_results = await self.check_all_components()
        system_metrics = await self.system_monitor.get_system_metrics()
        component_metrics = self.component_tracker.get_all_components()
        
        # Calculate overall health score
        healthy_count = sum(1 for status in health_results.values() 
                          if status.status == ComponentStatus.HEALTHY)
        total_count = len(health_results)
        health_score = (healthy_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "overall_health_score": health_score,
            "system_metrics": asdict(system_metrics),
            "component_health": {
                name: asdict(status) for name, status in health_results.items()
            },
            "component_metrics": {
                name: asdict(metrics) for name, metrics in component_metrics.items()
            },
            "uptime_seconds": self.system_monitor.get_uptime_seconds(),
            "timestamp": time.time()
        }
