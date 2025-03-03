from flask import flash, redirect, url_for
from functools import wraps
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.admin:
            flash('Vous devez être un administrateur pour accéder à cette page.', 'danger')
            return redirect(url_for('login'))  # Redirigez vers la page de connexion ou une autre page
        return f(*args, **kwargs)
    return decorated_function
