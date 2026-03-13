from flask import (Blueprint, render_template, request, redirect, flash, Response,
                   url_for, abort, current_app)
from flask_paginate import Pagination, get_page_parameter
from app.forms import NoteForm, AssignmentForm, NoteFilterForm
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, Note, Student, Matiere, Assignment, Classe
from flask_login import login_required, current_user
from sqlalchemy.orm import Query
import statistics
import csv
from datetime import datetime
from werkzeug.exceptions import HTTPException
from sqlalchemy import func
import logging
from collections import Counter
import io
import json
from app.services.statistiques_service import (
    calculer_moyennes_par_matiere,
    calculer_moyennes_generales,
    calculer_moyenne_generale
)


blueprint_resultat = Blueprint('resultat', __name__)
logger = logging.getLogger(__name__)


@blueprint_resultat.route('/note', methods=['GET', 'POST'])
@login_required
def grade():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(
            student_id=form.student_id.data,
            assignment_id=form.assignment_id.data,
            note=form.note.data
        )
        db.session.add(note)
        db.session.commit()
        flash('Note ajoutée avec succès.', 'success')
        return redirect(url_for('resultat.view_notes'))
    from app.models import Student, Matiere

    form.student_id.choices = [(s.id, s.full_name) for s in Student.query.all()]
    form.matiere_id.choices = [(m.id, m.nom) for m in Matiere.query.all()]

    notes_eleves = Note.query.all()
    return render_template('note_form.html', form=form, notes_eleves=notes_eleves)


