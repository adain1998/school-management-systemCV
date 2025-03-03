// edit_post.js

// Attendre que le DOM soit entièrement chargé
$(document).ready(function () {
    // Initialiser la validation du formulaire
    $("form").validate({
        // Définir les règles de validation
        rules: {
            title: {
                required: true,
                minlength: 5,
                maxlength: 100
            },
            body: {
                required: true,
                minlength: 20
            }
        },
        // Définir les messages d'erreur personnalisés
        messages: {
            title: {
                required: "Le titre est obligatoire.",
                minlength: "Le titre doit comporter au moins 5 caractères.",
                maxlength: "Le titre ne peut pas dépasser 100 caractères."
            },
            body: {
                required: "Le contenu est obligatoire.",
                minlength: "Le contenu doit comporter au moins 20 caractères."
            }
        },
        // Gérer la soumission du formulaire après validation réussie
        submitHandler: function (form) {
            form.submit();
        },
        // Placer les messages d'erreur après les champs correspondants
        errorPlacement: function (error, element) {
            error.insertAfter(element);
            error.addClass('text-danger'); // Ajouter une classe pour styliser les messages d'erreur
        },
        // Ajouter des classes pour les états de validation
        highlight: function (element) {
            $(element).addClass('is-invalid').removeClass('is-valid');
        },
        unhighlight: function (element) {
            $(element).addClass('is-valid').removeClass('is-invalid');
        }
    });
});
