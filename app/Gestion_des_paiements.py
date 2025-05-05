from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from datetime import datetime, timedelta
from pytz import timezone
import pytz
from flask_login import login_required
from app.forms import PaymentForm
from app.models import db, Student, Payment, Frais
from app.Gestion_des_notes import filter_and_sort
from sqlalchemy import func

paiem = Blueprint('paiem', __name__)


@paiem.route('/index')
def paiem_index():
    return render_template('acceuil.html')


@paiem.route('/payment/new', methods=['GET'])
@login_required
def new_payment():
    form = PaymentForm()
    return render_template('payment_form.html', form=form)


# Filtrer le paiement par classe
@paiem.route('/paiement/class/<int:class_id>', methods=['GET'])
@login_required
def payment_by_class(class_id):
    try:
        students = Student.query.filter_by(class_id=class_id).all()
        payments = Payment.query.filter(Payment.student_id.in_([student.id for student in students])).all()
        return render_template('filtrer_paiement.html', students=students, payments=payments)
    except Exception as e:
        flash(f"Erreur lors de la récupération des paiements: {str(e)}", "danger")
        return redirect(url_for('paiem.index'))



@paiem.route('/payments', methods=['GET'])
@login_required
def get_payments():
    period = request.args.get('period', 'today')
    now = datetime.now(pytz.utc)

    try:
        if period == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'yesterday':
            start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start = now - timedelta(weeks=1)
        elif period == 'two_weeks':
            start = now - timedelta(weeks=2)
        elif period == 'month':
            start = now - timedelta(days=30)
        elif period == 'three_months':
            start = now - timedelta(days=90)
        elif period == 'six_months':
            start = now - timedelta(days=180)
        elif period == 'year':
            start = now - timedelta(days=365)
        else:
            return jsonify({"message": "Période invalide"}), 400

        payments = Payment.query.filter(Payment.date >= start).all()
        return render_template('Get_payment.html', payments=payments, period=period)
    except Exception as e:
        flash(f"Erreur lors de la récupération des paiements: {str(e)}", "danger")
        return redirect(url_for('paiem.index'))



