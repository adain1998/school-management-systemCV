import pandas as pd
import os
import logging
from flask import flash
from typing import Optional

def process_student_data(file_path: str) -> Optional[pd.DataFrame]:
    """
    Charge les données des étudiants depuis un fichier CSV,
    vérifie les colonnes nécessaires, calcule les moyennes par étudiant
    et retourne un DataFrame enrichi.

    :param file_path: Chemin du fichier CSV à traiter.
    :return: DataFrame contenant les moyennes, ou None en cas d'erreur critique.
    """
    try:
        if not os.path.exists(file_path):
            msg = f"Fichier introuvable : {file_path}"
            logging.error(msg)
            flash(msg, "danger")
            return None

        df = pd.read_csv(file_path)

        # Vérifier la présence des colonnes nécessaires
        required_columns = {'student_id', 'Note'}
        if not required_columns.issubset(df.columns):
            msg = f"Colonnes manquantes dans le fichier CSV. Requis : {required_columns}"
            logging.error(msg)
            flash(msg, "danger")
            return None

        # Nettoyage des valeurs manquantes ou non numériques
        df = df.dropna(subset=['student_id', 'Note'])
        df['Note'] = pd.to_numeric(df['Note'], errors='coerce')
        df = df.dropna(subset=['Note'])

        # Calcul de la moyenne par étudiant
        df['moyenne'] = df.groupby('student_id')['Note'].transform('mean')

        logging.info("✅ Données des étudiants traitées avec succès")
        return df

    except pd.errors.EmptyDataError:
        msg = "Le fichier CSV est vide."
        logging.error(msg)
        flash(msg, "danger")
    except pd.errors.ParserError as e:
        msg = f"Erreur d'analyse du fichier CSV : {str(e)}"
        logging.error(msg)
        flash(msg, "danger")
    except Exception as e:
        msg = f"Erreur inattendue lors du traitement du fichier CSV : {str(e)}"
        logging.exception(msg)
        flash(msg, "danger")

    return None
