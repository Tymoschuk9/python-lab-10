import os
from unittest.mock import patch

try:
    from lab_10.config import Settings, get_settings
except ImportError:
    from online_store.config import Settings, get_settings


def test_settings_defaults():
    s = Settings()
    assert s.app_name == "Online Store Manager"
    assert s.environment in ["development", "testing", "production"]
    assert "shop.db" in s.database_url or "sqlite" in s.database_url


def test_settings_env_override():
    with patch.dict(os.environ, {
        "APP_NAME": "Custom Shop",
        "ENVIRONMENT": "production",
        "DATABASE_URL": "sqlite:///custom.db",
        "LOG_LEVEL": "DEBUG",
    }):
        s = Settings()
        assert s.app_name == "Custom Shop"
        assert s.environment == "production"
        assert s.database_url == "sqlite:///custom.db"
        assert s.log_level == "DEBUG"
