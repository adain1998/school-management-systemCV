from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.schemas.attendance_schema import attendance_schema, attendances_schema
from app.services.attendance_service import (
    create_attendance_record,
    fetch_attendance_by_student
)

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendances', methods=['POST'])
def create_attendance():
    try:
        # Validate and deserialize input
        data = attendance_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    result = create_attendance_record(
        student_id=data['student_id'],
        presence=data['presence'],
        date=data.get('date')  # Optional
    )

    if isinstance(result, dict) and result.get("error"):
        return jsonify(result), 400

    return attendance_schema.jsonify(result), 201


@attendance_bp.route('/attendances/student/<int:student_id>', methods=['GET'])
def get_attendances_for_student(student_id):
    attendances = fetch_attendance_by_student(student_id)

    if not attendances:
        return jsonify({"message": "No attendance records found for this student."}), 404

    return attendances_schema.jsonify(attendances), 200
