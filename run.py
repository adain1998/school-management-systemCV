import os
from config import Config, DevelopmentConfig, ProductionConfig
from flask import Flask
def create_app(config_class=None):

    """
    Fonction usine pour créer et configurer l'application Flask.
    """
    # Si aucun config_class n'est passé, déterminer la configuration en fonction de l'environnement
    if config_class is None:
        if os.getenv('FLASK_ENV') == 'production':
            config_class = ProductionConfig
        else:
            config_class = DevelopmentConfig

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Le reste de ta fonction create_app...
    return app
