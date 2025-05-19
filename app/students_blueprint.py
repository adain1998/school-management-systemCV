from flask import render_template, request, url_for, redirect, flash, Blueprint, jsonify
# from sqlalchemy import desc, asc
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
import logging
from app import db, mail
from app.decorators import roles_required
from app.models import Student, Classe, Sections, Option, Parent, Assignment, Message
from flask_mail import Message as MailMessage  # ✅ import à faire tout en haut
from sqlalchemy import or_, func
from sqlalchemy import asc
from werkzeug.exceptions import BadRequest
from datetime import datetime
import random
import string
import re



stud = Blueprint('stud', __name__)


@stud.route('/')
@stud.route('/students')
@login_required
def students():
    student = Student.query.all()
    return render_template('index.html', student=student)



@stud.route('/filter_student', methods=['GET'])
def filter_student():
    filter_class_name = request.args.get('filter_class_name', '')
    filter_religion = request.args.get('filter_religion', '')
    filter_username = request.args.get('filter_username', '')
    sort_by = request.args.get('sort_by', 'last_name')
    order = request.args.get('order', 'asc')

    # Appliquez vos filtres ici
    students_filtered = Student.query.all()

    if filter_class_name:
        students_filtered = [s for s in students_filtered if filter_class_name.lower() in s.class_name.lower()]
    if filter_religion:
        students_filtered = [s for s in students_filtered if filter_religion.lower() in s.religion.lower()]
    if filter_username:
        students_filtered = [s for s in students_filtered if filter_username.lower() in s.username.lower()]

    # Tri des étudiants
    if sort_by == 'last_name':
        students_filtered.sort(key=lambda s: s.last_name, reverse=(order == 'desc'))
    elif sort_by == 'first_name':
        students_filtered.sort(key=lambda s: s.first_name, reverse=(order == 'desc'))

    return render_template(
        'filter_students.html',
        students_filtered=students_filtered,
        filter_class_name=filter_class_name,
        filter_religion=filter_religion,
        filter_username=filter_username,
        sort_by=sort_by,
        order=order
    )



@stud.route('/edit_student/<int:id>', methods=['GET', 'POST'])
@roles_required('admin','superadmin','compable')
def edit_student():
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.last_name = request.form['last_name']
        student.first_name = request.form['first_name']
        student.class_name = request.form['class_name']
        student.date_naissance = request.form['date_naissance']
        student.registration_date = request.form['registration_date']
        student.numero_matricule = request.form['numero_matricule']
        student.fees_paid = request.form['fees_paid']
        student.class_id = request.form['class_id']
        student.debt = request.form['debt']
        student.religion = request.form['religion']
        student.notes = request.form['notes']
        student.absences = request.form['absences']
        student.presences = request.form['presences']
        student.classes = request.form['classes']
        student.sections = request.form['sections']
        student.options = request.form['options']
        student.parent = request.form['parent']
        assignment_ids = request.form.getlist('assignments')  # Récupère les devoirs sélectionnés
        assignments = Assignment.query.filter(Assignment.id.in_(assignment_ids)).all()
        student.assignments = assignments  # Associe les devoirs sélectionnés à l'étudiant

        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('index'))
    classe = Classe.query.all()

    # Récupération de tous les devoirs pour les afficher dans le formulaire
    assignments = Assignment.query.all()
    selected_assignment_ids = [a.id for a in student.assignments]
    return render_template('edit_student.html', student=student,
                           classe=classe, assignments=assignments, selected_assignment_ids=selected_assignment_ids)



@stud.route('/api/students', methods=['GET'])
def get_students():
    student = Student.query.all()
    return jsonify([{
        'id': student.id,
        'nom': student.nom,
        'prenom': student.prenom,
        'classe_id': student.class_name,
        'date_naissance': student.date_naissance.isoformat(),
        'registrationDate': student.registration_date.isoformat(),
        'paiement': student.paiement,
    } for student in student])


                                                                # recherche des étudiants
@stud.route('/student/rechercher', methods=['GET'])
def rechercher_eleves():
    try:
        # Paramètres de recherche
        search_query = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = 10

        students_query = Student.query

        # Si une requête de recherche est fournie
        if search_query:
            # Normalisation pour une recherche plus intelligente
            search_words = search_query.split()
            filters = []

            for word in search_words:
                word_pattern = f"%{word.lower()}%"
                filters.append(func.lower(Student.first_name).like(word_pattern))
                filters.append(func.lower(Student.last_name).like(word_pattern))
                filters.append(func.lower(Student.numero_matricule).like(word_pattern))

            # Utilise "or_" pour trouver toute correspondance
            students_query = students_query.filter(or_(*filters))

        # Exécuter la requête paginée
        students_paginated = students_query.order_by(Student.last_name).paginate(page=page, per_page=per_page)

        # Afficher un message si aucun résultat
        if not students_paginated.items:
            flash('Aucun étudiant trouvé avec ces critères', 'info')

        return render_template(
            'Student_list.html',
            students=students_paginated,
            search_query=search_query
        )

    except Exception as e:
        flash(f"Erreur lors de la recherche : {str(e)}", 'error')
        return redirect(url_for('stud.all_students'))



