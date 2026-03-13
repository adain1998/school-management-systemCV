import logging
from app.extensions import db
from sqlalchemy.orm import Query
from sqlalchemy.sql import asc, desc
from app.models import Matiere, Note  # à adapter selon votre structure

def apply_sorting(query: Query, sort_by: str, order: str = "asc") -> Query:
    """
    Applique un tri dynamique à une requête SQLAlchemy.

    :param query: La requête SQLAlchemy à trier.
    :param sort_by: Le nom du champ de tri (ex : 'nom', 'moyenne').
    :param order: L’ordre du tri ('asc' ou 'desc').
    :return: La requête triée.
    """
    try:
        valid_fields = {
            'nom': Matiere.nom,
            'moyenne': db.func.avg(Note.valeur)
        }

        column = valid_fields.get(sort_by, Matiere.nom)

        # Appliquer le tri
        sorted_query = query.order_by(asc(column) if order == "asc" else desc(column))
        logging.info(f"Tri appliqué sur '{sort_by}' en ordre '{order}'.")
        return sorted_query

    except Exception as e:
        logging.exception(f"Erreur lors de l'application du tri : {str(e)}")
        return query  # Retourne la requête non triée par défaut en cas d'erreur
