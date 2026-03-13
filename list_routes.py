from flask import Flask
from app import create_app

app = create_app()


def list_routes(flask_app, save_to_file=True):
    output = []
    for rule in flask_app.url_map.iter_rules():
        if "static" in rule.endpoint:
            continue
        methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        route = {
            'endpoint': rule.endpoint,
            'methods': methods,
            'rule': str(rule)
        }
        output.append(route)

    output.sort(key=lambda x: x['rule'])

    formatted_lines = []
    for route in output:
        line = f"{route['methods']:15s} | {route['rule']:40s} --> {route['endpoint']}"
        print(line)
        formatted_lines.append(line)

    if save_to_file:
        with open("routes.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(formatted_lines))
        print("\n✅ Fichier 'routes.txt' généré avec succès.")

if __name__ == '__main__':
    with app.app_context():
        list_routes(app)
