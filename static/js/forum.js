// forum.js

// Attendre que le DOM soit entièrement chargé
document.addEventListener('DOMContentLoaded', function () {
    // Sélectionner tous les boutons de suppression
    var deleteButtons = document.querySelectorAll('.btn-danger');

    // Ajouter un écouteur d'événement sur chaque bouton de suppression
    deleteButtons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            // Empêcher la soumission immédiate du formulaire
            event.preventDefault();

            // Afficher une boîte de dialogue de confirmation
            var userConfirmed = confirm('Êtes-vous sûr de vouloir supprimer ce post ? Cette action est irréversible.');

            // Si l'utilisateur confirme, soumettre le formulaire
            if (userConfirmed) {
                button.closest('form').submit();
            }
        });
    });

    // Sélectionner le formulaire de création de post
    var postForm = document.querySelector('form');

    // Ajouter un écouteur d'événement sur la soumission du formulaire
    postForm.addEventListener('submit', function (event) {
        // Empêcher la soumission si les champs sont vides
        var title = document.getElementById('title').value.trim();
        var body = document.getElementById('body').value.trim();

        if (!title || !body) {
            event.preventDefault();
            alert('Veuillez remplir tous les champs avant de soumettre le formulaire.');
        }
    });
});
