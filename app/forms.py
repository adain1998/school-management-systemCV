from datetime import date
from flask_wtf import FlaskForm
from wtforms import (FloatField,
                     DateField, SelectField, IntegerField,
                     TextAreaField, BooleanField, StringField,
                     PasswordField, SubmitField, FieldList, FormField)
from wtforms.fields.numeric import DecimalField
from wtforms.validators import NumberRange, Length, EqualTo, ValidationError, DataRequired, Email, Optional
from app.models import Frais, Parent, Student
from wtforms.fields import DateTimeField


current_year = date.today().year


class PaymentForm(FlaskForm):
    student_id = SelectField('Étudiant', coerce=int, validators=[DataRequired()])
    frais_id = SelectField('Type de Frais', coerce=int, validators=[DataRequired(message='Saisissez le type de frais')])
    montant = FloatField('Montant Payé', validators=[
        DataRequired(message="Veuillez saisir un montant positif"),
        NumberRange(min=0.01, message="Le montant doit être positif.")
    ])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired(message="Veuillez saisir une date")])
    statut = SelectField('Statut', choices=[
        ('En attente', 'En attente'),
        ('Complété', 'Complété'),
        ('Échoué', 'Échoué')
    ], validators=[DataRequired()])
    timestamp = DateTimeField('Horodatage', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    mois = IntegerField('Mois', validators=[
        DataRequired(),
        NumberRange(min=1, max=12, message="Le mois doit être compris entre 1 et 12.")
    ])
    annee = IntegerField('Année', validators=[
        DataRequired(),
        NumberRange(min=1900, max=current_year, message="Veuillez saisir une année valide.")
    ])

    submit = SubmitField('Ajouter le paiement')

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.frais_id.choices = [(frais.id, frais.description) for frais in Frais.query.all()]
        self.student_id.choices = [(student.id, f"{student.first_name} {student.last_name}") for student in Student.query.all()]

    def validate_date(self, field):
        if field.data > date.today():
            raise ValidationError("La date ne peut pas être dans le futur.")



class EditFeeForm(FlaskForm):
    student_full_name = StringField(
        "Nom complet de l’étudiant",
        validators=[DataRequired(message="Le nom est requis")]
    )
    montant = DecimalField(
        "Montant",
        validators=[
            DataRequired(message="Le montant est requis"),
            NumberRange(min=0, message="Le montant doit être positif")
        ]
    )
    status = SelectField(
        "Statut",
        choices=[
            ('paid', 'Payé'),
            ('unpaid', 'Impayé'),
            ('pending', 'En attente')
        ],
        validators=[DataRequired(message="Le statut est requis")]
    )
    submit = SubmitField("Mettre à jour")

    # noinspection PyMethodFirstArgAssignment
    def validate_student_full_name(self, field):
        if len(field.data.strip()) == 0:
            raise ValidationError("Le nom de l’étudiant ne peut pas être vide.")



class ModifierPaiement(FlaskForm):
    montant = FloatField('Montant', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d')
    frais_id = SelectField('Frais', coerce=int)



class studentForm(FlaskForm):
    nom = StringField('nom', validators=[DataRequired()])
    prenom = StringField('prenom', validators=[DataRequired()])
    date_naissaince = DateField('Date de naissance', format='%Y-%m-%d', validators=[DataRequired()])
    classe_id = IntegerField('Classe', validators=[DataRequired()])
    registration_date = DateTimeField("Date d'inscription", format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    fees_paid = FloatField('Frais Payés', default=0.0)
    numero_matricule = StringField('Numéro Matricule', validators=[DataRequired()])
    religion = StringField("Religion")
    adresse = StringField("Adresse")
    submit = SubmitField("Ajouter L'élève")



class LoginUtilisateurForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    remember = BooleanField("Se souvenir de moi")
    submit = SubmitField("Se connecter")



class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(message="Saisissez l'adresse email"), Email(), Length(min=6, max=35)])
    submit = SubmitField('Demander la réinitialisation de mot de passe')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nouveau mot de passe',
                             validators=[DataRequired(message="Entrez le nouveau mot de passe"), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirmer le mot de passe',
                                     validators=[DataRequired('Confirmer le nouveau mot de passe'),
                                                 EqualTo('password')])
    submit = SubmitField('Réinitialiser le mot de passe')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    query = StringField("query", validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')




class profilForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    Submit = SubmitField('enregistrer')



class MessageForm(FlaskForm):
    recipient = StringField('To', validators=[DataRequired()])
    body = TextAreaField('Message', validators=[DataRequired(message='Entrez le corps du message '),
                                                Length(max=500, min=10)])
    submit = SubmitField('Send')


class ForumPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(message='Entrez le titre')])
    body = TextAreaField('Body', validators=[DataRequired
                                             (message='Entrez le corps du message'), Length(min=5, max=900)])
    submit = SubmitField('Post')


class AssignemntForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired
                                                           (message='Veuillez entrer un format valide ')])
    due_date = DateField('Due Date', validators=[DataRequired()])
    submit = SubmitField('Create Assignment')


class NoteForm(FlaskForm):
    student_id = SelectField('Étudiant', coerce=int, validators=[DataRequired()])
    matiere_id = SelectField('Matière', coerce=int, validators=[DataRequired()])
    assignment_id = StringField('ID du devoir', validators=[DataRequired()])
    note = FloatField('Note', validators=[DataRequired()])
    submit = SubmitField('Soumettre une note')


class NoteFilterForm(FlaskForm):
    """
    Formulaire pour filtrer les notes.
    """
    filter_by = SelectField(
        'Filtrer par',
        choices=[
            ('valeur', 'Valeur'),
            ('Student_id', 'ID Étudiant'),
            ('note', 'Note'),
            ('date', 'Date'),
            ('commentaire', 'Commentaire'),
            ('subject', 'Matière')
        ],
        validators=[DataRequired()]
    )

    filter_value = StringField(
        'Valeur du filtre',
        validators=[Optional()]
    )

    order = SelectField(
        'Ordre',
        choices=[('asc', 'Croissant'), ('desc', 'Décroissant')],
        validators=[DataRequired()]
    )

    submit = SubmitField('Filtrer')


class SchoolInfoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post Info')


class EditInfoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Update')


class AbsenceForm(FlaskForm):
    date = DateTimeField('Date et Heure', format='%Y-%m-%d %H %M',
                         validators=[DataRequired(message='Entrez un format valide la Date et Heure ')])
    reason = StringField("Raison d'absence", validators=[DataRequired(message='Ecris la raison en format texte')])
    submit = SubmitField('Ajouter Absence')


class ScheduleForm(FlaskForm):
    class_id = SelectField('Classe', coerce=int)
    subject = StringField('Sujet', validators=[DataRequired()])
    time_slot = StringField('Horaire', validators=[DataRequired()])
    submit = SubmitField('Soumettre')




class ReportForm(FlaskForm):
    report_type = SelectField('Report Type', choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'),
                                                      ('quarterly', 'Quarterly'), ('semi_annually', 'Semi-Annually'),
                                                      ('annually', 'Annually')], validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Generate Report')


class ReportFilterForm(FlaskForm):
    report_type = SelectField('Report Type', choices=[('all', 'All'), ('daily', 'Daily'), ('weekly', 'Weekly'),
                                                      ('monthly', 'Monthly'), ('quarterly', 'Quarterly'),
                                                      ('semi_annually', 'Semi-Annually'), ('annually', 'Annually')],
                              validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d')
    end_date = DateField('End Date', format='%Y-%m-%d')
    submit = SubmitField('Filter Reports')


class AssignmentForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    due_date = DateField('Date d\'échéance', format='%Y-%m-%d', validators=[DataRequired()])



class ChoiceForm(FlaskForm):
    choice_text = StringField('Choix', validators=[DataRequired(), Length(max=200)])


class PollForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired(), Length(max=200)])
    choices = FieldList(FormField(ChoiceForm), min_entries=2, max_entries=10, label='Choix')
    end_date = DateTimeField('Date de fin', format='%Y-%m-%d %H:%M', validators=[DataRequired()])


class NotificationForm(FlaskForm):
    filter_by = SelectField('Filtrer par', choices=[('due_date', 'Date d\'échéance'), ('title', 'Titre'), ('description', 'Description')])
    order = SelectField('Ordre', choices=[('asc', 'Ascendant'), ('desc', 'Descendant')])
    submit = SubmitField('Appliquer le Filtre')


class OptionForm(FlaskForm):
    name = StringField('Option Name', validators=[DataRequired(), Length(min=3, max=100)])



class ResendConfirmationForm(FlaskForm):
    email = StringField("Adresse email", validators=[DataRequired(), Email()])
    submit = SubmitField("Renvoyer le lien")
# signup


