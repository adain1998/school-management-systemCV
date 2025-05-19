from flask import flash, redirect, url_for
from functools import wraps
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Vous devez être un administrateur pour accéder à cette page.', 'danger')
            return redirect(url_for('auth.login'))  # suppose que ton blueprint auth à une route 'login'
        return f(*args, **kwargs)
    return decorated_function
