import csv
from io import StringIO
from zoneinfo import ZoneInfo
import io
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, current_app, \
    make_response, Response, send_file
from datetime import datetime, timedelta
from pytz import timezone, utc
from flask_login import login_required
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from weasyprint import HTML
from app.forms import PaymentForm
from sqlalchemy.exc import SQLAlchemyError
import logging
import tempfile
import pandas as pd
from app.models import db, Student, Payment, Frais, Installment, Classe

blueprint_paiem = Blueprint('paiem', __name__, template_folder='templates')


logger = logging.getLogger(__name__)
# Page d'accueil des paiements
@blueprint_paiem.route('/paiements')
@login_required
def paiement_accueil():
    return render_template('/accueil.html')



# Nouvelle saisie de paiement
@blueprint_paiem.route('/paiements/nouveau', methods=['GET'])
@login_required
def paiement_nouveau():
    form = PaymentForm()

    students = Student.query.all()
    frais_list = Frais.query.all()
    form.student_id.choices = [(s.id, f"{s.first_name} {s.last_name}") for s in students]
    form.frais_id.choices = [(f.id, f"{f.nom} - {f.montant} €") for f in frais_list]

    return render_template('paiements/nouveau.html', form=form)


# Création de paiement - POST
@blueprint_paiem.route('/paiements', methods=['POST'])
@login_required
def create_payment():
    form = PaymentForm()

    if not form.validate_on_submit():
        flash("Formulaire invalide.", "danger")
        return redirect(url_for('paiem.paiement_nouveau'))

    try:
        new_payment = Payment(
            montant=form.montant.data,
            date=form.date.data,
            student_id=form.student_id.data,
            frais_id=form.frais_id.data,
            mois=form.mois.data,
            annee=form.annee.data,
            statut=form.statut.data,
            timestamp=datetime.now()
        )
        db.session.add(new_payment)
        db.session.commit()
        flash("Paiement enregistré avec succès.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur de création du paiement : {str(e)}", "danger")

    return redirect(url_for('paiem.liste_paiements'))


# Liste des paiements
@blueprint_paiem.route('/paiements/liste')
@login_required
def liste_paiements():
    paiements = Payment.query.order_by(Payment.date.desc()).all()
    return render_template('paiements/listes.html', paiements=paiements)



@blueprint_paiem.route('/paiements/classe/<int:class_id>')
@login_required
def paiements_par_classe(class_id):
    try:
        # 🔍 Vérifie si la classe existe
        classe = Classe.query.get_or_404(class_id)

        # 🎯 Récupère les étudiants de la classe avec leurs paiements
        students = Student.query.options(joinedload(Student.payments)) \
            .filter_by(class_id=class_id).all()

        if not students:
            flash("Aucun étudiant trouvé pour cette classe.", "info")
            return render_template("paiements/filtrer_par_classe.html", classe=classe, students=[], payments=[])

        # 🔁 Liste de tous les paiements pour les étudiants de la classe
        student_ids = [s.id for s in students]
        payments = Payment.query.filter(Payment.student_id.in_(student_ids)).all()

        return render_template("paiements/filtrer_par_classe.html",
                               classe=classe, students=students, payments=payments)

    except Exception as e:
        db.session.rollback()
        flash(f"Une erreur est survenue : {str(e)}", "danger")
        return redirect(url_for("paiem.liste_paiements"))



