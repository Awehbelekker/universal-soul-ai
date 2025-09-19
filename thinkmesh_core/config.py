"""
ThinkMesh Configuration Management
=================================

Centralized configuration system with environment-specific settings,
feature flags, and runtime optimization parameters.
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

from .logging import get_logger

logger = get_logger(__name__)


@dataclass
class ThinkMeshBranding:
    """ThinkMesh branding and UI configuration"""
    app_name: str = "ThinkMesh AI"
    company_name: str = "ThinkMesh AI Systems"
    tagline: str = "Your Private AI Companion"
    
    # Brand colors (Material Design 3 compatible)
    primary_color: str = "#1976D2"  # Deep Blue
    secondary_color: str = "#03DAC6"  # Teal
    accent_color: str = "#FF6B35"  # Orange
    background_color: str = "#FAFAFA"  # Light Gray
    surface_color: str = "#FFFFFF"  # White
    error_color: str = "#B00020"  # Red
    
    # Typography
    font_family: str = "Roboto"
    font_size_base: int = 16
    
    # Logo and assets
    logo_path: str = "assets/images/thinkmesh_logo.png"
    icon_path: str = "assets/images/thinkmesh_icon.png"


@dataclass
class HRMConfig:
    """Hierarchical Reasoning Model configuration"""
    model_path: str = "models/hrm_27m_mobile.gguf"
    quantization: str = "INT4"  # INT4, INT8, FP16, FP32
    max_context_length: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    
    # Mobile optimization
    mobile_optimized: bool = True
    battery_aware: bool = True
    thermal_throttling: bool = True
    memory_limit_mb: int = 512


@dataclass
class AgentConfig:
    """Multi-agent orchestrator configuration"""
    max_concurrent_agents: int = 3
    context_store_size_mb: int = 100
    agent_timeout_seconds: int = 30
    
    # Agent specializations
    orchestrator_enabled: bool = True
    explorer_agents: int = 1
    coder_agents: int = 1
    
    # Performance tuning
    token_budget_multiplier: float = 3.0
    quality_threshold: float = 0.95


@dataclass
class VoiceConfig:
    """Voice interface configuration"""
    stt_provider: str = "deepgram"  # deepgram, openai, local
    tts_provider: str = "elevenlabs"  # elevenlabs, openai, local
    vad_provider: str = "silero"  # silero, webrtc
    
    # Audio settings
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    
    # Real-time processing
    low_latency_mode: bool = True
    noise_suppression: bool = True
    echo_cancellation: bool = True


@dataclass
class LocalAIConfig:
    """Local AI infrastructure configuration"""
    server_port: int = 8080
    server_host: str = "127.0.0.1"
    
    # Model management
    auto_model_download: bool = True
    model_cache_size_gb: int = 5
    quantization_enabled: bool = True
    
    # Performance
    gpu_acceleration: bool = True
    cpu_threads: int = 0  # 0 = auto-detect
    memory_map: bool = True


@dataclass
class DataConfig:
    """Data management and privacy configuration"""
    storage_path: str = "data/thinkmesh"
    encryption_enabled: bool = True
    compression_enabled: bool = True
    
    # Privacy settings
    local_only: bool = True
    cloud_sync_enabled: bool = False
    data_retention_days: int = 365
    
    # Search and indexing
    semantic_search_enabled: bool = True
    index_update_interval_hours: int = 24


@dataclass
class MobileConfig:
    """Mobile-specific optimization configuration"""
    battery_optimization: bool = True
    background_processing: bool = True
    offline_mode: bool = True
    
    # Performance scaling
    auto_performance_scaling: bool = True
    thermal_monitoring: bool = True
    memory_pressure_handling: bool = True
    
    # Connectivity
    wifi_only_sync: bool = True
    cellular_data_limit_mb: int = 100


@dataclass
class MonitoringConfig:
    """Monitoring and health check configuration"""
    health_check_interval_seconds: int = 30
    metrics_collection_enabled: bool = True
    error_reporting_enabled: bool = True
    
    # Logging
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_file_path: str = "logs/thinkmesh.log"
    log_rotation_size_mb: int = 10
    log_retention_days: int = 30


@dataclass
class ThinkMeshConfig:
    """Main ThinkMesh configuration container"""
    
    # Component configurations
    branding: ThinkMeshBranding = field(default_factory=ThinkMeshBranding)
    hrm: HRMConfig = field(default_factory=HRMConfig)
    agents: AgentConfig = field(default_factory=AgentConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    local_ai: LocalAIConfig = field(default_factory=LocalAIConfig)
    data: DataConfig = field(default_factory=DataConfig)
    mobile: MobileConfig = field(default_factory=MobileConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Environment settings
    environment: str = "development"  # development, staging, production
    debug_mode: bool = True
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    
    @classmethod
    def load_from_file(cls, config_path: str) -> "ThinkMeshConfig":
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Create config instance with loaded data
            config = cls()
            config._update_from_dict(config_data)
            
            logger.info(f"Configuration loaded from {config_path}")
            return config
            
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return cls()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return cls()
    
    @classmethod
    def load_from_env(cls) -> "ThinkMeshConfig":
        """Load configuration from environment variables"""
        config = cls()
        
        # Environment-specific overrides
        if os.getenv("THINKMESH_ENV"):
            config.environment = os.getenv("THINKMESH_ENV")
        
        if os.getenv("THINKMESH_DEBUG"):
            config.debug_mode = os.getenv("THINKMESH_DEBUG").lower() == "true"
        
        # Component-specific environment variables
        if os.getenv("THINKMESH_HRM_MODEL_PATH"):
            config.hrm.model_path = os.getenv("THINKMESH_HRM_MODEL_PATH")
        
        if os.getenv("THINKMESH_DATA_PATH"):
            config.data.storage_path = os.getenv("THINKMESH_DATA_PATH")
        
        logger.info("Configuration loaded from environment variables")
        return config
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to JSON file"""
        try:
            # Ensure directory exists
            Path(config_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(self._to_dict(), f, indent=2)
            
            logger.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise
    
    def _update_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary"""
        for key, value in config_data.items():
            if hasattr(self, key):
                if isinstance(getattr(self, key), (ThinkMeshBranding, HRMConfig, AgentConfig, 
                                                 VoiceConfig, LocalAIConfig, DataConfig, 
                                                 MobileConfig, MonitoringConfig)):
                    # Update nested configuration objects
                    nested_config = getattr(self, key)
                    for nested_key, nested_value in value.items():
                        if hasattr(nested_config, nested_key):
                            setattr(nested_config, nested_key, nested_value)
                else:
                    setattr(self, key, value)
    
    def _to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if hasattr(value, '__dict__'):
                result[key] = value.__dict__
            else:
                result[key] = value
        return result
    
    def get_feature_flag(self, flag_name: str, default: bool = False) -> bool:
        """Get feature flag value"""
        return self.feature_flags.get(flag_name, default)
    
    def set_feature_flag(self, flag_name: str, enabled: bool) -> None:
        """Set feature flag value"""
        self.feature_flags[flag_name] = enabled
        logger.info(f"Feature flag '{flag_name}' set to {enabled}")


# Global configuration instance
_config: Optional[ThinkMeshConfig] = None


def get_config() -> ThinkMeshConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        # Try to load from file first, then environment, then defaults
        config_file = os.getenv("THINKMESH_CONFIG_FILE", "config/thinkmesh.json")
        if os.path.exists(config_file):
            _config = ThinkMeshConfig.load_from_file(config_file)
        else:
            _config = ThinkMeshConfig.load_from_env()
    return _config


def set_config(config: ThinkMeshConfig) -> None:
    """Set global configuration instance"""
    global _config
    _config = config
    logger.info("Global configuration updated")
