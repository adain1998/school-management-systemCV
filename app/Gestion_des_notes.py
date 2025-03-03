from flask import Blueprint, render_template, request, redirect, flash, url_for, abort, jsonify
from forms import NoteForm, AssignmentForm, NoteFilterForm
from models import db, Note, Student, Matiere, Assignment, Attendance
from flask_login import login_required, current_user
from sqlalchemy.orm import Query
import statistics
import pandas as pd
import numpy as np
from datetime import datetime
from werkzeug.exceptions import HTTPException

resultat = Blueprint('resultat', __name__)


@resultat.route('/note', methods=['GET', 'POST'])
@login_required
def grade():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(student_id=form.student_id.data, assignment_id=form.Assignment_id.data, Note=form.Note.data)
        db.session.add(note)
        db.session.commit()
        flash('Grade submitted successfully!', 'success')
        return redirect(url_for('main.notes'))
    point = Note.query.all()
    return render_template('Note.html', form=form, point=point)


# Routes pour Note
@resultat.route('/notes')
def view_notes():
    nots = Note.query.all()
    return render_template('note.html', nots=nots)


@resultat.route('/add_note', methods=['POST'])
def add_note():
    student_name = request.form['student_name']
    subject = request.form['subject']
    score = request.form['score']
    new_note = Note(student_name=student_name, subject=subject, score=score)
    db.session.add(new_note)
    db.session.commit()
    flash('Note added successfully!', 'success')
    return redirect(url_for('view_notes'))


@resultat.route('/edit_note/<int:id>', methods=['GET', 'POST'])
def edit_note():
    note = Note.query.get_or_404(id)
    if not note:
        return 'note introuvable', 404
    if request.method == 'POST':
        note.student_name = request.form['student_name']
        note.subject = request.form['subject']
        note.score = request.form['score']
        db.session.commit()
        flash('Note updated successfully!', 'success')
        return redirect(url_for('view_notes'))
    if request.method == 'GET':
        return render_template('Note.html', note=note)
    else:
        new_note = request.form.get('note')
        new_date = request.form.get('date')
        note.note = new_note
        note.date = new_date
        db.session.commit()
        return redirect(url_for('liste_notes'))


@resultat.route('/delete_note/<int:id>')
def delete_note():
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('view_notes'))


"""def filter_and_sort(model, filter_by: str, filter_value: str, order: str) -> Query:
    query = model.query
    if filter_by in ['valeur', 'Student_id', 'note', 'date']:
        query = query.filter(getattr(model, filter_by) == filter_value)
        if order == 'asc':
            query = query.order_by(getattr(model, filter_by).asc())
        elif order == 'desc':
            query = query.order_by(getattr(model, filter_by).desc())
        return query.all()"""



def filter_and_sort(model, filter_by: str, filter_value: str, order: str) -> Query:
    query = model.query

    # Vérifier si le champ à filtrer est valide
    if filter_by not in ['valeur', 'Student_id', 'note', 'date']:
        raise ValueError("Champ de filtre invalide")

    # Conversion de filter_value en fonction du type de la colonne
    if filter_by == 'date':
        filter_value = datetime.strptime(filter_value,
                                         '%Y-%m-%d')  # Exemple : convertir une chaîne 'YYYY-MM-DD' en datetime
    elif filter_by in ['note', 'valeur']:  # Supposons que ces champs sont numériques
        filter_value = float(filter_value)
    elif filter_by == 'Student_id':  # Supposons que c'est un identifiant (int)
        filter_value = int(filter_value)

    # Appliquer le filtre
    query = query.filter(getattr(model, filter_by) == filter_value)

    # Appliquer l'ordre
    if order == 'asc':
        query = query.order_by(getattr(model, filter_by).asc())
    elif order == 'desc':
        query = query.order_by(getattr(model, filter_by).desc())
    else:
        raise ValueError("L'option 'order' doit être 'asc' ou 'desc'")

    return query.all()



@resultat.route('/notes/filter', methods=['GET', 'POST'])
@login_required
def filter_notes():
    form = NoteFilterForm()
    notes_filter = []
    filter_value = ""

    if request.method == 'POST':
        filter_by = request.form.get('filter_by')
        filter_value = request.form.get('filter_value', '').strip()
        allowed_filters = ["valeur", "Student_id", "note", "date", "commentaire", "subject"]

        if filter_by not in allowed_filters:
            flash('Colonne de filtre invalide, merci de vérifier.', 'danger')
            return redirect(url_for('resultat.filter_notes'))

        order = request.form.get('order', 'asc').lower()
        if order not in ['asc', 'desc']:
            order = 'asc'  # Valeur par défaut

        try:
            notes_filter = filter_and_sort(Note.query, filter_by, filter_value, order)
        except Exception as e:
            flash(f"Erreur lors du filtrage des notes : {str(e)}", 'danger')

    return render_template('grades.html', form=form, notes_filter=notes_filter, filter_value=filter_value)