# Paiements selon une période
@blueprint_paiem.route('/paiements/periode')
@login_required
def paiements_par_periode():
    period = request.args.get('periode', 'today')
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    now = datetime.now(utc)

    periods = {
        'today': now.replace(hour=0, minute=0, second=0, microsecond=0),
        'yesterday': (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0),
        'week': now - timedelta(weeks=1),
        'two_weeks': now - timedelta(weeks=2),
        'month': now - timedelta(days=30),
        'three_months': now - timedelta(days=90),
        'six_months': now - timedelta(days=180),
        'year': now - timedelta(days=365)
    }

    try:
        if period == 'custom':
            if not start_str or not end_str:
                return jsonify({"error": "Période personnalisée requiert 'start' et 'end'."}), 400
            try:
                start = datetime.fromisoformat(start_str).replace(tzinfo=utc)
                end = datetime.fromisoformat(end_str).replace(tzinfo=utc)
            except ValueError:
                return jsonify({"error": "Format de date invalide. Utilisez ISO 8601."}), 400
        else:
            if period not in periods:
                return jsonify({"error": f"Période invalide : {period}"}), 400
            start = periods[period]
            end = now

        # Requête sécurisée
        paiements = Payment.query.filter(Payment.date >= start, Payment.date <= end).order_by(Payment.date.desc()).all()

        # Détection du type de réponse
        if request.accept_mimetypes.best == 'application/json':
            return jsonify([
                {
                    "id": p.id,
                    "montant": p.amount,
                    "date": p.date.isoformat(),
                    "client": p.client.name if p.client else "N/A"
                } for p in paiements
            ])

        return render_template('paiements/periode.jinja.html', payments=paiements, period=period, start=start, end=end)

    except SQLAlchemyError as e:
        logging.exception("Erreur lors de la récupération des paiements")
        flash(f"Erreur lors du chargement des paiements.:{e}", "danger")
        return redirect(url_for('paiem.liste_paiements'))

    except Exception as e:
        logging.exception("Erreur inattendue")
        flash(f"Erreur inattendue : {str(e)}", "danger")
        return redirect(url_for('paiem.liste_paiements'))



@blueprint_paiem.route('/retard')
@login_required
def paiements_en_retard():
    try:
        now = datetime.now(utc).date()
        page = request.args.get('page', 1, type=int)
        per_page = 20

        # Filtres
        nom_client = request.args.get('client', '').strip()
        mois = request.args.get('mois', '').strip().lower()  # Ex: janvier
        annee = request.args.get('annee', type=int)

        # Base de la requête : paiements en retard
        query = Payment.query.options(joinedload(Payment.student))\
            .filter(Payment.date < now, Payment.statut != 'payé')

        # Filtrer par nom du client (étudiant)
        if nom_client:
            query = query.join(Payment.student).filter(Student.nom.ilike(f'%{nom_client}%'))

        # Filtrer par mois et année si précisés
        if mois:
            query = query.filter(Payment.mois.ilike(mois))
        if annee:
            query = query.filter(Payment.annee == annee)

        # Pagination et tri
        pagination = query.order_by(Payment.date.desc())\
                          .paginate(page=page, per_page=per_page, error_out=False)

        return render_template(
            'paiements/paiement_en_retard.html',
            payments=pagination.items,
            pagination=pagination,
            filters={'client': nom_client, 'mois': mois, 'annee': annee}
        )

    except SQLAlchemyError as e:
        flash("Erreur lors de la récupération des paiements en retard.", "danger")
        print(f"[Erreur SQL] {e}")
        return render_template('paiements/paiement_en_retard.html', payments=[], pagination=None)



@blueprint_paiem.route('/paiements/rapport')
@login_required
def rapport_financier():
    # définir now en début de fonction, avant le try
    tz = timezone('Africa/Lubumbashi')
    now = datetime.now(utc).astimezone(tz)

    try:
        debut_mois = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if now.month == 1:
            debut_prec = debut_mois.replace(year=now.year - 1, month=12)
        else:
            debut_prec = debut_mois.replace(month=now.month - 1)

        rapports = db.session.query(
            func.date_trunc('month', func.timezone('Africa/Lubumbashi', Payment.date)).label('mois'),
            func.coalesce(func.sum(Payment.montant), 0).label('total')
        ).filter(
            Payment.date >= debut_prec,
            Payment.date < debut_mois
        ).group_by(
            func.date_trunc('month', Payment.date)
        ).order_by('mois').all()

        rapport_formatte = {r.mois.strftime('%B %Y'): float(r.total) for r in rapports}

        return render_template('paiements/rapport.html', report_data=rapport_formatte, current_month=now.strftime('%B %Y'))

    except Exception as e:
        flash(f"Erreur lors de la récupération du rapport financier. Veuillez réessayer plus tard.:{e}", "error")
        return render_template('paiements/rapport.html', report_data={}, current_month=now.strftime('%B %Y'))



