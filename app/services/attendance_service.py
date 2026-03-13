# app/services/attendance_service.py

from app.models import Attendance, db
from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)


def create_attendance_record(student_id: int, presence: bool, date: datetime = None):
    """Crée un enregistrement de présence pour un étudiant.

    Args:
        student_id (int) : ID de l'étudiant.
        Presence (bool) : Présence ou absence.
        Date (datetime, optional) : Date de la présence. Par défaut: now UTC.

    Returns:
        Attendance | dict: Instance d'Attendance ou dict d'erreur.
        :param date:
        :param student_id:
        :param presence:
    """
    try:
        date = date or datetime.now(pytz.utc)

        # Vérifier si une présence existe déjà à la même date pour cet étudiant
        existing = Attendance.query.filter_by(student_id=student_id, date=date).first()
        if existing:
            logger.warning(f"Présence déjà enregistrée pour l'étudiant {student_id} à la date {date}")
            return {"error": "Attendance already recorded for this student and date."}

        # Création du nouvel enregistrement
        attendance = Attendance(student_id=student_id, presence=presence, date=date)
        db.session.add(attendance)
        db.session.commit()

        logger.info(f"Présence enregistrée avec succès pour l'étudiant {student_id}")
        return attendance

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de l'enregistrement de la présence : {str(e)}")
        return {"error": f"Internal server error: {str(e)}"}


def fetch_attendance_by_student(student_id: int):
    """Récupère toutes les présences d'un étudiant.

    Args:
        student_id (int) : ID de l'étudiant.

    Returns:
        list[Attendance] : Liste des présences triées par date décroissante.
    """
    try:
        return Attendance.query.filter_by(student_id=student_id)\
            .order_by(Attendance.date.desc()).all()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des présences de l'étudiant {student_id}: {str(e)}")
        return []
