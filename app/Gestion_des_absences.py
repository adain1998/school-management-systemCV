from flask import Blueprint, render_template, flash, request, redirect, url_for, current_app
from app.models import db, Absence, Student
from app.forms import AbsenceForm
from flask_login import login_required
from app.decorators import roles_required

blueprint_absenc = Blueprint('absenc', __name__)


def get_absences_query(student_id, filter_reason=None, sort_by_date=None):
    """Construit la requête des absences avec filtres optionnels."""
    query = Absence.query.filter_by(student_id=student_id)

    if filter_reason:
        query = query.filter(Absence.reason.ilike(f'%{filter_reason}%'))

    if sort_by_date == 'asc':
        query = query.order_by(Absence.date.asc())
    elif sort_by_date == 'desc':
        query = query.order_by(Absence.date.desc())

    return query


@blueprint_absenc.route('/absences/<int:student_id>', methods=['GET', 'POST'])
@login_required
def manage_absences(student_id):
    student = Student.query.get_or_404(student_id)
    form = AbsenceForm()

    # Requête filtrée
    filter_reason = request.args.get('filter_reason', type=str)
    sort_by_date = request.args.get('sort_by_date', type=str)
    absences = get_absences_query(student.id, filter_reason, sort_by_date).all()

    if form.validate_on_submit():
        try:
            new_absence = Absence(
                date=form.date.data,
                reason=form.reason.data,
                student_id=student.id
            )
            db.session.add(new_absence)
            db.session.commit()
            flash('Absence ajoutée avec succès.', 'success')
            return redirect(url_for(request.url, student_id=student.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur ajout absence : {e}")
            flash('Une erreur est survenue lors de l’ajout de l’absence.', 'danger')

    return render_template(
        'absences.jinja.html',
        student=student,
        form=form,
        absences=absences,
        filter_reason=filter_reason,
        sort_by_date=sort_by_date
    )



@blueprint_absenc.route('/absences/edit/<int:absence_id>', methods=['GET', 'POST'])
@roles_required('admin', 'superadmin')
def edit_absence(absence_id):
    absence = Absence.query.get_or_404(absence_id)
    form = AbsenceForm(obj=absence)

    if form.validate_on_submit():
        try:
            form.populate_obj(absence)
            db.session.commit()
            flash('Absence modifiée avec succès.', 'success')
            return redirect(url_for('absenc.manage_absences', student_id=absence.student_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur modification absence : {e}")
            flash('Une erreur est survenue lors de la modification de l’absence.', 'danger')

    return render_template('edit_absence.html', form=form, absence=absence)



@blueprint_absenc.route('/absences/delete/<int:absence_id>', methods=['POST'])
@roles_required('admin', 'superadmin')
def delete_absence(absence_id):
    absence = Absence.query.get_or_404(absence_id)
    student_id = absence.student_id
    try:
        db.session.delete(absence)
        db.session.commit()
        flash('Absence supprimée avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur suppression absence : {e}")
        flash('Une erreur est survenue lors de la suppression de l’absence.', 'danger')

    return redirect(url_for('absenc.manage_absences', student_id=student_id))