from flask import Blueprint, render_template, request, redirect, flash, url_for
from app.models import db, Classe, Sections, Option, Student
from werkzeug.exceptions import NotFound, BadRequest

# Initialisation du Blueprint
niveau = Blueprint('niveau', __name__)


# View pour afficher toutes les classes
@niveau.route('/classes')
def view_classes():
    try:
        # Pagination des classes (ex. 10 classes par page)
        page = int(request.args.get('page', 1))
        per_page = 10
        classes = Classe.query.paginate(page, per_page, False)

        # Récupérer la liste des élèves (facultatif, avec pagination côté serveur pour les élèves)
        student_page = int(request.args.get('student_page', 1))
        students_per_page = 10
        students = Student.query.paginate(student_page, students_per_page, False)

        # Passer les données à la vue
        return render_template('classe.html', classes=classes.items, students=students.items,
                               classes_page=classes.page, students_page=students.page)
    except Exception as e:
        flash(f"Une erreur s'est produite lors de la récupération des classes : {str(e)}", 'danger')
        return redirect(url_for('index'))  # Redirection vers la page d'accueil en cas d'erreur
# View pour ajouter une classe

@niveau.route('/add_class', methods=['POST'])
def add_class():
    try:
        nom = request.form.get('nom')

        if not nom:
            raise BadRequest("Le nom de la classe est requis.")

        new_class = Classe(nom=nom)
        db.session.add(new_class)
        db.session.commit()

        flash('Classe ajoutée avec succès!', 'success')
        return redirect(url_for('niveau.view_classes'))

    except BadRequest as e:
        flash(str(e), 'danger')
        return redirect(url_for('niveau.view_classes'))

    except Exception as e:
        flash(f"Une erreur s'est produite lors de l'ajout de la classe : {str(e)}", 'danger')
        return redirect(url_for('niveau.view_classes'))


# View pour modifier une classe existante
@niveau.route('/edit_class/<int:id>', methods=['GET', 'POST'])
def edit_class():
    try:
        class_ = Classe.query.get_or_404(id)

        if request.method == 'POST':
            new_name = request.form.get('name')
            if not new_name:
                raise BadRequest("Le nom de la classe est requis.")

            class_.nom = new_name
            db.session.commit()

            flash('Classe mise à jour avec succès!', 'success')
            return redirect(url_for('niveau.view_classes'))

        return render_template('edit_class.html', class_=class_)

    except NotFound:
        flash("Classe introuvable.", 'danger')
        return redirect(url_for('niveau.view_classes'))

    except BadRequest as e:
        flash(str(e), 'danger')
        return redirect(url_for('niveau.view_classes'))

    except Exception as e:
        flash(f"Une erreur s'est produite lors de la modification de la classe : {str(e)}", 'danger')
        return redirect(url_for('niveau.view_classes'))


# View pour supprimer une classe
@niveau.route('/delete_classe/<int:id>', methods=['POST'])
def delete_classe():
    try:
        classe = Classe.query.get_or_404(id)
        db.session.delete(classe)
        db.session.commit()

        flash('Classe supprimée avec succès!', 'success')
        return redirect(url_for('niveau.view_classes'))

    except NotFound:
        flash("Classe introuvable.", 'danger')
        return redirect(url_for('niveau.view_classes'))

    except Exception as e:
        flash(f"Une erreur s'est produite lors de la suppression de la classe : {str(e)}", 'danger')
        return redirect(url_for('niveau.view_classes'))


# View pour la gestion des classes avec filtres
@niveau.route('/gestion_classes', methods=['GET'])
def gestion_classes():
    try:
        # Récupérer les paramètres de requête pour filtrer
        class_name = request.args.get('class_name')
        section_name = request.args.get('section_name')
        option_name = request.args.get('option_name')

        # Filtrer les classes
        query = Classe.query
        if class_name:
            query = query.filter(Classe.nom.ilike(f"%{class_name}%"))
        classes = query.all()

        # Filtrer les sections
        query_sections = Sections.query
        if section_name:
            query_sections = query_sections.filter(Sections.nom.ilike(f"%{section_name}%"))
        sections = query_sections.all()

        # Filtrer les options
        query_options = Option.query
        if option_name:
            query_options = query_options.filter(Option.nom.ilike(f"%{option_name}%"))
        options = query_options.all()

        return render_template('gestion-classes.html', classes=classes, sections=sections, options=options)

    except Exception as e:
        flash(f"Une erreur s'est produite lors de la récupération des données : {str(e)}", 'danger')
        return redirect(url_for('niveau.view_classes'))

