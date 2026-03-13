import pytest
from app import create_app
from config import TestingConfig

@pytest.fixture
def app():
    app = create_app(config_class=TestingConfig)
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False  # désactiver CSRF en test
    })
    yield app
