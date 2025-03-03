<script>
    function validateForm() {
        var montant = document.getElementById("montant").value;
        var date = document.getElementById("date").value;
        var isValid = true;

        // Réinitialiser les messages d'erreur
        $('.invalid-feedback').remove();
        $('.is-invalid').removeClass('is-invalid');

        // Validation du montant
        if (isNaN(montant) || montant <= 0) {
            isValid = false;
            $('#montant').addClass('is-invalid');
            $('#montant').after('<div class="invalid-feedback">Veuillez entrer un montant valide supérieur à 0.</div>');
        }

        // Validation de la date
        if (!date) {
            isValid = false;
            $('#date').addClass('is-invalid');
            $('#date').after('<div class="invalid-feedback">Veuillez sélectionner une date.</div>');
        }

        return isValid;
    }

    // Attacher la validation au formulaire
    $('form').on('submit', function(event) {
        if (!validateForm()) {
            event.preventDefault();
            toastr.error('Veuillez corriger les erreurs dans le formulaire.');
        }
    });
</script>
<script>
    $(document).ready(function() {
        $('#date').datepicker({
            format: 'yyyy-mm-dd',
            autoclose: true,
            todayHighlight: true
        });
    });
</script>
