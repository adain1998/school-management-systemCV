
document.addEventListener("DOMContentLoaded", function() {
    // Confirmation avant la suppression d'une absence
    const deleteForms = document.querySelectorAll('form[action*="delete"]');

    deleteForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const confirmation = confirm("Êtes-vous sûr de vouloir supprimer cette absence ?");
            if (!confirmation) {
                event.preventDefault(); // Empêche l'envoi du formulaire
            }
        });
    });

    // Validation dynamique des formulaires (par exemple, vérifier que le champ raison n'est pas vide)
    const absenceForm = document.querySelector('form');

    if (absenceForm) {
        absenceForm.addEventListener('submit', function(event) {
            const reasonInput = document.querySelector('input[name="reason"]');
            if (reasonInput.value.trim() === '') {
                alert("Le champ 'Raison' ne peut pas être vide.");
                event.preventDefault(); // Empêche l'envoi du formulaire
            }
        });
    }
});


