# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime

from flask import Flask, render_template, request, url_for as flask_url_for, has_request_context, redirect
from werkzeug.utils import secure_filename
import click

from app.context import inject_globals
from config import DevelopmentConfig, ProductionConfig
from app.extensions import db, ma, migrate, login_manager, mail, argon2, csrf, limiter

from app.authentification import blueprint_auth
from app.Gestion_denregistrement_tous_utilisateur import blueprint_connex

# === LOGGER APPLICATION PRINCIPALE ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("app")

# === DOSSIER DE TÉLÉVERSEMENT ===
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def register_blueprints(app: Flask) -> dict:
    from app.Gestion_des_section import blueprint_sect
    from app.gestion_exams import blueprint_examen
    from app.Gestion_des_rapports_financiers import blueprint_rapport
    from app.students_blueprint import blueprint_stud
    from app.gestion_des_performances import blueprint_application
    from app.Gestion_des_paiements import blueprint_paiem
    from app.Gestion_des_tableaux_de_bord import blueprint_tableau
    from app.Gestion_des_notes import blueprint_resultat
    from app.Gestion_des_messages import blueprint_mes
    from app.attendance_routes import attendance_bp
    from app.GESTION_des_frais import blueprint_paie
    from app.Gestion_des_absences import blueprint_absenc
    from app.Gestion_des_classes import blueprint_niveau
    from app.Gestion_des_forum import blueprint_meeting
    from app.Gestion_des_options import blueprint_opt
    from app.horaires_blueprint import blueprint_schedul
    from app.footer_routes import blueprint_public
    from app.service_worker import service_worker_bp

    blueprints = {
        "blueprint_sect": blueprint_sect,
        "blueprint_examen": blueprint_examen,
        "blueprint_rapport": blueprint_rapport,
        "blueprint_stud": blueprint_stud,
        "blueprint_application": blueprint_application,
        "blueprint_tableau": blueprint_tableau,
        "blueprint_paiem": blueprint_paiem,
        "blueprint_auth": blueprint_auth,
        "blueprint_connex": blueprint_connex,
        "blueprint_resultat": blueprint_resultat,
        "blueprint_mes": blueprint_mes,
        "attendance_bp": attendance_bp,
        "blueprint_paie": blueprint_paie,
        "blueprint_absenc": blueprint_absenc,
        "blueprint_niveau": blueprint_niveau,
        "blueprint_meeting": blueprint_meeting,
        "blueprint_opt": blueprint_opt,
        "blueprint_schedul": blueprint_schedul,
        "blueprint_public": blueprint_public,
        "service_worker_bp": service_worker_bp,
    }

    for name, blueprint in blueprints.items():
        # Extraire un préfixe URL propre à partir du nom du blueprint
        # Ex : blueprint_auth → /auth, attendance_bp → /attendance
        parts = name.split('_', 1)
        prefix = "/" + (parts[1] if len(parts) > 1 else parts[0])
        prefix = prefix.replace("bp", "").replace("blueprint", "").rstrip('/')
        prefix = prefix or "/"
        app.register_blueprint(blueprint, url_prefix=prefix)

    return blueprints


