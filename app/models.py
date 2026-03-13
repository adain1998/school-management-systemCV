import uuid
import jwt
import pytz
from datetime import datetime, timedelta, timezone
from flask_login import UserMixin
# from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from app.Argon import PasswordHasher
from app.extensions import db
from flask import current_app

ph = PasswordHasher


class TokenManager:
    SECRET_KEY = 'adainkapangala1998'



# Modèle de base pour les utilisateurs
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password_hash = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    query = db.Column(db.String(255))
    last_name = db.Column(db.String(50), nullable=False)
    admin = db.Column(db.Boolean, default=False)  # Indique si un utilisateur est administrateur
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': role
    }

    def __init__(self, username, email, last_name, role, admin=False, password_hash=None, image_file='default.jpg',created_at=None):
        self.username = username
        self.email = email
        self.last_name = last_name
        self.role = role
        self.admin = admin
        self.password_hash=password_hash
        self.image_file=image_file
        self.created_at = created_at if created_at else datetime.now(timezone.utc)

    # Méthodes pour gérer le mot de passe
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Modèle pour l'Enseignant
class Enseignant(User):
    __tablename__ = 'enseignants'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    specialite = db.Column(db.String(120))

    __mapper_args__ = {
        'polymorphic_identity': 'enseignant',
    }

    def __init__(self, username, email, last_name, role, specialite=None):
        super().__init__(username=username, email=email, last_name=last_name, role=role)
        self.specialite = specialite

# Modèle pour l'Élève
class Eleve(User):
    __tablename__ = 'eleves'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    niveau = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'eleve',
    }

    def __init__(self, username, email, last_name, role, niveau=None):
        super().__init__(username=username, email=email, last_name=last_name, role=role)
        self.niveau = niveau

# Modèle pour l'Administrateur
class Administrateur(User):
    __tablename__ = 'administrateurs'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    role_admin = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'administrateur',
    }

    def __init__(self, username, email, last_name, role, role_admin=None):
        super().__init__(username=username, email=email, last_name=last_name, role=role)
        self.role_admin = role_admin



class Visitor(db.Model):
    __tablename__ = 'visitors'  # Nom de la table dans la base de données

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    visit_date = db.Column(db.DateTime, server_default=db.func.now())  # Date de visite



class Note(db.Model):
    __tablename__ = 'note'

    id = db.Column(db.Integer, primary_key=True)
    valeur = db.Column(db.Float, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(pytz.utc))
    commentaire = db.Column(db.Text)

    # Relations
    student = db.relationship('Student', back_populates='notes')
    matiere = db.relationship('Matiere', back_populates='notes')

    def __repr__(self):
        return f'<Note {self.id} - Valeur: {self.valeur}>'




class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.utc))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    presence = db.Column(db.Boolean, nullable=False)

    student = db.relationship('Student', back_populates='attendances')

    __table_args__ = (
        db.UniqueConstraint('student_id', 'date', name='unique_student_date'),
    )

    def __init__(self, student_id, presence, date=None):
        self.student_id = student_id
        self.presence = presence
        self.date = date if date else datetime.now(pytz.utc)


# Assure-toi que le modèle Student est correctement défini comme suit :

