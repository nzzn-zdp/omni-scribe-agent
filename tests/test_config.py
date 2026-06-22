import pytest
from src.config import Settings, load_platform_config

def test_settings_default():
    settings = Settings()
    assert settings.app_name == "OmniScribeAgent"
    assert settings.app_version == "1.0.0"
    assert settings.debug is False
    assert "sqlite+aiosqlite" in settings.database_url
    assert settings.hotspot_check_interval == 300
    assert settings.publish_retry_count == 3

def test_load_platform_config_nonexistent():
    result = load_platform_config("nonexistent")
    assert result == {}