// acceuil.js

// Attendre que le DOM soit entièrement chargé
document.addEventListener('DOMContentLoaded', function () {
    // Sélectionner les boutons
    var newPaymentButton = document.querySelector('.btn-primary');
    var viewPaymentsButton = document.querySelector('.btn-secondary');

    // Ajouter un effet de clic sur le bouton "Nouveau Paiement"
    newPaymentButton.addEventListener('click', function () {
        alert('Redirection vers la page de création d\'un nouveau paiement.');
    });

    // Ajouter un effet de clic sur le bouton "Voir les Paiements"
    viewPaymentsButton.addEventListener('click', function () {
        alert('Redirection vers la page de consultation des paiements.');
    });
});
// acceuil.js

// Configuration globale de Toastr
toastr.options = {
    "closeButton": true, // Affiche un bouton de fermeture
    "debug": false,
    "newestOnTop": true,
    "progressBar": true, // Affiche une barre de progression
    "positionClass": "toast-top-right", // Position en haut à droite
    "preventDuplicates": true, // Empêche les doublons
    "onclick": null,
    "showDuration": "300", // Durée de l'animation d'affichage
    "hideDuration": "1000", // Durée de l'animation de fermeture
    "timeOut": "5000", // Durée d'affichage
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
};

// Exemple d'utilisation de Toastr lors du clic sur "Nouveau Paiement"
document.getElementById('new-payment-btn').addEventListener('click', function(event) {
    event.preventDefault(); // Empêche la redirection immédiate
    toastr.success('Redirection vers la page de création d\'un nouveau paiement.');
    // Redirection après un court délai pour permettre l'affichage de la notification
    setTimeout(function() {
        window.location.href = event.target.href;
    }, 1000);
});

// Exemple d'utilisation de Toastr lors du clic sur "Voir les Paiements"
document.getElementById('view-payments-btn').addEventListener('click', function(event) {
    event.preventDefault();
    toastr.info('Redirection vers la page de consultation des paiements.');
    setTimeout(function() {
        window.location.href = event.target.href;
    }, 1000);
});
