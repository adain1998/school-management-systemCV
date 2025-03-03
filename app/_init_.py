import logging
from flask import Flask, render_template
from flask_argon2 import Argon2
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config, DevelopmentConfig, ProductionConfig

# Initialisation des extensions
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
argon2 = Argon2()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"], storage_uri="memory://")


def create_app(config_class=Config):
    """
    Factory function pour créer et configurer l'application Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configuration spécifique pour l'environnement (dev ou prod)
    if app.config["ENV"] == "development":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Initialisation des extensions avec l'application
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    argon2.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Gestion des erreurs
    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning("Page non trouvée: %s", error)
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error("Erreur interne du serveur: %s", error)
        return render_template("500.html"), 500

    # 📌 Importation explicite des blueprints sans points
    from Gestion_des_section import sect
    from gestion_exams import examen
    from Gestion_des_rapports_financiers import rapport
    from students_blueprint import stud
    from gestion_des_performances import application
    from Gestion_des_paiements import paiem
    from Gestion_des_options import opt
    from Gestion_des_notes import resultat
    from Gestion_des_messages import mes
    from GESTION_des_frais import paie
    from Gestion_des_forum import meeting
    from Gestion_des_classes import niveau
    from Gestion_des_absences import absenc
    from authentification import auth
    from Gestion_des_tableaux_de_bord import tableau
    from Gestion_denregistrement_tous_utilisateur import connex

    # 📌 Enregistrement des blueprints
    app.register_blueprint(sect, url_prefix="/sect")
    app.register_blueprint(examen, url_prefix="/examen")
    app.register_blueprint(rapport, url_prefix="/rapports")
    app.register_blueprint(stud, url_prefix="/students")
    app.register_blueprint(application, url_prefix="/application")
    app.register_blueprint(paiem, url_prefix="/paiem")
    app.register_blueprint(opt, url_prefix="/opt")
    app.register_blueprint(resultat, url_prefix="/resultat")
    app.register_blueprint(mes, url_prefix="/mes")
    app.register_blueprint(paie, url_prefix="/paie")
    app.register_blueprint(meeting, url_prefix="/meeting")
    app.register_blueprint(niveau, url_prefix="/niveau")
    app.register_blueprint(absenc, url_prefix="/absenc")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(tableau, url_prefix="/tableau")
    app.register_blueprint(connex, url_prefix="/connex")

    logger.info("Application Flask initialisée avec succès.")
    return app


# 📌 Exposer create_app
__all__ = ["create_app", "db", "login_manager", "mail"]

