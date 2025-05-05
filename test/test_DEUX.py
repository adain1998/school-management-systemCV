import sys
import os
import unittest
from app import create_app, db  # Assurez-vous d'importer db de la manière correcte
from app.models import Exam  # Si vous avez déjà défini votre modèle Exam dans models.py

# Ajouter le chemin du projet pour éviter les erreurs d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class ExamTestCase(unittest.TestCase):

    def setUp(self):
        """Configuration de l'application pour les tests."""
        self.app = create_app()  # Assurez-vous que create_app() initialise bien l'app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de données en mémoire pour les tests
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Désactive les notifications inutiles
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()  # Crée toutes les tables nécessaires pour les tests

    def tearDown(self):
        """Nettoyage après chaque test."""
        with self.app.app_context():
            db.session.remove()  # Ferme la session de la base de données
            db.drop_all()  # Supprime toutes les tables après le test

    def test_add_exam(self):
        """Test de l'ajout d'un examen."""
        response = self.client.post('/exams/add', data=dict(
            student_id=1,
            subject='Mathematics',
            score=85.5
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Examen ajouté avec succès', response.data.decode('utf-8'))

        with self.app.app_context():
            exam = Exam.query.filter_by(student_id=1).first()  # Vérification que l'examen a bien été ajouté
            self.assertIsNotNone(exam)

    def test_view_exams(self):
        """Test de la consultation des examens."""
        with self.app.app_context():
            db.session.add(Exam(student_id=1, subject='Science', score=90))
            db.session.commit()

        response = self.client.get('/exams')  # Correction de la route, à ajuster si nécessaire
        self.assertEqual(response.status_code, 200)
        self.assertIn('Science', response.data.decode('utf-8'))

    def test_filter_exams(self):
        """Test du filtrage des examens."""
        with self.app.app_context():
            db.session.add(Exam(student_id=1, subject='History', score=78))
            db.session.commit()

        response = self.client.post('/exams/filter_and_search', data=dict(
            subject='History'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('History', response.data.decode('utf-8'))

    def test_delete_exam(self):
        """Test de la suppression d'un examen."""
        with self.app.app_context():
            exam = Exam(student_id=1, subject='Physics', score=88)
            db.session.add(exam)
            db.session.commit()
            exam_id = exam.id

        response = self.client.post(f'/exams/delete/{exam_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Examen supprimé avec succès', response.data.decode('utf-8'))

        with self.app.app_context():
            exam = Exam.query.get(exam_id)
            self.assertIsNone(exam)


if __name__ == '__main__':
    unittest.main()
