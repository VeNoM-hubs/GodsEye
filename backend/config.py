"""
Configuration Management for GodsEye
Handles all system configuration and settings
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class MQTTConfig(BaseModel):
    """MQTT broker configuration"""
    broker_host: str = Field(default="localhost")
    broker_port: int = Field(default=1883)
    username: Optional[str] = None
    password: Optional[str] = None
    topics: Dict[str, str] = Field(default_factory=lambda: {
        "access_events": "godseye/access",
        "honeypot_events": "godseye/honeypot",
        "network_events": "godseye/network",
        "endpoint_events": "godseye/endpoint",
        "teapot_events": "godseye/teapot"
    })


class StorageConfig(BaseModel):
    """Storage configuration"""
    storage_type: str = Field(default="json")  # json, postgres
    log_directory: str = Field(default="logs")
    retention_days: int = Field(default=90)
    
    # Database config (future)
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_name: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None


class AlertConfig(BaseModel):
    """Alert engine configuration"""
    alert_threshold: float = Field(default=0.7, description="Anomaly score threshold")
    enable_notifications: bool = Field(default=True)
    notification_channels: list = Field(default_factory=lambda: ["log", "console"])
    
    # Severity levels
    severity_levels: Dict[str, int] = Field(default_factory=lambda: {
        "INFO": 1,
        "LOW": 2,
        "MEDIUM": 3,
        "HIGH": 4,
        "CRITICAL": 5
    })


class AccessControlConfig(BaseModel):
    """Access control rule configuration"""
    max_failed_attempts: int = Field(default=3, description="Max failed attempts before alert")
    failed_attempt_window_seconds: int = Field(default=300, description="Time window for counting failures")
    
    # Normal access hours (24-hour format)
    normal_access_hours_start: int = Field(default=6, ge=0, le=23)
    normal_access_hours_end: int = Field(default=22, ge=0, le=23)
    
    # Known locations
    known_locations: list = Field(default_factory=lambda: [
        "Server Room A",
        "Control Room",
        "Main Entrance"
    ])
    
    # Require both RFID and fingerprint
    require_multi_factor: bool = Field(default=True)


class HoneypotConfig(BaseModel):
    """Honeypot configuration"""
    enabled: bool = Field(default=True)
    honeypot_devices: list = Field(default_factory=list)
    alert_on_any_interaction: bool = Field(default=True)


class TeapotConfig(BaseModel):
    """Teapot (decoy) configuration"""
    enabled: bool = Field(default=True)
    decoy_cards: list = Field(default_factory=lambda: [
        "FAKE_CARD_001",
        "FAKE_CARD_002",
        "DECOY_999"
    ])
    decoy_fingerprints: list = Field(default_factory=lambda: [
        "FAKE_FP_001",
        "FAKE_FP_002"
    ])


class MLConfig(BaseModel):
    """Machine Learning configuration"""
    enabled: bool = Field(default=False, description="Enable ML anomaly detection")
    model_type: str = Field(default="isolation_forest")
    training_data_path: Optional[str] = None
    model_save_path: str = Field(default="ml_models")
    retrain_interval_hours: int = Field(default=24)


class SystemConfig(BaseModel):
    """Main system configuration"""
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    
    mqtt: MQTTConfig = Field(default_factory=MQTTConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    alerts: AlertConfig = Field(default_factory=AlertConfig)
    access_control: AccessControlConfig = Field(default_factory=AccessControlConfig)
    honeypot: HoneypotConfig = Field(default_factory=HoneypotConfig)
    teapot: TeapotConfig = Field(default_factory=TeapotConfig)
    ml: MLConfig = Field(default_factory=MLConfig)


class ConfigManager:
    """Configuration manager for loading and accessing config"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        return os.path.join(
            Path(__file__).parent.parent,
            "config",
            "config.yaml"
        )
    
    def _load_config(self) -> SystemConfig:
        """Load configuration from file or use defaults"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config_dict = yaml.safe_load(f)
                return SystemConfig(**config_dict)
        else:
            # Use defaults and save
            config = SystemConfig()
            self.save_config(config)
            return config
    
    def save_config(self, config: SystemConfig):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(config.model_dump(), f, default_flow_style=False)
    
    def get(self) -> SystemConfig:
        """Get current configuration"""
        return self.config
    
    def reload(self):
        """Reload configuration from file"""
        self.config = self._load_config()


# Global configuration instance
_config_manager: Optional[ConfigManager] = None

def get_config() -> SystemConfig:
    """Get global configuration instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.get()

def reload_config():
    """Reload global configuration"""
    global _config_manager
    if _config_manager is not None:
        _config_manager.reload()
