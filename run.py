import os
import sys
import traceback
from dotenv import load_dotenv  # ✅ Importer dotenv
from app import create_app  # ✅ Importation de la fonction create_app depuis app.__init__.py
from config import DevelopmentConfig, ProductionConfig

# ✅ Charger les variables du fichier .env
load_dotenv()
print("📂 Dossier courant:", os.getcwd())
print("📜 Fichiers disponibles:", os.listdir(os.getcwd()))
print('Python %s on %s' % (sys.version, sys.platform))

# Ajouter le chemin de l'application à sys.path pour que les modules dans School_management soient accessibles
sys.path.extend(['C:\\Users\\pc\\Videos\\School_management'])
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


def create_flask_app_instance():
    """
    Fonction pour créer et configurer l'instance de l'application Flask.
    """
    # ✅ Forcer FLASK_ENV à "development" si non spécifié dans les variables d'environnement
    os.environ.setdefault("FLASK_ENV", "development")

    # ✅ Choisir la configuration appropriée
    config_class = DevelopmentConfig if os.getenv("FLASK_ENV") == "development" else ProductionConfig

    # Créer l'application Flask avec la configuration spécifiée
    flask_app = create_app(config_class=config_class)

    @flask_app.route("/")
    def home():
        return "Bienvenue sur l'application School Management!"

    return flask_app


# ✅ Démarrer l'application Flask avec gestion des erreurs
if __name__ == "__main__":
    try:
        app_instance = create_flask_app_instance()  # Créer l'instance de l'application
        print(f"🚀 FLASK_ENV: {os.getenv('FLASK_ENV')}")  # Afficher l'environnement utilisé
        app_instance.run(debug=True)  # Lancer l'application en mode debug
    except Exception as e:
        print("🚨 Erreur lors du démarrage:", str(e))
        traceback.print_exc()
