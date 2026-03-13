// accueil.js

document.addEventListener('DOMContentLoaded', function () {
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

    // Gestion du bouton "Nouvelle Transaction"
    const newPaymentBtn = document.getElementById('new-payment-btn');
    if (newPaymentBtn) {
        newPaymentBtn.addEventListener('click', function (event) {
            event.preventDefault();
            toastr.success("Redirection vers la page de création d'un nouveau paiement.");
            setTimeout(() => {
                window.location.href = newPaymentBtn.href;
            }, 1000);
        });
    }

    // Gestion du bouton "Historique"
    const viewPaymentsBtn = document.getElementById('view-payments-btn');
    if (viewPaymentsBtn) {
        viewPaymentsBtn.addEventListener('click', function (event) {
            event.preventDefault();
            toastr.info("Redirection vers la page de consultation des paiements.");
            setTimeout(() => {
                window.location.href = viewPaymentsBtn.href;
            }, 1000);
        });
    }
});