class Student(db.Model):
    __tablename__ = 'student'

    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    registration_date = db.Column(db.DateTime, default=lambda: datetime.now(pytz.utc), nullable=False)
    fees_paid = db.Column(db.Float, default=0.0)
    numero_matricule = db.Column(db.String(20), nullable=False, unique=True)
    class_id = db.Column(db.Integer, db.ForeignKey("classe.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=True)
    debt = db.Column(db.Float, default=0.0)
    religion = db.Column(db.String(20), nullable=True)

    # Relations
    parent = db.relationship("Parent", back_populates="students")
    notes = db.relationship('Note', back_populates='student', lazy=True, cascade="all, delete-orphan")
    absences = db.relationship('Absence', back_populates='student', lazy=True, cascade="all, delete-orphan")
    attendances = db.relationship('Attendance', back_populates='student', lazy=True, cascade="all, delete-orphan")

    # 🔄 Nouvelle relation avec StudentAssignment
    student_assignments = db.relationship("StudentAssignment", back_populates="student", cascade="all, delete-orphan")

    # Classe (Many-to-One)
    classe = db.relationship('Classe', back_populates='students')
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'))
    section = db.relationship('Sections', back_populates='students')

    # Relations Many-to-Many avec Sections et Options
    # sections = db.relationship('Sections', secondary='students_sections', backref='students')
    options = db.relationship('Option', secondary='students_options', back_populates='students')

    def __init__(self, last_name, first_name, date_naissance, numero_matricule, class_id, parent_id, fees_paid=0.0, debt=0.0, religion=None):
        self.last_name = last_name
        self.first_name = first_name
        self.date_naissance = date_naissance
        self.registration_date = datetime.now(pytz.utc)
        self.numero_matricule = numero_matricule
        self.class_id = class_id
        self.parent_id = parent_id
        self.fees_paid = fees_paid
        self.debt = debt
        self.religion = religion

    def __repr__(self):
        return f'<Student {self.first_name} {self.last_name}>'

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def avg_grade(self) -> float:
        notes = self.notes or []
        if isinstance(notes, list) and notes:
            return round(sum(note.note for note in notes) / len(notes), 2)
        return 0.0

    @property
    def attendance_rate(self) -> float:
        absences = self.absences or []
        presences = self.attendances or []
        total_days = len(absences) + len(presences)
        return round((len(presences) / total_days) * 100, 2) if total_days > 0 else 0

    @property
    def absences_count(self):
        return len(self.absences or [])

    @property
    def completed_assignments(self) -> int:
        sas = self.student_assignments or []
        return sum(1 for sa in sas if sa.completed)


    @property
    def total_assignments(self) -> int:
        sas = self.student_assignments or []
        return len(sas)


class Classe(db.Model):
    __tablename__ = 'classe'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    matieres = db.relationship('Matiere', back_populates='classe', lazy='dynamic', cascade="all, delete-orphan")
    # Relation avec Student
    students = db.relationship('Student', back_populates='classe')

    def __repr__(self):
        return f'<Classe {self.name}>'


class Option(db.Model):
    __tablename__ = 'option'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)

    # Relation many-to-many avec Student via la table de liaison students_options
    students = db.relationship('Student', secondary='students_options', back_populates='options')
    matieres = db.relationship('Matiere', back_populates='option', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Option {self.nom}>'

class Sections(db.Model):
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    matieres = db.relationship('Matiere', back_populates='section', lazy='dynamic', cascade="all, delete-orphan")
    students = db.relationship('Student', back_populates='section')

    # Relation many-to-many avec Student via la table de liaison students_sections
    # students = db.relationship('Student', secondary='students_sections', backref='sections')

    # students = db.relationship('Student', secondary='students_sections', backref='sections')


    def __repr__(self):
        return f'<Section {self.name}>'

# Table de liaison pour les étudiants et leurs sections
students_sections = db.Table('students_sections',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('section_id', db.Integer, db.ForeignKey('sections.id'), primary_key=True)
)

# Table de liaison pour les étudiants et leurs options
students_options = db.Table('students_options',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('option_id', db.Integer, db.ForeignKey('option.id'), primary_key=True)
)

# Table de liaison pour les étudiants et leurs classes
students_classes = db.Table('students_classes',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('classe_id', db.Integer, db.ForeignKey('classe.id'), primary_key=True)
)


class Matiere(db.Model):
    __tablename__ = 'matieres'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)

    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classe.id'), nullable=False)  # Assurez-vous que __tablename__ = 'classe'
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=True)

    # Relations explicites
    teacher = db.relationship('Teacher', back_populates='matieres')
    classe = db.relationship('Classe', back_populates='matieres')
    section = db.relationship('Sections', back_populates='matieres')
    option = db.relationship('Option', back_populates='matieres')

    notes = db.relationship('Note', back_populates='matiere', lazy='dynamic', cascade="all, delete-orphan")
    assignments = db.relationship('Assignment', back_populates='matiere', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        prof = self.teacher.nom if self.teacher else "Inconnu"
        classe_nom = self.classe.nom if self.classe else "Inconnue"
        return f"<Matiere {self.nom} - Prof: {prof} - Classe: {classe_nom}>"



class Frais(db.Model):
    __tablename__ = 'frais'
    id = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateur_id'), nullable=False)
    user = db.relationship('User', backref='frais', lazy=True)
    paiement = db.relationship('Payment', backref='frais', lazy=True)
    student = db.relationship('Student', back_populates='Frais')

    def __repr__(self):
        return f'<Frais {self.id} {self.montant}{self.description}{self.user_id}{self.user}{self.paiement} >'



class Payment(db.Model):
    __tablename__ = 'Payment'
    id = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), index=True, default=datetime.now(pytz.utc))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    frais_id = db.Column(db.Integer, db.ForeignKey('frais.id'), nullable=False)
    frais = db.relationship('Frais', backref='payments')
    db.relationship('student', backref="payment", lazy=True)
    mois = db.Column(db.String(20), nullable=False)
    annee = db.Column(db.Integer, nullable=False)
    statut = db.Column(db.Enum('en attente', 'payé', 'annulé'))  # EX de statut de paiement
    student = db.relationship('Student', back_populates='payment')

    def __repr__(self):
        return (f'<Payment {self.id} {self.montant}{self.date}{self.timestamp}{self.frais}'
                f'{self.frais_id}{self.student_id}{self.mois}{self.annee}{self.statut}{self.student} >')



