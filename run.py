import os
import sys
import logging
import traceback
from dotenv import load_dotenv
from flask_migrate import Migrate

from app import create_app
from config import DevelopmentConfig, ProductionConfig
from app.utils.config_loader import load_config
from app.extensions import db
from app import models  # noqa

# === Création des dossiers nécessaires ===
os.makedirs('logs', exist_ok=True)
os.makedirs('static/images', exist_ok=True)

# === Configuration du logging professionnel ===
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ✅ Charger les variables d'environnement depuis le fichier .env
load_dotenv()
app_config = load_config()

# ✅ Informations de démarrage
print("📂 Dossier courant:", os.getcwd())
print("📜 Fichiers disponibles:", os.listdir(os.getcwd()))
print(f"Python {sys.version} on {sys.platform}")
print("Nom de l'école :", app_config["school_name"])

# ✅ Ajouter le répertoire courant au sys.path si nécessaire
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

def create_flask_app_instance():
    #
    os.environ.setdefault("FLASK_ENV", "development")
    config_class = DevelopmentConfig if os.getenv("FLASK_ENV") == "development" else ProductionConfig

    logging.info(f"Environnement Flask : {os.getenv('FLASK_ENV')}")
    flask_app = create_app(config_class=config_class)

    logging.info("✅ Application Flask créée avec succès")
    return flask_app

# ✅ Point d'entrée de l'application
# ✅ Instance Flask globale requise pour les commandes CLI comme flask db
app = create_flask_app_instance()
migrate = Migrate(app, db)

# ✅ Point d'entrée principal
if __name__ == "__main__":
    try:
        logging.info("🚀 Lancement de l'application Flask...")
        app.run(
            debug=(os.getenv("FLASK_ENV") == "development"),
            use_reloader=(os.getenv("FLASK_ENV") == "development"),
            port=5000
        )
    except Exception as e:
        logging.error(f"🚨 Erreur critique lors du démarrage de l'application : {e}")
        traceback.print_exc()
        print(f"🚨 Erreur lors du démarrage de l'application : {e}")