# Gestion globale des paiements
@blueprint_paiem.route('/paiements/gerer')
@login_required
def gerer_paiements():
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        statut = request.args.get('statut', '')

        query = Payment.query

        if search:
            query = query.join(Student).filter(
                db.or_(
                    Student.nom_complet.ilike(f'%{search}%'),
                    Payment.mois.ilike(f'%{search}%')
                )
            )

        if statut:
            query = query.filter(Payment.statut == statut)

        payments = query.order_by(Payment.date.desc()).paginate(page=page, per_page=20)

        return render_template('paiements/gerer_paiement.jinja.html', payments=payments)

    except Exception as e:
        flash(f"Erreur lors de la récupération des paiements : {e}", "error")
        return render_template('paiements/gerer_paiement.jinja.html', payments=None)



@blueprint_paiem.route('/paiements/installments/<int:payment_id>', methods=['GET'])
@login_required
def show_installments(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    installments = Installment.query.filter_by(payment_id=payment.id).order_by(Installment.due_date).all()

    if not installments:
        flash("Aucune échéance trouvée pour ce paiement.", "info")
        return redirect(url_for('paiem.paiement_accueil'))

    return render_template('paiements/installments_list.html', payment=payment, installments=installments)



@blueprint_paiem.route('/installments/<int:installment_id>/pay', methods=['POST'])
def pay_installment(installment_id):
    installment = Installment.query.get_or_404(installment_id)
    installment.paid = True
    installment.date_paid = datetime.now(ZoneInfo("Africa/Lubumbashi"))
    installment.payment_method = request.form.get('payment_method')
    db.session.commit()
    flash('Paiement effectué avec succès.', 'success')
    return redirect(url_for('paiem.show_installments', payment_id=installment.payment_id))



@blueprint_paiem.route('/paiements/installments/edit/<int:installment_id>', methods=['GET', 'POST'])
@login_required
def edit_installment(installment_id):
    installment = Installment.query.get_or_404(installment_id)
    if request.method == 'POST':
        try:
            installment.amount = float(request.form['amount'])
            installment.due_date = datetime.strptime(request.form['due_date'], "%Y-%m-%d").date()
            db.session.commit()
            flash("Échéance mise à jour avec succès.", "success")
            return redirect(url_for('paiem.show_installments', payment_id=installment.payment_id))
        except Exception as e:
            flash("Erreur lors de la mise à jour : " + str(e), "danger")
    return render_template('paiements/edit_installment.html', installment=installment)




@blueprint_paiem.route('/paiements/installments/add/<int:payment_id>', methods=['GET', 'POST'])
@login_required
def add_installment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            due_date = datetime.strptime(request.form['due_date'], "%Y-%m-%d").date()
            new_installment = Installment(payment_id=payment.id, amount=amount, due_date=due_date, paid=False)
            db.session.add(new_installment)
            db.session.commit()
            flash("Nouvelle échéance ajoutée.", "success")
            return redirect(url_for('paiem.show_installments', payment_id=payment.id))
        except Exception as e:
            flash("Erreur lors de l’ajout : " + str(e), "danger")
    return render_template('paiements/add_installment.html', payment=payment)



@blueprint_paiem.route('/installment/<int:installment_id>/delete', methods=['POST'])
def delete_installment(installment_id):
    installment = Installment.query.get_or_404(installment_id)

    try:
        db.session.delete(installment)
        db.session.commit()
        flash("Échéance supprimée avec succès.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la suppression de l’échéance: {e}", "danger")

    # Rediriger vers la page des échéances liées au paiement
    return redirect(url_for('paiem.show_installments', payment_id=installment.payment_id))



@blueprint_paiem.route('/installment/<int:installment_id>/cancel', methods=['POST'])
def cancel_payment(installment_id):
    installment = Installment.query.get_or_404(installment_id)
    if installment.paid:
        installment.paid = False
        installment.date_paid = None
        installment.payment_method = None
        db.session.commit()
        flash("Paiement annulé avec succès.", "warning")
    else:
        flash("Cette échéance n’a pas encore été payée.", "info")
    return redirect(url_for('paiem.show_installments', payment_id=installment.payment_id))



@blueprint_paiem.route('/installments/<int:payment_id>/export/excel')
@login_required
def export_installments_excel(payment_id):
    try:
        payment = Payment.query.get_or_404(payment_id)

        # Préparer les données
        data = [{
            "Montant": inst.amount,
            "Date échéance": inst.due_date.strftime("%d/%m/%Y"),
            "Statut": "Payé" if inst.paid else "En attente",
            "Date payé": inst.date_paid.strftime("%d/%m/%Y") if inst.date_paid else "",
            "Méthode de paiement": inst.payment_method or ""
        } for inst in payment.installments]

        df = pd.DataFrame(data)

        # Créer un fichier temporaire pour Excel
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_name = tmp.name  # chemin du fichier

        # Écriture dans le fichier Excel temporaire
        with pd.ExcelWriter(tmp_name, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Echéances')

        # Lire le contenu du fichier pour le renvoyer
        with open(tmp_name, 'rb') as f:
            excel_data = f.read()

        return Response(
            excel_data,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment; filename=echeances_{payment.id}.xlsx"}
        )

    except Exception as e:
        logger.exception("Erreur lors de l’export Excel")
        flash(f"Échec de l’export Excel : {e}", "danger")
        return redirect(url_for('paiem.paiement_accueil'))



@blueprint_paiem.route('/installments/<int:payment_id>/export/pdf')
def export_installments_pdf(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    installments = Installment.query.filter_by(payment_id=payment.id).all()

    html_out = render_template('paiements/installments_pdf.html', payment=payment, installments=installments)
    pdf = HTML(string=html_out).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=echéances_{payment_id}.pdf'

    return response



@blueprint_paiem.route('/paiements/historique', methods=['GET'])
def historique_paiements():
    start_date = None
    end_date = None
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        export = request.args.get('export')
        page = request.args.get('page', 1, type=int)

        query = Payment.query.order_by(desc(Payment.timestamp))

        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Payment.timestamp >= start)
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(Payment.timestamp <= end)

        if export == 'csv':
            paiements = query.all()
            si = StringIO()
            writer = csv.writer(si)
            writer.writerow(['ID', 'Montant', 'Date', 'Étudiant', 'Frais'])

            for p in paiements:
                writer.writerow([
                    p.id,
                    p.amount,
                    p.timestamp.strftime('%d/%m/%Y %H:%M'),
                    getattr(p.student, 'full_name', 'N/A'),
                    getattr(p.frais, 'libelle', 'N/A')
                ])
            si.seek(0)
            # Convertir le contenu texte en bytes
            bytes_io = io.BytesIO()
            bytes_io.write(si.getvalue().encode('utf-8'))  # encodage UTF-8
            bytes_io.seek(0)

            return send_file(
                bytes_io,
                mimetype='text/csv',
                as_attachment=True,
                download_name='historique_paiements.csv'
            )

        pagination = query.paginate(page=page, per_page=10)
        paiements = pagination.items

    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des paiements : {e}")
        paiements = []
        pagination = None

    return render_template(
        'paiements/historique_paiements.html',
        paiements=paiements,
        pagination=pagination,
        blueprint_paiem='paiem',
        start_date=start_date,
        end_date=end_date
    )
