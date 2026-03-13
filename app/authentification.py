
from flask import render_template, redirect, url_for, flash, Blueprint, request, jsonify, current_app
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.exc import SQLAlchemyError
import secrets
import hashlib
import pytz
from datetime import datetime, timedelta,timezone
from werkzeug.security import generate_password_hash
from app.extensions import limiter
from app.forms import (ParentRegistrationForm,
                       ResetPasswordRequestForm, ParentLoginForm, ResendConfirmationForm, ResetPasswordForm)
from app.models import db, Parent, User, Visitor, Student
from flask_mail import Message
from app.admin_decorateur import admin_required
from app import mail
import logging
logger = logging.getLogger(__name__)



blueprint_auth = Blueprint('auth', __name__)



@blueprint_auth.route('/signup/parent', methods=['GET', 'POST'])
@limiter.limit('5 per minute')
def signup_parent():
    form = ParentRegistrationForm()

    if form.validate_on_submit():
        try:
            # Création du parent
            new_parent = Parent()
            new_parent.name = form.name.data.strip()
            new_parent.email = form.email.data.strip().lower()
            new_parent.set_password(form.password.data)
            new_parent.set_confirmation_token()

            db.session.add(new_parent)
            db.session.flush()  # obtenir l'ID pour la relation avec les enfants

            # Liste structurée des enfants à ajouter
            children_data = [
                {
                    'first_name': form.child1_first_name.data,
                    'last_name': form.child1_last_name.data,
                    'birth_date': form.child1_birth_date.data,
                    'class_id': form.child1_class_id.data,
                    'religion': form.child1_religion.data,
                },
                {
                    'first_name': form.child2_first_name.data,
                    'last_name': form.child2_last_name.data,
                    'birth_date': form.child2_birth_date.data,
                    'class_id': form.child2_class_id.data,
                    'religion': form.child2_religion.data,
                }
            ]

            for child in children_data:
                if child['first_name'] and child['last_name']:
                    student = Student(
                        first_name=child['first_name'].strip(),
                        last_name=child['last_name'].strip(),
                        date_naissance=child['date_naissance'],
                        class_id=child['class_id'],
                        numero_matricule=['numero_matricule'],
                        religion=child['religion'].strip() if child['religion'] else None,
                        parent_id=new_parent.id  # associer via ID
                    )
                    db.session.add(student)

            db.session.commit()

            send_confirmation_email(new_parent)
            flash(f"Bienvenue {new_parent.name} ! Un e-mail de confirmation a été envoyé.", "success")
            return redirect(url_for('auth.login_parent'))

        except SQLAlchemyError as db_err:
            db.session.rollback()
            logger.error(f"Erreur base de données lors de l'inscription parent : {db_err}")
            flash("Une erreur est survenue lors de l'inscription. Merci de réessayer plus tard.", 'danger')

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de l'inscription parent : {e}")
            flash("Une erreur inattendue est survenue. Merci de réessayer.", 'danger')

    return render_template('signup_parent.html', form=form)



@blueprint_auth.route('/login_parent', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login_parent():
    if current_user.is_authenticated:
        return redirect(url_for('tableau.dashboard'))

    form = ParentLoginForm()

    if form.validate_on_submit():
        try:
            user = Parent.query.filter(
                db.func.lower(Parent.email) == form.email.data.lower()
            ).first()

            if user:
                if user.check_password(form.password.data):
                    if not user.is_active:
                        flash("Votre compte est désactivé. Veuillez contacter l'administration.", "danger")
                    else:
                        login_user(user, remember=form.remember.data)
                        flash(f"Bienvenue {user.name} !", "success")
                        next_page = request.args.get('next')
                        return redirect(next_page) if next_page else redirect(url_for('tableau.dashboard'))
                else:
                    flash("Mot de passe incorrect.", "danger")
            else:
                flash("Aucun compte parent trouvé avec cet email.", "warning")

        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Une erreur est survenue. Veuillez réessayer plus tard.", "danger")
            print(f"[Erreur DB] login_parent: {e}")

    return render_template('Login_parents.html', form=form)



@blueprint_auth.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)



@blueprint_auth.route('/admin/visitors', methods=['GET'])
@login_required
@admin_required
def manage_visitors():
    visitors = Visitor.query.all()
    return render_template('admin/manager_visitors.html', visitors=visitors)



@blueprint_auth.route('/users')
@login_required
@admin_required  # Ajout pour sécuriser cette route
def user_list():
    users = User.query.all()
    return render_template('admin/users_list.html', users=users)



