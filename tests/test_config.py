import pytest
import os
from config import Config

def test_config_validation():
    """Test configuration validation."""
    # Test invalid config
    config = Config()
    assert not config.validate()
    
    # Test valid config
    config.telegram_bot_token = "test_token"
    config.openai_api_key = "test_key"
    assert config.validate()

def test_config_defaults():
    """Test default configuration values."""
    config = Config()
    
    assert config.openai_model == "gpt-4o-mini"
    assert config.max_file_size_mb == 100
    assert config.file_retention_hours == 24
    assert config.log_level == "INFO"
    assert config.port == 8000