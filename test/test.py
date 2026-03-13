def test_app_creation(app):
    """✅ Vérifie que l'application Flask est créée avec succès."""
    assert app is not None
    assert app.testing

def test_blueprints_registered(app):
    """✅ Vérifie que les principaux blueprints sont bien enregistrés."""
    expected_blueprints = [
        'blueprint_auth',
        'blueprint_connex',
        'blueprint_stud',
        'blueprint_niveau',
        'blueprint_opt'
    ]
    for bp_name in expected_blueprints:
        assert bp_name in app.blueprints, f"⚠️ Le blueprint '{bp_name}' n'est pas enregistré"

def test_routes_page_exist(client):
    """✅ Vérifie que la route /routes retourne un code 200."""
    response = client.get("/routes")
    assert response.status_code == 200
    assert b"Endpoint:" in response.data