@resultat.route('/Notes/<int:student_id>', methods=['GET', 'POST'])
@login_required
def manage_grades(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        subject = request.form.get('subject')
        score = request.form.get('score')

        # Validation des données
        if not subject or not score:
            flash("Tous les champs sont requis", "danger")
            return redirect(url_for('main.manage_grades', student_id=student.id))

        try:
            score = float(score)
            if score < 0 or score > 100:
                flash("Le score doit être compris entre 0 et 100", "danger")
                return redirect(url_for('main.manage_grades', student_id=student.id))
        except ValueError:
            flash("Score invalide", "danger")
            return redirect(url_for('main.manage_grades', student_id=student.id))

        try:
            new_grades = Note(subject=subject, score=score, student_id=student.id)
            db.session.add(new_grades)
            db.session.commit()
            flash("Note ajoutée avec succès", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout de la note: {str(e)}", "danger")
        return redirect(url_for('main.manage_grades', student_id=student.id))

    notes_ecole = Note.query.filter_by(student_id=student.id).all()
    return render_template('gestion_notes.html', student=student, notes_ecole=notes_ecole)


# calcul de la moyenne de notes des élèves
@resultat.route('/')
@login_required
def index_note():
    return render_template('index_note.html')


@resultat.route('/calculate', methods=['POST'])
@login_required
def calculate():
    try:
        names = request.form.getlist('names')
        grades = request.form.getlist('grades')
        grades = [list(map(float, g.split(','))) for g in grades]

        if not all(len(g) > 0 for g in grades):
            flash('Toutes les notes doivent être fournies pour chaque étudiant.', 'error')
            return redirect(url_for('main.index'))

        if not all(validate_grades(g) for g in grades):
            flash('Les notes doivent être comprises entre 0 et 20.', 'error')
            return redirect(url_for('main.index'))

        individual_averages = [statistics.mean(g) for g in grades]
        general_average = statistics.mean([point for sublist in grades for point in sublist])

        return render_template('results_notes.html', names=names, individual_averages=individual_averages,
                               general_average=general_average)
    except Exception as e:
        flash(f'Erreur de calcul: {e}', 'error')
        return redirect(url_for('main.index'))


def validate_grades(grades):
    for point in grades:
        if point < 0 or point > 20:
            return False
    return True


@resultat.route('/')
def index_note():
    try:
        notes_with_matieres = db.session.query(Note, Matiere).join(Matiere).all()
        moyennes_par_matiere = {}
        for note, matiere in notes_with_matieres:
            if matiere.nom not in moyennes_par_matiere:
                moyennes_par_matiere[matiere.nom] = []
            moyennes_par_matiere[matiere.nom].append(note.valeur)
        moyennes_generales = {matiere: sum(notes) / len(notes) if notes else 0
                              for matiere, notes in moyennes_par_matiere.items()}
        moyenne_generale = sum(moyennes_generales.values()) / len(moyennes_generales) if moyennes_generales else 0
    except Exception as e:
        flash(f"Moyenne ajoutée avec succes.{e}", "succes")
        return render_template('matieres.html', erreurs=[str(e)])
    return render_template('matieres.html', matieres=moyennes_par_matiere,
                           moyennes_generales=moyennes_generales, moyenne_generale=moyenne_generale)


@resultat.route('/', methods=['GET', 'POST'])
def results(plt=None):
    page = request.args.get('page', 1, type=int)
    per_page = 15
    sort_by = request.args.get('sort_by', 'nom')
    order = request.args.get('order', 'asc')
    filter_value = request.args.get('filter')
    try:
        query = Matiere.query.join(Note, Matiere.id == Note.matiere_id).add_columns(db.func.avg(Note.valeur).label
                                                                                    ('moyenne')).group_by(Matiere.id)
        if filter_value == 'sup':
            if filter_value == 'inf':
                query = query.having(db.func.avg(Note.valeur) <= 5)
            elif filter_value == 'sup':
                query = query.having(db.func.avg(Note.valeur) >= 5)
        if sort_by:
            if sort_by == 'moyenne':
                column = db.func.avg(Note.valeur)
            else:
                column = getattr(Matiere, sort_by)
                query = query.order_by(getattr(column, order))
        matieres = query.paginate(page=page, per_page=per_page)
        df = pd.read_csv("bureau_student.csv")
        print(df.head(5))
        df['moyenne'] = df.groupby('student_id')['Note'].transform('mean')
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        plt.plot(x, y, color='red', linewidth=2, linestyle="--")
        plt.show()
        plt.scatter(x, y, color='green', marker='o', s=50)
        plt.show()
        plt.hist(df['moyenne'], bins=10)
        plt.xlabel('moyenne')
        plt.savefig('moyenne_student.png')
    except Exception as e:
        return render_template('error.html', error=str(e))
    return render_template('performance_report.html', matieres=matieres, page=page, per_page=per_page,
                           sort_by=sort_by, order=order, filter_value=filter_value)


# Affichage de notes qui seront visibles par les parents
@resultat.route('/')
@login_required
def notes():
    if request.method == 'POST':
        student_id = request.form['student_id']
        assignment_id = request.form['assignment_id']
        score = request.form['score']
        if not score.isdigit() or int(score) < 0 or int(score) > 100:
            flash('La note doit être un nombre entre 0 et 100', 'danger')
        else:
            note = Note(student_id=student_id, assignment_id=assignment_id, score=int(score))
            db.session.add(note)
            db.session.commit()
            flash('Note ajoutée avec succès', 'success')
        return redirect(url_for('notes'))

    children_ids = current_user.children_ids.split(',')
    points = Note.query.filter(Note.student_id.in_(children_ids)).all()
    return render_template('Note.html', points=points)


# nouvelles routes
@resultat.route('/report')
def report():
    if not report.Note:
        return render_template("performance_report.html", error_message="Aucune note disponible")
    return render_template('performance_report.html', report=report)


@resultat.route('/assignments', methods=['GET', 'POST'])
@login_required
def assignments():
    form = AssignmentForm()
    if form.validate_on_submit():
        assignment = Assignment(teacher_id=current_user.id, title=form.title.data, description=form.description.data,
                                due_date=form.due_date.data)
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('assignments'))
    assignment_ecole = Assignment.query.order_by(Assignment.due_date.asc()).all()
    return render_template('Devoirs.html', form=form, assignment_ecole=assignment_ecole)


@resultat.route('/assignments/edit/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def edit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.teacher_id != current_user.id:
        abort(403)
    form = AssignmentForm()
    if form.validate_on_submit():
        assignment.title = form.title.data
        assignment.description = form.description.data
        assignment.due_date = form.due_date.data
        db.session.commit()
        flash('Assignment updated successfully!', 'success')
        return redirect(url_for('assignments'))
    elif request.method == 'GET':
        form.title.data = assignment.title
        form.description.data = assignment.description
        form.due_date.data = assignment.due_date
    return render_template('edit_assignment.html', form=form, assignment=assignment)


@resultat.route('/assignments/delete/<int:assignment_id>', methods=['POST'])
@login_required
def delete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.teacher_id != current_user.id:
        abort(403)
    db.session.delete(assignment)
    db.session.commit()
    flash('Assignment deleted successfully!', 'success')
    return redirect(url_for('assignments'))


@resultat.errorhandler(HTTPException)
def handle_exception(e):
    return render_template('error_assignment.html', error=e), e.code


@resultat.route('/performance', methods=['GET'])
@login_required
def performance():
    children_ids = current_user.children_ids.split(',')
    notes_student = Note.query.filter(Note.student_id.in_(children_ids)).all()
    students = Student.query.filter(Student.id.in_(children_ids)).all()
    data = {
        "students": [
            {
                "student_id": student.id,
                "name": student.name,
                "avg_grade":
                    sum(note.score for note in notes_student if note.student_id == student.id) / len(notes_student),
                "attendance_rate": student.attendance_rate,
                "completed_assignments": student.completed_assignments,
                "total_assignments": student.total_assignments
            }
            for student in students
        ]
    }
    return jsonify(data)


@resultat.route('/student/<int:student_id>', methods=['GET'])
@login_required
def student_performance(student_id):
    student = Student.query.get_or_404(student_id)
    notes_performance = Note.query.filter_by(student_id=student_id).all()
    attendances = Attendance.query.filter_by(student_id=student_id).all()
    assignments_performance = Assignment.query.filter_by(student_id=student_id).all()
    return render_template('student_performance.html', student=student,
                           notes_performance=notes_performance, attendances=attendances,
                           assignments_performance=assignments_performance)


@resultat.errorhandler(HTTPException)
def handle_exception(e):
    return render_template('error_performance.html', error=e), e.code


import csv


def get_data_from_csv(filename):
    report = {}  # Dictionnaire pour stocker les données

    try:
        # Ouvrir le fichier CSV en mode lecture
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                subject = row['subject']

                # Si la matière n'est pas dans le rapport, l'ajouter
                if subject not in report:
                    report[subject] = []

                # Ajouter les données de l'étudiant pour cette matière
                report[subject].append({
                    'nom': row['nom'],
                    'prenom': row['prenom'],
                    'note': row['note']
                })

    except FileNotFoundError:
        print("Fichier introuvable. Veuillez vérifier le nom du fichier et réessayer.")

    return report


# Exemple d'utilisation
filename = 'data.csv'
data = get_data_from_csv(filename)
print(data)


# note filtrer
"""@resultat.route('/notes/filter', methods=['GET', 'POST'])
@login_required
def filter_notes():
    form = NoteForm()
    notes_filter = []
    filter_value = []
    if request.method == 'POST':
        filter_by = request.form.get('filter_by')
        filter_value = request.form.get('filter_value')
        allowed_filter = ["valeur", "Student_id", "note", "date", "commentaire", "subject"]
        if filter_by not in allowed_filter:
            return 'colonne de filtre invalide merci!', 500
        order = request.args.get('order', 'asc')
        notes_filter = filter_and_sort(Note, filter_by, filter_value, order)
    return render_template('grades.html', form=form, notes_filter=notes_filter, filter_value=filter_value)"""


