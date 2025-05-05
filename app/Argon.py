from flask_argon2 import Argon2

# Initialisation d'Argon2
argon2 = Argon2()

class PasswordHasher:
    def __init__(self, app=None):
        """Initialisation de l'instance avec l'application Flask"""
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialiser l'extension Argon2 avec l'application Flask"""
        argon2.init_app(app)

    def hash_password(self, password):
        """Retourne un mot de passe hashé"""
        return argon2.generate_password_hash(password)

    def check_password(self, hashed_password, password):
        """Vérifie si le mot de passe correspond au hash"""
        return argon2.check_password_hash(hashed_password, password)
