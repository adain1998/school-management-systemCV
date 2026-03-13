from run import app
from app.extensions import db
from flask_migrate import Migrate
from app import models # noqa: F401 # très important pour enregistrer les tables

migrate = Migrate(app, db)
