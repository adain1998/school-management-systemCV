import requests
from app import create_app
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"
RESULT_FILE = "test_routes_result.txt"

def get_all_routes():
    """Récupère toutes les routes GET sans paramètres dynamiques."""
    app = create_app()
    routes = []
    with app.app_context():
        for rule in app.url_map.iter_rules():
            if "GET" in rule.methods and not rule.arguments:
                routes.append(str(rule))
    return routes

def test_routes():
    routes = get_all_routes()
    total = len(routes)
    success, failed = 0, 0
    log_lines = []

    log_lines.append(f"📅 Date du test : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_lines.append(f"🔍 Test de {total} routes GET sans arguments...\n")

    for route in routes:
        url = BASE_URL + route
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                line = f"[✅] {url} → OK"
                success += 1
            else:
                line = f"[❌] {url} → Code: {response.status_code}"
                failed += 1
        except requests.exceptions.RequestException as e:
            line = f"[💥] {url} → Exception: {type(e).__name__} - {e}"
            failed += 1

        print(line)
        log_lines.append(line)

    summary = [
        "\n🔚 Résumé des tests :",
        f"  ✅ Réussis : {success}",
        f"  ❌ Échecs  : {failed}",
        f"  🔢 Total   : {total}"
    ]

    print("\n".join(summary))
    log_lines.extend(summary)

    # Enregistrer dans le fichier texte
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print(f"\n📝 Résultats sauvegardés dans : {RESULT_FILE}")

if __name__ == "__main__":
    test_routes()
