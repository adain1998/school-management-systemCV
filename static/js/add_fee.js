// add_fee.js

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
    $('#add-fee-form').on('submit', function (event) {
        let isValid = true;

        // Réinitialiser les messages d'erreur
        $('.form-control').removeClass('is-invalid');
        $('.invalid-feedback').remove();

        // Vérifier le type de frais
        const feeType = $('#fee_type').val().trim();
        if (feeType === '') {
            isValid = false;
            $('#fee_type').addClass('is-invalid');
            $('#fee_type').after('<div class="invalid-feedback">Le type de frais est obligatoire.</div>');
        }

        // Vérifier le montant
        const amount = $('#amount').val().trim();
        if (amount === '' || isNaN(amount) || parseFloat(amount) <= 0) {
            isValid = false;
            $('#amount').addClass('is-invalid');
            $('#amount').after('<div class="invalid-feedback">Veuillez entrer un montant valide supérieur à zéro.</div>');
        }

        // Si le formulaire n'est pas valide, empêcher la soumission
        if (!isValid) {
            event.preventDefault();
            toastr.error('Veuillez corriger les erreurs avant de soumettre le formulaire.', 'Erreur de validation');
        } else {
            // Afficher une notification de succès
            toastr.success('Les frais ont été ajoutés avec succès.', 'Succès');
        }
    });
});
