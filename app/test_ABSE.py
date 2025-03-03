import pytest
import os
import sys
from datetime import datetime
from flask import Flask
from app import create_app  # Assure-toi que create_app est bien exposée dans le fichier __init__.py de app
from models import db, Student, Absence, Message


# 🔥 Ajouter `app/` au chemin d'importation si nécessaire
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def app():
    """Créer une instance de l'application pour les tests."""
    app = create_app()  # Utiliser la fonction create_app importée depuis app
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()  # Créer les tables en mémoire
        yield app  # Renvoyer l'application pour les tests
        db.session.remove()  # Nettoyer la session
        db.drop_all()  # Supprimer toutes les tables après les tests


@pytest.fixture
def client(app):
    """Créer un client de test Flask."""
    return app.test_client()


@pytest.fixture
def student(app):
    """Créer un étudiant de test."""
    with app.app_context():
        student = Student(first_name="John", last_name="Doe", class_name="10A", religion="None", username="johndoe")
        db.session.add(student)
        db.session.commit()
        return student


@pytest.fixture
def absences(app, student):
    """Créer des absences de test."""
    with app.app_context():
        absence1 = Absence(date="2023-01-01", reason="Sick", student_id=student.id)
        absence2 = Absence(date="2023-01-02", reason="Family Event", student_id=student.id)
        db.session.add_all([absence1, absence2])
        db.session.commit()
        return [absence1, absence2]


def test_manage_absences(client, student, absences):
    """Tester la gestion des absences."""

    # Test ordre croissant
    response = client.get(f'/absences/{student.id}?sort_by_date=asc')
    assert response.status_code == 200
    assert b"2023-01-01" in response.data
    assert b"2023-01-02" in response.data

    # Test ordre décroissant
    response = client.get(f'/absences/{student.id}?sort_by_date=desc')
    assert response.status_code == 200
    assert b"2023-01-02" in response.data
    assert b"2023-01-01" in response.data

    # Test filtrage par raison
    response = client.get(f'/absences/{student.id}?filter_reason=Sick')
    assert response.status_code == 200
    assert b"Sick" in response.data
    assert b"Family Event" not in response.data


@pytest.fixture
def sample_message(app):
    """Créer des messages de test."""
    with app.app_context():
        message1 = Message(timestamp=datetime(2022, 1, 1), sender_id=1, body="HELLO", recepient_id=2)
        message2 = Message(timestamp=datetime(2022, 1, 2), sender_id=2, body="Hi", recepient_id=1)
        db.session.add_all([message1, message2])
        db.session.commit()
        return [message1, message2]


def test_get_filtered_messages_by_timestamp(app, sample_message):
    """Tester le filtrage des messages par timestamp."""
    with app.app_context():
        messages_asc = Message.query.order_by(Message.timestamp.asc()).all()
        assert len(messages_asc) == 2
        assert messages_asc[0].timestamp == datetime(2022, 1, 1)

        messages_desc = Message.query.order_by(Message.timestamp.desc()).all()
        assert len(messages_desc) == 2
        assert messages_desc[0].timestamp == datetime(2022, 1, 2)


@pytest.fixture
def new_student():
    """Créer un nouvel étudiant pour le test."""
    return Student(
        last_name='ADIN',
        first_name='WA SHEMA',
        class_name='P3',
        absences=0,
        class_id=1,
        date_naissance='2000-01-02',
        debt=0.0,
        fees_paid=True,
        notes='Aucune',
        numero_matricule='123456',
        options='Option A',
        parent='ALI',
        presences=10,
        religion='Catholique',
        registration_date='2023-01-01',
        sections='Section A',
        parent_id='1'
    )


def test_student_create(new_student):
    """Tester la création d'un étudiant."""
    assert new_student.numero_matricule == '123456'
