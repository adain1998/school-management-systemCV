from flask import render_template, redirect, url_for, request, Blueprint, flash
from app.models import db, Exam


examen = Blueprint('examen', __name__)


# ROUTE pour les examens
@examen.route('/exams /add', methods=['GET', 'POST'])
def add_exam():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        subject = request.form.get('subject')
        score = request.form.get('score')
        if not student_id or not subject or score is None:
            flash('Tous les champs sont requis.', 'error')
            return render_template('Ajouter_exam.html')
        try:
            new_schedule = Exam(student_id=int(student_id)),
            subject = subject.strip(),
            score = float(score)
            db.session.add(new_schedule)
            db.session.commit()
            flash('Examen ajouté avec succès', 'success')
            return redirect(url_for('view_exams'))
        except InterruptedError:
            db.session.rollback()
            flash('Erreur: ce score existe déjà.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur de lors de l'ajout de l'examen {e} ", 'error')
        return render_template('Ajouter_exam.html',
                               subject=subject, score=score, new_schedule=student_id)


# route vue des examens

@examen.route('/schedules')
def view_exam():
    try:
        exam = Exam.query.all()
    except Exception as e:
        flash(f'Erreur lors de la récupération des examens  : {str(e)}', 'error')
        exam = []
    return render_template('voir_exam.html', exam=exam)


# route filtrage des examens
@examen.route('/exams/filter_and_search', methods=['GET', 'POST'])  # route pour filtrer les matières
def filter_and_search_exams():
    exams = []
    if request.method == 'POST':
        subject_filter = request.form.get('subject')
        score_filter = request.form.get('score')
        filters = []
        if subject_filter:
            filters.append(Exam.subject.like(f'%{subject_filter.strip()}%'))
        if score_filter:
            try:
                score_value = float(score_filter)
                filters.append(Exam.score == score_value)
            except ValueError:
                flash('Veuillez entrer une note valide.', 'error')
        if filters:
            exams = Exam.query.filter(*filters).all()
        else:
            flash('Veuillez entrer au moins un critère de filtrage', 'error')
    else:
        exams = Exam.query.all()  # Charger tous les examens si pas de filtrage
    return render_template('voir_exam.html', exams=exams)



# SUPPRIMER LES EXAMENS
@examen.route('/exams/delete/<int:exam_id>', methods=['POST'])
def delete_exam(exam_id):
    try:
        exam = Exam.query.get(exam_id)
        if exam:
            db.session.delete(exam)
            db.session.commit()
            flash('Examen supprimé avec succès', 'success')
        else:
            flash('Examen non trouvé.', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la suppression de l'examen: {str(e)}", 'error')
    return redirect(url_for('examen.filter_and_search_exams'))
