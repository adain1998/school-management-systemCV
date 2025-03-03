from flask import render_template, Blueprint, url_for, redirect, flash
from models import Student, Note, Absence, Teacher, Report, Attendance, Message, Poll, ForumPost, SchoolInfo
from flask_login import current_user, login_required
tableau = Blueprint('tableau', __name__)


@tableau.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    children_ids = current_user.children_ids.split(',')
    students = Student.query.filter(Student.id.in_(children_ids)).all()
    notes_student = Note.query.filter(Note.student_id.in_(children_ids)).all()

    for student in students:
        student.avg_grade = sum(note.score for note in notes_student if note.student_id == student.id) / len(
            notes_student)
        student.attendance_rate = student.attendance_rate
        student.completed_assignments = student.completed_assignments
        student.total_assignments = student.total_assignments

    return render_template('dashboard_performance.html', students=students)

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
def eleve_dashboard():
    if current_user.role != 'eleve':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('index'))  # Redirige vers la page d'accueil si l'utilisateur n'est pas élève
    return render_template('dashboard_eleves.html')  # Affiche le tableau de bord de l'élève


#tableau de bord administrateur

@tableau.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'administrateur':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('index'))  # Redirige vers la page d'accueil si l'utilisateur n'est pas administrateur
    return render_template('dashboard_admin.html')  # Affiche le tableau de bord de l'administrateur

# acceuil
@tableau.route('/')
def index():
    return render_template('index.html')  # Affiche la page d'accueil générique


@tableau.route('/')
def dashboard():
    students_count = Student.query.count()
    note_count = Note.query.count()
    teachers_count = Teacher.query.count()
    absences_count = Absence.query.count()
    report_count = Report.query.count()
    attendance_count = Attendance.query.count()
    messages_count = Message.query.count()
    forumpost_count = ForumPost.query.count()
    schoolinfo_count = SchoolInfo.query.count()
    pool_count = Poll.query.count()
    # Ajoute ici les autres requêtes pour les autres classes

    data = {
        'students': students_count,
        'note': note_count,
        'teachers': teachers_count,
        'absence': absences_count,
        'report_count': report_count,
        'attendance': attendance_count,
        'messages_count': messages_count,
        'forumpost_count': forumpost_count,
        'schoolinfo_count': schoolinfo_count,
        'pool_count': pool_count

        # Ajoute ici les autres données
    }
    return render_template('dashboard.html', data=data,
                           students_count=students_count,
                           note_count=note_count,
                           teachers_count=teachers_count,
                           absences_count=absences_count,
                           report_count=report_count,
                           attendance_count=attendance_count,
                           messages_count=messages_count,
                           forumpost_count=forumpost_count,
                           schoolinfo_count=schoolinfo_count,
                           pool_count=pool_count)
