from flask import render_template, request, url_for, redirect, flash, Blueprint, jsonify
from sqlalchemy import desc, asc
from flask_login import login_required
from models import db, Student, Payment, Classe, Sections, Option, Parent
from datetime import datetime
import pytz


stud = Blueprint('stud', __name__)


@stud.route('/')
@stud.route('/students')
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
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('index'))
    classe = Classe.query.all()
    return render_template('edit_student.html', student=student, classe=classe)



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
        # Récupération des paramètres de la recherche
        nom = request.args.get('nom', '')
        prenom = request.args.get('prenom', '')
        page = request.args.get('page', 1, type=int)  # Pagination : numéro de page
        per_page = 10  # Nombre d'éléments par page

        # Filtrer les étudiants par nom et prénom
        students_query = Student.query.filter(
            Student.nom.ilike(f'%{nom}%'),
            Student.prenom.ilike(f'%{prenom}%')
        ).paginate(page=page, per_page=per_page)

        if not students_query.items:
            flash('Aucun étudiant trouvé avec ces critères', 'info')

        return render_template('Student_list.html', students=students_query, nom=nom, prenom=prenom)

    except Exception as e:
        flash(f"Erreur lors de la recherche: {str(e)}", 'error')
        return redirect(url_for('stud.all_students'))  # Redirection vers la page des étudiants



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
        # Récupérer l'étudiant avec l'ID
        student = Student.query.get_or_404(student_id)

        if request.method == 'POST':
            # Récupérer les données du formulaire pour la mise à jour
            student.nom = request.form.get('nom')
            student.prenom = request.form.get('prenom')
            student.date_naissance = request.form.get('date_naissance')
            student.paiement = request.form.get('paiement')

            try:
                # Sauvegarder les modifications dans la base de données
                db.session.commit()
                flash('Les informations de l\'étudiant ont été mises à jour avec succès.', 'success')
                return redirect(url_for('student_details', student_id=student.id))
            except Exception as e:
                db.session.rollback()
                flash(f'Une erreur est survenue lors de la mise à jour de l\'étudiant.{e}', 'danger')

        # Si la méthode est GET, afficher les détails de l'étudiant
        return render_template('student_details.html', student=student)



@stud.route('/student/contact/<int:student_id>', methods=['POST'])
def contact_student(student_id):
        student = Student.query.get_or_404(student_id)
        email = request.form.get('email')
        message = request.form.get('message')

        # Processus pour envoyer un email ou enregistrer le message
        try:
            # Logique d'envoi de message (email, etc.)
            flash('Votre message a été envoyé avec succès.', 'success')
            return redirect(url_for('student_details', student_id=student.id))
        except Exception as e:
            flash(f'Une erreur est survenue lors de l\'envoi de votre message.{e}', 'danger')
            return redirect(url_for('student_details', student_id=student.id, message=message, email=email))

    # ... (Code existant pour afficher les détails d'un élève)


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


@stud.route('/student')
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
    return render_template('student_list.html', student=student.items, pagination=student)



@stud.route('/all_students')
def all_students():
    student = Student.query.all()  # Vous récupérez tous les étudiants
    return render_template('add_student.html', student=student)



