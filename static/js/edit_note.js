// edit_note.js

$(document).ready(function() {
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
    $('#note-form').submit(function(event) {
        var score = $('#score').val();
        var errorMessage = $('#error-message');

        // Réinitialiser le message d'erreur
        errorMessage.hide().text('');

        // Vérifier si la note est un nombre entre 0 et 100
        if (isNaN(score) || score < 0 || score > 100) {
            errorMessage.text('La note doit être un nombre entre 0 et 100.').show();
            event.preventDefault();
            toastr.error('Erreur : La note doit être entre 0 et 100.', 'Erreur de validation');
        } else {
            toastr.success('La note a été mise à jour avec succès.', 'Succès');
        }
    });
});