def create_app(config_class: type = None) -> Flask:
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )

    env = os.getenv("FLASK_ENV", "development")
    config_class = config_class or (DevelopmentConfig if env == "development" else ProductionConfig)
    app.config.from_object(config_class)
    app.config.setdefault("ENV", "development")

    logger.setLevel(logging.DEBUG if app.config["ENV"] == "development" else logging.INFO)
    logger.info(f"🚀 ENV Loaded: {app.config.get('ENV')}")

    # Initialisation des extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    argon2.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Import modèles pour user_loader
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Enregistrement des blueprints
    registered_blueprints = register_blueprints(app)

    # Ajout des noms de blueprints dans les globaux Jinja (pour compatibilité)
    app.jinja_env.globals.update({key: bp.name for key, bp in registered_blueprints.items()})
    app.jinja_env.globals.update({
        "blueprint_auth": blueprint_auth.name,
        "blueprint_connex": blueprint_connex.name,
    })

    # Injection des variables globales dans les templates (inject_globals ne doit pas importer registered_blueprints)
    app.context_processor(inject_globals)

    # Gestion des uploads dans les requêtes POST/PUT/PATCH
    @app.before_request
    def track_file_uploads():
        if request.method in ["POST", "PUT", "PATCH"] and "multipart/form-data" in (request.content_type or ""):
            for key, file in request.files.items():
                timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
                safe_filename = f"{timestamp}_{secure_filename(file.filename)}"
                save_path = os.path.join(UPLOAD_FOLDER, safe_filename)
                file.save(save_path)
                logger.info(f"📁 Fichier reçu : champ='{key}', nom_fichier='{file.filename}', sauvegardé à='{save_path}'")

    @app.errorhandler(500)
    def internal_error(error):
        logger.error("Erreur interne: %s", error)
        return render_template("5001.html"), 500

    @app.route('/routes')
    def show_routes():
        return render_template('routes.html', routes=[
            f"Endpoint: {rule.endpoint} - URL: {rule}" for rule in app.url_map.iter_rules()
        ])

    # Custom url_for qui ajoute le blueprint si nécessaire
    def url_for_with_blueprint(endpoint, **values):
        if has_request_context():
            if endpoint == 'static':
                return flask_url_for(endpoint, **values)
            if '.' not in endpoint:
                bp = request.blueprint
                if bp:
                    endpoint = f"{bp}.{endpoint}"
        return flask_url_for(endpoint, **values)

    app.jinja_env.globals['url_for'] = url_for_with_blueprint
    app.jinja_env.globals['flask_url_for'] = flask_url_for

    @app.cli.command("scan-templates")
    def scan_templates_command():
        click.echo("🔍 Analyse des templates...")
        from update_templates import scan_templates
        scan_templates()

    @app.cli.command("restore-backups")
    def restore_backups_command():
        click.echo("♻️ Restauration des templates depuis les backups...")
        from update_templates import restore_backups
        restore_backups()

    @app.route("/")
    def redirect_to_tableau():
        return redirect(flask_url_for("tableau.index"))

    logger.info("✅ Application Flask initialisée avec succès.")
    return app




