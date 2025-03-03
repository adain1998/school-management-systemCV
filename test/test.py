import pytest
import sys
import os
from flask import Flask
from app.models import db, Exam


# Ajouter le dossier app au chemin d'importation
sys.path.insert(0, r'C:\Users\pc\Videos\School_management\app')

# Importer les éléments de l'application Flask et les blueprints
from app.gestion_exams import examen

@pytest.fixture
def app():
    """Créer une instance de l'application pour les tests."""
    app = Flask(__name__)
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "testsecretkey"
    })

    db.init_app(app)

    with app.app_context():
        db.create_all()  # Créer les tables dans la base de données en mémoire
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Créer un client de test Flask."""
    return app.test_client()


@pytest.fixture
def sample_exam(app):
    """Créer un examen de test."""
    with app.app_context():
        exam = Exam(student_id=1, subject="Math", score=85.0)
        db.session.add(exam)
        db.session.commit()
        return exam


def test_add_exam(client):
    """Tester l'ajout d'un examen."""
    response = client.post('/exams/add', data={
        'student_id': 1,
        'subject': 'Math',
        'score': '95.0'
    })
    assert response.status_code == 302  # Redirection vers la vue des examens
    assert b'Examen ajouté avec succès' in response.data  # Vérifier le message flash


def test_add_exam_invalid(client):
    """Tester l'ajout d'un examen avec des données invalides."""
    response = client.post('/exams/add', data={
        'student_id': '',
        'subject': '',
        'score': ''
    })
    assert response.status_code == 200  # Reste sur la même page
    assert b'Tous les champs sont requis.' in response.data  # Vérifier le message flash


def test_view_exam(client, sample_exam):
    """Tester la vue des examens."""
    response = client.get('/schedules')
    assert response.status_code == 200
    assert b'Math' in response.data  # Vérifier que le sujet de l'examen est affiché


def test_filter_and_search_exams(client, sample_exam):
    """Tester le filtrage des examens."""
    response = client.post('/exams/filter_and_search', data={
        'subject': 'Math',
        'score': '85.0'
    })
    assert response.status_code == 200
    assert b'Math' in response.data
    assert b'85.0' in response.data


def test_delete_exam(client, sample_exam):
    """Tester la suppression d'un examen."""
    response = client.post(f'/exams/delete/{sample_exam.id}')
    assert response.status_code == 302  # Redirection après suppression
    assert b'Examen supprimé avec succès' in response.data  # Vérifier le message flash

    # Vérifier que l'examen est bien supprimé
    deleted_exam = Exam.query.get(sample_exam.id)
    assert deleted_exam is None
