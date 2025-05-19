from flask import Blueprint, render_template, request, redirect, flash, url_for, abort, jsonify
from app.forms import NoteForm, AssignmentForm, NoteFilterForm
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, Note, Student, Matiere, Assignment, Attendance, Classe
from flask_login import login_required, current_user
from sqlalchemy.orm import Query
import statistics
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
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
        # Récupération des notes et matières
        notes_with_matieres = db.session.query(Note, Matiere).join(Matiere).all()
        moyennes_par_matiere = calculer_moyennes_par_matiere(notes_with_matieres)
        moyennes_generales = calculer_moyennes_generales(moyennes_par_matiere)
        moyenne_generale = calculer_moyenne_generale(moyennes_generales)

    except Exception as e:
        # Gestion des erreurs
        flash(f"Une erreur est survenue lors du calcul des moyennes: {e}", "danger")
        return render_template('matieres.html', erreurs=[str(e)])

    # Affichage des résultats
    return render_template('matieres.html', matieres=moyennes_par_matiere,
                           moyennes_generales=moyennes_generales, moyenne_generale=moyenne_generale)


def calculer_moyennes_par_matiere(notes_with_matieres: list) -> dict:
    """
    Calculer les moyennes par matière en regroupant les notes par matière.
    """
    moyennes_par_matiere = {}

    # Regrouper les notes par matière
    for note, matiere in notes_with_matieres:
        if matiere.nom not in moyennes_par_matiere:
            moyennes_par_matiere[matiere.nom] = []
        moyennes_par_matiere[matiere.nom].append(note.valeur)

    return moyennes_par_matiere


def calculer_moyennes_generales(moyennes_par_matiere: dict) -> dict:
    """
    Calculer la moyenne générale pour chaque matière.
    """
    moyennes_generales = {}

    for matiere, liste_notes in moyennes_par_matiere.items():
        moyennes_generales[matiere] = sum(liste_notes) / len(liste_notes) if liste_notes else 0

    return moyennes_generales


def calculer_moyenne_generale(moyennes_generales: dict) -> float:
    """
    Calculer la moyenne générale globale basée sur les moyennes des matières.
    """
    total_moyenne = sum(moyennes_generales.values())
    total_matieres = len(moyennes_generales)

    return total_moyenne / total_matieres if total_matieres else 0



@resultat.route('/', methods=['GET', 'POST'])
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



def apply_sorting(query, sort_by, order):
    """Applique le tri dynamique à la requête"""
    if sort_by == 'moyenne':
        column = db.func.avg(Note.valeur)
    else:
        column = getattr(Matiere, sort_by)

    # Tri croissant ou décroissant
    return query.order_by(column.asc() if order == 'asc' else column.desc())


def process_student_data(file_path):
    """Charge les données des étudiants depuis un fichier CSV et calcule les moyennes"""
    try:
        # Chargement du fichier CSV dans un DataFrame pandas
        df = pd.read_csv(file_path)

        # Calcul de la moyenne par étudiant
        df['moyenne'] = df.groupby('student_id')['Note'].transform('mean')

        return df  # Retourne le DataFrame avec les moyennes calculées

    except Exception as e:
        # Gestion des erreurs, affichage d'un message via flash
        flash(f"Erreur lors du traitement des données : {str(e)}", "danger")
        raise  # Relève l'exception pour la gestion ultérieure



