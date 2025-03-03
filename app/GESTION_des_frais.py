from flask import render_template, request, redirect, flash, url_for, Blueprint, abort
from models import db, Frais, Payment, User, Finance
from admin_decorateur import admin_required
paie = Blueprint('paie', __name__)


@paie.route('/fees')
def view_fees():
    frais = Frais.query.all()
    return render_template('fee.html', frais=frais)


@paie.route('/add_fee', methods=['POST'])
@admin_required
def add_fee():
    student_nom = request.form['student_nom']
    montant = request.form['montant']
    status = request.form['status']
    description = request.form['description']
    new_fee = Frais(student_nom=student_nom, montant=montant, status=status, description=description)
    db.session.add(new_fee)
    db.session.commit()
    flash('Fee added successfully!', 'success')
    return redirect(url_for('view_fees'))


@paie.route("/add_fee", methods=['GET', 'POST'])
@admin_required
def add_fee():
    if request.method == 'POST':
        fee_type = request.form['fee_type']
        amount = float(request.form['amount'])
        description = request.form.get('description', '')
        fee = Finance(fee_type=fee_type, amount=amount, description=description)
        db.session.add(fee)
        db.session.commit()
        flash('Fee added successfully!', 'success')
        return redirect(url_for('add_fee'))
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


@paie.route('/delete_fee/<int:id>')
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
                           frais=frais, utilisateur=utilisateur, paiements=paiements)


@paie.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')
