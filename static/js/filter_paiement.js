// filter_paiement.js

$(document).ready(function() {
    // Configuration globale de Toastr
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

    // Exemple d'utilisation de Toastr pour afficher un message de succès
    $('#someButton').click(function() {
        toastr.success('Opération réussie !', 'Succès');
    });

    // Exemple d'utilisation de Toastr pour afficher un message d'erreur
    $('#anotherButton').click(function() {
        toastr.error('Une erreur est survenue.', 'Erreur');
    });

    // Vous pouvez ajouter d'autres notifications selon les actions de l'utilisateur
});
