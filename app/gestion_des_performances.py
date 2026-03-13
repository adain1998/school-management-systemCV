import os
from datetime import datetime
from tempfile import NamedTemporaryFile

import pandas as pd
from flask import render_template, Blueprint, request, flash, make_response, send_file, redirect, after_this_request
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from weasyprint import HTML
from app.utils.data_processing import process_student_data
from app.utils.charting import generate_charts
from app.services.sorting_service import apply_sorting
from app.models import Note, Exam, Absence, Attendance, Assignment, Matiere, Student, Notification, Classe
from app.extensions import db
blueprint_application = Blueprint("application", __name__)


@blueprint_application.route('/performance', methods=['GET'])
@login_required
def performance():
    try:
        role = current_user.role  # Supposons que l'utilisateur à un attribut `role`
        performance_data = []

        if role == 'Parent' or role == 'Élève':
            # Récupération des enfants (ou de soi-même) si Parent ou Élève
            student_ids = current_user.children_ids.split(',') if role == 'Parent' else [str(current_user.student_id)]
            students = Student.query.filter(Student.id.in_(student_ids)).all()

        elif role == 'Enseignant':
            # Les enseignants voient les élèves des classes dont ils sont responsables
            classes = current_user.classes  # Supposons que l'enseignant à un attribut `classes`
            students = Student.query.join(Classe).filter(Classe.id.in_([c.id for c in classes])).all()

        elif role == 'Admin':
            # Admin voit tous les étudiants
            students = Student.query.all()

        else:
            flash("Rôle non reconnu. Accès refusé.", "danger")
            return render_template("error_performance.html", error="Accès non autorisé.")

        for student in students:
            notes = Note.query.filter_by(student_id=student.id).all()
            exams = Exam.query.filter_by(student_id=student.id).all()
            absences = Absence.query.filter_by(student_id=student.id).all()
            attendance = Attendance.query.filter_by(student_id=student.id).all()
            assignments = Assignment.query.filter_by(student_id=student.id).all()

            performance_data.append({
                'student': student,
                'notes': [note.serialize() for note in notes],
                'exams': [exam.serialize() for exam in exams],
                'absences': [absence.serialize() for absence in absences],
                'attendance': [att.serialize() for att in attendance],
                'assignments': [ass.serialize() for ass in assignments]
            })

        return render_template('performance.html', performance_data=performance_data, role=role,year=datetime.now().year)

    except SQLAlchemyError as e:
        flash(f"Erreur de base de données : {str(e)}", "danger")
        return render_template('error_performance.html', error="Erreur de base de données.")
    except Exception as e:
        flash(f"Erreur : {str(e)}", "danger")
        return render_template('error_performance.html', error="Erreur inattendue.")



@blueprint_application.route('/', methods=['GET', 'POST'])
def results():
    # Récupération des paramètres de requête avec gestion des valeurs par défaut
    page = request.args.get('page', 1, type=int)
    per_page = 15
    sort_by = request.args.get('sort_by', 'nom')
    order = request.args.get('order', 'asc')
    filter_value = request.args.get('filter')

    try:
        # Construction de la requête SQLAlchemy avec jointure pour calculer les moyennes
        query = Matiere.query.join(Note, Matiere.id == Note.matiere_id).add_columns(
            db.func.avg(Note.valeur).label('moyenne')).group_by(Matiere.id)

        # Application du filtre pour les moyennes supérieures ou inférieures à
        if filter_value == 'sup':
            query = query.having(db.func.avg(Note.valeur) >= 5)
        elif filter_value == 'inf':
            query = query.having(db.func.avg(Note.valeur) <= 5)

        # Application du tri dynamique
        query = apply_sorting(query, sort_by, order)

        # Récupération des résultats paginés
        matieres = query.paginate(page=page, per_page=per_page)

        # Traitement des données avec Pandas
        df = process_student_data("bureau_student.csv")

        # Génération des graphiques avec Matplotlib
        generate_charts(df)

    except SQLAlchemyError as e:
        flash(f"Erreur de base de données : {str(e)}", "danger")
        return render_template('error_performance.html', error="Problème avec la base de données")
    except Exception as e:
        flash(f"Erreur : {str(e)}", "danger")
        return render_template('error_performance.html', error="Une erreur inconnue est survenue")

    return render_template('performance_report.html', matieres=matieres, page=page, per_page=per_page,
                           sort_by=sort_by, order=order, filter_value=filter_value)




@blueprint_application.route('/student/<int:student_id>', methods=['GET'])
@login_required
def student_performance(student_id):
    student = Student.query.get_or_404(student_id)
    notes_performance = Note.query.filter_by(student_id=student_id).all()
    attendances = Attendance.query.filter_by(student_id=student_id).all()
    assignments_performance = Assignment.query.filter_by(student_id=student_id).all()
    return render_template('student_performance.html', student=student,
                           notes_performance=notes_performance, attendances=attendances,
                           assignments_performance=assignments_performance)


# Crétion de bulletins pour les élèves
@blueprint_application.route("/performance/<int:student_id>/bulletin")
@login_required
def export_pdf(student_id):
    student = Student.query.get_or_404(student_id)
    notes = Note.query.filter_by(student_id=student_id).all()
    html = render_template('bulletin_pdf.html', student=student, notes=notes)
    pdf = HTML(string=html).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=bulletin.pdf'
    return response


def notify_user(user_id, message):
    notification = Notification(user_id=user_id, message=message)
    db.session.add(notification)
    db.session.commit()



@blueprint_application.route("/export/notes")
@login_required
def export_notes():
    try:
        notes = Note.query.all()

        if not notes:
            flash("Aucune note trouvée à exporter.", "warning")
            return redirect(request.referrer or '/')

        data = [{
            'Élève': note.student.nom,
            'Matière': note.matiere.nom,
            'Valeur': note.valeur
        } for note in notes]

        df = pd.DataFrame(data)

        # Fichier temporaire
        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            tmp_path = tmp.name
            with pd.ExcelWriter(tmp_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Notes')

        # Supprimer le fichier après l'envoi
        @after_this_request
        def remove_file(response):
            try:
                os.remove(tmp_path)
            except Exception as er:
                print(f"Erreur de suppression du fichier temporaire : {er}")
            return response

        return send_file(
            tmp_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='notes.xlsx'
        )

    except Exception as e:
        flash(f"Erreur lors de l'exportation des notes : {str(e)}", "danger")
        return redirect(request.referrer or '/')