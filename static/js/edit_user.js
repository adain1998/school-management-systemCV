// edit_user.js

$(document).ready(function () {
    // Configuration globale de Toastr
    toastr.options = {
        "closeButton": true,
        "progressBar": true,
        "positionClass": "toast-top-right",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    };

    // Validation du formulaire avant soumission
    $('#edit-user-form').on('submit', function (event) {
        let isValid = true;

        // Réinitialiser les messages d'erreur
        $('.form-control').removeClass('is-invalid');
        $('.invalid-feedback').remove();

        // Vérifier le nom d'utilisateur
        const username = $('#username').val().trim();
        if (username === '') {
            isValid = false;
            $('#username').addClass('is-invalid');
            $('#username').after('<div class="invalid-feedback">Le nom d\'utilisateur est obligatoire.</div>');
        }

        // Vérifier l'email
        const email = $('#email').val().trim();
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$/;
        if (email === '') {
            isValid = false;
            $('#email').addClass('is-invalid');
            $('#email').after('<div class="invalid-feedback">L\'adresse e-mail
::contentReference[oaicite:0]{index=0}

