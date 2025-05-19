import os
import re
import shutil
import sys

# 📁 Dossier contenant les templates HTML
TEMPLATES_DIR = os.path.join(os.getcwd(), 'templates')

# 📌 Dictionnaire des blueprints
BLUEPRINTS = {
    'sect': 'blueprint_sect',
    'examen': 'blueprint_examen',
    'rapport': 'blueprint_rapport',
    'stud': 'blueprint_stud',
    'application': 'blueprint_application',
    'paiem': 'blueprint_paiem',
    'opt': 'blueprint_opt',
    'resultat': 'blueprint_resultat',
    'mes': 'blueprint_mes',
    'paie': 'blueprint_paie',
    'meeting': 'blueprint_meeting',
    'niveau': 'blueprint_niveau',
    'absenc': 'blueprint_absenc',
    'auth': 'blueprint_auth',
    'tableau': 'blueprint_tableau',
    'connex': 'blueprint_connex'
}

# 🔍 Expression régulière pour détecter les appels url_for('blueprint.route')
pattern = re.compile(r"url_for\(\s*'(?P<bp>\w+)\.(?P<route>\w+)'\s*\)")

def process_file(filepath: str) -> None:
    """Modifie les appels url_for dans un fichier HTML."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"❌ Lecture échouée : {filepath} — {e}")
        return

    matches = pattern.findall(content)
    if not matches:
        print(f"➡️ Aucun appel url_for détecté dans {filepath}")
        return

    modified = False
    for bp, route in matches:
        if bp in BLUEPRINTS:
            old_call = f"url_for('{bp}.{route}')"
            new_call = f"url_for({BLUEPRINTS[bp]} + '.{route}')"
            if old_call in content and new_call not in content:
                content = content.replace(old_call, new_call)
                modified = True

    if modified:
        try:
            backup_path = filepath + '.bak'
            shutil.copy(filepath, backup_path)
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"✅ Modifié : {filepath} (→ backup : {backup_path})")
        except Exception as e:
            print(f"❌ Erreur écriture : {filepath} — {e}")
    else:
        print(f"✔️ Aucun changement requis : {filepath}")

def scan_templates() -> None:
    """Analyse tous les templates HTML pour appliquer les modifications."""
    if not os.path.exists(TEMPLATES_DIR):
        print(f"🚫 Dossier inexistant : {TEMPLATES_DIR}")
        return

    print("🔍 Début de l'analyse...\n")
    for root, _, files in os.walk(TEMPLATES_DIR):
        for filename in files:
            if filename.endswith('.html'):
                filepath = os.path.join(root, filename)
                process_file(filepath)
    print("\n🎯 Modification terminée.")

def restore_backups() -> None:
    """Restaure tous les fichiers .bak en écrasant les fichiers modifiés."""
    restored = 0
    for root, _, files in os.walk(TEMPLATES_DIR):
        for filename in files:
            if filename.endswith('.bak'):
                bak_path = os.path.join(root, filename)
                original_path = bak_path[:-4]  # retire '.bak'
                try:
                    shutil.copy(bak_path, original_path)
                    os.remove(bak_path)
                    print(f"♻️ Restauration : {original_path}")
                    restored += 1
                except Exception as e:
                    print(f"❌ Erreur restauration {bak_path} → {original_path} — {e}")
    if restored == 0:
        print("ℹ️ Aucun fichier .bak trouvé à restaurer.")
    else:
        print(f"\n✅ {restored} fichier(s) restauré(s) avec succès.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        print("♻️ Restauration des templates depuis les sauvegardes...\n")
        restore_backups()
    else:
        scan_templates()
