document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    form.addEventListener('submit', function(event) {
        // Exemple de validation : vérifier que le montant est positif
        const montant = document.querySelector('input[name="montant"]');
        if (montant && parseFloat(montant.value) <= 0) {
            event.preventDefault();
            toastr.error('Le montant doit être supérieur à zéro.');
            montant.focus();
        }

        // Ajouter d'autres validations personnalisées ici
    });
});
