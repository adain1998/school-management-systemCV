from flask import render_template, Blueprint, url_for, redirect, flash, request
from app.models import (db, Student, Note, Absence, Teacher,
                        Report, Attendance, Message, Poll, ForumPost, SchoolInfo, Matiere)
from datetime import datetime
from flask_login import current_user, login_required
from app.decorators import roles_required  # Assure-toi que le chemin d'importation est correct
from sqlalchemy import extract
import locale

tableau = Blueprint('tableau', __name__)



@tableau.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    children_ids = current_user.children_ids.split(',')
    students = Student.query.filter(Student.id.in_(children_ids)).all()
    notes_student = Note.query.filter(Note.student_id.in_(children_ids)).all()

    for student in students:
        student_notes = [note.score for note in notes_student if note.student_id == student.id]
        student.avg_grade = sum(student_notes) / len(student_notes) if student_notes else 0

    return render_template('dashboard_admin.html', students=students)


# tableau de bord enseignant
@tableau.route('/enseignant/dashboard')
@login_required
def enseignant_dashboard():
    if current_user.role != 'enseignant':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('index'))  # Redirige vers la page d'accueil si l'utilisateur n'est pas enseignant
    return render_template('dashboard_enseignants.html')  # Affiche le tableau de bord de l'enseignant

#tableau de bord eleve

@tableau.route('/eleve/dashboard')
@login_required
@roles_required('eleve')
def eleve_dashboard():
    student = Student.query.get(current_user.id)  # ou utilise une jointure si current_user n'est pas Student

    # Moyenne par matière
    matieres_notes = (
        db.session.query(Matiere.nom, db.func.avg(Note.note).label('moyenne'))
        .join(Note, Note.matiere_id == Matiere.id)
        .filter(Note.student_id == student.id)
        .group_by(Matiere.nom)
        .all()
    )

    grades_by_subject = [{"subject": nom, "grade": round(moyenne, 2)} for nom, moyenne in matieres_notes]

    # Supposons que tu ajoutes un champ "trimestre" dans Note pour cette partie
    evolution_notes = (
        db.session.query(Note.date, db.func.avg(Note.note).label('moyenne'))
        .filter(Note.student_id == student.id)
        .group_by(db.func.strftime('%Y-%m', Note.date))  # group by mois ou trimestre
        .order_by(db.func.strftime('%Y-%m', Note.date))
        .all()
    )
    average_trend = [{"term": date.strftime('%B %Y'), "average": round(avg, 2)} for date, avg in evolution_notes]

    # Statistiques de présence et d'absences
    total_absences = len(student.absences or [])
    attendance_rate = student.attendance_rate

    return render_template(
        'dashboard_eleves.html',
        grades_by_subject=grades_by_subject,
        average_trend=average_trend,
        total_absences=total_absences,
        attendance_rate=attendance_rate
    )


#tableau de bord administrateur

@tableau.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'administrateur':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('index'))  # Redirige vers la page d'accueil

    students = Student.query.all()

    for student in students:
        # Calcul de la moyenne des notes
        student_notes = [note.score for note in student.notes]
        student.avg_grade = round(sum(student_notes) / len(student_notes), 2) if student_notes else 0

        # Calcul du taux de présence à partir de la propriété
        student.attendance_rate = student.attendance_rate

        # Nombre d'absences
        student.absences_count = len(student.absences)

    return render_template('dashboard_performance.html', students=students)


@tableau.route('/')
def index():
    user = {
        "name": "Kampangala François",
        "role": "Administrateur",
        "last_login": "08/05/2025 à 12:00"
    }
    return render_template(
        'index.html',
        title="Accueil - Gestion Scolaire",
        user_name=user["name"],
        user_role=user["role"],
        last_login=user["last_login"],
        current_date=datetime.now().strftime("%d/%m/%Y"),
        current_year=datetime.now().year
    )



