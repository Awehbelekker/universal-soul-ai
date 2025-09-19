"""
ThinkMesh Core Interfaces
========================

Abstract base classes and interfaces for all ThinkMesh components.
Enables dependency injection, testing, and modular architecture.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator, Union
from dataclasses import dataclass
from enum import Enum
import asyncio


class ComponentStatus(Enum):
    """Component health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class AgentRole(Enum):
    """Multi-agent system roles"""
    ORCHESTRATOR = "orchestrator"
    EXPLORER = "explorer"
    CODER = "coder"
    ANALYZER = "analyzer"
    VERIFIER = "verifier"


@dataclass
class HealthStatus:
    """Component health status information"""
    status: ComponentStatus
    message: str
    details: Dict[str, Any]
    timestamp: float
    component_name: str


@dataclass
class TaskRequest:
    """Task request structure"""
    id: str
    description: str
    priority: TaskPriority
    context: Dict[str, Any]
    user_id: Optional[str] = None
    timeout_seconds: Optional[int] = None


@dataclass
class TaskResult:
    """Task execution result"""
    task_id: str
    success: bool
    result: Any
    error_message: Optional[str] = None
    execution_time_seconds: float = 0.0
    metadata: Dict[str, Any] = None


@dataclass
class VoiceInput:
    """Voice input data structure"""
    audio_data: bytes
    sample_rate: int
    channels: int
    format: str
    timestamp: float


@dataclass
class VoiceOutput:
    """Voice output data structure"""
    audio_data: bytes
    text: str
    sample_rate: int
    channels: int
    format: str


@dataclass
class UserContext:
    """User context and preferences"""
    user_id: str
    preferences: Dict[str, Any]
    session_data: Dict[str, Any]
    device_info: Dict[str, Any]
    privacy_settings: Dict[str, Any]


class IHealthCheck(ABC):
    """Health check interface for all components"""
    
    @abstractmethod
    async def check_health(self) -> HealthStatus:
        """Check component health status"""
        pass
    
    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """Get component performance metrics"""
        pass


class IAIEngine(ABC):
    """Abstract interface for AI reasoning engines"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the AI engine"""
        pass
    
    @abstractmethod
    async def process_request(self, request: str, context: UserContext) -> str:
        """Process a user request and return response"""
        pass
    
    @abstractmethod
    async def learn_from_interaction(self, request: str, response: str, 
                                   feedback: Optional[Dict[str, Any]] = None) -> None:
        """Learn from user interaction"""
        pass
    
    @abstractmethod
    async def get_capabilities(self) -> List[str]:
        """Get list of engine capabilities"""
        pass


class IAgentOrchestrator(ABC):
    """Abstract interface for multi-agent orchestration"""
    
    @abstractmethod
    async def execute_task(self, task: TaskRequest) -> TaskResult:
        """Execute a task using appropriate agents"""
        pass
    
    @abstractmethod
    async def create_agent(self, role: AgentRole, config: Dict[str, Any]) -> str:
        """Create a new agent and return its ID"""
        pass
    
    @abstractmethod
    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status of a specific agent"""
        pass
    
    @abstractmethod
    async def terminate_agent(self, agent_id: str) -> None:
        """Terminate a specific agent"""
        pass


class IVoiceInterface(ABC):
    """Abstract interface for voice processing"""
    
    @abstractmethod
    async def speech_to_text(self, voice_input: VoiceInput) -> str:
        """Convert speech to text"""
        pass
    
    @abstractmethod
    async def text_to_speech(self, text: str, voice_config: Dict[str, Any]) -> VoiceOutput:
        """Convert text to speech"""
        pass
    
    @abstractmethod
    async def start_voice_session(self, user_context: UserContext) -> str:
        """Start a voice interaction session"""
        pass
    
    @abstractmethod
    async def end_voice_session(self, session_id: str) -> None:
        """End a voice interaction session"""
        pass


class IDataManager(ABC):
    """Abstract interface for data management"""
    
    @abstractmethod
    async def store_data(self, key: str, data: Any, 
                        encryption: bool = True) -> None:
        """Store data with optional encryption"""
        pass
    
    @abstractmethod
    async def retrieve_data(self, key: str) -> Optional[Any]:
        """Retrieve stored data"""
        pass
    
    @abstractmethod
    async def search_data(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Semantic search through stored data"""
        pass
    
    @abstractmethod
    async def delete_data(self, key: str) -> bool:
        """Delete stored data"""
        pass
    
    @abstractmethod
    async def backup_data(self, backup_path: str) -> bool:
        """Create data backup"""
        pass