def generate_charts(df):
    """Génère et sauvegarde les graphiques pour l'affichage"""
    try:
        # Génération des graphiques avec matplotlib
        x = np.linspace(0, 10, 100)
        y = np.sin(x)

        plt.figure(figsize=(8, 4))
        plt.plot(x, y, color='red', linewidth=2, linestyle="--")
        plt.title("Courbe Sinusoïdale")
        plt.savefig('static/images/sinus_plot.png')
        plt.close()

        plt.figure(figsize=(8, 4))
        plt.scatter(x, y, color='green', marker='o', s=50)
        plt.title("Points Dispersés")
        plt.savefig('static/images/scatter_plot.png')
        plt.close()

        plt.figure(figsize=(8, 4))
        plt.hist(df['moyenne'], bins=10, color='blue', alpha=0.7)
        plt.xlabel('Moyenne')
        plt.ylabel('Nombre d\'étudiants')
        plt.title("Distribution des Moyennes")
        plt.savefig('static/images/moyenne_student.png')
        plt.close()

    except Exception as e:
        flash(f"Erreur lors de la génération des graphiques : {str(e)}", "danger")
        raise



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
    try:
        # Récupération des identifiants des enfants liés à l'utilisateur actuel
        children_ids = current_user.children_ids.split(',')

        # Récupération des notes des étudiants en fonction des enfants de l'utilisateur
        notes_student = Note.query.filter(Note.student_id.in_(children_ids)).all()
        students = Student.query.filter(Student.id.in_(children_ids)).all()

        # Calcul des données de performance
        performance_data = {
            "students": [
                {
                    "student_id": student.id,
                    "name": student.name,
                    "avg_grade": sum(note.score for note in notes_student if note.student_id == student.id) / len([note for note in notes_student if note.student_id == student.id]),
                    "attendance_rate": student.attendance_rate,
                    "completed_assignments": student.completed_assignments,
                    "total_assignments": student.total_assignments
                }
                for student in students
            ]
        }

        return jsonify(performance_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



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



def get_data_from_csv(file_path):
        report_data = {}  # Dictionnaire pour stocker les données

        try:
            # Ouvrir le fichier CSV en mode lecture
            with open(file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    subject = row['subject']

                    # Si la matière n'est pas dans le rapport, l'ajouter
                    if subject not in report_data:
                        report_data[subject] = []

                    # Ajouter les données de l'étudiant pour cette matière
                    report_data[subject].append({
                        'nom': row['nom'],
                        'prenom': row['prenom'],
                        'note': row['note']
                    })

        except FileNotFoundError:
            print("Fichier introuvable. Veuillez vérifier le nom du fichier et réessayer.")

        except Exception as e:
            print(f"Une erreur s'est produite: {e}")

        return report_data



# Exemple d'utilisation
filename = 'data.csv'
data = get_data_from_csv(filename)
print(data)

# Affichage de la moyenne par classe

def calcul_moyennes_par_classe(classe_id):
    try:
        # Vérifier si la classe existe
        classe = Classe.query.get(classe_id)
        if not classe:
            flash("Classe non trouvée.", "danger")
            return None

        # Récupérer tous les élèves de la classe
        eleves = Student.query.filter_by(classe_id=classe_id).all()

        # Stocker les moyennes par élève et matière
        moyennes_par_classe = {}

        for eleve in eleves:
            moyennes_par_classe[eleve.nom] = {}

            # Récupérer toutes les matières de la classe
            matieres = Matiere.query.filter_by(classe_id=classe_id).all()

            for matiere in matieres:
                # Récupérer les notes de l'élève pour cette matière
                notes_classe = Note.query.filter_by(etudiant_id=eleve.id, matiere_id=matiere.id).all()
                valeurs_notes = [note.valeur for note in notes_classe]

                # Calcul de la moyenne
                moyenne = sum(valeurs_notes) / len(valeurs_notes) if valeurs_notes else 0
                moyennes_par_classe[eleve.nom][matiere.nom] = moyenne

        return {"classe": classe.nom, "moyennes": moyennes_par_classe}

    except SQLAlchemyError as e:
        flash(f"Erreur de base de données : {e}", "danger")
        return None



resultat = Blueprint('resultat', __name__)

@resultat.route('/moyennes/<int:classe_id>')
def afficher_moyennes(classe_id):
    resultats = calcul_moyennes_par_classe(classe_id)
    if resultats:
        return render_template("moyennes_classes.html", resultats=resultats)
    else:
        return render_template("moyennes_classes.html", erreurs=["Aucune donnée disponible."])