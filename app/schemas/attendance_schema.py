# app/schemas/attendance_schema.py

from marshmallow import fields, validate, EXCLUDE
from app.extensions import ma  # Assure-toi que ma = Marshmallow() est initialisé dans les extensions.py



class AttendanceSchema(ma.Schema):
    """
    Schéma de validation et de sérialisation pour les objets Attendance.
    """

    class Meta:
        unknown = EXCLUDE  # Ignore les champs inconnus au lieu de lever une erreur
        ordered = True     # Garde l'ordre des champs dans l'output JSON

    id = fields.Int(dump_only=True)
    date = fields.DateTime(required=False)
    student_id = fields.Int(required=True, validate=validate.Range(min=1))
    presence = fields.Bool(required=True)

# Instances uniques pour l'utilisation dans les routes ou services
attendance_schema = AttendanceSchema()
attendances_schema = AttendanceSchema(many=True)
