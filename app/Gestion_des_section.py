
from flask import Blueprint, render_template, request, redirect, flash, url_for, current_app, jsonify
from app.models import db, Sections, Classe
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from sqlalchemy import asc, desc
from werkzeug.exceptions import NotFound
import logging

sect = Blueprint('sect', __name__)


@sect.route('/sections', methods=['GET'])
def view_sections():
    try:
        sections = Sections.query.order_by(Sections.nom.asc()).all()
        if not sections:
            flash("Aucune section enregistrée pour le moment.", "info")
        return render_template('sections/view_sections.html', sections=sections)
    except Exception as e:
        current_app.logger.error(f"Erreur lors du chargement des sections : {str(e)}")
        flash("Une erreur s’est produite lors du chargement des sections. Veuillez réessayer.", "danger")
        return render_template('/view_sections.html', sections=[])



@sect.route('/sections/add', methods=['POST'])
def add_section():
    try:
        nom = request.form.get('nom', '').strip()
        classe_id = request.form.get('classe_id', '').strip()

        # 🔎 Validation basique
        if not nom or not classe_id:
            flash("Le nom de la section et la classe associée sont requis.", "warning")
            return redirect(url_for('sect.view_sections'))

        # 🔒 Vérification d’unicité (ex : pas deux sections du même nom pour une classe)
        existing_section = Sections.query.filter_by(nom=nom, classe_id=classe_id).first()
        if existing_section:
            flash("Une section portant ce nom existe déjà pour cette classe.", "info")
            return redirect(url_for('sect.view_sections'))

        # ✅ Création de la section
        new_section = Sections(nom=nom, classe_id=classe_id)
        db.session.add(new_section)
        db.session.commit()

        flash("✅ Section ajoutée avec succès !", "success")
        return redirect(url_for('sect.view_sections'))

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur SQL lors de l'ajout de la section : {str(e)}")
        flash("Une erreur s’est produite lors de l’ajout. Veuillez réessayer.", "danger")
        return redirect(url_for('sect.view_sections'))

    except Exception as e:
        current_app.logger.exception(f"Erreur inattendue lors de l'ajout de la section : {str(e)}")
        flash("Une erreur inattendue s’est produite.", "danger")
        return redirect(url_for('sect.view_sections'))



@sect.route('/sections/edit/<int:section_id>', methods=['GET', 'POST'])
def edit_section(section_id):
    section = Sections.query.get_or_404(section_id)

    if request.method == 'POST':
        try:
            nom = request.form.get('name', '').strip()
            classe_id = request.form.get('classe_id', '').strip()

            # ✅ Validation basique
            if not nom or not classe_id:
                flash("Le nom de la section et la classe sont requis.", "warning")
                return redirect(url_for('sect.edit_section', section_id=section_id))

            # 🔒 Vérification d’unicité (éviter doublons avec une autre section)
            existing = Sections.query.filter(
                Sections.nom == nom,
                Sections.classe_id == classe_id,
                Sections.id != section_id
            ).first()

            if existing:
                flash("Une autre section portant ce nom existe déjà pour cette classe.", "info")
                return redirect(url_for('sect.edit_section', section_id=section_id))

            # ✅ Mise à jour des données
            section.nom = nom
            section.classe_id = classe_id
            db.session.commit()

            flash("✅ Section modifiée avec succès.", "success")
            return redirect(url_for('sect.view_sections'))

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur d'intégrité lors de la modification : {str(e)}")
            flash("Erreur de données : modification invalide.", "danger")
            return redirect(url_for('sect.edit_section', section_id=section_id))

        except DataError as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur de données lors de la modification : {str(e)}")
            flash("Format de données incorrect. Veuillez vérifier les champs.", "danger")
            return redirect(url_for('sect.edit_section', section_id=section_id))

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur SQL : {str(e)}")
            flash("Erreur technique lors de la modification. Réessayez plus tard.", "danger")
            return redirect(url_for('sect.edit_section', section_id=section_id))

        except Exception as e:
            current_app.logger.exception(f"Erreur inattendue : {str(e)}")
            flash("Une erreur inattendue s’est produite. Contactez l’administrateur.", "danger")
            return redirect(url_for('sect.edit_section', section_id=section_id))
    classes = Classe.query.all()
            # 🖊️ Affichage du formulaire en GET
    return render_template('edit_section.html', section=section, classes=classes)



@sect.route('/delete_section/<int:section_id>', methods=['POST'])
def delete_section(section_id):
    try:
        section = Sections.query.get_or_404(section_id)
        db.session.delete(section)
        db.session.commit()

        flash(f"La section « {section.nom} » a été supprimée avec succès.", 'success')
        return redirect(url_for('sect.view_sections'))

    except IntegrityError as e:
        db.session.rollback()
        logging.warning(f"Conflit d'intégrité lors de la suppression de la section ID {section_id} : {e}")
        flash("Impossible de supprimer cette section car elle est utilisée ailleurs (conflit d'intégrité).", 'warning')
        return redirect(url_for('sect.view_sections'))

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Erreur SQLAlchemy lors de la suppression de la section ID {section_id} : {e}")
        flash("Erreur de base de données. Veuillez réessayer plus tard.", 'danger')
        return redirect(url_for('sect.view_sections'))

    except NotFound:
        flash("La section demandée est introuvable.", 'danger')
        return redirect(url_for('sect.view_sections'))

    except Exception as e:
        db.session.rollback()
        logging.critical(f"Erreur inattendue lors de la suppression de la section ID {section_id} : {e}", exc_info=True)
        flash("Une erreur inattendue est survenue. L’administrateur a été notifié.", 'danger')
        return redirect(url_for('sect.view_sections'))



@sect.route('/', methods=['GET'])
def get_sections():
    # Récupérer les paramètres de tri
    sort_by = request.args.get('sortBy', 'name')
    order = request.args.get('order', 'asc')

    # Validation allowlist des champs triables
    allowed_sort_fields = {'name': Sections.name, 'created_at': Sections.created_at}
    if sort_by not in allowed_sort_fields:
        return jsonify({'error': 'Champ de tri invalide.'}), 400

    # Choisir la direction du tri
    order_func = asc if order == 'asc' else desc

    try:
        sections = Sections.query.order_by(order_func(allowed_sort_fields[sort_by])).all()

        # Sérialiser les sections
        result = []
        for section in sections:
            result.append({
                'id': section.id,
                'name': section.name,
                'created_at': section.created_at.isoformat()
            })

        return jsonify({'data': result})

    except Exception as e:
        print(f"Erreur lors de la récupération des sections : {e}")
        return jsonify({'error': 'Erreur serveur'}), 500



"""@sect.route('/gestion_classes', methods=['GET'])
def gestion_classes():
    # Récupérer les paramètres de requête pour filtrer
    class_name = request.args.get('class_name')
    section_name = request.args.get('section_name')
    option_name = request.args.get('option_name')

    # Filtrer les classes
    query = Classe.query
    if class_name:
        query = query.filter(Classe.name.ilike(f"%{class_name}%"))

    classes = query.all()

    # Filtrer les sections
    query_sections = Sections.query
    if section_name:
        query_sections = query_sections.filter(Sections.name.ilike(f"%{section_name}%"))

    sections = query_sections.all()

    # Filtrer les options
    query_options = Option.query
    if option_name:
        query_options = query_options.filter(Option.name.ilike(f"%{option_name}%"))

    options = query_options.all()

    return render_template('gestion_classes.html', classes=classes, sections=sections, options=options)"""