@stud.route('/all_students')
def all_students():
    try:
        page = request.args.get('page', 1, type=int)  # Pagination : numéro de page
        per_page = 10  # Nombre d'éléments par page
        students_query = Student.query.paginate(page=page, per_page=per_page)

        if not students_query.items:
            flash('Aucun étudiant trouvé.', 'info')

        return render_template('add_student.html', students=students_query)

    except Exception as e:
        flash(f"Erreur lors de la récupération des étudiants: {str(e)}", 'error')
        return redirect(url_for('stud.rechercher_eleves'))  # Redirection en cas d'erreur



@stud.route('/student/<int:student_id>', methods=['GET', 'POST'])
def student_details(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        # Récupération des champs depuis le formulaire
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        date_naissance_str = request.form.get('date_naissance', '').strip()
        paiement_str = request.form.get('paiement', '').strip()
        debt_str = request.form.get('debt', '').strip()
        religion = request.form.get('religion', '').strip() or None
        parent_id = request.form.get('parent_id')
        class_id = request.form.get('class_id')

        # === VALIDATIONS ===
        if not first_name or not last_name:
            flash("Le prénom et le nom sont obligatoires.", "warning")
            return redirect(request.url)

        student.first_name = first_name
        student.last_name = last_name

        # Date de naissance
        if date_naissance_str:
            try:
                student.date_naissance = datetime.strptime(date_naissance_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Format de date invalide (AAAA-MM-JJ).", "danger")
                return redirect(request.url)

        # Paiement
        if paiement_str:
            try:
                paiement = float(paiement_str)
                if paiement < 0:
                    raise ValueError
                student.fees_paid = paiement
            except ValueError:
                flash("Montant de paiement invalide.", "warning")
                return redirect(request.url)

        # Dette
        if debt_str:
            try:
                debt = float(debt_str)
                if debt < 0:
                    raise ValueError
                student.debt = debt
            except ValueError:
                flash("Montant de dette invalide.", "warning")
                return redirect(request.url)

        # Religion
        student.religion = religion

        # Parent (optionnel)
        if parent_id:
            if parent_id.isdigit() and Parent.query.get(int(parent_id)):
                student.parent_id = int(parent_id)
            else:
                flash("Parent non trouvé.", "warning")
                return redirect(request.url)

        # Classe (obligatoire)
        if class_id:
            if class_id.isdigit() and Classe.query.get(int(class_id)):
                student.class_id = int(class_id)
            else:
                flash("Classe invalide ou introuvable.", "warning")
                return redirect(request.url)

        # === COMMIT AVEC GESTION D'ERREUR SPÉCIFIQUE ===
        try:
            db.session.commit()
            flash("Les informations de l'étudiant ont été mises à jour avec succès.", "success")
            return redirect(url_for('stud.student_details', student_id=student.id))
        except SQLAlchemyError as db_err:
            db.session.rollback()
            logging.exception(f"Erreur SQLAlchemy : {db_err}")
            flash("Une erreur de base de données est survenue. Veuillez réessayer.", "danger")

    return render_template('student_detail.html', student=student)



@stud.route('/student/contact/<int:student_id>', methods=['POST'])
def contact_student(student_id):
    student = Student.query.get_or_404(student_id)

    email = request.form.get('email')
    message_content = request.form.get('message')

    # Vérification des champs requis
    if not email or not message_content:
        flash('L\'email et le message sont requis.', 'danger')
        return redirect(url_for('stud.student_details', student_id=student.id))

    # Validation de l'email
    if not validate_email(email):
        flash('Adresse email invalide.', 'danger')
        return redirect(url_for('stud.student_details', student_id=student.id))

    try:
        # Enregistrement facultatif dans la base
        msg_record = Message(student_id=student.id, email=email, message=message_content)
        db.session.add(msg_record)
        db.session.commit()

        # Envoi de l'e-mail
        subject = f"Message concernant l'élève {student.first_name} {student.last_name}"
        mail_msg = MailMessage(subject=subject,
                               recipients=[email],
                               body=message_content)
        mail.send(mail_msg)

        flash('Votre message a été envoyé avec succès.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de l\'envoi : {str(e)}', 'danger')

    return redirect(url_for('stud.student_details', student_id=student.id))


def validate_email(email):
    """Valide une adresse email simple avec regex."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None
@stud.route('/delete_student/<int:student_id>', methods=['GET', 'POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)

    try:
        # Suppression de l'étudiant
        db.session.delete(student)
        db.session.commit()

        # Message flash de succès
        flash('L\'étudiant a été supprimé avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        # Message flash d'erreur
        flash(f'Une erreur est survenue lors de la suppression de l\'étudiant.{e}', 'danger')

    # Rediriger vers la liste des étudiants après la suppression
    return redirect(url_for('stud.list_student'))



@stud.route('/view_student/<int:student_id>', methods=['GET'])
def view_student(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('View_list.html', student=student)


""""@stud.route('/student')
def list_student():
    # Récupérer la page de la requête ou par défaut la première page
    page = request.args.get('page', 1, type=int)

    # Nombre d'étudiants par page
    per_page = 10

    # Récupérer le paramètre de tri (par exemple 'nom') depuis l'URL ou par défaut 'nom'
    sort_by = request.args.get('sort_by', 'nom')

    # Appliquer le tri en fonction du paramètre
    student = Student.query.order_by(getattr(Student, sort_by)).paginate(page, per_page, error_out=False)

    # Récupérer la pagination et les étudiants pour le template
    return render_template('student_list.html', student=student.items, pagination=student)"""


# Liste blanche des champs triables pour éviter les abus
VALID_SORT_FIELDS = {
    'nom': Student.last_name,
    'prenom': Student.first_name,
    'matricule': Student.numero_matricule,
    'date': Student.registration_date  # à adapter si tu as un champ de création
}

@stud.route('/student')
def list_students():
    try:
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = 10

        # Paramètre de tri sécurisé
        sort_key = request.args.get('sort_by', 'nom')
        sort_field = VALID_SORT_FIELDS.get(sort_key)

        if not sort_field:
            raise BadRequest(f"Champ de tri invalide : '{sort_key}'")

        # Récupération paginée et triée des étudiants
        students_paginated = Student.query.order_by(asc(sort_field)).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # Si aucun étudiant n’est trouvé à cette page
        if not students_paginated.items and page > 1:
            flash("Aucune donnée trouvée pour cette page.", "info")

        return render_template(
            'student_list.html',
            students=students_paginated,
        )

    except BadRequest as e:
        flash(str(e), "error")
        return render_template('student_list.html', students=[], pagination=None)

    except Exception as e:
        # Log l'erreur si tu as un système de logs
        flash(f"Erreur serveur : {str(e)}", "error")
        return render_template('student_list.html', students=[], pagination=None)
def generate_matricule(length=8):
    """
    Génère un numéro de matricule alphanumérique de longueur 'length'.
    """
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))




@stud.route('/add_student', methods=['POST'])
def add_student():
    try:
        # Récupération et validation des champs
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        date_naissance = request.form.get('date_naissance')
        # registration_date n'est pas récupéré, car il est géré par défaut dans le modèle
        numero_matricule = generate_matricule()  # Numéro de matricule généré automatiquement
        fees_paid = float(request.form.get('fees_paid', 0))
        class_id = request.form.get('class_id')
        debt = float(request.form.get('debt', 0))
        religion = request.form.get('religion', 'N/A')
        parent_id = request.form.get('parent_id')

        # Validation des champs obligatoires
        if not all([last_name, first_name, date_naissance, class_id, parent_id]):
            flash("Tous les champs obligatoires doivent être remplis!", "danger")
            return redirect(url_for('stud.add_student'))

        # Conversion de la date de naissance
        try:
            date_naissance = datetime.strptime(date_naissance, "%Y-%m-%d")
        except ValueError:
            flash("Le format de la date de naissance est invalide. Utilisez le format YYYY-MM-DD.", "danger")
            return redirect(url_for('stud.add_student'))

        # Vérification de l'existence du parent et de la classe
        parents = Parent.query.all()
        classe = Classe.query.get(class_id)

        if not parents:
            flash("Le parent spécifié n'existe pas.", "danger")
            return redirect(url_for('stud.add_student'))
        if not classe:
            flash("La classe spécifiée n'existe pas.", "danger")
            return redirect(url_for('stud.add_student'))

        # Création du nouvel étudiant (registration_date est géré par le modèle)
        new_student = Student(
            last_name=last_name,
            first_name=first_name,
            date_naissance=date_naissance,
            numero_matricule=numero_matricule,
            fees_paid=fees_paid,
            class_id=class_id,
            parent_id=parent_id,
            debt=debt,
            religion=religion
        )

        # Ajouter les relations avec les classes, sections et options
        selected_classes = request.form.getlist('classes')  # Liste des classes supplémentaires (identifiants ou objets)
        selected_sections = request.form.getlist('sections')  # Liste des sections supplémentaires
        selected_options = request.form.getlist('options')    # Liste des options supplémentaires

        options = Option.query.filter(Option.id.in_(selected_options)).all()
        sections = Sections.query.filter(Sections.id.in_(selected_sections)).all()

        new_student.classes.extend(selected_classes)
        new_student.sections.extend(sections)
        new_student.options.extend(options)

        db.session.add(new_student)
        db.session.commit()

        flash("L'étudiant a été ajouté avec succès!", "success")
        return redirect(url_for('stud.all_students'))

    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de l'ajout de l'étudiant : {e}", "danger")
        return redirect(url_for('stud.add_student'))