@blueprint_auth.route('/admin/user/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Ajoute un nouvel utilisateur."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')  # Le mot de passe est obligatoire.
        last_name = request.form.get('last_name')
        role = request.form.get('role', 'user')  # Défaut à "user" si non spécifié
        is_admin = request.form.get('admin') == 'on'  # Convertir en booléen

        # Vérification des champs obligatoires
        if not username or not email or not password or not last_name:
            flash("Tous les champs sont requis.", 'danger')
            return redirect(url_for('auth.add_user'))

        # Vérification si l'utilisateur existe déjà
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Cet email est déjà utilisé.", 'warning')
            return redirect(url_for('auth.add_user'))

        try:
            # Création d'un nouvel utilisateur
            new_user = User(
                username=username,
                email=email,
                last_name=last_name,
                role=role,
                admin=is_admin,
                password_hash=generate_password_hash(password),
                created_at=datetime.now(timezone.utc)
            )

            db.session.add(new_user)
            db.session.commit()

            flash(f"Utilisateur {username} ajouté avec succès.", 'success')
            return redirect(url_for('auth.manage_users'))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout : {str(e)}", 'danger')

    return render_template('admin/add_user.html')



@blueprint_auth.route('/admin/users/json')
@login_required
@admin_required
def get_users_json():
    """Retourne la liste des utilisateurs en JSON pour des appels AJAX."""
    users = User.query.all()
    users_data = [{"id": user.id, "username": user.username, "email": user.email, "admin": user.admin} for user in users]
    return jsonify(users_data)



@blueprint_auth.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)  # Récupère l'utilisateur par ID

    if request.method == 'POST':
        # Validation des données envoyées
        username = request.form.get('username')
        email = request.form.get('email')

        # Vérification de la présence des champs nécessaires
        if not username or not email:
            flash('Le nom d\'utilisateur et l\'email sont requis.', 'danger')
            return render_template('admin/edit_user.html', user=user)

        # Mise à jour des champs de l'utilisateur
        user.username = username
        user.email = email

        try:
            db.session.commit()
            flash('Utilisateur mis à jour avec succès.', 'success')
            return redirect(url_for('auth.manage_users'))  # Redirige vers la gestion des utilisateurs
        except Exception as e:
            db.session.rollback()  # En cas d'erreur, annule les changements
            flash(f'Erreur lors de la mise à jour de l\'utilisateur: {str(e)}', 'danger')

    return render_template('admin/edit_user.html', user=user)  # Affiche le formulaire d'édition




