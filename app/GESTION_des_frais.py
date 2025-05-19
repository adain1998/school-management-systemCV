from flask import render_template, request, redirect, flash, url_for, Blueprint, abort
from app.models import db, Frais, Payment, User
from app.admin_decorateur import admin_required
from flask_login import login_required
from app.decorators import roles_required

paie = Blueprint('paie', __name__)


@paie.route('/fees')
@login_required
@roles_required('admin', 'superadmin', 'comptable')
def view_fees():
    frais = Frais.query.all()
    return render_template('fee.html', frais=frais)


@paie.route("/add_fee", methods=['GET', 'POST'])
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



@paie.route('/edit_fee/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'superadmin')
def edit_fee():
    frais = Frais.query.get_or_404(id)
    if request.method == 'POST':
        try:
            frais.student_nom = request.form.get('student_nom', frais.student_nom)
            frais.montant = float(request.form.get('montant', frais.montant))
            frais.status = request.form.get('status', frais.status)
            db.session.commit()
            flash('Frais mis à jour avec succès.', 'success')
            return redirect(url_for('paie.view_fees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la mise à jour : {str(e)}', 'danger')
    return render_template('edit_fee.html', frais=frais)


@paie.route('/delete_fee/<int:id>', methods=['POST'])
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


@paie.route('/')
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


@paie.route('/details_frais/<int:frais_id>')
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




"""from flask import render_template, request, redirect, flash, url_for, Blueprint, abort
from app.models import db, Frais, Payment, User, Finance
from app.admin_decorateur import admin_required
paie = Blueprint('paie', __name__)


@paie.route('/fees')
def view_fees():
    frais = Frais.query.all()
    return render_template('fee.html', frais=frais)


@paie.route('/add_fee', methods=['POST'], endpoint='add_fee_post')
def add_fee_post():
    student_nom = request.form['student_nom']
    montant = request.form['montant']
    status = request.form['status']
    description = request.form['description']
    new_fee = Frais(student_nom=student_nom, montant=montant, status=status, description=description)
    db.session.add(new_fee)
    db.session.commit()
    flash('Fee added successfully!', 'success')
    return redirect(url_for('view_fees'))



@paie.route("/add_fee", methods=['GET', 'POST'], endpoint='add_fee_form')
@admin_required
def add_fee_form():
    if request.method == 'POST':
        fee_type = request.form['fee_type']
        amount = float(request.form['amount'])
        description = request.form.get('description', '')
        fee = Finance(fee_type=fee_type, amount=amount, description=description)
        db.session.add(fee)
        db.session.commit()
        flash('Fee added successfully!', 'success')
        return redirect(url_for('add_fee_form'))
    return render_template('add_fee.html')



@paie.route('/edit_fee/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_fee():
    frais = Frais.query.get_or_404(id)
    if request.method == ['POST']:
        frais.student_nom = request.form['student_nom']
        frais.montant = request.form['montant']
        frais.status = request.form['status']
        db.session.commit()
        flash('Fee updated successfully!', 'success')
        return redirect(url_for('view_fees'))
    return render_template('edit_fee.html', frais=frais)


@paie.route('/delete_fee/<int:id>',  methods=['POST'])
@admin_required
def delete_fee():
    frais = Frais.query.get_or_404(id)
    db.session.delete(frais)
    db.session.commit()
    flash('Fee deleted successfully!', 'success')
    return redirect(url_for('view_fees'))


@paie.route('/')
def index_frais():
    frais_list = ["Inscription", "Frais de l'Etat", "Frais scolaire", "frais de transport,frais de fonctionnement"]
    return render_template('index_student.html', frais_list=frais_list)


def frais_serialize(frais):
    return {"id": frais.id, "type": frais.type, "montant": frais.montant, "description": frais.description,
            "statut": frais.statut}


# route pour verifier si vous êtes administrateur

@paie.route('/details_frais/<int:frais_id>')
@admin_required
def details_frais(frais_id):
    if frais_id <= 0:
        abort(404)  # Frais ID invalide

    frais = Frais.query.get(frais_id)
    if frais is None or frais.montant <= 0:
        abort(404)  # Frais introuvable ou montant invalide

    # Récupération des détails de l'utilisateur associé
    utilisateur = User.query.get(frais.user_id)

    # Récupération des paiements associés
    paiements = Payment.query.filter_by(frais_id=frais.id).all()

    return render_template("Détails_des_frais.html",
                           frais=frais, utilisateur=utilisateur, paiements=paiements)"""


