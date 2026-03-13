from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask import current_app as app
from app.decorators import roles_required
from app.models import db, Option
from app.forms import OptionForm
from sqlalchemy.exc import IntegrityError
# Blueprint pour la gestion des options
blueprint_opt = Blueprint('opt', __name__)


# Vue pour afficher toutes les options

@blueprint_opt.route('/options')
@login_required  # Protège la route si nécessaire
@roles_required('admin', 'superadmin')  # Ajoute une sécurité si besoin
def view_options():
    try:
        options = Option.query.order_by(Option.nom.asc()).all()

        if not options:
            flash("Aucune option trouvée dans la base de données.", "info")

        return render_template('option.html', options=options)

    except Exception as e:
        app.logger.error(f"[view_options] Erreur lors du chargement des options : {str(e)}", exc_info=True)
        flash("Une erreur est survenue lors du chargement des options. Veuillez réessayer plus tard.", "danger")
        return redirect(url_for('tableau.index'))



# Vue pour ajouter une option
@blueprint_opt.route('/add_option', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'superadmin')
def add_option():
    form = OptionForm()

    if form.validate_on_submit():
        try:
            # Vérifie si une option avec le même nom existe déjà
            existing = Option.query.filter_by(name=form.name.data.strip()).first()
            if existing:
                flash("Cette option existe déjà.", "warning")
                return redirect(url_for('opt.add_option'))

            new_option = Option(name=form.name.data.strip())
            db.session.add(new_option)
            db.session.commit()

            flash("Option ajoutée avec succès !", "success")
            return redirect(url_for('opt.view_options'))

        except IntegrityError:
            db.session.rollback()
            flash("Erreur d'intégrité : il se peut que cette option existe déjà.", "danger")
            return redirect(url_for('opt.add_option'))

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"[add_option] Erreur : {str(e)}", exc_info=True)
            flash("Une erreur est survenue lors de l'ajout de l'option. Veuillez réessayer.", "danger")
            return redirect(url_for('opt.add_option'))

    return render_template('add_option.html', form=form)


# Vue pour éditer une option
@blueprint_opt.route('/edit_option/<int:option_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'superadmin')
def edit_option(option_id):
    option = Option.query.get_or_404(option_id)
    form = OptionForm()

    if form.validate_on_submit():
        try:
            # Empêcher les doublons
            existing = Option.query.filter(Option.name == form.name.data.strip(), Option.id != option_id).first()
            if existing:
                flash("Une autre option avec ce nom existe déjà.", "warning")
                return redirect(url_for('opt.edit_option', option_id=option_id))

            option.name = form.name.data.strip()
            db.session.commit()
            flash('Option mise à jour avec succès !', 'success')
            return redirect(url_for('opt.view_options'))

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"[edit_option] Erreur : {str(e)}", exc_info=True)
            flash(f'Une erreur est survenue : {str(e)}', 'danger')
            return redirect(url_for('opt.view_options'))

    # Préremplir le formulaire en GET uniquement
    if request.method == 'GET':
        form.name.data = option.name

    return render_template('edit_option.html', form=form, option=option)



# Vue pour supprimer une option
@blueprint_opt.route('/delete_option/<int:option_id>', methods=['POST'])
@login_required
@roles_required('admin', 'superadmin')
def delete_option(option_id):  # renommer ici aussi
    try:
        option = Option.query.get_or_404(option_id)
        db.session.delete(option)
        db.session.commit()
        flash('Option supprimée avec succès !', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression de l’option : {str(e)}', 'danger')
    return redirect(url_for('opt.view_options'))
