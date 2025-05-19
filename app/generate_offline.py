from flask import Flask, render_template
import os

app = Flask(__name__, template_folder="app/templates")

@app.route("/generate-offline")
def generate_offline_file():
    html = render_template("offline.html")
    static_path = os.path.join("app", "static", "offline.html")
    with open(static_path, "w", encoding="utf-8") as f:
        f.write(html)
    return "Fichier offline.html généré dans /static."

if __name__ == "__main__":
    app.run(debug=True)
