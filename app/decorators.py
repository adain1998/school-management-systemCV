from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

# Dictionnaire de redirection selon le rôle
REDIRECTS_PAR_ROLE = {
    'admin': 'admin.dashboard',
    'superadmin': 'admin.dashboard',  # Peut avoir le même tableau que l'admin
    'parent': 'parent.dashboard',
    'eleve': 'tableau.eleve_dashboard',
    'enseignant': 'teacher.dashboard',
    'comptable': ''
    # Tu peux en ajouter d'autres ici au besoin
}

def roles_required(*roles):
    """
    Décorateur pour restreindre l'accès à des rôles spécifiques.
    :param roles: Liste des rôles autorisés (ex : 'eleve', 'admin', etc.)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Veuillez vous connecter pour accéder à cette page.", "warning")
                return redirect(url_for('auth.login'))

            if current_user.role not in roles:
                flash("Accès non autorisé pour ce rôle.", "danger")
                redirect_view = REDIRECTS_PAR_ROLE.get(current_user.role, 'index')
                return redirect(url_for(redirect_view))

            return f(*args, **kwargs)
        return decorated_function
    return decorator
