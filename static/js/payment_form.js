// payment_form.js

$(document).ready(function() {
    // Configuration globale de Toastr
    toastr.options = {
        "closeButton": true,
        "progressBar": true,
        "positionClass": "toast-top-right",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
    };

    // Validation du formulaire Bootstrap
    var form = document.getElementById('paymentForm');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        event.stopPropagation();
        if (form.checkValidity() === true) {
            // Soumission du formulaire si valide
            form.submit();
        } else {
            // Affichage des messages d'erreur pour les champs invalides
            $(form).addClass('was-validated');
            toastr.error('Veuillez corriger les erreurs dans le formulaire avant de soumettre.', 'Erreur de validation');
        }
    }, false);
});
