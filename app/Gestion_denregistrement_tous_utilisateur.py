from flask import render_template, flash, redirect, url_for, Blueprint, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash  # Import de la fonction pour le hashage du mot de passe
from app.models import db, User, Enseignant, Eleve, Administrateur
from app.forms import SignupForm, LoginForm
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging


connex = Blueprint('connex', __name__)
logger = logging.getLogger(__name__)

@connex.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data.strip().lower()
        username = form.username.data.strip()
        last_name = form.last_name.data.strip()
        role = form.role.data.strip().lower()

        specialite = form.specialite.data.strip() if form.specialite.data else None
        niveau = form.niveau.data.strip() if form.niveau.data else None
        role_admin = form.role_admin.data.strip() if form.role_admin.data else None

        new_user = None  # ✅ initialisation

        try:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("Cette adresse email est déjà utilisée.", "danger")
                logger.warning(f"Tentative d'inscription avec email existant : {email}")
                return redirect(url_for('connex.signup'))

            if role == 'enseignant':
                new_user = Enseignant(
                    username=username,
                    email=email,
                    last_name=last_name,
                    role=role,
                    specialite=specialite
                )
            elif role == 'eleve':
                new_user = Eleve(
                    username=username,
                    email=email,
                    last_name=last_name,
                    role=role,
                    niveau=niveau
                )
            elif role == 'administrateur':
                new_user = Administrateur(
                    username=username,
                    email=email,
                    last_name=last_name,
                    role=role,
                    role_admin=role_admin
                )
            else:
                flash("Rôle invalide.", "danger")
                logger.error(f"Rôle inconnu : {role}")
                return redirect(url_for('connex.signup'))

            # ✅ Sécurité : s'assurer que new_user n'est pas None
            if new_user:
                new_user.set_password(form.password.data)
                db.session.add(new_user)
                db.session.commit()

                login_user(new_user)
                flash("Bienvenue ! Votre compte a été créé avec succès.", "success")
                logger.info(f"Nouvel utilisateur inscrit : {email} ({role})")
                return redirect(url_for('tableau.dashboard_generale'))

        except IntegrityError:
            db.session.rollback()
            flash("Erreur d'intégrité : email probablement déjà utilisé.", "danger")
            logger.warning(f"Conflit d'intégrité lors de l'inscription de : {email}")

        except SQLAlchemyError as db_err:
            db.session.rollback()
            flash("Erreur de base de données. Veuillez réessayer.", "danger")
            logger.exception(f"Erreur SQLAlchemy lors de l'inscription : {db_err}")

        except Exception as e:
            db.session.rollback()
            flash("Une erreur inattendue est survenue. Veuillez réessayer plus tard.", "danger")
            logger.exception(f"Erreur inattendue lors de l'inscription : {e}")

    return render_template('signup.html', form=form)



@connex.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("Vous êtes déjà connecté.", "info")
        return redirect(url_for('tableau.dashboard'))  # Rediriger vers un tableau de bord général

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            remember = form.remember.data  # Récupérer la valeur de "Se souvenir de moi"
            login_user(user, remember=remember)  # Passer la valeur à login_user
            flash("Connexion réussie !", "success")

            # Redirection en fonction du rôle
            if user.role == "enseignant":
                return redirect(url_for('tableau.enseignant.dashboard'))
            elif user.role == "eleve":
                return redirect(url_for('tableau.eleve.dashboard'))
            elif user.role == "administrateur":
                return redirect(url_for('tableau.admin.dashboard'))
            else:
                return redirect(url_for('tableau.dashboard'))

        else:
            flash("Email ou mot de passe incorrect.", "danger")

    return render_template('login.html', form=form)



@connex.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for('connex.login'))