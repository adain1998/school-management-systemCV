import os
import logging
import numpy as np
import matplotlib.pyplot as plt

def generate_charts(df, output_dir='static/images'):
    """
    Génère et sauvegarde les graphiques de performance des étudiants.

    :param df: DataFrame contenant au moins les colonnes 'nom' et 'moyenne'
    :param output_dir: Répertoire de sauvegarde des images
    :raises ValueError: si le DataFrame est invalide
    """
    try:
        # Vérifie que le DataFrame est valide
        if df is None or df.empty:
            raise ValueError("Le DataFrame fourni est vide ou non valide.")

        required_columns = {'nom', 'moyenne'}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"Le DataFrame doit contenir les colonnes {required_columns}")

        # Crée le dossier de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)

        # 1. Courbe sinusoïdale
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        plt.figure(figsize=(8, 4))
        plt.plot(x, y, color='red', linewidth=2, linestyle="--")
        plt.title("Courbe Sinusoïdale")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'sinus_plot.png'))
        plt.close()

        # 2. Nuage de points
        plt.figure(figsize=(8, 4))
        plt.scatter(x, y, color='green', marker='o', s=50)
        plt.title("Points Dispersés")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'scatter_plot.png'))
        plt.close()

        # 3. Histogramme des moyennes
        plt.figure(figsize=(8, 4))
        plt.hist(df['moyenne'], bins=10, color='blue', alpha=0.7)
        plt.xlabel('Moyenne')
        plt.ylabel("Nombre d'étudiants")
        plt.title("Distribution des Moyennes")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'moyenne_student.png'))
        plt.close()

        # 4. Graphique barres "performance par étudiant"
        df_sorted = df.sort_values('moyenne', ascending=False)
        plt.figure(figsize=(10, 5))
        plt.bar(df_sorted['nom'], df_sorted['moyenne'], color='purple')
        plt.xticks(rotation=45, ha='right')
        plt.title("Performance par Étudiant")
        plt.ylabel("Moyenne")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'performance_chart.png'))
        plt.close()

    except Exception as e:
        logging.exception("Erreur lors de la génération des graphiques")
        raise RuntimeError(f"Erreur lors de la génération des graphiques : {str(e)}")
