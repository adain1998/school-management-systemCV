import logging
import os
from datetime import datetime
from flask import Flask, render_template, request, url_for as flask_url_for
from flask_argon2 import Argon2
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv  # ← Ajouté

# Charger les variables d’environnement depuis. Env
load_dotenv()  # ← Ajouté

from config import DevelopmentConfig, ProductionConfig
import click
from update_templates import scan_templates, restore_backups

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

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def create_app(config_class=None):
    app = Flask(__name__)

    if config_class is None:
        env = os.getenv("FLASK_ENV", "development")
        config_class = DevelopmentConfig if env == "development" else ProductionConfig

    app.config.from_object(config_class)
    app.config.setdefault("ENV", "development")

    print(f"🚀 ENV Loaded: {app.config.get('ENV')}")

    if app.config["ENV"] == "development":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    argon2.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # 📁 Suivi global + sauvegarde temporaire des fichiers uploadés
    @app.before_request
    def track_file_uploads():
        if request.method in ["POST", "PUT", "PATCH"] and request.content_type and "multipart/form-data" in request.content_type:
            for key, file in request.files.items():
                timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
                safe_filename = f"{timestamp}_{file.filename}"
                save_path = os.path.join(UPLOAD_FOLDER, safe_filename)
                file.save(save_path)
                logger.info(f"📁 Fichier reçu : champ='{key}', nom_fichier='{file.filename}', type='{file.content_type}', sauvegardé dans='{save_path}'")

    @app.errorhandler(500)
    def internal_error(error):
        logger.error("Erreur interne du serveur: %s", error)
        logger.warning("Tentative de rendre la page 5001")
        return render_template("5001.html"), 500

    # Enregistrement des blueprints
    from app.Gestion_des_section import sect
    from app.gestion_exams import examen
    from app.Gestion_des_rapports_financiers import rapport
    from app.students_blueprint import stud
    from app.gestion_des_performances import application
    from app.Gestion_des_paiements import paiem
    from app.Gestion_des_options import opt
    from app.Gestion_des_notes import resultat
    from app.Gestion_des_messages import mes
    from app.GESTION_des_frais import paie
    from app.Gestion_des_forum import meeting
    from app.Gestion_des_classes import niveau
    from app.Gestion_des_absences import absenc
    from app.authentification import auth
    from app.Gestion_des_tableaux_de_bord import tableau
    from app.Gestion_denregistrement_tous_utilisateur import connex
    from .service_worker import service_worker_bp  # <-- Import ici

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
    app.register_blueprint(service_worker_bp)

    # --- Wrapper professionnel pour url_for dans Jinja ---
    def url_for_with_blueprint(endpoint, **values):
        # Si l'endpoint contient déjà un blueprint, on ne touche pas
        if '.' in endpoint:
            return flask_url_for(endpoint, **values)
        # Sinon, on récupère le blueprint courant depuis la requête
        bp = request.blueprint
        if bp:
            endpoint = f"{bp}.{endpoint}"
        return flask_url_for(endpoint, **values)

    # Remplace url_for dans Jinja par ce wrapper
    app.jinja_env.globals['url_for'] = url_for_with_blueprint

    @app.route('/routes')
    def show_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"Endpoint: {rule.endpoint} - URL: {rule}")
        return render_template('routes.html', routes=routes)

    logger.info("Application Flask initialisée avec succès.")

    # Ajout des commandes CLI
    @app.cli.command("scan-templates")
    def scan_templates_command():
        """Analyse et modifie-les templates HTML."""
        click.echo("🔍 Début de l'analyse des templates...")
        scan_templates()
        click.echo("🎯 Analyse terminée.")

    @app.cli.command("restore-templates")
    def restore_templates_command():
        """Restaure les fichiers templates depuis les sauvegardes."""
        click.echo("♻️ Restauration des templates depuis les sauvegardes...")
        restore_backups()
        click.echo("✅ Restauration terminée.")
    return app


__all__ = ["create_app", "db", "login_manager", "mail", "limiter"]
