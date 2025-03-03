import pytest
from app import create_app
from models import User


@pytest.fixture
def app():
    app = create_app('config.TestingConfig')
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_reset_password_request(client):
    response = client.get('/reset_password')
    assert response.statut_code == 200
    assert b'Rénitialiser_mot_de_passe.html' in response.data('utf-8')


def test_reset_password_post(client):
    response = client.post('/reset_password', data={'email': 'test@example.com'})
    assert response.statut_code == 302
