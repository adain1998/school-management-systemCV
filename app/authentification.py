
from flask import render_template, redirect, url_for, flash, Blueprint, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.exc import SQLAlchemyError
import secrets
import hashlib
import pytz
from datetime import datetime, timedelta,timezone
from werkzeug.security import generate_password_hash
from app.__init__ import limiter
from app.forms import SignupForm, ParentLoginForm, LoginForm, ResetPasswordRequestForm, RegistrationForm
from app.models import db, Parent, User, Visitor, User_Parent
from flask_mail import Message
from app.admin_decorateur import admin_required
from app import mail



auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['GET', 'POST'])
@limiter.limit('5 per minute')
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        try:
            existing_parent = Parent.query.filter_by(email=form.email.data).first()
            if existing_parent:
                flash('Cet e-mail est déjà utilisé.', 'danger')
                return redirect(url_for('auth.signup'))

            # Création de l'utilisateur avec les bons arguments
            new_parent = Parent()
            new_parent.email = form.email.data
            new_parent.set_password(form.password.data)

            db.session.add(new_parent)
            db.session.commit()

            send_confirmation_email(new_parent)

            flash('Un e-mail de confirmation a été envoyé.', 'success')
            return redirect(url_for('auth.login_parent'))
        except Exception as e:
            db.session.rollback()
            flash(f"Une erreur est survenue lors de l'inscription: {e}", 'danger')

    return render_template('signup.html', form=form)



@auth.route('/login_parent', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login_parent():
    if current_user.is_authenticated:
        return redirect(url_for('tableau.dashboard'))
    form = ParentLoginForm()
    if form.validate_on_submit():
        parent_from_db = Parent.query.filter_by(email=form.email.data).first()
        if parent_from_db and parent_from_db.check_password(form.password.data):
            login_user(parent_from_db, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('tableau.dashboard'))
        flash('Échec de la connexion.', 'danger')
    return render_template('Login_parents.html', form=form)



@auth.route('/reset_password', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user_laod = User.query.filter_by(email=form.email.data).first()
        if user_laod:
            token = secrets.token_urlsafe(32)
            hashed_token = hashlib.sha3_256(token.encode('utf-8')).hexdigest()
            user_laod.reset_token = hashed_token
            user_laod.reset_token_expires = datetime.now(pytz.utc) + timedelta(hours=1)
            db.session.commit()
            send_email(user_laod.email, token)
            flash('Un email a été envoyé.', 'info')
        else:
            flash('Aucun compte trouvé.', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)



@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register_parent():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        try:
            utilisateur = User_Parent()
            utilisateur.email = form.email.data
            utilisateur.set_password(form.password.data)

            db.session.add(utilisateur)
            db.session.commit()

            flash('Compte créé avec succès!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f"Une erreur est survenue lors de l'inscription: {e}", 'danger')

    return render_template('register.html', form=form)



@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user_from_db = User.query.filter_by(email=form.email.data).first()
            if user_from_db:
                if user_from_db.check_password(form.password.data):
                    login_user(user_from_db, remember=form.remember.data)
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for('home'))
                else:
                    flash('Échec de la connexion. Veuillez vérifier votre email et mot de passe.', 'danger')
            else:
                flash('Échec de la connexion. Veuillez vérifier votre email et mot de passe.', 'danger')
        except SQLAlchemyError as e:
            flash(f'Erreur de base de données : {e}', 'danger')
    return render_template('login.html', title='Se connecter', form=form)



@auth.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)



@auth.route('/admin/visitors', methods=['GET'])
@login_required
@admin_required
def manage_visitors():
    visitors = Visitor.query.all()
    return render_template('admin/manage_visitors.html', visitors=visitors)



@auth.route('/users')
@login_required
@admin_required  # Ajout pour sécuriser cette route
def user_list():
    users = User.query.all()
    return render_template('admin/users_list.html', users=users)



@auth.route('/admin/user/add', methods=['GET', 'POST'])
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



@auth.route('/admin/users/json')
@login_required
@admin_required
def get_users_json():
    """Retourne la liste des utilisateurs en JSON pour des appels AJAX."""
    users = User.query.all()
    users_data = [{"id": user.id, "username": user.username, "email": user.email, "admin": user.admin} for user in users]
    return jsonify(users_data)



@auth.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
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




def send_email(user_email, token):
    msg = Message('Réinitialisation de mot de passe', sender='your_email@example.com', recipients=[user_email])
    link = url_for('auth.reset_with_token', token=token, _external=True)
    msg.body = f"Cliquez ici pour réinitialiser votre mot de passe: {link}"
    mail.send(msg)

def send_confirmation_email(parent):
    parent.set_confirmation_token()
    db.session.commit()
    msg = Message("Confirmation de votre compte", recipients=[parent.email])
    confirmation_link = url_for('auth.confirm_email', token=parent.confirmation_token, _external=True)
    msg.body = f"Veuillez confirmer votre inscription en cliquant ici: {confirmation_link}"
    mail.send(msg)



@auth.route('/confirm/<token>')
def confirm_email(token):
    parent = Parent.query.filter_by(confirmation_token=token).first()
    if parent and parent.token_expiration > datetime.now(pytz.utc):
        parent.is_active = True
        parent.confirmation_token = None
        db.session.commit()
        flash("Compte confirmé avec succès!", 'success')
        return redirect(url_for('auth.login_parent'))
    flash("Le lien est invalide ou expiré.", 'danger')
    return redirect(url_for('auth.signup'))



@auth.route('/admin/visitor/<int:visitor_id>/edit', methods=[ 'POST'])
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
        return redirect(url_for('admin.manager_visitors'))



@auth.route('/admin/visitor/<int:visitor_id>/edit', methods=[ 'POST'])
@limiter.limit("5 per minute")
@admin_required
def edit_visitor(visitor_id):
    visitor = Visitor.query.get_or_404(visitor_id)

    if request.method == 'POST':
        visitor.name = request.form['name']
        visitor.email = request.form['email']

        db.session.commit()
        flash('Visiteur mis à jour avec succès.', 'success')
        return redirect(url_for('admin.manage_visitors'))

    return render_template('admin/edit_visitors.html', visitor=visitor)


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    """Déconnecte l'utilisateur de manière sécurisée"""
    logout_user()
    flash("Vous avez été déconnecté avec succès.", "success")
    return redirect(url_for('auth.login'))