class ILocalAIService(ABC):
    """Abstract interface for local AI model serving"""
    
    @abstractmethod
    async def load_model(self, model_path: str, config: Dict[str, Any]) -> str:
        """Load a model and return model ID"""
        pass
    
    @abstractmethod
    async def unload_model(self, model_id: str) -> None:
        """Unload a model from memory"""
        pass
    
    @abstractmethod
    async def inference(self, model_id: str, input_data: Any) -> Any:
        """Run inference on loaded model"""
        pass
    
    @abstractmethod
    async def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get information about loaded model"""
        pass


class IMobileOptimizer(ABC):
    """Abstract interface for mobile-specific optimizations"""
    
    @abstractmethod
    async def optimize_for_battery(self, current_level: float) -> Dict[str, Any]:
        """Optimize system for current battery level"""
        pass
    
    @abstractmethod
    async def handle_thermal_throttling(self, temperature: float) -> None:
        """Handle device thermal throttling"""
        pass
    
    @abstractmethod
    async def manage_memory_pressure(self, available_memory: int) -> None:
        """Manage system under memory pressure"""
        pass
    
    @abstractmethod
    async def adapt_to_connectivity(self, connection_type: str, 
                                  bandwidth: float) -> None:
        """Adapt system to connectivity changes"""
        pass


class IEventBus(ABC):
    """Abstract interface for event-driven communication"""
    
    @abstractmethod
    async def publish(self, event_type: str, data: Any) -> None:
        """Publish an event"""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: str, 
                       callback: callable) -> str:
        """Subscribe to event type, return subscription ID"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> None:
        """Unsubscribe from events"""
        pass


class ISecurityManager(ABC):
    """Abstract interface for security and privacy management"""
    
    @abstractmethod
    async def encrypt_data(self, data: bytes, key_id: str) -> bytes:
        """Encrypt data using specified key"""
        pass
    
    @abstractmethod
    async def decrypt_data(self, encrypted_data: bytes, key_id: str) -> bytes:
        """Decrypt data using specified key"""
        pass
    
    @abstractmethod
    async def generate_key(self, key_type: str) -> str:
        """Generate new encryption key, return key ID"""
        pass
    
    @abstractmethod
    async def validate_permissions(self, user_id: str, 
                                 resource: str, action: str) -> bool:
        """Validate user permissions for resource action"""
        pass


class IConfigManager(ABC):
    """Abstract interface for configuration management"""
    
    @abstractmethod
    async def get_config(self, key: str) -> Any:
        """Get configuration value"""
        pass
    
    @abstractmethod
    async def set_config(self, key: str, value: Any) -> None:
        """Set configuration value"""
        pass
    
    @abstractmethod
    async def reload_config(self) -> None:
        """Reload configuration from source"""
        pass
    
    @abstractmethod
    async def validate_config(self) -> List[str]:
        """Validate configuration, return list of errors"""
        pass


# Dependency injection container interface
class IDependencyContainer(ABC):
    """Abstract interface for dependency injection"""
    
    @abstractmethod
    def register(self, interface_type: type, implementation: Any, 
                singleton: bool = True) -> None:
        """Register implementation for interface"""
        pass
    
    @abstractmethod
    def resolve(self, interface_type: type) -> Any:
        """Resolve implementation for interface"""
        pass
    
    @abstractmethod
    def is_registered(self, interface_type: type) -> bool:
        """Check if interface is registered"""
        pass