@stud.route('/add_student', methods=['POST'])
def add_student():
    try:
        # Récupération et validation des champs
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        class_name = request.form.get('class_name')
        date_naissance = request.form.get('date_naissance')
        registration_date = request.form.get('registration_date',
                                             datetime.now(pytz.utc))  # Utilise la date actuelle si non spécifiée
        # date sous forme de chaîne
        numero_matricule = request.form.get('numero_matricule')
        fees_paid = float(request.form.get('fees_paid', 0))  # Par défaut à 0 si non fourni
        class_id = request.form.get('class_id')
        debt = float(request.form.get('debt', 0))  # Valeur par défaut 0 si non fournie
        religion = request.form.get('religion', 'N/A')  # Valeur par défaut si non fournie
        parent_id = request.form.get('parent_id')  # ID du parent

        # Validation des champs obligatoires
        if not last_name or not first_name or not class_name or not date_naissance or not registration_date or not numero_matricule or not class_id or not parent_id:
            flash("Tous les champs obligatoires doivent être remplis!", "danger")
            return redirect(url_for('stud.add_student'))

        # Conversion de la date de naissance et de la date d'enregistrement
        try:
            date_naissance = datetime.strptime(date_naissance, "%Y-%m-%d")  # Format YYYY-MM-DD
            registration_date = datetime.strptime(registration_date, "%Y-%m-%d").date()  # Conversion en date (sans l'heure)
        except ValueError:
            flash("Le format des dates est invalide. Utilisez le format YYYY-MM-DD.", "danger")
            return redirect(url_for('stud.add_student'))

        # Vérification de l'existence du parent et de la classe
        parents = Parent.query.all()  # Récupérer tous les parents
        classe = Classe.query.get(class_id)

        if not parents:
            flash("Le parent spécifié n'existe pas.", "danger")
            return redirect(url_for('stud.add_student'))

        if not classe:
            flash("La classe spécifiée n'existe pas.", "danger")
            return redirect(url_for('stud.add_student'))

        # Création du nouvel étudiant
        new_student = Student(
            last_name=last_name,
            first_name=first_name,
            class_name=class_name,
            date_naissance=date_naissance,
            registration_date=registration_date,  # Date correcte
            numero_matricule=numero_matricule,
            fees_paid=fees_paid,
            class_id=class_id,
            parent_id=parent_id,
            debt=debt,
            religion=religion
        )

        # Ajouter les relations avec les classes, sections et options
        selected_classes = request.form.getlist('classes')  # Liste des classes supplémentaires
        selected_sections = request.form.getlist('sections')  # Liste des sections supplémentaires
        selected_options = request.form.getlist('options')  # Liste des options supplémentaires

        # Vérifier que les options et sections existent
        options = Option.query.filter(Option.id.in_(selected_options)).all()
        sections = Sections.query.filter(Sections.id.in_(selected_sections)).all()

        # Ajouter les relations
        new_student.classes.extend(classe for classe in selected_classes if classe)
        new_student.sections.extend(sections)
        new_student.options.extend(options)

        # Sauvegarde dans la base de données
        db.session.add(new_student)
        db.session.commit()

        flash('L\'étudiant a été ajouté avec succès!', 'success')
        return redirect(url_for('stud.all_students'))  # Redirection vers la liste des étudiants

    except Exception as e:
        db.session.rollback()  # Annuler la transaction en cas d'erreur
        flash(f"Erreur lors de l'ajout de l'étudiant : {e}", "danger")
        return redirect(url_for('stud.add_student'))




# Ajout des élèves code mis en reserve

