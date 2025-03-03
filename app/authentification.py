
from flask import render_template, redirect, url_for, flash, Blueprint, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.exc import SQLAlchemyError
import secrets
import hashlib
import pytz
import uuid
from datetime import datetime, timedelta
from flask_limiter import Limiter
from forms import SignupForm, ParentLoginForm, LoginForm, ResetPasswordRequestForm, ResetPasswordForm, RegistrationForm
from models import db, Parent, User, Visitor, User_Parent
from flask_mail import Message, mail
from admin_decorateur import admin_required



auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['GET', 'POST'])
@Limiter.limit('5 per minute')
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
@Limiter.limit("5 per minute")
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
@Limiter.limit("5 per minute")
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
@Limiter.limit("5 per minute")
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
@Limiter.limit("5 per minute")
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
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)



@auth.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@Limiter.limit("5 per minute")
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        db.session.commit()
        flash('Utilisateur mis à jour.', 'success')
        return redirect(url_for('auth.manage_users'))
    return render_template('admin/edit_user.html', user=user)



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
@Limiter.limit("5 per minute")
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
@Limiter.limit("5 per minute")
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




@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))



@auth.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@Limiter.limit("5 per minute")
@admin_required
def edit_user(use_id: int):
    use: User = User.query.get_or_404(use_id)