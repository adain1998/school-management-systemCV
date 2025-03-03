"""import unittest
from flask import Flask
from models import db, Exam
from app import create_app




class ExamTestCase(unittest.TestCase):

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

    def test_add_exam(self):
        response = self.client.post('/exams/add', data=dict(
            student_id=1,
            subject='Mathematics',
            score=85.5
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Examen ajout\xc3\xa9 avec succ\xc3\xa8s', response.data)
        with self.app.app_context():
            exam = Exam.query.filter_by(student_id=1).first()
            self.assertIsNotNone(exam)

    def test_view_exams(self):
        with self.app.app_context():
            db.session.add(Exam(student_id=1, subject='Science', score=90))
            db.session.commit()
        response = self.client.get('/schedules')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Science', response.data)

    def test_filter_exams(self):
        with self.app.app_context():
            db.session.add(Exam(student_id=1, subject='History', score=78))
            db.session.commit()
        response = self.client.post('/exams/filter_and_search', data=dict(
            subject='History'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'History', response.data)

    def test_delete_exam(self):
        with self.app.app_context():
            exam = Exam(student_id=1, subject='Physics', score=88)
            db.session.add(exam)
            db.session.commit()
            exam_id = exam.id
        response = self.client.post(f'/exams/delete/{exam_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Examen supprim\xc3\xa9 avec succ\xc3\xa8s', response.data)
        with self.app.app_context():
            exam = Exam.query.get(exam_id)
            self.assertIsNone(exam)


if __name__ == '__main__':
    unittest.main()"""

import sys
import os
import unittest
from flask import Flask
from models import db, Exam

# Ajouter le chemin du projet pour éviter les erreurs d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

class ExamTestCase(unittest.TestCase):

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

    def test_add_exam(self):
        response = self.client.post('/exams/add', data=dict(
            student_id=1,
            subject='Mathematics',
            score=85.5
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Examen ajoutÃ© avec succÃ¨s', response.data)
        with self.app.app_context():
            exam = Exam.query.filter_by(student_id=1).first()
            self.assertIsNotNone(exam)

    def test_view_exams(self):
        with self.app.app_context():
            db.session.add(Exam(student_id=1, subject='Science', score=90))
            db.session.commit()
        response = self.client.get('/schedules')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Science', response.data)

    def test_filter_exams(self):
        with self.app.app_context():
            db.session.add(Exam(student_id=1, subject='History', score=78))
            db.session.commit()
        response = self.client.post('/exams/filter_and_search', data=dict(
            subject='History'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'History', response.data)

    def test_delete_exam(self):
        with self.app.app_context():
            exam = Exam(student_id=1, subject='Physics', score=88)
            db.session.add(exam)
            db.session.commit()
            exam_id = exam.id
        response = self.client.post(f'/exams/delete/{exam_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Examen supprimÃ© avec succÃ¨s', response.data)
        with self.app.app_context():
            exam = Exam.query.get(exam_id)
            self.assertIsNone(exam)

if __name__ == '__main__':
    unittest.main()
