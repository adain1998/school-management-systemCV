import ast

def is_sqlalchemy_model(class_node):
    for base in class_node.bases:
        if isinstance(base, ast.Attribute) and base.attr == "Model":
            return True
        elif isinstance(base, ast.Name) and base.id == "Model":
            return True
    return False

def extract_model_classes(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        node = ast.parse(file.read())

    model_classes = [
        class_node.name
        for class_node in node.body
        if isinstance(class_node, ast.ClassDef) and is_sqlalchemy_model(class_node)
    ]
    return model_classes

# Exemple d’utilisation
if __name__ == "__main__":
    file_path = "app/models.py"  # Mets ici le bon chemin si besoin
    models = extract_model_classes(file_path)

    print("Classes SQLAlchemy détectées dans le fichier :")
    for i, cls in enumerate(models, 1):
        print(f"{i}. {cls}")
