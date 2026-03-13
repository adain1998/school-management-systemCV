import os
from dotenv import load_dotenv
from flask_argon2 import Argon2

# Charger les variables d'environnement depuis un fichier .env
load_dotenv()

def strtobool(val):
    return val.lower() in ('true', '1', 'yes', 'on')

class Config:
    """
    Configuration principale de l'application Flask.
    """
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')  # La clé secrète pour les sessions
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///school.db')  # URI de la base de données
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Désactiver les notifications de modifications dans SQLAlchemy

    # Configuration du mail
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = strtobool(os.getenv('MAIL_USE_TLS', 'true'))
    MAIL_USE_SSL = strtobool(os.getenv('MAIL_USE_SSL', 'false'))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_EMAIL')

    # Sécurité et protection CSRF
    WTF_CSRF_ENABLED = True  # Activer CSRF pour la sécurité des formulaires

    # Configuration de Argon2 pour le hachage des mots de passe
    ARGON2_SECRET = os.getenv('ARGON2_SECRET', 'your_argon2_secret')
    ARGON2_ROUNDS = int(os.getenv('ARGON2_ROUNDS', 4))

class DevelopmentConfig(Config):
    """
    Configuration spécifique pour l'environnement de développement.
    """
    ENV = "development"
    DEBUG = True  # Active le mode debug pour afficher des erreurs détaillées
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL", "sqlite:///dev.db")  # URI pour la base de données de développement
    FLASK_ENV = "development"  # Indique à Flask que l'application est en mode développement

class ProductionConfig(Config):
    """
    Configuration spécifique pour l'environnement de production.
    """
    ENV = "production"
    DEBUG = False  # Désactive le mode debug en production pour des raisons de sécurité
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///prod.db")  # URI pour la base de données de production
    FLASK_ENV = "production"  # Indique à Flask que l'application est en mode production
    MAIL_USE_TLS = False  # Désactive TLS en production, si nécessaire
    MAIL_USE_SSL = True  # Active SSL en production pour sécuriser les communications mail
    MAIL_PORT = 465  # Utilise le port SSL pour les mails en production

class ConfigSQL:
    """
    Configuration spécifique pour la base de données et l'authentification.
    """
    SQLALCHEMY_DATABASE_URI = 'sqlite:///school.db'  # URI de la base de données pour l'application
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Désactive le suivi des modifications pour la base de données

    # Initialisation de Argon2
    argon2 = Argon2()  # Hachage des mots de passe pour une meilleure sécurité


class TestingConfig(DevelopmentConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