"""# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime

from flask import Flask, render_template, request, url_for as flask_url_for, has_request_context, redirect
from werkzeug.utils import secure_filename
import click

from app.footer_routes import blueprint_public
from config import DevelopmentConfig, ProductionConfig
from app.extensions import db, ma, migrate, login_manager, mail, argon2, csrf, limiter
from update_templates import scan_templates, restore_backups
from app.Gestion_denregistrement_tous_utilisateur import blueprint_connex
from app.authentification import blueprint_auth

# === LOGGER APPLICATION PRINCIPALE ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("app")

# === DOSSIER DE TÉLÉVERSEMENT ===
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def register_blueprints(app: Flask) -> dict:
    from app.Gestion_des_section import blueprint_sect
    from app.gestion_exams import blueprint_examen
    from app.Gestion_des_rapports_financiers import blueprint_rapport
    from app.students_blueprint import blueprint_stud
    from app.gestion_des_performances import blueprint_application
    from app.Gestion_des_paiements import blueprint_paiem
    from app.Gestion_des_tableaux_de_bord import blueprint_tableau
    from app.Gestion_des_notes import blueprint_resultat
    from app.Gestion_des_messages import blueprint_mes
    from app.attendance_routes import attendance_bp
    from app.GESTION_des_frais import blueprint_paie
    from app.Gestion_des_absences import blueprint_absenc
    from app.Gestion_des_classes import blueprint_niveau
    from app.Gestion_des_forum import blueprint_meeting
    from app.Gestion_des_options import blueprint_opt
    from app.horaires_blueprint import blueprint_schedul
    from app.footer_routes import blueprint_public
    from app.service_worker import service_worker_bp

    blueprints = {
        "blueprint_sect": blueprint_sect,
        "blueprint_examen": blueprint_examen,
        "blueprint_rapport": blueprint_rapport,
        "blueprint_stud": blueprint_stud,
        "blueprint_application": blueprint_application,
        "blueprint_tableau": blueprint_tableau,
        "blueprint_paiem": blueprint_paiem,
        "blueprint_auth": blueprint_auth,
        "blueprint_connex": blueprint_connex,
        "blueprint_resultat": blueprint_resultat,
        "blueprint_mes": blueprint_mes,
        "attendance_bp": attendance_bp,
        "blueprint_paie": blueprint_paie,
        "blueprint_absenc": blueprint_absenc,
        "blueprint_niveau": blueprint_niveau,
        "blueprint_meeting": blueprint_meeting,
        "blueprint_opt": blueprint_opt,
        "blueprint_schedul": blueprint_schedul,
        "blueprint_public": blueprint_public,
        "service_worker_bp": service_worker_bp,
    }

    for name, blueprint in blueprints.items():
        prefix = f"/{name.split('_', 1)[-1].replace('bp', '').replace('blueprint', '')}".rstrip('/')
        app.register_blueprint(blueprint, url_prefix=prefix if prefix else "/")

    return blueprints

def create_app(config_class: type = None) -> Flask:
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )

    #app = Flask(__name__, template_folder='../templates')
    env = os.getenv("FLASK_ENV", "development")
    config_class = config_class or (DevelopmentConfig if env == "development" else ProductionConfig)
    app.config.from_object(config_class)
    app.config.setdefault("ENV", "development")
    logger.setLevel(logging.DEBUG if app.config["ENV"] == "development" else logging.INFO)
    print(f"🚀 ENV Loaded: {app.config.get('ENV')}")

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    argon2.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    from app.models import (
        User, Visitor, Note, Attendance, Student, Classe, Option, Sections, Matiere, Frais,
        Payment, Installment, Absence, Finance, Report, Message, ForumPost, Reaction, Post,
        Assignment, StudentAssignment, Notification, SchoolInfo, Teacher, Poll, Choice,
        Parent, Schedule, Exam
    )

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.before_request
    def track_file_uploads():
        if request.method in ["POST", "PUT", "PATCH"] and "multipart/form-data" in (request.content_type or ""):
            for key, file in request.files.items():
                timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
                safe_filename = f"{timestamp}_{secure_filename(file.filename)}"
                save_path = os.path.join(UPLOAD_FOLDER, safe_filename)
                file.save(save_path)
                logger.info(f"📁 Fichier reçu : champ='{key}', nom_fichier='{file.filename}', sauvegardé à='{save_path}'")

    @app.errorhandler(500)
    def internal_error(error):
        logger.error("Erreur interne: %s", error)
        return render_template("5001.html"), 500

    # Enregistrement des blueprints et exposition dans les templates
    registered_blueprints = register_blueprints(app)

    app.jinja_env.globals.update({
        "blueprint_auth": blueprint_auth.name,
        "blueprint_connex": blueprint_connex.name,
        "blueprint_stud": registered_blueprints["blueprint_stud"].name,
        "blueprint_niveau": registered_blueprints["blueprint_niveau"].name,
        "blueprint_opt": registered_blueprints["blueprint_opt"].name,
        "blueprint_paie": registered_blueprints["blueprint_paie"].name,
        "blueprint_schedul": registered_blueprints["blueprint_schedul"].name,
        "blueprint_examen": registered_blueprints["blueprint_examen"].name,
        "blueprint_paiem": registered_blueprints["blueprint_paiem"].name,
        "blueprint_application": registered_blueprints["blueprint_application"].name,
        "blueprint_resultat": registered_blueprints["blueprint_resultat"].name,
        "blueprint_mes": registered_blueprints["blueprint_mes"].name,
        "blueprint_meeting": registered_blueprints["blueprint_meeting"].name,
        "blueprint_public": registered_blueprints["blueprint_public"].name,
    })

    @app.route('/routes')
    def show_routes():
        return render_template('routes.html', routes=[
            f"Endpoint: {rule.endpoint} - URL: {rule}" for rule in app.url_map.iter_rules()
        ])

    def url_for_with_blueprint(endpoint, **values):
        if has_request_context():
            if endpoint == 'static':
                return flask_url_for(endpoint, **values)
            if '.' not in endpoint:
                bp = request.blueprint
                if bp:
                    endpoint = f"{bp}.{endpoint}"
        return flask_url_for(endpoint, **values)

    app.jinja_env.globals['url_for'] = url_for_with_blueprint
    app.jinja_env.globals['flask_url_for'] = flask_url_for

    @app.cli.command("scan-templates")
    def scan_templates_command():
        click.echo("🔍 Analyse des templates...")
        scan_templates()

    @app.cli.command("restore-backups")
    def restore_backups_command():
        click.echo("♻️ Restauration des templates depuis les backups...")
        restore_backups()


    @app.route("/")
    def redirect_to_tableau():
        # Redirige vers la page d'accueil du tableau de bord
        return redirect(flask_url_for("tableau.index"))

    logger.info("✅ Application Flask initialisée avec succès.")
    return app
"""