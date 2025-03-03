from flask import Blueprint, render_template, request, redirect, flash, url_for
from models import db, Sections, Classe, Option


sect = Blueprint('sect', __name__)


@sect.route('/sections')
def view_sections():
    sections = Sections.query.all()
    return render_template('section.html', sections=sections)


@sect.route('/add_section', methods=['POST'])
def add_section():
    nom = request.form['nom']
    classe_id = request.form['classe_id']
    new_section = Sections(nom=nom, classe_id=classe_id)
    db.session.add(new_section)
    db.session.commit()
    flash('Section added successfully!', 'success')
    return redirect(url_for('view_sections'))


@sect.route('/edit_section/<int:id>', methods=['GET', 'POST'])
def edit_section():
    section = Sections.query.get_or_404(id)
    if request.method == 'POST':
        section.name = request.form['name']
        section.class_id = request.form['classe_id']
        db.session.commit()
        flash('Section updated successfully!', 'success')
        return redirect(url_for('view_sections'))
    return render_template('edit_section.html', section=section)


@sect.route('/delete_section/<int:id>')
def delete_section():
    section = Sections.query.get_or_404(id)
    db.session.delete(section)
    db.session.commit()
    flash('Section deleted successfully!', 'success')
    return redirect(url_for('view_sections'))


@sect.route('/gestion_classes', methods=['GET'])
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

    return render_template('gestion_classes.html', classes=classes, sections=sections, options=options)
