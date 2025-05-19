from flask import Blueprint, render_template, flash, request, redirect, url_for
from app.models import db, Absence, Student
from app.forms import AbsenceForm
from flask_login import login_required
from app.decorators import roles_required

absenc = Blueprint('abscen', __name__)


@absenc.route('/absences/<int:student_id>', methods=['GET', 'POST'])
@login_required
def manage_absences(student_id):
    student = Student.query.get_or_404(student_id)
    form = AbsenceForm()

    # Filtrage et tri
    filter_reason = request.args.get('filter_reason')
    sort_by_date = request.args.get('sort_by_date')

    # Création de la requête pour récupérer les absences de l'étudiant
    query = Absence.query.filter(Absence.student_id == student.id)

    if filter_reason:
        query = query.filter(Absence.reason.ilike(f'%{filter_reason}%'))  # Filtrage insensible à la casse

    if sort_by_date == 'asc':
        query = query.order_by(Absence.date.asc())
    elif sort_by_date == 'desc':
        query = query.order_by(Absence.date.desc())

    absences = query.all()

    if form.validate_on_submit():
        try:
            # Création d'une nouvelle absence
            new_absence = Absence(
                date=form.date.data,
                reason=form.reason.data,
                student=student
            )
            db.session.add(new_absence)
            db.session.commit()
            flash('Absence ajoutée avec succès.', 'success')
            return redirect(url_for('manage_absences', student_id=student.id))
        except Exception as e:
            db.session.rollback()  # En cas d'erreur, rollback
            flash(f'Une erreur est survenue lors de l\'ajout de l\'absence : {e}', 'danger')

    return render_template('absences.html', student=student, form=form, absences=absences)



@absenc.route('/absences/edit/<int:absence_id>', methods=['GET', 'POST'])
@roles_required('admin', 'superadmin')
def edit_absence(absence_id):
    absence = Absence.query.get_or_404(absence_id)
    form = AbsenceForm()

    if form.validate_on_submit():
        try:
            absence.date = form.date.data
            absence.reason = form.reason.data
            db.session.commit()
            flash('Absence modifiée avec succès.', 'success')
            return redirect(url_for('manage_absences', student_id=absence.student.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Une erreur est survenue lors de la modification de l\'absence.{e}', 'danger')

    form.date.data = absence.date
    form.reason.data = absence.reason

    return render_template('edit_absence.html', form=form)


@absenc.route('/absences/delete/<int:absence_id>', methods=['POST'])
@roles_required('admin', 'superadmin')
def delete_absence(absence_id):
    absence = Absence.query.get_or_404(absence_id)
    student_id = absence.student.id
    try:
        db.session.delete(absence)
        db.session.commit()
        flash('Absence supprimée avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Une erreur est survenue lors de la suppression de l\'absence.{e}', 'danger')

    return redirect(url_for('manage_absences', student_id=student_id))