# Afficher toutes les notes
@blueprint_resultat.route('/notes', methods=['GET'])
@login_required
def view_notes():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10

    student_id = request.args.get('student_id', type=int)
    matiere_id = request.args.get('matiere_id', type=int)

    query = Note.query

    if student_id:
        query = query.filter_by(student_id=student_id)
    if matiere_id:
        query = query.filter_by(matiere_id=matiere_id)

    total = query.count()
    notes_paginated = query.order_by(Note.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    students = Student.query.all()
    matieres = Matiere.query.all()

    pagination = Pagination(page=page, total=total, record_name='notes', css_framework='bootstrap5')

    return render_template(
        'note_list.html',
        notes_ensemble=notes_paginated.items,
        students=students,
        matieres=matieres,
        pagination=pagination
    )


# Ajouter une note manuellement (sans formulaire WTForms)
@blueprint_resultat.route('/add_note', methods=['POST'])
@login_required
def add_note():
    student_name = request.form.get('student_name')
    subject = request.form.get('subject')
    score = request.form.get('score')

    if not student_name or not subject or not score:
        flash("Tous les champs sont requis.", 'danger')
        return redirect(url_for('resultat.view_notes'))

    try:
        score = float(score)
    except ValueError:
        flash("Le score doit être un nombre.", 'danger')
        return redirect(url_for('resultat.view_notes'))

    new_note = Note(student_name=student_name, subject=subject, score=score)
    db.session.add(new_note)
    db.session.commit()
    flash('Note ajoutée avec succès.', 'success')
    return redirect(url_for('resultat.view_notes'))


# Éditer une note
@blueprint_resultat.route('/edit_note/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_note(id_edit):
    note = Note.query.get_or_404(id_edit)

    if request.method == 'POST':
        student_name = request.form.get('student_name')
        subject = request.form.get('subject')
        score = request.form.get('score')

        if not student_name or not subject or not score:
            flash("Tous les champs sont requis.", 'danger')
            return redirect(url_for('resultat.edit_note', id_edit=id_edit))

        try:
            note.score = float(score)
        except ValueError:
            flash("Le score doit être un nombre.", 'danger')
            return redirect(url_for('resultat.edit_note', id_edit=id_edit))

        note.student_name = student_name
        note.subject = subject
        db.session.commit()
        flash('Note mise à jour avec succès.', 'success')
        return redirect(url_for('resultat.view_notes'))

    return render_template('note_edit.html', note=note)



@blueprint_resultat.route('/delete_note/<int:id>')
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



@blueprint_resultat.route('/notes/filter', methods=['GET', 'POST'])
@login_required
def filter_notes():
    form = NoteFilterForm()
    notes_filter = []
    filter_value = ""
    filter_by = None
    order = 'asc'
    pagination = None

    if request.method == 'POST':
        filter_by = request.form.get('filter_by')
        filter_value = request.form.get('filter_value', '').strip()
        order = request.form.get('order', 'asc').lower()

        allowed_filters = {
            "valeur": float,           # suppose numérique
            "Student_id": int,
            "note": float,
            "date": 'date',
            "commentaire": str,
            "subject": str,
        }

        if filter_by not in allowed_filters:
            flash('Colonne de filtre invalide, merci de vérifier.', 'danger')
            return redirect(url_for('resultat.filter_notes'))

        if order not in ['asc', 'desc']:
            order = 'asc'

        # Validation avancée du filter_value selon type attendu
        filter_type = allowed_filters[filter_by]
        filter_expr = None

        try:
            query = Note.query

            if filter_type == float:
                filter_expr = getattr(Note, filter_by) == float(filter_value)
            elif filter_type == int:
                filter_expr = getattr(Note, filter_by) == int(filter_value)
            elif filter_type == 'date':
                # Gestion date flexible : supporte YYYY-MM-DD
                filter_date = datetime.strptime(filter_value, '%Y-%m-%d')
                filter_expr = getattr(Note, filter_by).date() == filter_date.date()
            else:
                # Recherche insensible à la casse, recherche partielle
                filter_expr = getattr(Note, filter_by).ilike(f"%{filter_value}%")

            # Appliquer le filtre
            query = query.filter(filter_expr)

            # Appliquer l’ordre
            order_column = getattr(Note, filter_by)
            if order == 'desc':
                order_column = order_column.desc()
            else:
                order_column = order_column.asc()

            query = query.order_by(order_column)

            # Pagination simple (optionnel)
            page = request.args.get('page', 1, type=int)
            per_page = 15
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            notes_filter = pagination.items

        except ValueError:
            flash(f"Valeur invalide pour le filtre '{filter_by}'.", 'danger')
        except Exception as e:
            current_app.logger.error(f"Erreur filtrage notes : {e}")
            flash(f"Erreur lors du filtrage des notes.", 'danger')

    return render_template(
        'grades.jinja.html',
        form=form,
        notes_filter=notes_filter,
        filter_value=filter_value,
        filter_by=filter_by,
        order=order,
        pagination=pagination if 'pagination' in locals() else None,
    )



@blueprint_resultat.route('/Notes/<int:student_id>', methods=['GET', 'POST'])
@login_required
def manage_grades(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        matiere_id = request.form.get('matiere_id', '').strip()
        score_input = request.form.get('score', '').strip()

        # --- Validation des champs ---
        if not matiere_id or not score_input:
            flash("Tous les champs sont obligatoires.", "danger")
            return redirect(url_for('resultat.manage_grades', student_id=student.id))

        try:
            score = float(score_input)
            if not (0 <= score <= 100):
                flash("Le score doit être compris entre 0 et 100.", "danger")
                return redirect(url_for('resultat.manage_grades', student_id=student.id))
        except ValueError:
            flash("Le score doit être un nombre valide.", "danger")
            return redirect(url_for('resultat.manage_grades', student_id=student.id))

        # --- Vérifie si la matière existe ---
        matiere = Matiere.query.get(matiere_id)
        if not matiere:
            flash("La matière sélectionnée est introuvable.", "danger")
            return redirect(url_for('resultat.manage_grades', student_id=student.id))

        # --- Empêche les doublons de note ---
        existing_note = Note.query.filter_by(student_id=student.id, matiere_id=matiere.id).first()
        if existing_note:
            flash("Une note pour cette matière existe déjà. Veuillez la modifier si besoin.", "warning")
            return redirect(url_for('resultat.manage_grades', student_id=student.id))

        # --- Enregistrement sécurisé ---
        try:
            note = Note(
                student_id=student.id,
                matiere_id=matiere.id,
                score=score
            )
            db.session.add(note)
            db.session.commit()
            flash("Note ajoutée avec succès.", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout de la note : {str(e)}", "danger")

        return redirect(url_for('resultat.manage_grades', student_id=student.id))

    # --- Récupération des notes et matières ---
    recuperation = Note.query.filter_by(student_id=student.id).join(Matiere).order_by(Matiere.nom).all()

    # Récupère les matières liées à la classe de l’élève
    matieres = Matiere.query.filter_by(classe_id=student.classe_id).order_by(Matiere.nom).all()

    return render_template(
        'gestion_notes.html',
        student=student,
        notes_ecole=recuperation,
        matieres=matieres
    )



@blueprint_resultat.route('/')
@login_required
def index_note():
    try:
        # Récupération des moyennes par étudiant
        student_notes = db.session.query(
            Student.id,
            Student.first_name,
            Student.last_name,
            func.avg(Note.score).label('average_score'),
            func.count(Note.id).label('note_count')
        ).join(Note, Student.id == Note.student_id)\
         .group_by(Student.id)\
         .order_by(Student.last_name.asc())\
         .all()

        # Si aucun résultat
        if not student_notes:
            flash("Aucune note trouvée dans la base de données.", "warning")

        return render_template('index_note.html', student_notes=student_notes)

    except Exception as e:
        db.session.rollback()
        flash(f"Une erreur est survenue lors du chargement des résultats.:{e}", "danger")
        return render_template('index_note.html', student_notes=[])



def validate_grades(grades):
    for point in grades:
        if point < 0 or point > 20:
            return False
    return True



@blueprint_resultat.route('/')
def index_note_stats():
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



@blueprint_resultat.route('/calculate', methods=['POST'])
@login_required
def calculate():
    try:
        # 1. Récupération et nettoyage des données
        names_raw = request.form.getlist('names')
        grades_raw = request.form.getlist('grades')

        names = [n.strip() for n in names_raw if n.strip()]
        grades = []

        # 2. Vérification des erreurs
        errors = []

        # Nom vide ou en double
        name_counts = Counter(names)
        duplicates = [n for n, count in name_counts.items() if count > 1]
        if len(names) != len(names_raw):
            errors.append("Certains noms sont vides.")
        if duplicates:
            errors.append(f"Noms en double détectés : {', '.join(duplicates)}")

        # Notes invalides
        for i, g in enumerate(grades_raw):
            try:
                note_list = list(map(float, g.split(',')))
                if not validate_grades(note_list):
                    raise ValueError
                grades.append(note_list)
            except ValueError:
                errors.append(f"Notes invalides pour {names_raw[i] if i < len(names_raw) else 'Étudiant inconnu'} (notes doivent être numériques entre 0 et 20).")

        if errors:
            for err in errors:
                flash(err, "danger")
            return redirect(url_for('resultat.index_note'))

        # 3. Calcul des moyennes
        individual_averages = [round(statistics.mean(g), 2) for g in grades]
        all_notes = [note for sublist in grades for note in sublist]
        general_average = round(statistics.mean(all_notes), 2) if all_notes else 0.0

        # 4. Préparation des données pour exportation et visualisation
        results_data = [
            {"name": name, "grades": gr, "average": avg}
            for name, gr, avg in zip(names, grades, individual_averages)
        ]

        return render_template(
            '/results_notes.html',
            results=results_data,
            general_average=general_average
        )

    except Exception as e:
        logger.exception("Erreur lors du calcul des moyennes.")
        flash(f"Erreur inattendue. Veuillez réessayer ou contacter l'administrateur.:{e}", "danger")
        return redirect(url_for('resultat.index_note'))



# Importation en PDF et CSV
@blueprint_resultat.route('/export_csv', methods=['POST'])
@login_required
def export_csv():
    try:
        results_json = request.form.get('results')
        result = json.loads(results_json)

        # Création d'un CSV en mémoire
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['Nom', 'Notes', 'Moyenne'])  # Entêtes
        for item in result:
            cw.writerow([
                item.get('name', 'Inconnu'),
                ', '.join(map(str, item.get('grades', []))),
                item.get('average', 0)
            ])

        output = si.getvalue()
        return Response(
            output,
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment;filename=resultats.csv"}
        )

    except Exception as e:
        logger.exception("Erreur lors de l’export CSV")
        flash(f"Échec de l’export CSV.:{e}", "danger")
        return redirect(url_for('resultat.index_note'))



# Affichage de notes qui seront visibles par les parents
@blueprint_resultat.route('/')
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
        return redirect(url_for('resultat.notes'))

    children_ids = current_user.children_ids.split(',')
    points = Note.query.filter(Note.student_id.in_(children_ids)).all()
    return render_template('Note.html', points=points)


# nouvelles routes
@blueprint_resultat.route('/report')
def report():
    if not report.Note:
        return render_template("performance_report.html", error_message="Aucune note disponible")
    return render_template('performance_report.html', report=report)



@blueprint_resultat.route('/assignments', methods=['GET', 'POST'])
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



@blueprint_resultat.route('/assignments/edit/<int:assignment_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('resultat.performance'))
    elif request.method == 'GET':
        form.title.data = assignment.title
        form.description.data = assignment.description
        form.due_date.data = assignment.due_date
    return render_template('edit_assignment.html', form=form, assignment=assignment)



@blueprint_resultat.route('/assignments/delete/<int:assignment_id>', methods=['POST'])
@login_required
def delete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.teacher_id != current_user.id:
        abort(403)
    db.session.delete(assignment)
    db.session.commit()
    flash('Assignment deleted successfully!', 'success')
    return redirect(url_for('resultat.assignments'))



@blueprint_resultat.errorhandler(HTTPException)
def handle_exception(e):
    if request.path.startswith('/assignment'):
        template = 'error_assignment.html'
    else:
        template = 'error_performance.html'
    return render_template(template, error=e), e.code



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



@blueprint_resultat.route('/moyennes/<int:classe_id>')
def afficher_moyennes(classe_id):
    resultats = calcul_moyennes_par_classe(classe_id)
    if resultats:
        return render_template("moyennes_classes.html", resultats=resultats)
    else:
        return render_template("moyennes_classes.html", erreurs=["Aucune donnée disponible."])
