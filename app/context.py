from flask import session, current_app
from datetime import datetime

def inject_globals():
    # Récupérer les noms des blueprints depuis current_app.jinja_env.globals
    blueprint_names = {key: value for key, value in current_app.jinja_env.globals.items() if key.startswith("blueprint_")}

    return {
        "user_name": session.get("user_name", "Invité"),
        "user_role": session.get("user_role", "Utilisateur"),
        "last_login": session.get("last_login", "Non défini"),
        "current_date": datetime.now().strftime("%d/%m/%Y"),
        "current_year": datetime.now().year,
        **blueprint_names
    }



"""from flask import session
from datetime import datetime

from app import blueprint_auth, blueprint_connex, blueprint_public
from app.Gestion_des_forum import blueprint_meeting
from app.Gestion_des_messages import blueprint_mes
from app.Gestion_des_notes import blueprint_resultat
from app.Gestion_des_paiements import blueprint_paiem
from app.gestion_des_performances import blueprint_application


# Import des blueprints (à adapter selon l'organisation de ton projet)


def inject_globals():
    return {
        "user_name": session.get("user_name", "Invité"),
        "user_role": session.get("user_role", "Utilisateur"),
        "last_login": session.get("last_login", "Non défini"),
        "current_date": datetime.now().strftime("%d/%m/%Y"),
        "current_year": datetime.now().year,
        "blueprint_auth": blueprint_auth.name,
        "blueprint_connex": blueprint_connex.name,
        "blueprint_meeting": blueprint_meeting.name,
        "blueprint_paiem": blueprint_paiem.name,
        "blueprint_application": blueprint_application.name,
        "blueprint_resultat": blueprint_resultat.name,
        "blueprint_mes": blueprint_mes.name,
        "blueprint_public": blueprint_public.name
    }
"""