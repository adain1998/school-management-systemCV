from flask import render_template, request, redirect, url_for, flash, Blueprint
from models import db, Schedule

schedul = Blueprint('schedul', __name__)


@schedul.route('/schedules')
def view_schedules():
    try:
        schedules = Schedule.query.all()
    except Exception as e:
        flash(f'Erreur lors de la récupération des horaires : {str(e)}', 'error')
        schedules = []
    return render_template('voir_schedules.html', schedules=schedules)


@schedul.route('/schedules/filter', methods=['GET', 'POST'])  # route pour filtrer les matières
def filter_schedules():
    schedules = []
    if request.method == 'POST':
        subject_filter = request.form.get('subject')
        if subject_filter:
            schedules = Schedule.query.filter(Schedule.subject.like(f'%{subject_filter.strip()}%')).all()
        else:
            flash('Veuillez entrer une matière à filtrer.', 'error')
    else:
        schedules = Schedule.query.all()
    return render_template('voir_schedules.html', schedules=schedules)


@schedul.route('/schedules/delete/<int:schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):
    try:
        schedule = Schedule.query.get(schedule_id)
        if schedule:
            db.session.delete(schedule)
            db.session.commit()
            flash('Horaire supprimé avec succès', 'success')
        else:
            flash('Horaire non trouvé.', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la suppression de l'horaire: {str(e)}", 'error')
    return redirect(url_for('view_schedules'))


# ajout de schedules ou horaire
@schedul.route('/schedules/add', methods=['GET', 'POST'])
def add_schedule():
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        subject = request.form.get('subject')
        time_slot = request.form.get('time_slot')
        if not class_id or not subject or not time_slot:
            flash('Tous les champs sont requis.', 'error')
            return render_template('Ajouter_schedules.html')
        try:
            new_schedule = Schedule(class_id=int(class_id)),
            subject = subject.strip(),
            time_slot = time_slot.strip()
            db.session.add(new_schedule)
            db.session.commit()
            flash('Horaire ajouté avec succès', 'success')
            return redirect(url_for('view_schedules'))
        except InterruptedError:
            db.session.rollback()
            flash('Erreur: cet horaire existe déjà.', 'error')
        except ValueError as ve:
            db.session.rollback()
            flash(f"Erreur de valeur: {ve}", 'error')
        except Exception as e:
            flash(message=f"Erreur lors de l'ajout de l'horaire: {e}", category="error")
        return render_template('Ajouter_schedules.html',
                               subject=subject, time_slot=time_slot, new_schedule=class_id)
    else:
        return render_template('Ajouter_schedules.html')


@schedul.route('/calendar')
def view_calendar(schedule=None):
    try:
        schedules = Schedule.query.all()
        events = [{'title': schedules.subject, 'start': schedules.time_slot.isoformat()}
                  for schedule in schedules]
    except Exception as e:
        flash(f'Erreur lors de la récupération des horaires: {str(e)}', 'error')
        events = []
    return render_template('view_calendar.html', events=events, schedule=schedule)
