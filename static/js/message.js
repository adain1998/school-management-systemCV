// message.js

// Attendre que le DOM soit entièrement chargé
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

    // Vérifier si un message flash est présent et afficher la notification correspondante
    const flashMessage = document.getElementById('flash-message');
    if (flashMessage) {
        const messageType = flashMessage.dataset.category;
        const messageText = flashMessage.textContent;
        switch (messageType) {
            case 'success':
                toastr.success(messageText);
                break;
            case 'error':
                toastr.error(messageText);
                break;
            case 'info':
                toastr.info(messageText);
                break;
            case 'warning':
                toastr.warning(messageText);
                break;
            default:
                toastr.info(messageText);
        }
    }

    // Validation du formulaire avant soumission
    const messageForm = document.querySelector('form');
    messageForm.addEventListener('submit', function (event) {
        const recipient = document.getElementById('recipient').value.trim();
        const body = document.getElementById('body').value.trim();

        if (!recipient || !body) {
            event.preventDefault();
            toastr.error('Veuillez remplir tous les champs avant de soumettre le formulaire.');
        }
    });
});