@tableau.route('/dashboard')
def dashboard_generale():
    selected_month = request.args.get('month', type=int)
    selected_year = request.args.get('year', type=int)
    if not selected_year:
        selected_year = datetime.now().year

    years = list(range(2022, datetime.now().year + 1))

    def apply_date_filter(query, model_field):
        query = query.filter(extract('year', model_field) == selected_year)
        if selected_month:
            query = query.filter(extract('month', model_field) == selected_month)
        return query

    students_count = apply_date_filter(Student.query, Student.registration_date).count()
    teachers_count = apply_date_filter(Teacher.query, Teacher.created_at).count()
    note_count = apply_date_filter(Note.query, Note.date).count()
    absences_count = apply_date_filter(Absence.query, Absence.date).count()
    attendance_count = apply_date_filter(Attendance.query, Attendance.date).count()
    messages_count = apply_date_filter(Message.query, Message.timestamp).count()
    forumpost_count = apply_date_filter(ForumPost.query, ForumPost.timestamp).count()
    report_count = apply_date_filter(Report.query, Report.generated_at).count()
    schoolinfo_count = apply_date_filter(SchoolInfo.query, SchoolInfo.timestamp).count()
    pool_count = apply_date_filter(Poll.query, Poll.end_date).count()

    data = {
        'students': students_count,
        'teachers': teachers_count,
        'note': note_count,
        'absence': absences_count,
        'attendance': attendance_count,
        'messages': messages_count,
        'forumpost': forumpost_count,
        'report': report_count,
        'schoolinfo': schoolinfo_count,
        'poll': pool_count
    }
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  # Pour avoir les noms des mois en français

    # Liste manuelle des mois en français
    months = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }

    return render_template(
        'dashboard.html',
        data=data,
        students_count=students_count,
        teachers_count=teachers_count,
        note_count=note_count,
        absences_count=absences_count,
        attendance_count=attendance_count,
        messages_count=messages_count,
        forumpost_count=forumpost_count,
        report_count=report_count,
        schoolinfo_count=schoolinfo_count,
        pool_count=pool_count,
        current_year=datetime.now().year,
        selected_month=selected_month,
        selected_year=selected_year,
        years=years,
        months=months
    )

"""@tableau.route('/')
def dashboard_generale():
    # Récupération des filtres temporels
    selected_month = request.args.get('month', type=int)
    selected_year = request.args.get('year', type=int)

    if not selected_year:
        selected_year = datetime.now().year

    # Liste des années disponibles pour les filtres
    years = list(range(2022, datetime.now().year + 1))

    # Requêtes des statistiques
    students_count = Student.query.count()
    teachers_count = Teacher.query.count()
    note_count = Note.query.count()
    absences_count = Absence.query.count()
    attendance_count = Attendance.query.count()
    messages_count = Message.query.count()
    forumpost_count = ForumPost.query.count()
    report_count = Report.query.count()
    schoolinfo_count = SchoolInfo.query.count()
    pool_count = Poll.query.count()

    # Préparation des données (optionnel si vous l’utilisez dans le template)
    data = {
        'students': students_count,
        'teachers': teachers_count,
        'note': note_count,
        'absence': absences_count,
        'attendance': attendance_count,
        'messages': messages_count,
        'forumpost': forumpost_count,
        'report': report_count,
        'schoolinfo': schoolinfo_count,
        'poll': pool_count
    }

    # Rendu du template avec toutes les variables nécessaires
    return render_template(
        'dashboard.html',
        data=data,
        students_count=students_count,
        teachers_count=teachers_count,
        note_count=note_count,
        absences_count=absences_count,
        attendance_count=attendance_count,
        messages_count=messages_count,
        forumpost_count=forumpost_count,
        report_count=report_count,
        schoolinfo_count=schoolinfo_count,
        pool_count=pool_count,
        current_year=datetime.now().year,
        selected_month=selected_month,
        selected_year=selected_year,
        years=years
    )"""