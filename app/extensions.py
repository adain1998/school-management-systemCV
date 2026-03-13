# app/extensions.py
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_argon2 import Argon2
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialisation des extensions (sans app ici)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
argon2 = Argon2()
csrf = CSRFProtect()
ma = Marshmallow()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
