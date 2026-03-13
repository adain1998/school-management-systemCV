from flask import render_template, request, redirect, flash, url_for, Blueprint, abort

from app.forms import EditFeeForm
from app.models import db, Frais, Payment, User
from flask_login import login_required
from app.decorators import roles_required

blueprint_paie = Blueprint('paie', __name__)


@blueprint_paie.route('/fees')
@login_required
@roles_required('admin', 'superadmin', 'comptable')
def view_fees():
    frais = Frais.query.all()
    return render_template('fee.html', frais=frais)



@blueprint_paie.route("/add_fee", methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'superadmin')
def add_fee():
    if request.method == 'POST':
        try:
            student_nom = request.form.get('student_nom', '').strip()
            montant = float(request.form.get('montant', 0))
            status = request.form.get('status', '').strip()
            description = request.form.get('description', '').strip()

            if not student_nom or montant <= 0 or not status:
                flash('Veuillez remplir correctement tous les champs.', 'warning')
                return redirect(url_for('paie.add_fee'))

            new_fee = Frais(student_nom=student_nom, montant=montant, status=status, description=description)
            db.session.add(new_fee)
            db.session.commit()
            flash('Frais ajouté avec succès !', 'success')
            return redirect(url_for('paie.view_fees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout du frais : {str(e)}', 'danger')

    return render_template('add_fee.html')



@blueprint_paie.route('/edit_fee/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'superadmin')
def edit_fee(id_frais):
    frais = Frais.query.get_or_404(id_frais)
    form = EditFeeForm()

    if form.validate_on_submit():
        try:
            # Mise à jour avec les nouvelles données du formulaire
            frais.student_nom = form.student_full_name.data.strip()
            frais.montant = form.montant.data
            frais.status = form.status.data
            db.session.commit()
            flash('Frais mis à jour avec succès.', 'success')
            return redirect(url_for('paie.view_fees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la mise à jour : {str(e)}', 'danger')
    else:
        # Préremplir le formulaire si GET
        form.student_full_name.data = frais.student_nom
        form.montant.data = frais.montant
        form.status.data = frais.status

    return render_template('edit_fee.html', form=form, frais=frais)




@blueprint_paie.route('/delete_fee/<int:id>', methods=['POST'])
@login_required
@roles_required('admin', 'superadmin')
def delete_fee():
    frais = Frais.query.get_or_404(id)
    try:
        db.session.delete(frais)
        db.session.commit()
        flash('Frais supprimé avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression : {str(e)}', 'danger')
    return redirect(url_for('paie.view_fees'))



@blueprint_paie.route('/')
@roles_required('admin', 'comptable')
@login_required
def index_frais():
    frais_list = ["Inscription", "Frais de l'Etat", "Frais scolaire", "Frais de transport", "Frais de fonctionnement"]
    return render_template('index_student.html', frais_list=frais_list)


def frais_serialize(frais):
    return {
        "id": frais.id,
        "type": frais.type,
        "montant": frais.montant,
        "description": frais.description,
        "statut": frais.statut
    }



@blueprint_paie.route('/details_frais/<int:frais_id>')
@roles_required('admin', 'superadmin','comptable')
def details_frais(frais_id):
    if frais_id <= 0:
        abort(404)

    frais = Frais.query.get(frais_id)
    if frais is None or frais.montant <= 0:
        abort(404)

    utilisateur = User.query.get(frais.user_id)
    paiements = Payment.query.filter_by(frais_id=frais.id).all()

    return render_template("Détails_des_frais.html", frais=frais, utilisateur=utilisateur, paiements=paiements)