import json
import os
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "school_name": "École par défaut",
    "timezone": "UTC",
    "default_locale": "en"
}

def load_config(path='app_config.json'):
    if not os.path.exists(path):
        logger.warning(f"Fichier de configuration introuvable : {path}. Valeurs par défaut utilisées.")
        return DEFAULT_CONFIG

    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info(f"Configuration chargée depuis {path}.")
            return config
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration : {str(e)}")
        return DEFAULT_CONFIG
