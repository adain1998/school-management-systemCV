import json

# Charger le fichier manifest.json
with open("static/manifest.json", "r", encoding="utf-8") as file:
    manifest_data = json.load(file)

# Écrire le fichier minifié
with open("static/manifest.min.json", "w", encoding="utf-8") as file:
    json.dump(manifest_data, file, separators=(',', ':'))
    print("✅ Fichier manifest.min.json généré avec succès.")
