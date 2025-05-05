from flask import render_template, Blueprint
from flask_login import login_required, current_user
from app.models import Note, Exam, Absence, Attendance, Assignment

application = Blueprint("application", __name__)


@application.route('/performance')
@login_required
def performance():
    students_per = current_user.students
    performance_data = []
    for student in students_per:
        student = current_user.students[student]
        nts = Note.query.filter_by(student_id=student.id).all()
        exams = Exam.query.filter_by(student_id=student.id).all()
        absenc = Absence.query.filter_by(student_id=student.id).all()
        pst = Attendance.query.filter_by(student_id=student.id).all()
        assign = Assignment.query.filter_by(student_id=student.id).all()
        performance_data.append({'student': student, 'nts': nts,
                                 'exams': exams,
                                 'absenc': absenc,
                                 'pst': pst,
                                 'assign': assign})
    return render_template('performance.html', performance_data=performance_data)
