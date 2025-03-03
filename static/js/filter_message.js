// messages.js

// Attendre que le DOM soit entièrement chargé
document.addEventListener('DOMContentLoaded', function () {
    // Vérifier s'il y a un message d'erreur
    const errorMessage = document.querySelector('.alert-danger');
    if (errorMessage) {
        // Afficher une notification d'erreur avec Toastr
        toastr.error(errorMessage.textContent.trim());
    }

    // Ajouter un écouteur d'événement sur le formulaire de filtrage
    const filterForm = document.querySelector('form');
    filterForm.addEventListener('submit', function (event) {
        const filterBy = document.getElementById('filter_by').value;
        const order = document.getElementById('order').value;

        // Vérifier si les champs de filtrage sont remplis
        if (!filterBy || !order) {
            event.preventDefault();
            toastr.warning('Veuillez sélectionner un critère de filtrage et un ordre.');
        }
    });
});
