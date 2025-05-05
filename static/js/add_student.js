// Utilisation de Toastr pour les messages flash
document.addEventListener("DOMContentLoaded", function() {
  // Si le formulaire est soumis, afficher les messages appropriés avec Toastr
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for category, message in messages %}
        // Utilisation de Toastr pour afficher les messages en fonction de leur catégorie
        if (category === 'success') {
          toastr.success('{{ message }}', 'Succès');
        } else if (category === 'danger') {
          toastr.error('{{ message }}', 'Erreur');
        } else {
          toastr.info('{{ message }}', 'Info');
        }
      {% endfor %}
    {% endif %}
  {% endwith %}

  // Validation du formulaire
  const form = document.querySelector('form');
  form.addEventListener('submit', function(event) {
    let valid = true;

    // Validation des champs obligatoires
    const requiredFields = document.querySelectorAll('input[required], select[required]');
    requiredFields.forEach(field => {
      if (!field.value.trim()) {
        valid = false;
        field.classList.add('is-invalid');
        toastr.warning('Veuillez remplir tous les champs obligatoires.', 'Attention');
      } else {
        field.classList.remove('is-invalid');
      }
    });

    // Empêche la soumission si des champs sont invalides
    if (!valid) {
      event.preventDefault();
    }
  });
});

// Initialisation de Toastr
toastr.options = {
  "closeButton": true,
  "debug": false,
  "newestOnTop": true,
  "progressBar": true,
  "positionClass": "toast-top-right",
  "preventDuplicates": true,
  "onclick": null,
  "showDuration": "300",
  "hideDuration": "1000",
  "timeOut": "5000",
  "extendedTimeOut": "1000",
  "showEasing": "swing",
  "hideEasing": "linear",
  "showMethod": "fadeIn",
  "hideMethod": "fadeOut"
};
