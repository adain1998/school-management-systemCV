from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash  # Import de la fonction pour le hashage du mot de passe
from app.models import db, User, Enseignant, Eleve, Administrateur
from app.forms import SignupForm, LoginForm

connex = Blueprint('connex', __name__)

@connex.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        try:
            # Vérifier si l'email est déjà utilisé
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Cet email est déjà utilisé. Veuillez en saisir un autre.', 'danger')
                return redirect(url_for('connex.signup'))

            # Créer un nouvel utilisateur en fonction du rôle sélectionné
            if form.role.data == 'enseignant':
                new_user = Enseignant(
                    username=form.username.data,
                    email=form.email.data,
                    last_name=form.last_name.data,
                    role='enseignant'
                )
            elif form.role.data == 'eleve':
                new_user = Eleve(
                    username=form.username.data,
                    email=form.email.data,
                    last_name=form.last_name.data,
                    role='eleve'
                )
            elif form.role.data == 'administrateur':
                new_user = Administrateur(
                    username=form.username.data,
                    email=form.email.data,
                    last_name=form.last_name.data,
                    role='administrateur'
                )
            else:
                flash("Erreur: Le type d'utilisateur sélectionné n'est pas valide.", 'danger')
                return redirect(url_for('connex.signup'))

            # Définir le mot de passe pour l'utilisateur
            new_user.set_password(form.password.data)

            # Sauvegarder le nouvel utilisateur dans la base de données
            db.session.add(new_user)
            db.session.commit()

            # Connexion automatique après l'inscription
            login_user(new_user)

            flash('Votre inscription a été réussie ! Un email de confirmation a été envoyé.', 'success')

            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f"Une erreur est survenue lors de l'inscription : {e}", 'danger')

    return render_template('signup.html', form=form)



@connex.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("Vous êtes déjà connecté.", "info")
        return redirect(url_for('dashboard'))  # Rediriger vers un tableau de bord général

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            remember = form.remember.data  # Récupérer la valeur de "Se souvenir de moi"
            login_user(user, remember=remember)  # Passer la valeur à login_user
            flash("Connexion réussie !", "success")

            # Redirection en fonction du rôle
            if user.role == "enseignant":
                return redirect(url_for('enseignant.dashboard'))
            elif user.role == "eleve":
                return redirect(url_for('eleve.dashboard'))
            elif user.role == "administrateur":
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('dashboard'))

        else:
            flash("Email ou mot de passe incorrect.", "danger")

    return render_template('login.html', form=form)


@connex.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for('connex.login'))