class Installment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    date_paid = db.Column(db.Date)
    payment_method = db.Column(db.String(50))  # Ex: "Espèces", "Mobile Money", "Banque", etc

    payment = db.relationship('Payment', backref=db.backref('installments', lazy=True))



class Absence(db.Model):
    __tablename__ = 'Absence'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(100), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    student = db.relationship('Student', back_populates='absences')

    def __repr__(self):
        return f'<Absence {self.id}{self.date}{self.reason}{self.student_id}{self.student} >'


# Add more models for Finance, Schedule, etc.

class Finance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fee_type = db.Column(db.String(50), nullable=False)  # Type de frais (ex : frais scolaire, frais d'inscription, etc.)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.utc))
    description = db.Column(db.String(100))


def utc_now():
    return datetime.now(pytz.utc)



class Report(db.Model):
    __tablename__ = 'Report'
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False)  # Type de rapport (ex : journalier, mensuel, etc.)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    generated_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    def __repr__(self):
        return (f'<Report {self.id} {self.report_type} {self.start_date} {self.end_date} '
                f'{self.total_amount} {self.generated_at}>')



class Message(db.Model):
    __tablename__ = 'Message'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now(pytz.utc))
    email = db.Column(db.String(120), nullable=False)
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')

    def __repr__(self):
        return f'<Message {self.id}{self.sender_id}{self.recipient_id}{self.body}{self.timestamp} >'



class ForumPost(db.Model):
    __tablename__ = 'ForumPost'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='forum_posts')  # 👈 important pour afficher l’auteur
    title = db.Column(db.String(140))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now(pytz.utc))

    def __repr__(self):
        return f'<ForumPost {self.id}{self.user_id}{self.title}{self.body}{self.timestamp} >'



class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    reaction_type = db.Column(db.String(20), nullable=False)  # like, love, haha, wow, sad, angry
    timestamp = db.Column(db.DateTime, default=datetime.now(pytz.utc))
    user = db.relationship('User', backref='reactions')
    post = db.relationship('Post', backref='reactions')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_reaction'),
    )


class Post(db.Model):
    __tablename__ = 'Post'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User_id'))
    content = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Post {self.id}{self.user_id}{self.content} >'

