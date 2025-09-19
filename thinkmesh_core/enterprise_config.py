"""
SynergyCore™ Enterprise AI Platform Configuration
================================================

Enterprise-grade configuration system for the SynergyCore™ AI Platform,
providing scalable, reliable, and cost-effective AI solutions for enterprise deployment.

Copyright (c) 2025 SynergyCore™ AI Systems
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

from .logging import get_logger

logger = get_logger(__name__)


@dataclass
class SynergyCoreEnterpriseBranding:
    """SynergyCore™ Enterprise Platform branding and UI configuration"""
    platform_name: str = "SynergyCore™ AI Platform"
    company_name: str = "SynergyCore™ AI Systems"
    tagline: str = "Enterprise AI. Simplified. Secured."
    
    # Enterprise brand colors (Professional palette)
    primary_color: str = "#1565C0"  # Professional Blue
    secondary_color: str = "#00ACC1"  # Cyan
    accent_color: str = "#FF8F00"  # Amber
    background_color: str = "#FAFAFA"  # Light Gray
    surface_color: str = "#FFFFFF"  # White
    error_color: str = "#D32F2F"  # Red
    success_color: str = "#388E3C"  # Green
    warning_color: str = "#F57C00"  # Orange
    
    # Enterprise typography
    font_family: str = "Inter"  # Modern, professional font
    font_size_base: int = 16
    
    # Enterprise assets
    logo_path: str = "assets/images/synergycore_logo.png"
    icon_path: str = "assets/images/synergycore_icon.png"
    enterprise_logo_path: str = "assets/images/synergycore_enterprise.png"


@dataclass
class CogniFlowConfig:
    """CogniFlow™ Reasoning Engine configuration"""
    model_path: str = "models/cogniflow_27m_mobile.gguf"
    quantization: str = "INT4"  # INT4, INT8, FP16, FP32
    max_context_length: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    
    # Enterprise optimization
    enterprise_optimized: bool = True
    resource_aware: bool = True
    thermal_throttling: bool = True
    memory_limit_mb: int = 1024  # Increased for enterprise
    
    # Enterprise features
    audit_logging: bool = True
    compliance_mode: bool = True
    enterprise_security: bool = True


@dataclass
class SynergyCoreConfig:
    """SynergyCore™ Orchestration Platform configuration"""
    max_concurrent_agents: int = 8  # Increased for enterprise
    context_store_size_mb: int = 500  # Increased for enterprise
    agent_timeout_seconds: int = 60  # Increased for enterprise
    
    # Agent specializations
    orchestrator_enabled: bool = True
    explorer_agents: int = 2
    coder_agents: int = 2
    codeswarm_agents: int = 1  # New CodeSwarm™ agents
    
    # Enterprise performance tuning
    token_budget_multiplier: float = 5.0  # Increased for enterprise
    quality_threshold: float = 0.98  # Higher quality for enterprise
    enterprise_scaling: bool = True
    load_balancing: bool = True


@dataclass
class EdgeMindConfig:
    """EdgeMind™ Local AI Service configuration"""
    server_port: int = 8080
    server_host: str = "0.0.0.0"  # Enterprise binding
    
    # Enterprise model management
    auto_model_download: bool = True
    model_cache_size_gb: int = 20  # Increased for enterprise
    quantization_enabled: bool = True
    
    # Enterprise performance
    gpu_acceleration: bool = True
    cpu_threads: int = 0  # 0 = auto-detect
    memory_map: bool = True
    distributed_inference: bool = True  # Enterprise feature
    
    # Enterprise security
    api_authentication: bool = True
    ssl_enabled: bool = True
    enterprise_encryption: bool = True


@dataclass
class OptiCoreConfig:
    """OptiCore™ Resource Optimizer configuration"""
    # Resource optimization (expanded beyond mobile)
    cpu_optimization: bool = True
    memory_optimization: bool = True
    gpu_optimization: bool = True
    network_optimization: bool = True
    
    # Enterprise scaling
    auto_scaling: bool = True
    load_balancing: bool = True
    resource_pooling: bool = True
    
    # Cost optimization
    cost_optimization: bool = True
    efficiency_monitoring: bool = True
    usage_analytics: bool = True
    
    # Legacy mobile support
    battery_optimization: bool = True  # Backward compatibility
    thermal_monitoring: bool = True
    memory_pressure_handling: bool = True


@dataclass
class NeuralMeshDataConfig:
    """NeuralMesh™ Data Management configuration"""
    storage_path: str = "data/neuralmesh"
    encryption_enabled: bool = True
    compression_enabled: bool = True
    
    # Enterprise privacy settings
    enterprise_privacy: bool = True
    compliance_logging: bool = True
    data_governance: bool = True
    audit_trail: bool = True
    
    # Enterprise data management
    distributed_storage: bool = True
    backup_enabled: bool = True
    disaster_recovery: bool = True
    data_retention_days: int = 2555  # 7 years for enterprise compliance
    
    # Search and indexing
    semantic_search_enabled: bool = True
    enterprise_search: bool = True
    index_update_interval_hours: int = 12  # More frequent for enterprise


@dataclass
class EnterpriseMonitoringConfig:
    """Enterprise monitoring and compliance configuration"""
    health_check_interval_seconds: int = 15  # More frequent for enterprise
    metrics_collection_enabled: bool = True
    error_reporting_enabled: bool = True
    
    # Enterprise logging
    log_level: str = "INFO"
    log_file_path: str = "logs/synergycore.log"
    log_rotation_size_mb: int = 50  # Larger for enterprise
    log_retention_days: int = 90  # Longer for enterprise
    
    # Enterprise monitoring
    performance_monitoring: bool = True
    security_monitoring: bool = True
    compliance_monitoring: bool = True
    cost_monitoring: bool = True
    
    # Enterprise alerting
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cpu_usage": 80.0,
        "memory_usage": 85.0,
        "response_time_ms": 2000.0,
        "error_rate": 5.0
    })


@dataclass
class NeuralMeshConfig:
    """Main NeuralMesh™ Enterprise Platform configuration container"""
    
    # Component configurations
    branding: SynergyCoreEnterpriseBranding = field(default_factory=SynergyCoreEnterpriseBranding)
    cogniflow: CogniFlowConfig = field(default_factory=CogniFlowConfig)
    synergycore: SynergyCoreConfig = field(default_factory=SynergyCoreConfig)
    edgemind: EdgeMindConfig = field(default_factory=EdgeMindConfig)
    opticore: OptiCoreConfig = field(default_factory=OptiCoreConfig)
    data: NeuralMeshDataConfig = field(default_factory=NeuralMeshDataConfig)
    monitoring: EnterpriseMonitoringConfig = field(default_factory=EnterpriseMonitoringConfig)
    
    # Enterprise environment settings
    environment: str = "enterprise"  # development, staging, enterprise, production
    debug_mode: bool = False  # Disabled by default for enterprise
    enterprise_mode: bool = True
    compliance_mode: bool = True
    
    # Enterprise feature flags
    feature_flags: Dict[str, bool] = field(default_factory=lambda: {
        "synergycore_orchestration": True,
        "cogniflow_reasoning": True,
        "edgemind_local_ai": True,
        "opticore_optimization": True,
        "codeswarm_development": True,
        "enterprise_security": True,
        "compliance_monitoring": True,
        "cost_optimization": True,
        "distributed_processing": True,
        "enterprise_analytics": True
    })
    
    # Backward compatibility aliases
    @property
    def hrm(self) -> CogniFlowConfig:
        """Backward compatibility alias for CogniFlow™"""
        logger.warning("'hrm' configuration is deprecated. Use 'cogniflow' instead.")
        return self.cogniflow
    
    @property
    def agents(self) -> SynergyCoreConfig:
        """Backward compatibility alias for SynergyCore™"""
        logger.warning("'agents' configuration is deprecated. Use 'synergycore' instead.")
        return self.synergycore
    
    @property
    def local_ai(self) -> EdgeMindConfig:
        """Backward compatibility alias for EdgeMind™"""
        logger.warning("'local_ai' configuration is deprecated. Use 'edgemind' instead.")
        return self.edgemind
    
    @property
    def mobile(self) -> OptiCoreConfig:
        """Backward compatibility alias for OptiCore™"""
        logger.warning("'mobile' configuration is deprecated. Use 'opticore' instead.")
        return self.opticore
    
    @classmethod
    def load_from_file(cls, config_path: str) -> "NeuralMeshConfig":
        """Load configuration from JSON file with backward compatibility"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Handle backward compatibility mappings
            config_data = cls._migrate_legacy_config(config_data)
            
            # Create config instance with loaded data
            config = cls()
            config._update_from_dict(config_data)
            
            logger.info(f"NeuralMesh™ configuration loaded from {config_path}")
            return config
            
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using enterprise defaults")
            return cls()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return cls()
    
    @classmethod
    def _migrate_legacy_config(cls, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate legacy ThinkMesh configuration to NeuralMesh™"""
        migrations = {
            "hrm": "cogniflow",
            "agents": "synergycore", 
            "local_ai": "edgemind",
            "mobile": "opticore"
        }
        
        migrated_data = config_data.copy()
        
        for old_key, new_key in migrations.items():
            if old_key in migrated_data and new_key not in migrated_data:
                migrated_data[new_key] = migrated_data[old_key]
                logger.info(f"Migrated configuration: {old_key} -> {new_key}")
        
        return migrated_data
    
    @classmethod
    def load_from_env(cls) -> "NeuralMeshConfig":
        """Load configuration from environment variables"""
        config = cls()
        
        # Environment-specific overrides
        if os.getenv("NEURALMESH_ENV"):
            config.environment = os.getenv("NEURALMESH_ENV")
        
        if os.getenv("NEURALMESH_DEBUG"):
            config.debug_mode = os.getenv("NEURALMESH_DEBUG").lower() == "true"
        
        if os.getenv("NEURALMESH_ENTERPRISE_MODE"):
            config.enterprise_mode = os.getenv("NEURALMESH_ENTERPRISE_MODE").lower() == "true"
        
        # Component-specific environment variables
        if os.getenv("NEURALMESH_COGNIFLOW_MODEL_PATH"):
            config.cogniflow.model_path = os.getenv("NEURALMESH_COGNIFLOW_MODEL_PATH")
        
        if os.getenv("NEURALMESH_DATA_PATH"):
            config.data.storage_path = os.getenv("NEURALMESH_DATA_PATH")
        
        # Backward compatibility environment variables
        if os.getenv("THINKMESH_HRM_MODEL_PATH"):
            logger.warning("THINKMESH_HRM_MODEL_PATH is deprecated. Use NEURALMESH_COGNIFLOW_MODEL_PATH")
            config.cogniflow.model_path = os.getenv("THINKMESH_HRM_MODEL_PATH")
        
        logger.info("NeuralMesh™ configuration loaded from environment variables")
        return config
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to JSON file"""
        try:
            # Ensure directory exists
            Path(config_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(self._to_dict(), f, indent=2)
            
            logger.info(f"NeuralMesh™ configuration saved to {config_path}")
            
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise
    
    def _update_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary"""
        for key, value in config_data.items():
            if hasattr(self, key):
                attr = getattr(self, key)
                if hasattr(attr, '__dict__'):
                    # Update nested configuration objects
                    for nested_key, nested_value in value.items():
                        if hasattr(attr, nested_key):
                            setattr(attr, nested_key, nested_value)
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
        """Get enterprise feature flag value"""
        return self.feature_flags.get(flag_name, default)
    
    def set_feature_flag(self, flag_name: str, enabled: bool) -> None:
        """Set enterprise feature flag value"""
        self.feature_flags[flag_name] = enabled
        logger.info(f"Enterprise feature flag '{flag_name}' set to {enabled}")


# Global configuration instance
_enterprise_config: Optional[NeuralMeshConfig] = None


def get_enterprise_config() -> NeuralMeshConfig:
    """Get global NeuralMesh™ enterprise configuration instance"""
    global _enterprise_config
    if _enterprise_config is None:
        # Try to load from file first, then environment, then defaults
        config_file = os.getenv("NEURALMESH_CONFIG_FILE", "config/neuralmesh.json")
        if os.path.exists(config_file):
            _enterprise_config = NeuralMeshConfig.load_from_file(config_file)
        else:
            _enterprise_config = NeuralMeshConfig.load_from_env()
    return _enterprise_config


def set_enterprise_config(config: NeuralMeshConfig) -> None:
    """Set global NeuralMesh™ enterprise configuration instance"""
    global _enterprise_config
    _enterprise_config = config
    logger.info("Global NeuralMesh™ enterprise configuration updated")


# Backward compatibility functions
def get_config() -> NeuralMeshConfig:
    """Backward compatibility alias for get_enterprise_config()"""
    logger.warning("get_config() is deprecated. Use get_enterprise_config() instead.")
    return get_enterprise_config()


def set_config(config: NeuralMeshConfig) -> None:
    """Backward compatibility alias for set_enterprise_config()"""
    logger.warning("set_config() is deprecated. Use set_enterprise_config() instead.")
    set_enterprise_config(config)