@blueprint_auth.route('/reset_password', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def reset_password_request():
    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # Génération du token même si l'utilisateur n'existe pas (prévention leak)
        token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha3_256(token.encode('utf-8')).hexdigest()

        if user:
            try:
                user.reset_token = hashed_token
                user.reset_token_expires = datetime.now(pytz.utc) + timedelta(hours=1)
                db.session.commit()
                send_password_reset_email(user.email, token)
                logger.info(f"Email de réinitialisation envoyé à {user.email}")
            except Exception as e:
                logger.exception(f"Erreur lors de la mise à jour du token de réinitialisation:{e}")
                flash("Une erreur est survenue. Veuillez réessayer.", "danger")
                return redirect(url_for("auth.reset_password_request"))

        # Toujours afficher ce message pour des raisons de sécurité
        flash('Si un compte existe avec cet e-mail, un lien de réinitialisation a été envoyé.', 'info')
        return redirect(url_for('auth.login_parent'))

    return render_template('reset_password.html', form=form)



def send_password_reset_email(user_email, token):
    """Envoie un e-mail de réinitialisation de mot de passe à l'utilisateur."""
    if not user_email or not token:
        logger.error("Email ou token manquant pour l'envoi de l'e-mail de réinitialisation.")
        return False

    try:
        reset_link = url_for('auth.reset_with_token', token=token, _external=True)
        body = f"Cliquez ici pour réinitialiser votre mot de passe : {reset_link}"

        msg = Message(
            subject='Réinitialisation de mot de passe',
            sender='noreply@example.com',  # utilise MAIL_DEFAULT_SENDER de préférence
            recipients=[user_email],
            body=body
        )
        mail.send(msg)
        logger.info(f"Email de réinitialisation envoyé à {user_email}")
        return True

    except Exception as e:
        logger.exception(f"Erreur lors de l'envoi de l'e-mail : {e}")
        return False



@blueprint_auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    # Hash le token reçu pour comparer avec celui stocké en base
    hashed_token = hashlib.sha3_256(token.encode('utf-8')).hexdigest()

    # Cherche utilisateur avec token valide et pas expiré
    user = User.query.filter_by(reset_token=hashed_token).first()

    if not user or user.reset_token_expires < datetime.now(pytz.utc):
        flash("Le lien de réinitialisation est invalide ou expiré.", "danger")
        return redirect(url_for('auth.reset_password_request'))

    form = ResetPasswordForm()  # Formulaire avec champ nouveau mot de passe

    if form.validate_on_submit():
        user.set_password(form.password.data)  # Méthode à définir pour hasher et enregistrer
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        flash("Votre mot de passe a été réinitialisé avec succès.", "success")
        return redirect(url_for('auth.login_parent'))

    return render_template('reset_with_token.html', form=form)




def send_confirmation_email(parent):
    try:
        # Génération du token
        parent.set_confirmation_token()
        db.session.commit()

        # Construction du lien de confirmation
        confirmation_link = url_for(
            'auth.confirm_email',
            token=parent.confirmation_token,
            _external=True
        )

        # Création du message
        msg = Message(
            subject="Confirmation de votre compte",
            sender=current_app.config['MAIL_EMAIL'],
            recipients=[parent.email]
        )

        msg.body = (
            f"Bonjour,\n\n"
            f"Merci de vous être inscrit. Veuillez confirmer votre adresse email en cliquant sur le lien suivant :\n"
            f"{confirmation_link}\n\n"
            f"Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer ce message."
        )

        # Envoi de l'email
        mail.send(msg)
        logger.info(f"E-mail de confirmation envoyé à {parent.email}")

    except Exception as e:
        logger.exception(f"Erreur lors de l'envoi de l'e-mail de confirmation:{e}")



@blueprint_auth.route('/confirm/<token>')
def confirm_email(token):
    try:
        parent = Parent.query.filter_by(confirmation_token=token).first()

        if not parent:
            logger.warning(f"Tentative de confirmation avec un token invalide : {token}")
            flash("Lien de confirmation invalide.", "danger")
            return redirect(url_for('auth.signup_parent'))

        if parent.token_expiration < datetime.now(pytz.utc):
            logger.info(f"Token expiré pour l'email : {parent.email}")
            flash("Le lien de confirmation a expiré. Veuillez en demander un nouveau.", "warning")
            return redirect(url_for('auth.signup_parent'))

        # Activation du compte
        parent.is_active = True
        parent.confirmation_token = None
        parent.token_expiration = None  # nettoyage
        db.session.commit()

        logger.info(f"Compte activé avec succès : {parent.email}")
        flash("Compte confirmé avec succès!", "success")
        return redirect(url_for('auth.login_parent'))

    except Exception as e:
        logger.exception(f"Erreur lors de la confirmation de l'email:{e}")
        flash("Une erreur est survenue lors de la confirmation. Veuillez réessayer.", "danger")
        return redirect(url_for('auth.signup_parent'))



@blueprint_auth.route('/resend_confirmation', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def resend_confirmation():
    form = ResendConfirmationForm()
    if form.validate_on_submit():
        parent = Parent.query.filter_by(email=form.email.data).first()

        if not parent:
            flash("Aucun compte trouvé avec cette adresse email.", "warning")
            return redirect(url_for('auth.resend_confirmation'))

        if parent.is_active:
            flash("Ce compte est déjà confirmé.", "info")
            return redirect(url_for('auth.login_parent'))

        parent.set_confirmation_token()
        db.session.commit()
        send_confirmation_email(parent)
        flash("Un nouveau lien de confirmation a été envoyé.", "success")
        return redirect(url_for('auth.login_parent'))

    return render_template('resend_confirmation.html', form=form)



@blueprint_auth.route('/admin/visitor/<int:visitor_id>/delete', methods=[ 'POST'])
@limiter.limit("5 per minute")
@admin_required
def delete_visitor(visitor_id):
    visitor = Visitor.query.get_or_404(visitor_id)

    if request.method == 'POST':
        visitor.name = request.form['name']
        visitor.email = request.form['email']
        db.session.delete(visitor)
        db.session.commit()
        flash('Visiteur supprimé avec succès.', 'success')
        return redirect(url_for('auth.manager_visitors'))



@blueprint_auth.route('/admin/visitor/<int:visitor_id>/edit', methods=[ 'POST'])
@limiter.limit("5 per minute")
@admin_required
def edit_visitor(visitor_id):
    visitor = Visitor.query.get_or_404(visitor_id)

    if request.method == 'POST':
        visitor.name = request.form['name']
        visitor.email = request.form['email']

        db.session.commit()
        flash('Visiteur mis à jour avec succès.', 'success')
        return redirect(url_for('auth.manage_visitors'))

    return render_template('admin/edit_visitors.html', visitor=visitor)



@blueprint_auth.route('/logout', methods=['POST'])
@login_required
def logout():
    """Déconnecte l'utilisateur (Parent ou autre User) et redirige au login adapté"""

    # On stocke l'instance avant la déconnexion
    user = current_user

    logout_user()
    flash("Vous avez été déconnecté avec succès.", "success")

    # Détection du type d'utilisateur
    from app.models import Parent  # adapte le chemin si besoin

    if isinstance(user, Parent):
        # Si c'est un parent, redirige vers login_parent
        return redirect(url_for('auth.login_parent'))
    else:
        # Sinon redirige vers login_utilisateur
        return redirect(url_for('connex.login_utilisateur'))