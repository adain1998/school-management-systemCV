// payment.js

$(document).ready(function() {
    // Configuration globale de Toastr
    toastr.options = {
        "closeButton": true,
        "progressBar": true,
        "positionClass": "toast-top-right",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
    };

    // Validation du formulaire lors de la soumission
    $('#paymentForm').on('submit', function(event) {
        // Empêcher la soumission du formulaire
        event.preventDefault();

        // Réinitialiser les messages d'erreur
        $('.invalid-feedback').hide();
        $('.form-control').removeClass('is-invalid');

        // Variables de validation
        let isValid = true;
        let montant = $('#montant').val().trim();
        let date = $('#date').val().trim();
        let studentId = $('#student_id').val().trim();
        let fraisId = $('#frais_id').val().trim();
        let mois = $('#mois').val().trim();
        let annee = $('#annee').val().trim();
        let statut = $('#statut').val().trim();

        // Validation du montant
        if (montant === '' || isNaN(montant) || parseFloat(montant) <= 0) {
            isValid = false;
            $('#montant').addClass('is-invalid');
            $('#montant').next('.invalid-feedback').text('Veuillez saisir un montant valide.').show();
        }

        // Validation de la date
        if (date === '') {
            isValid = false;
            $('#date').addClass('is-invalid');
            $('#date').next('.invalid-feedback').text('Veuillez sélectionner une date valide.').show();
        }

        // Validation de l'ID étudiant
        if (studentId === '') {
            isValid = false;
            $('#student_id').addClass('is-invalid');
            $('#student_id').next('.invalid-feedback').text('Veuillez sélectionner un étudiant.').show();
        }

        // Validation de l'ID frais
        if (fraisId === '') {
            isValid = false;
            $('#frais_id').addClass('is-invalid');
            $('#frais_id').next('.invalid-feedback').text('Veuillez sélectionner un type de frais.').show();
        }

        // Validation du mois
        if (mois === '') {
            isValid = false;
            $('#mois').addClass('is-invalid');
            $('#mois').next('.invalid-feedback').text('Veuillez saisir le mois concerné.').show();
        }

        // Validation de l'année
        if (annee === '' || isNaN(annee) || parseInt(annee) <= 0) {
            isValid = false;
            $('#annee').addClass('is-invalid');
            $('#annee').next('.invalid-feedback').text('Veuillez saisir une année valide.').show();
        }

        // Validation du statut
        if (statut === '') {
            isValid = false;
            $('#statut').addClass('is-invalid');
            $('#statut').next('.invalid-feedback').text('Veuillez sélectionner le statut du paiement.').show();
        }

        // Si le formulaire est valide, soumettre le formulaire
        if (isValid) {
            this.submit();
        } else {
            toastr.error('Veuillez corriger les erreurs dans le formulaire avant de soumettre.', 'Erreur de validation');
        }
    });
});
