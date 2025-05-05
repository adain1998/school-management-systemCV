from flask import Blueprint, render_template, redirect, url_for, flash
from app.models import db, Option
from app.forms import OptionForm
# Blueprint pour la gestion des options
opt = Blueprint('opt', __name__)


# Vue pour afficher toutes les options
@opt.route('/options')
def view_options():
    try:
        options = Option.query.all()
        return render_template('option.html', options=options)
    except Exception as e:
        flash('An error occurred while fetching options: {}'.format(str(e)), 'danger')
        return redirect(url_for('main.index'))  # Retour à la page principale ou une page d'erreur


# Vue pour ajouter une option
@opt.route('/add_option', methods=['POST', 'GET'])
def add_option():
    form = OptionForm()
    if form.validate_on_submit():
        try:
            new_option = Option(name=form.name.data)
            db.session.add(new_option)
            db.session.commit()
            flash('Option added successfully!', 'success')
            return redirect(url_for('opt.view_options'))
        except Exception as e:
            db.session.rollback()  # Annule les changements en cas d'erreur
            flash('An error occurred while adding the option: {}'.format(str(e)), 'danger')
            return redirect(url_for('opt.view_options'))

    return render_template('add_option.html', form=form)


# Vue pour éditer une option
@opt.route('/edit_option/<int:id>', methods=['GET', 'POST'])
def edit_option():
    form = OptionForm()
    option = Option.query.get_or_404(id)

    if form.validate_on_submit():
        try:
            option.name = form.name.data
            db.session.commit()
            flash('Option updated successfully!', 'success')
            return redirect(url_for('opt.view_options'))
        except Exception as e:
            db.session.rollback()  # Annule les changements en cas d'erreur
            flash('An error occurred while updating the option: {}'.format(str(e)), 'danger')
            return redirect(url_for('opt.view_options'))

    form.name.data = option.name  # Remplir le champ du formulaire avec l'option existante
    return render_template('edit_option.html', form=form, option=option)


# Vue pour supprimer une option
@opt.route('/delete_option/<int:id>', methods=['POST'])
def delete_option():
    try:
        option = Option.query.get_or_404(id)
        db.session.delete(option)
        db.session.commit()
        flash('Option deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()  # Annule les changements en cas d'erreur
        flash('An error occurred while deleting the option: {}'.format(str(e)), 'danger')

    return redirect(url_for('opt.view_options'))
