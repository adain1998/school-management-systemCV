School Management System
Projet développé intégralement par François KAMPANGALA WA SHEMA 
dans le cadre de la digitalisation complète de la gestion scolaire.
PrésentationSchool Management System est une plateforme web complète développée en Python/Flask, conçue pour digitaliser et centraliser l'ensemble des opérations administratives, académiques et financières d'un établissement scolaire.
Objectifs du ProjetAutomatiser les processus administratifs scolaires.Centraliser les données académiques et financières.
Réduire les tâches manuelles et les erreurs de gestion.Faciliter le suivi des élèves et des performances scolaires.
Fournir des outils d'aide à la décision grâce aux rapports et statistiques.
Fonctionnalités Principales
Gestion AcadémiqueGestion des élèves, des classes, des options/filières et des enseignants.Gestion complète des horaires, examens, notes et performances scolaires.Suivi quotidien des absences et des présences.
Gestion FinancièreGestion des frais scolaires et des paiements.Rapports financiers détaillés et suivi des soldes des élèves.
Communication & Reporting
Messagerie interne, forum scolaire et notifications système.Génération de documents administratifs et exportation de données.Statistiques académiques et financières.
Sécurité et Bonnes PratiquesAuthentification sécurisée avec Argon2 (chiffrement des mots de passe).Gestion fine des rôles et permissions (RBAC).
Séparation des responsabilités via Blueprints.Architecture modulaire et maintenable.
Architecture du ProjetPlaintextschool-management-system/
├── app/
│   ├── schemas/services/utils/
│   ├── authentication.py, models.py, forms.py, context.py, decorators.py
│   ├── Gestion_des_classes.py, Gestion_des_notes.py, Gestion_des_absences.py
│   ├── Gestion_des_paiements.py, Gestion_des_frais.py, Gestion_des_messages.py
│   ├── Gestion_des_forum.py, gestion_exams.py, gestion_des_performances.py
│   └── horaires_blueprint.py
├── migrations/instance/static/templates/
├── requirements.txt, config.py, run.py
└── README.md
🛠 Technologies UtiliséesBackend : Python 3.x, Flask, Flask Blueprint, Flask-WTF, 
Flask-Login, Flask-Migrate, SQLAlchemy.Base de Données : MySQL.Sécurité :
Argon2, Gestion des sessions.Frontend : HTML5, CSS3, JavaScript, Bootstrap.
⚙️ InstallationCloner le dépôt : git clone https://github.com/adain1998/school-management-systemCV/edit/main/README.md
Créer l'environnement virtuel :
python -m venv venvActiver l'environnement : source venv/bin/activate (Linux/Mac)
ou venv\Scripts\activate (Windows)
Installer les dépendances : pip install -r requirements.txt
Configurer la base de données : DATABASE_URL=mysql://user:password@localhost/school_management
Lancer les migrations et l'application : flask db upgrade puis python run.py
 Profils UtilisateursLe système prend en charge : Administrateur, Direction, Enseignant, Comptable, Secrétariat, Élève, Parent.
 📈 Modules DisponiblesModuleDescriptionGestion des élèves
 Administration des dossiers scolaires
 Gestion des classesOrganisation académique
 Gestion des présences/absences
 Suivi quotidien et contrôleGestion des notes/examens
 Enregistrement, calcul et évaluationGestion financièrePaiements et frais scolaires
 Forum & MessagerieCollaboration et communication interne
 AuteurFrançois KAMPANGALA WA SHEMAAnalyste de Données Opérationnelles | Développeur & Architecte Solutions IT📍 Kolwezi, RDC
 📧 adainkapangala1998@gmail.com / shemaadain055@gmail.com
 📱 +243 973 987 886 / +243 819 249 752
 Ce projet démontre mes compétences en : Python/Flask, Architecture logicielle, MySQL, Authentification/Sécurité, Gestion des rôles, Développement Full Stack, Gestion de projet logiciel, Analyse et modélisation des processus métiers.
 📄 Licence : Ce projet est développé à des fins professionnelles. Toute utilisation commerciale doit faire l'objet d'une autorisation préalable.
