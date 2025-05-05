// matieres.js
document.addEventListener('DOMContentLoaded', function () {
    // Initialisation de Toastr
    toastr.options = {
        "closeButton": true,
        "progressBar": true,
        "timeOut": "5000", // 5 secondes
        "extendedTimeOut": "1000", // 1 seconde d'extension après l'hover
        "positionClass": "toast-top-right", // Position en haut à droite
        "preventDuplicates": true,
        "newestOnTop": true,
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut",
        "showDuration": 300,
        "hideDuration": 300
    };

    // Exemple de message de succès
    if (document.querySelector('#succes-message')) {
        toastr.success('Les moyennes ont été calculées avec succès !');
    }

    // Exemple de message d'erreur
    if (document.querySelector('#error-message')) {
        toastr.error('Une erreur s\'est produite lors du calcul des moyennes.');
    }

    // Gestion des erreurs via Toastr
    const erreurs = document.querySelectorAll('.alert-danger li');
    if (erreurs.length > 0) {
        erreurs.forEach(function (erreur) {
            toastr.error(erreur.textContent);
        });
    }
});
