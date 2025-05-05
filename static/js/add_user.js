// Assurer que le DOM est prêt avant d'exécuter du code JavaScript
$(document).ready(function() {

    // Validation du formulaire d'ajout d'utilisateur
    $('form').on('submit', function(e) {
        var username = $('#username').val();
        var email = $('#email').val();
        var password = $('#password').val();
        var last_name = $('#last_name').val();

        // Vérifier si tous les champs obligatoires sont remplis
        if (!username || !email || !password || !last_name) {
            toastr["error"]("Tous les champs sont requis.");
            e.preventDefault();
        }

        // Vérification du mot de passe (au moins 6 caractères)
        if (password.length < 6) {
            toastr["warning"]("Le mot de passe doit comporter au moins 6 caractères.");
            e.preventDefault();
        }

        // Vérification de l'email (format valide)
        var emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailPattern.test(email)) {
            toastr["warning"]("Veuillez entrer un email valide.");
            e.preventDefault();
        }
    });

    // Afficher un message Toastr lors du clic sur le bouton "Ajouter Utilisateur"
    $('button[type="submit"]').on('click', function() {
        toastr["info"]("Chargement de l'utilisateur...");
    });
});