class SignupForm(FlaskForm):
    username = StringField(
        "Nom d'utilisateur",
        validators=[
            DataRequired(message="Le nom d'utilisateur est requis."),
            Length(min=3, max=50, message="Le nom d'utilisateur doit contenir entre 3 et 50 caractères.")
        ]
    )

    email = StringField(
        "Adresse email",
        validators=[
            DataRequired(message="L'adresse email est requise."),
            Email(message="Adresse email invalide."),
            Length(max=120)
        ]
    )

    password = PasswordField(
        "Mot de passe",
        validators=[
            DataRequired(message="Le mot de passe est requis."),
            Length(min=6, message="Le mot de passe doit contenir au moins 6 caractères.")
        ]
    )

    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        validators=[
            DataRequired(message="Veuillez confirmer votre mot de passe."),
            EqualTo('password', message="Les mots de passe ne correspondent pas.")
        ]
    )

    last_name = StringField(
        "Nom",
        validators=[
            DataRequired(message="Le nom est requis."),
            Length(min=2, max=50)
        ]
    )

    role = SelectField(
        "Rôle",
        choices=[
            ('enseignant', 'Enseignant'),
            ('eleve', 'Élève'),
            ('administrateur', 'Administrateur')
        ],
        validators=[DataRequired(message="Le rôle est requis.")]
    )

    specialite = StringField(
        "Spécialité",
        validators=[Optional(), Length(max=100)]
    )

    niveau = StringField(
        "Niveau",
        validators=[Optional(), Length(max=100)]
    )

    role_admin = StringField(
        "Rôle Administratif",
        validators=[Optional(), Length(max=100)]
    )

    submit = SubmitField("S'inscrire")



class ParentRegistrationForm(FlaskForm):
    name = StringField("Nom du parent", validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirmer le mot de passe", validators=[DataRequired(), EqualTo("password")])

    # Enfant 1
    child1_first_name = StringField("Prénom de l'enfant 1", validators=[Length(max=100), Optional()])
    child1_last_name = StringField("Nom de l'enfant 1", validators=[Length(max=100), Optional()])
    child1_birth_date = DateField("Date de naissance de l'enfant 1", format="%Y-%m-%d", validators=[Optional()])
    child1_class_id = IntegerField("Classe ID de l'enfant 1", validators=[Optional()])
    child1_religion = StringField("Religion de l'enfant 1", validators=[Length(max=20), Optional()])

    # Enfant 2 (optionnel)
    child2_first_name = StringField("Prénom de l'enfant 2 (optionnel)", validators=[Length(max=100), Optional()])
    child2_last_name = StringField("Nom de l'enfant 2 (optionnel)", validators=[Length(max=100), Optional()])
    child2_birth_date = DateField("Date de naissance de l'enfant 2", format="%Y-%m-%d", validators=[Optional()])
    child2_class_id = IntegerField("Classe ID de l'enfant 2", validators=[Optional()])
    child2_religion = StringField("Religion de l'enfant 2", validators=[Length(max=20), Optional()])

    submit = SubmitField("Créer le compte")

    def validate_email(self, field):
        existing_parent = Parent.query.filter_by(email=field.data.lower()).first()
        if existing_parent:
            raise ValidationError("Cet e-mail est déjà utilisé. Veuillez en choisir un autre.")



class ParentLoginForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(message="L'email est requis"),
        Email(message="Format de l'email invalide")
    ])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    remember = BooleanField("Se souvenir de moi")
    submit = SubmitField("Connexion")



"""class LoginparentForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired(), Length(min=5, max=30)])
    email = StringField('Email', validators=[DataRequired
                                             (message="L'email est requis"),
                                             Email(message="Format de l'email invalide"), Length(max=35, min=8,
                                                                                                 message="L'email "
                                                                                                         "n'est pas "
                                                                                                         "depassé 35 "
                                                                                                         "caractères.")]
                        )
    password = PasswordField('Mon de passe', validators=[DataRequired()])
    child_name_1 = StringField("Nom de l'enfant 1 ",
                               validators=[DataRequired(message="Le nom de l'enfant est requis")])
    child_name_2 = StringField("Nom de l'enfant 2",
                               validators=[DataRequired(
                                   message="Le nom de l'enfant 2 est requis"),
                                   Length(max=35, min=3, message="Le Nom de l'enfant n'est pas depasser 35 "
                                                                 "caractères ")])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Connexion ')


def validate_username(username):
    user = User.query.filter_by(username=username.data).first()
    if user:
        raise ValidationError('That username is taken. Please choose a different one.')


def validate_email(email):
    user = User.query.filter_by(email=email.data).first()
    if user:
        raise ValidationError('That email is taken. Please choose a different one.')"""