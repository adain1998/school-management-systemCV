// gestion_paiements.js

document.addEventListener('DOMContentLoaded', function() {
    // Fonction pour afficher une notification Toastr
    function showNotification(type, message) {
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
        toastr[type](message);
    }

    // Gestionnaire d'événement pour le bouton "Mettre à Jour"
    const updateButtons = document.querySelectorAll('.btn-primary');
    updateButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const paymentId = this.getAttribute('data-payment-id');
            // Logique pour mettre à jour le paiement
            // Par exemple, redirection vers une page de mise à jour
            window.location.href = `/update_payment/${paymentId}`;
        });
    });

    // Gestionnaire d'événement pour le bouton "Paiements Échelonnés"
    const installmentButtons = document.querySelectorAll('.btn-secondary');
    installmentButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const paymentId = this.getAttribute('data-payment-id');
            // Logique pour gérer les paiements échelonnés
            // Par exemple, redirection vers une page de détails des paiements échelonnés
            window.location.href = `/payment_installments/${paymentId}`;
        });
    });

    // Exemple de notification au chargement de la page
    showNotification('success', 'Bienvenue sur la page de gestion des paiements.');
});
