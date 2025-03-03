from flask import Blueprint, render_template, request, redirect, flash, url_for
from models import db, Classe, Sections, Option

niveau = Blueprint('niveau', __name__)


@niveau.route('/classes')
def view_classes():
    classes = Classe.query.all()
    return render_template('classe.html', classes=classes)


@niveau.route('/add_class', methods=['POST'])
def add_class():
    nom = request.form['nom']
    new_class = Classe(nom=nom)
    db.session.add(new_class)
    db.session.commit()
    flash('Class added successfully!', 'success')
    return redirect(url_for('view_classes'))


@niveau.route('/edit_class/<int:id>', methods=['GET', 'POST'])
def edit_class():
    class_ = Classe.query.get_or_404(id)
    if request.method == 'POST':
        class_.name = request.form['name']
        db.session.commit()
        flash('Class updated successfully!', 'success')
        return redirect(url_for('view_classes'))
    return render_template('edit_class.html', class_=class_)


@niveau.route('/delete_classe/<int:id>', 'DELETE')
def delete_classe():
    classe_id = Classe.query.get_or_404(id)
    db.session.delete(classe_id)
    db.session.commit()
    flash('Class deleted successfully!', 'success')
    return redirect(url_for('view_classes'))


@niveau.route('/gestion_classes', methods=['GET'])
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

    return render_template('gestion-classes.html', classes=classes, sections=sections, options=options)
