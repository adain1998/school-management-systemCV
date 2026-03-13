from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime
import logging

blueprint_public = Blueprint('public', __name__)

logger = logging.getLogger(__name__)

# Injection de l’année actuelle dans tous les templates
@blueprint_public.app_context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

# === ROUTES PUBLIQUES ===
@blueprint_public.route('/confidentialite')
def confidentialite():
    return render_template('confidentialite.html')

@blueprint_public.route('/mentions-legales', endpoint='mentions_legales')
def mentions_legales():
    return render_template('mentions_legales.html')

@blueprint_public.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        logger.info(f"📩 Message reçu : {name} <{email}> - Sujet : {subject} - Contenu : {message}")

        flash('Merci pour votre message, nous vous répondrons rapidement.', 'success')
        return redirect(url_for('public.contact'))  # car dans un blueprint
    return render_template('contact.html')