"""import os
import sys
import traceback
from dotenv import load_dotenv
from app import create_app
from config import DevelopmentConfig, ProductionConfig
from app.utils.config_loader import load_config

# ✅ Charger les variables d'environnement depuis le fichier .env
load_dotenv()
app_config = load_config()

print("📂 Dossier courant:", os.getcwd())
print("📜 Fichiers disponibles:", os.listdir(os.getcwd()))
print(f"Python {sys.version} on {sys.platform}")
print("Nom de l'école :", app_config["school_name"])

# ✅ Ajouter le répertoire courant au sys.path si nécessaire
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

def create_flask_app_instance():
    os.environ.setdefault("FLASK_ENV", "development")
    config_class = DevelopmentConfig if os.getenv("FLASK_ENV") == "development" else ProductionConfig
    flask_app = create_app(config_class=config_class)

    # ✅ Route par défaut pour tester le bon fonctionnement
    # @flask_app.route("/")
    # def home():
        # return render_template("index.html")
    return flask_app

# ✅ Point d'entrée de l'application
# ✅ Point d'entrée de l'application
if __name__ == "__main__":
    try:
        app = create_flask_app_instance()  # ✅ Création correcte de l'instance
        print(f"🚀 FLASK_ENV: {os.getenv('FLASK_ENV')}")
        app.run(
            debug=(os.getenv("FLASK_ENV") == "development"),
            use_reloader=(os.getenv("FLASK_ENV") == "development"),
            port=5000
        )
    except Exception as e:
        print(f"🚨 Erreur lors du démarrage de l'application:{e}")
        traceback.print_exc()
        import os
import sys
import logging
import traceback
from dotenv import load_dotenv
from app import create_app
from config import DevelopmentConfig, ProductionConfig
from app.utils.config_loader import load_config

# === Création des dossiers nécessaires ===
os.makedirs('logs', exist_ok=True)
os.makedirs('static/images', exist_ok=True)

# === Configuration du logging professionnel ===
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ✅ Charger les variables d'environnement depuis le fichier .env
load_dotenv()
app_config = load_config()

# ✅ Informations de démarrage
print("📂 Dossier courant:", os.getcwd())
print("📜 Fichiers disponibles:", os.listdir(os.getcwd()))
print(f"Python {sys.version} on {sys.platform}")
print("Nom de l'école :", app_config["school_name"])

# ✅ Ajouter le répertoire courant au sys.path si nécessaire
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

def create_flask_app_instance():
    #
    os.environ.setdefault("FLASK_ENV", "development")
    config_class = DevelopmentConfig if os.getenv("FLASK_ENV") == "development" else ProductionConfig

    logging.info(f"Environnement Flask : {os.getenv('FLASK_ENV')}")
    flask_app = create_app(config_class=config_class)

    logging.info("✅ Application Flask créée avec succès")
    return flask_app

# ✅ Point d'entrée de l'application
# ✅ Instance Flask globale requise pour les commandes CLI comme flask db
app = create_flask_app_instance()

# ✅ Point d'entrée principal
if __name__ == "__main__":
    try:
        logging.info("🚀 Lancement de l'application Flask...")
        app.run(
            debug=(os.getenv("FLASK_ENV") == "development"),
            use_reloader=(os.getenv("FLASK_ENV") == "development"),
            port=5000
        )
    except Exception as e:
        logging.error(f"🚨 Erreur critique lors du démarrage de l'application : {e}")
        traceback.print_exc()
        print(f"🚨 Erreur lors du démarrage de l'application : {e}")



import os
import sys
import traceback
from dotenv import load_dotenv

# === Création des dossiers nécessaires ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(BASE_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'static', 'images'), exist_ok=True)

import logging
# === Configuration du logging professionnel ===
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'app.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# === Charger les variables d'environnement ===
load_dotenv()

# === Afficher le répertoire courant et les fichiers pour le debug ===
cwd = os.getcwd()
files = os.listdir(cwd)
print(f"📂 Dossier courant: {cwd}")
print(f"📜 Fichiers disponibles: {files}")
logging.info(f"Dossier courant: {cwd}")
logging.info(f"Fichiers disponibles: {files}")
logging.info(f"Python version: {sys.version}")
logging.info(f"Plateforme: {sys.platform}")

# ✅ Ajout du chemin de base
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# === Chargement sécurisé de la configuration ===
try:
    from app.utils.config_loader import load_config
    app_config = load_config()
    school_name = app_config.get("school_name", "Nom non défini")
    print("Nom de l'école :", school_name)
    logging.info(f"Configuration chargée avec succès depuis app_config.json : Nom de l'école = {school_name}")
except FileNotFoundError as fe:
    logging.error("❌ Fichier de configuration 'app_config.json' introuvable.")
    logging.error(f"Exception : {fe}")
    print("🚨 Erreur : Fichier 'app_config.json' introuvable. Vérifiez son emplacement.")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    logging.error("❌ Une erreur inattendue est survenue lors du chargement de la configuration.")
    logging.error(f"Exception : {e}")
    traceback.print_exc()
    sys.exit(1)

# ✅ Création de l'application Flask
from app import create_app
from config import DevelopmentConfig, ProductionConfig

def create_flask_app_instance():
    os.environ.setdefault("FLASK_ENV", "development")
    config_class = DevelopmentConfig if os.getenv("FLASK_ENV") == "development" else ProductionConfig

    logging.info(f"Environnement Flask : {os.getenv('FLASK_ENV')}")
    flask_app = create_app(config_class=config_class)

    logging.info("✅ Application Flask créée avec succès")
    return flask_app

app = create_flask_app_instance()

# ✅ Lancement sécurisé
if __name__ == "__main__":
    try:
        logging.info("🚀 Lancement de l'application Flask...")
        app.run(
            debug=(os.getenv("FLASK_ENV") == "development"),
            use_reloader=(os.getenv("FLASK_ENV") == "development"),
            port=5000
        )
    except Exception as e:
        logging.error(f"🚨 Erreur critique lors du démarrage de l'application : {e}")
        traceback.print_exc()
        print(f"🚨 Erreur lors du démarrage de l'application : {e}")

        """