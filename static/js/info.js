// info.js

// Attendre que le DOM soit entièrement chargé
document.addEventListener('DOMContentLoaded', function () {
    // Sélectionner le formulaire à valider
    var form = document.querySelector('.needs-validation');

    // Ajouter un écouteur d'événement sur la soumission du formulaire
    form.addEventListener('submit', function (event) {
        // Si le formulaire n'est pas valide
        if (!form.checkValidity()) {
            // Empêcher la soumission du formulaire
            event.preventDefault();
            event.stopPropagation();
        }

        // Ajouter la classe 'was-validated' pour activer les styles de validation de Bootstrap
        form.classList.add('was-validated');
    }, false);
});