# ============================
# Assignment Model
# ============================
class Assignment(db.Model):
    __tablename__ = 'assignment'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Référence à l'enseignant
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.String(140), nullable=True)
    due_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.utc), nullable=False)

    # Relation avec les liaisons élèves-devoirs
    student_assignments = db.relationship("StudentAssignment", back_populates="assignment", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Assignment {self.id} "{self.title}" by Teacher {self.teacher_id}>'

# ============================
# Table de jonction pour Many-to-Many
# Table de jonction enrichie
# ============================
class StudentAssignment(db.Model):
    __tablename__ = 'students_assignments'

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), primary_key=True)
    completed = db.Column(db.Boolean, default=False)
    submission_date = db.Column(db.DateTime, nullable=True)

    # Relations explicites pour navigation
    student = db.relationship("Student", back_populates="student_assignments")
    assignment = db.relationship("Assignment", back_populates="student_assignments")

    def __repr__(self):
        return (f"<StudentAssignment student_id={self.student_id} "
                f"assignment_id={self.assignment_id} completed={self.completed} "
                f"submission_date={self.submission_date}>")



class Notification(db.Model):
    __tablename__ = 'Notification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime(timezone=True), index=True, default=datetime.now(pytz.utc))

    def __repr__(self):
        return f'<Notification {self.id}{self.user_id}{self.message}{self.timestamp} >'



class SchoolInfo(db.Model):
    __tablename__ = 'SchoolInfo'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    content = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime(timezone=True), index=True, default=datetime.now(pytz.utc))

    def __repr__(self):
        return f'<SchoolInfo {self.id}{self.title}{self.content}{self.timestamp.isoformat()} >'



class Teacher(db.Model):
    __tablename__ = 'Teacher'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(pytz.utc))
    matieres = db.relationship('Matiere', back_populates='teacher', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Teacher{self.id}{self.name}{self.subject} >'



class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    choices = db.relationship('Choice', backref='poll', lazy=True, cascade="all, delete-orphan")

    def __init__(self, question, end_date):
        self.question = question
        self.end_date = end_date



class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    choice_text = db.Column(db.String(200), nullable=False)
    votes = db.Column(db.Integer, default=0)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)



class Parent(UserMixin, db.Model):
    __tablename__ = 'parent'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)  # Retire unique si pas nécessaire
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    confirmation_token = db.Column(db.String(36), nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)

    students = db.relationship("Student", back_populates="parent")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_confirmation_token(self):
        self.confirmation_token = str(uuid.uuid4())
        self.token_expiration = datetime.now(pytz.utc) + timedelta(hours=24)

    @staticmethod
    def generate_confirmation_token(email):
        unique_id = str(uuid.uuid4())
        expiration = datetime.now(pytz.utc) + timedelta(days=1)
        payload = {'confirm': email, 'id': unique_id, 'exp': expiration}
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return token

    @staticmethod
    def verify_confirmation_token(token):
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload['confirm'], payload['id']
        except jwt.ExpiredSignatureError:
            return None, None
        except jwt.InvalidTokenError:
            return None, None

    def __repr__(self):
        return f'<Parent {self.name} {self.email}>'

# Example of querying the Parent's model
# Assuming you're trying to get all parents in a route or function
# parents = Parents.query.all()

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('Classe_id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    time_slot = db.Column(db.DateTime(50), nullable=False)


def __repr__(self):
    return f'Event {self.id}{self.class_id} {self.subject}, time_slot: {self.time_slot.isoformat()}'


def get_time_slot(self):
    return self.time_slot.isoformat()



class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)


def create_tables():
    db.create_all()




    """class User_Parent(UserMixin, db.Model):
    __tablename__ = 'user_parents'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    child_name_1 = db.Column(db.String(100), nullable=True)
    child_name_2 = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(10), default='parent')

    confirmation_token = db.Column(db.String(128), nullable=True)
    confirmed_at = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_confirmation_token(self, expires_in=3600):
        #Génère un token JWT pour confirmation d'email.
        payload = {
            'confirm_email': self.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        self.confirmation_token = token
        return token

    def confirm(self, token):
        #Valide le token de confirmation.
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            if payload.get('confirm_email') != self.id:
                return False
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

        self.confirmed_at = datetime.datetime.utcnow()
        self.confirmation_token = None
        return True

    def __repr__(self):
        return f"<Parent {self.email}>"""
