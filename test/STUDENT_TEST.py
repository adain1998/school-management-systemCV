# -*- coding: utf-8 -*-
import unittest
from routes import create_app, db
from models import Student


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(u'Liste des Étudiants', response.data)

    def test_add_student(self):
        response = self.client.post('/add_student', data=dict(
            nom='Doe',
            prenom='John',
            date_naissance='2000-01-01',
            classe_id=1,
            registration_date='2022-01-01',
            religion='None',
            adresse='123 Main St'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(u'Student added successfully!', response.data)
        student = Student.query.filter_by(last_name='Doe').first()
        self.assertIsNotNone(student)

    """ def test_edit_student(self):
        student = Student(
            last_name='Doe',
            first_name='John',
            class_name='Math',
            date_naissance='2000-01-01',
            registration_date='2022-01-01',
            fees_paid=100.0,
            class_id=1,
            debt=0.0,
            religion='None',
            adresse='123 Main St'
        )
        with self.app.app_context():
            db.session.add(student)
            db.session.commit()
        response = self.client.post(f'/edit_student/{student.id}', data=dict(
            nom='Doe',
            prenom='Jane',
            date_naissance='2000-01-01',
            classe_id=1,
            registration_date
        if __name__ == '__main__':
            email = "exemple@domaine.com"
        token = TokenManager.generate_confirmation_token(email)
        print('jeton généré:', token)
        email_verifie, unique_id = TokenManager.verify_confirmation_token(token)
        print("Email verifié:", email_verifie)
        print("UUID verifié:", unique_id)"""