@paiem.route('/payment', methods=['POST'])
@login_required
def create_payment():
    montant = request.form.get('montant')
    date = request.form.get('date')
    student_id = request.form.get('student_id')
    frais_id = request.form.get('frais_id')
    mois = request.form.get('mois')
    annee = request.form.get('annee')
    statut = request.form.get('statut')

    if not all([montant, date, student_id, frais_id, mois, annee, statut]):
        flash("Informations manquantes", "danger")
        return redirect(url_for('paiem.new_payment'))

    try:
        montant = float(montant)
    except ValueError:
        flash("Montant invalide", "danger")
        return redirect(url_for('paiem.new_payment'))

    try:
        payment = Payment(
            montant=montant,
            date=datetime.strptime(date, '%Y-%m-%d'),
            student_id=int(student_id),
            frais_id=int(frais_id),
            mois=mois,
            annee=int(annee),
            statut=statut
        )
        db.session.add(payment)
        db.session.commit()
        flash("Paiement créé avec succès", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la création du paiement: {str(e)}", "danger")
        return redirect(url_for('paiem.new_payment'))

    return redirect(url_for('paiem.get_payments'))



@paiem.route('/paiement/add', methods=['GET', 'POST'])
@login_required
def add_paiement(students):
    form = PaymentForm()
    form.student_id.choices = [(student.id, student.nom) for student in Student.query.all()]
    form.frais_id.choices = [(frais.id, frais.description) for frais in Frais.query.all()]
    if request.method == 'POST':
        if form.validate_on_submit():
            montant = form.montant.data
            date = form.date.data
            student_id = form.student_id.data
            frais_id = form.frais_id.data
            mois = form.mois.data
            annee = form.annee.data
            statut = form.statut.data
            if not all([date, student_id, frais_id, montant]):
                flash("Toutes les informations sont requises", "danger")
                return redirect(url_for('paiem.add_payment'))

            if not montant.isdigit() or int(montant) <= 0:
                return render_template('error.html', message='Le Montant doit être un nombre positif')

            new_paiement = Payment(montant=montant, date=datetime.strptime(date, '%Y-%m-%d'), student_id=student_id,
                                   frais_id=frais_id, annee=annee, mois=mois, statut=statut)
            db.session.add(new_paiement)
            db.session.commit()
            flash('Paiement ajouté avec succès.', 'success')
            return redirect(url_for('paiem.get_payments'))
        students = Student.query.all()
    return render_template('Ajouter_paiement.html', form=form, students=students)



@paiem.route('/paiements/manage', methods=['GET'])
@login_required
def manage_payments():
    payments = Payment.query.all()
    return render_template('manage_payments.html', payments=payments)



@paiem.route('/paiements/overdue', methods=['GET'])
@login_required
def overdue_payments():
    today = datetime.now(pytz.utc)
    impaye_payments = Payment.query.filter(Payment.echeance < today).all()
    return render_template('overdue_payment.html', payments=impaye_payments)



@paiem.route('/paiements/report', methods=['GET'])
@login_required
def financial_report():
    # Récupérer le fuseau horaire local
    local_tz = timezone('Africa/Lubumbashi')

    # Obtenir la date actuelle en UTC et la convertir en heure locale
    now = datetime.now(pytz.utc).astimezone(local_tz)

    # Calculer le premier jour du mois en cours
    first_day_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Calculer le premier jour du mois précédent
    if first_day_of_current_month.month == 1:
        first_day_of_previous_month = first_day_of_current_month.replace(year=first_day_of_current_month.year - 1,
                                                                         month=12)
    else:
        first_day_of_previous_month = first_day_of_current_month.replace(month=first_day_of_current_month.month - 1)

    # Requête pour obtenir le total des paiements par mois
    report_data = db.session.query(
        func.date_trunc('month', func.timezone('Africa/Lubumbashi', Payment.date)).label('mois'),
        func.sum(Payment.montant).label('total_paiements')
    ).filter(
        Payment.date >= first_day_of_previous_month,
        Payment.date < first_day_of_current_month
    ).group_by(
        func.date_trunc('month', Payment.date)
    ).order_by('mois').all()

    # Formatage des résultats pour l'affichage
    formatted_report_data = {
        record.mois.strftime('%B %Y'): record.total_paiements or 0
        for record in report_data
    }

    return render_template('Rapport_financier.html', report_data=formatted_report_data)



@paiem.route('/paiements/installments/<int:payment_id>', methods=['GET', 'POST'])
@login_required
def payment_installments(payment_id):
    payment = Payment.query.get_or_404(payment_id)

    if request.method == 'POST':
        montant = request.form.get('montant')
        echeance = request.form.get('echeance')
        nombre_echeances = int(request.form.get('nombre_echeances'))

        # Logique pour créer les paiements échelonnés
        montant_par_echeance = float(montant) / nombre_echeances
        for i in range(nombre_echeances):
            echeance_date = datetime.strptime(echeance, '%Y-%m-%d') + timedelta(days=i * 30)
            new_paie = Payment(
                montant=montant_par_echeance,
                echeance=echeance_date,
                statut='En attente',
                parent_payment_id=payment.id
            )
            db.session.add(new_paie)
        db.session.commit()

        flash('Paiements échelonnés créés avec succès.', 'success')
        return redirect(url_for('app.manage_payments'))

    return render_template('payment_installments.html', payment=payment)


# Historique de paiement


@paiem.route('/payment_history')
@login_required
def payment_history():
    payments = Payment.query.all()
    return render_template('payment_history.html', payments=payments)



@paiem.route('/make_payment/<int:payment_id>', methods=['GET', 'POST'])
@login_required
def make_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    if request.method == 'POST':
        # Process payment using Stripe or another gateway
        payment.paid = True
        payment.payment_date = datetime.now(pytz.utc)
        payment.payment_status = 'Paid'
        db.session.commit()
        return redirect(url_for('paiem.payment_history'))
    return render_template('make_payment.html', payment=payment)



def check_overdue_payments():
    today = datetime.now(pytz.utc).date()
    mis_payments = Payment.query.filter(Payment.due_date <= today, not Payment.paid).all()
    for payment in mis_payments:
        # Send reminder email or notification
        print(f"Reminder: Payment {payment.id} is overdue.")

# Schedule this function to run daily using a cron job


@paiem.route('/payment/filter', methods=['GET', 'POST'])
@login_required
def filter_payment():
    form = PaymentForm()

    filter_by = request.args.get('filter_by', 'timestamp')
    order = request.args.get('order', 'asc')
    filter_value = request.args.get('filter_value', '')

    valid_columns = {'timestamp', 'amount', 'status'}
    if filter_by not in valid_columns:
        flash("Filtrage invalide.", "danger")
        return redirect(url_for('paiem.filter_payment'))

    if order not in {'asc', 'desc'}:
        flash("Ordre de tri invalide.", "danger")
        return redirect(url_for('paiem.filter_payment'))

    try:
        payments = filter_and_sort(Payment, filter_by, filter_value, order)
    except Exception as e:
        flash(f"Erreur lors du filtrage des paiements: {e}", "danger")
        payments = []

    return render_template('finance.html', form=form, payments=payments)