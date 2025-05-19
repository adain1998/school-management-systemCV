document.addEventListener("DOMContentLoaded", function() {
  const form = document.querySelector('form');
  const studentNom = document.getElementById('student_nom');
  const montant = document.getElementById('montant');
  const status = document.getElementById('status');
  const description = document.getElementById('description');

  // Validation du formulaire
  form.addEventListener("submit", function(event) {
    event.preventDefault(); // Empêcher l'envoi immédiat du formulaire

    let errors = [];

    // Vérification du champ "Nom de l'élève"
    if (studentNom.value.trim() === "") {
      errors.push("Le nom de l'élève est requis.");
    }

    // Vérification du champ "Montant"
    if (montant.value.trim() === "" || parseFloat(montant.value) <= 0) {
      errors.push("Le montant doit être un nombre supérieur à zéro.");
    }

    // Vérification du champ "Statut"
    if (status.value.trim() === "") {
      errors.push("Le statut est requis.");
    }

    // Si des erreurs sont détectées, les afficher
    if (errors.length > 0) {
      errors.forEach(function(error) {
        toastr.error(error);
      });
    } else {
      // Si aucun problème, soumettre le formulaire
      form.submit();
    }
  });

  // Initialisation des messages Toastr
  toastr.options = {
    "closeButton": true,
    "progressBar": true,
    "positionClass": "toast-top-right",
    "timeOut": "5000"
  };

  // Affichage des messages flash de Flask (si présents)
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for category, message in messages %}
        {% if category == 'success' %}
          toastr.success("{{ message }}");
        {% elif category == 'error' %}
          toastr.error("{{ message }}");
        {% elif category == 'warning' %}
          toastr.warning("{{ message }}");
        {% else %}
          toastr.info("{{ message }}");
        {% endif %}
      {% endfor %}
    {% endif %}
  {% endwith %}
});
