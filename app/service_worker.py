from flask import Blueprint, send_from_directory, current_app, abort, Response, request
import os
import logging

# Configuration du Blueprint pour servir le service worker
service_worker_bp = Blueprint('service_worker', __name__)

@service_worker_bp.route('/service-worker.js')
def service_worker():
    try:
        # Récupération de la version (facultative)
        version = request.args.get('v', 'unknown')

        # Définition du chemin du dossier static
        static_folder = os.path.join(current_app.root_path, 'static')
        file_path = os.path.join(static_folder, 'service-worker.js')

        # Vérification si le fichier existe
        if not os.path.isfile(file_path):
            logging.warning(f"⚠️ service-worker.js introuvable (version {version})")
            abort(404, description="Fichier service-worker.js introuvable.")

        # Renvoi du fichier JS avec le bon type MIME
        response = send_from_directory(
            static_folder,
            'service-worker.js',
            mimetype='application/javascript',
            as_attachment=False
        )

        # Log de la version qui est servie
        logging.info(f"✅ Service Worker v{version} servi avec succès.")
        return response

    except Exception as e:
        # Log d'erreur et renvoi d'une réponse d'erreur interne
        logging.error(f"❌ Erreur service-worker.js (v{request.args.get('v')}): {str(e)}")
        return Response("Erreur interne lors du chargement du service worker.", status=500)
