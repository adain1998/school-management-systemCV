from collections import defaultdict
from typing import List, Tuple, Dict
from app.models import Note, Matiere  # Assure-toi que l'import correspond à ta structure

def calculer_moyennes_par_matiere(notes_with_matieres: List[Tuple[Note, Matiere]]) -> Dict[str, List[float]]:
    """
    Calcule les notes regroupées par matière.

    :param notes_with_matieres: Liste de tuples (Note, Matiere)
    :return: Dictionnaire {nom_matiere : [notes]}
    """
    moyennes_par_matiere = defaultdict(list)

    for note, matiere in notes_with_matieres:
        if note and matiere:
            moyennes_par_matiere[matiere.nom].append(note.valeur)

    return dict(moyennes_par_matiere)


def calculer_moyennes_generales(moyennes_par_matiere: Dict[str, List[float]]) -> Dict[str, float]:
    """
    Calcule la moyenne de chaque matière.

    :param moyennes_par_matiere: Dictionnaire {matière : [notes]}
    :return: Dictionnaire {matière: moyenne}
    """
    moyennes_generales = {}

    for matiere, notes_generale in moyennes_par_matiere.items():
        if notes_generale:
            moyenne = sum(notes_generale) / len(notes_generale)
        else:
            moyenne = 0.0
        moyennes_generales[matiere] = round(moyenne, 2)

    return moyennes_generales


def calculer_moyenne_generale(moyennes_generales: Dict[str, float]) -> float:
    """
    Calcule la moyenne générale de toutes les matières.

    :param moyennes_generales: Dictionnaire {matière: moyenne}
    :return: Moyenne globale
    """
    total_matieres = len(moyennes_generales)
    if total_matieres == 0:
        return 0.0

    total_moyenne = sum(moyennes_generales.values())
    return round(total_moyenne / total_matieres, 2)
