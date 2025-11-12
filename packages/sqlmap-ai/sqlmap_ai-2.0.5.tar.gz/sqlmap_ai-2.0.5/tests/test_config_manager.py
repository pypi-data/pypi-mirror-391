#!/usr/bin/env python3
"""
Test suite for Configuration Manager
"""

import pytest
import tempfile
import json
from pathlib import Path
from sqlmap_ai.config_manager import ConfigManager, AppConfig, AIProviderConfig


class TestConfigManager:
    """Test configuration manager functionality"""
    
    def test_config_manager_initialization(self):
        """Test config manager initializes with defaults"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.yaml"
            manager = ConfigManager(str(config_file))
            
            assert manager.config.version is not None
            assert len(manager.config.ai_providers) > 0
    
    def test_ai_provider_configuration(self):
        """Test AI provider configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.yaml"
            manager = ConfigManager(str(config_file))
            
            # Test getting provider config
            groq_config = manager.get_ai_provider_config("groq")
            assert groq_config is not None
            assert groq_config.name == "groq"
            
            # Test updating provider config
            success = manager.update_ai_provider("groq", enabled=False)
            assert success
            assert not manager.get_ai_provider_config("groq").enabled
    
    def test_config_validation(self):
        """Test configuration validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.yaml"
            manager = ConfigManager(str(config_file))
            
            # Default config should be mostly valid
            issues = manager.validate_config()
            # May have issues due to missing API keys, but structure should be valid
            assert isinstance(issues, list)
    
    def test_config_save_load(self):
        """Test saving and loading configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.yaml"
            manager = ConfigManager(str(config_file))
            
            # Modify config
            original_timeout = manager.config.sqlmap.default_timeout
            manager.config.sqlmap.default_timeout = 300
            
            # Save config
            success = manager.save_config()
            assert success
            assert config_file.exists()
            
            # Create new manager and load
            manager2 = ConfigManager(str(config_file))
            assert manager2.config.sqlmap.default_timeout == 300
    
    def test_enabled_providers(self):
        """Test getting enabled providers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.yaml"
            manager = ConfigManager(str(config_file))
            
            # Disable all providers
            for name in manager.config.ai_providers:
                manager.update_ai_provider(name, enabled=False)
            
            enabled = manager.get_enabled_ai_providers()
            assert len(enabled) == 0
            
            # Enable one provider
            manager.update_ai_provider("groq", enabled=True)
            enabled = manager.get_enabled_ai_providers()
            assert len(enabled) == 1
            assert enabled[0].name == "groq"
    
    def test_custom_settings(self):
        """Test custom settings functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.yaml"
            manager = ConfigManager(str(config_file))
            
            # Set custom setting
            manager.set_custom_setting("test_key", "test_value")
            assert manager.get_custom_setting("test_key") == "test_value"
            
            # Get non-existent setting with default
            assert manager.get_custom_setting("non_existent", "default") == "default"
    
    def test_export_config(self):
        """Test configuration export"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.yaml"
            export_file = Path(temp_dir) / "exported_config.json"
            
            manager = ConfigManager(str(config_file))
            
            # Export config
            success = manager.export_config(str(export_file), include_sensitive=False)
            assert success
            assert export_file.exists()
            
            # Verify exported content
            with open(export_file) as f:
                exported_data = json.load(f)
            
            assert "version" in exported_data
            assert "ai_providers" in exported_data


if __name__ == "__main__":
    pytest.main([__file__])