"""@stud.route('/add_student', methods=['POST'])
def add_student():
    last_name = request.form['last_name']
    first_name = request.form['first_name']
    class_name = request.form['class_name']
    date_naissance = request.form['date_naissance']
    registration_date = request.form['registration_date']
    numero_matricule = request.form['numero_matricule']
    fees_paid = request.form['fees_paid']
    class_id = request.form['class_id']
    debt = float(request.form['debt'])
    religion = request.form['religion']
    notes = 0
    absences = int(request.form.get('absences', 0))
    presences = int(request.form.get('presences', "T"))
    classes = request.form.getlist('classes')
    sections = request.form.getlist('sections')
    options = request.form.get('options', {})
    parent = None
    parent_id = request.form.get('parent_id')
    new_student = Student(first_name=first_name,
                          last_name=last_name,
                          classe_name=class_name,
                          date_naissance=date_naissance,
                          registration_date=registration_date,
                          numero_matricule=numero_matricule,
                          fees_paid=fees_paid,
                          class_id=class_id,
                          debt=debt,
                          religion=religion,
                          notes=notes,
                          absences=absences,
                          presences=presences,
                          classes=classes,
                          sections=sections,
                          options=options,
                          parent=parent,
                          parent_id=parent_id)
    db.session.add(new_student)
    db.session.commit()
    flash('Student added successfully!', 'success')
    return redirect(url_for('eleves_tout.html'))
@stud.route('/add_student', methods=['POST'])
def add_student():
    try:
        # Récupération et validation des champs
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        class_name = request.form.get('class_name')
        date_naissance = request.form.get('date_naissance')
        registration_date = request.form.get('registration_date')
        numero_matricule = request.form.get('numero_matricule')
        fees_paid = request.form.get('fees_paid', 0)  # Par défaut à 0 si non fourni
        class_id = request.form.get('class_id')
        debt = float(request.form.get('debt', 0))  # Valeur par défaut 0 si non fournie
        religion = request.form.get('religion', 'N/A')  # Valeur par défaut si non fournie
        absences = int(request.form.get('absences', 0))  # Valeur par défaut 0
        presences = int(request.form.get('presences', 0))  # Valeur par défaut 0
        classes = request.form.getlist('classes')  # Liste de classes
        sections = request.form.getlist('sections')  # Liste de sections
        options = request.form.get('options', {})  # Options par défaut à un dictionnaire vide
        parent_id = request.form.get('parent_id', None)  # Parent optionnel

        # Validation des champs requis
        if not last_name or not first_name or not class_name or not date_naissance or not registration_date or not numero_matricule:
            flash("Tous les champs obligatoires doivent être remplis!", "danger")
            return redirect(url_for('stud.add_student'))

        # Conversion des dates en format datetime (validation basique)
        try:
            date_naissance = datetime.strptime(date_naissance, "%Y-%m-%d")  # Exemple de format : 2025-02-25
            registration_date = datetime.strptime(registration_date, "%Y-%m-%d")
        except ValueError:
            flash("Le format de la date est invalide. Utilisez le format YYYY-MM-DD.", "danger")
            return redirect(url_for('stud.add_student'))

        # Création du nouvel étudiant
        new_student = Student(
            first_name=first_name,
            last_name=last_name,
            classe_name=class_name,
            date_naissance=date_naissance,
            registration_date=registration_date,
            numero_matricule=numero_matricule,
            fees_paid=fees_paid,
            class_id=class_id,
            debt=debt,
            religion=religion,
            notes=0,  # Par défaut
            absences=absences,
            presences=presences,
            classes=classes,
            sections=sections,
            options=options,
            parent_id=parent_id
        )

        # Ajout dans la base de données
        db.session.add(new_student)
        db.session.commit()

        flash('L\'étudiant a été ajouté avec succès!', 'success')
        # Vérifier que la route existe bien sous ce nom
        return redirect(url_for('stud.all_students'))  # Redirection vers la liste des étudiants

    except Exception as e:
        db.session.rollback()  # Annuler la transaction en cas d'erreur
        flash(f"Erreur lors de l'ajout de l'étudiant : {e}", "danger")
        return redirect(url_for('stud.add_student'))
# recherche des étudiants 

@stud.route('/student/rechercher', methods=['GET'])
def rechercher_eleves():
    try:
        # Récupération des paramètres 'nom' et 'prenom' de la requête GET
        nom = request.args.get('nom', '')
        prenom = request.args.get('prenom', '')

        # Recherche des étudiants en filtrant par 'nom' et 'prenom'
        student = Student.query.filter(
            Student.nom.ilike(f'%{nom}%'),  # Utilisation de ilike pour une recherche insensible à la casse
            Student.prenom.ilike(f'%{prenom}%')
        ).all()

        if not students:
            flash('Aucun étudiant trouvé avec ces critères', 'info')

        return render_template('student_list.html', student=student)

    except Exception as e:
        flash(f"Erreur lors de la recherche: {str(e)}", 'error')
        return redirect(url_for('stud.all_students'))  # Redirection vers la page des étudiants en cas d'erreur


@stud.route('/all_students')
def all_students():
    try:
        # Récupération de tous les étudiants de la base de données
        stude = Student.query.all()

        if not students:
            flash('Aucun étudiant trouvé.', 'info')

        return render_template('add_student.html', stude=stude)

    except Exception as e:
        flash(f"Erreur lors de la récupération des étudiants: {str(e)}", 'error')
        return redirect(url_for('stud.rechercher_eleves'))  # Redirection en cas d'erreur


@stud.route('/students', methods=['GET'])
def search_students():
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    students_query = Student.query.filter(Student.nom.like(f'%{search_query}%')).paginate(page=page, per_page=10)
    return render_template('Rechercher_student.html', students=students_query, search=search_query)

# filter les informations 


@stud.route('/filter/<int:id>', methods=['GET', 'POST'])
@login_required
def filter_student():
    filter_class_name = request.args.get('filter_class_name', default='', type=str)
    filter_religion = request.args.get('filter_religion', default='', type=str)
    filter_username = request.args.get('username', default='', type=str)
    sort_by = request.args.get('sort_by', 'last_name', type=str)
    order = request.args.get('order', 'asc', type=str)

    query = Student.query

    if filter_class_name:
        query = query.filter(Student.class_name.ilike(f'%{filter_class_name}%'))
    if filter_religion:
        query = query.filter(Student.religion.ilike(f'%{filter_religion}%'))
    if filter_username:
        query = query.filter(Student.username.ilike(f'%{filter_username}%'))

    if order == 'asc':
        query = query.order_by(asc(sort_by))
    else:
        query = query.order_by(desc(sort_by))

    student_filtrer = query.all()

    return render_template('Filtrer_student.html', student_filtrer=student_filtrer)


# liste etudiant 

@stud.route('/student')
def list_student():
    student = Student.query.all()
    return render_template('Student_list.html', student=student)
    
    
@stud.route('/student')
def list_student():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    student = Student.query.order_by(Student.nom).paginate(page, per_page, error_out=False)
    return render_template('student_list.html', stutents=students.items, pagination=students, student=student)
    
    # supprimer etudiant 
    @stud.route('/student/supprimer/<int:student_id>', methods=['POST'])
def supprimer_eleve(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('liste_student'))
    
    
    
@stud.route('/delete_student/<int:id>', methods=['POST'])
def delete_student():
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Étudiant supprimé avec succès !', 'success')
    return redirect(url_for('student_list'))
    #  details etudiant 
    
@stud.route('/students/<int:student_id>')
def student_details(student_id):
    student = Student.query.get_or_404(student_id)
    paiements = Payment.query.filter_by(etudiant_id=student.id).all()
    return render_template('student_detail.html', student=student, paiements=paiements)"""

