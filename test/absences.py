import unittest
import os
import sys
from datetime import date
from app.__init__ import create_app
from app.models import db, Student, Absence

# Ajouter le chemin du projet pour éviter les erreurs d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class AbsenceTestCase(unittest.TestCase):

    def setUp(self):
        """Configuration de l'application pour les tests."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Création d'un étudiant fictif pour les tests
            self.student = Student(
                last_name="Doe",
                first_name="John",
                class_name="Terminale S",
                date_naissance=date(2005, 5, 20),
                numero_matricule="MAT123456",
                class_id=1,  # Simulons une classe ID fictive
                parent_id=1,  # Simulons un parent ID fictif
            )
            db.session.add(self.student)
            db.session.commit()

    def tearDown(self):
        """Nettoyage après chaque test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_absence(self):
        """Test de l'ajout d'une absence."""
        with self.app.app_context():
            response = self.client.post(
                f'/absences/{self.student.id}',
                data={'date': date.today().strftime('%Y-%m-%d'), 'reason': 'Maladie'},
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn('Absence ajoutée avec succès', response.data.decode('utf-8'))

            # Vérification dans la base de données
            absence = Absence.query.filter_by(student_id=self.student.id).first()
            self.assertIsNotNone(absence)
            self.assertEqual(absence.reason, 'Maladie')

    def test_view_absences(self):
        """Test de l'affichage des absences d'un étudiant."""
        with self.app.app_context():
            db.session.add(Absence(date=date.today(), reason='Voyage', student=self.student))
            db.session.commit()

        response = self.client.get(f'/absences/{self.student.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Voyage', response.data.decode('utf-8'))

    def test_edit_absence(self):
        """Test de la modification d'une absence."""
        with self.app.app_context():
            absence = Absence(date=date.today(), reason='Problème familial', student=self.student)
            db.session.add(absence)
            db.session.commit()
            absence_id = absence.id

        response = self.client.post(
            f'/absences/edit/{absence_id}',
            data={'date': date.today().strftime('%Y-%m-%d'), 'reason': 'Motif mis à jour'},
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('Absence modifiée avec succès', response.data.decode('utf-8'))

        with self.app.app_context():
            updated_absence = Absence.query.get(absence_id)
            self.assertEqual(updated_absence.reason, 'Motif mis à jour')

    def test_delete_absence(self):
        """Test de la suppression d'une absence."""
        with self.app.app_context():
            absence = Absence(date=date.today(), reason='Sortie scolaire', student=self.student)
            db.session.add(absence)
            db.session.commit()
            absence_id = absence.id

        response = self.client.post(f'/absences/delete/{absence_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Absence supprimée avec succès', response.data.decode('utf-8'))

        with self.app.app_context():
            deleted_absence = Absence.query.get(absence_id)
            self.assertIsNone(deleted_absence)


if __name__ == '__main__':
    unittest.main()
