// manager_visitor.js

$(document).ready(function() {
    // Affichage des messages flash avec Toastr
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                toastr["{{ category }}"]("{{ message }}");
            {% endfor %}
        {% endif %}
    {% endwith %}

    // Confirmation avant suppression d'un visiteur
    $('a.btn-danger').on('click', function(event) {
        var result = confirm("Etes-vous sûr de vouloir supprimer ce visiteur?");
        if (!result) {
            event.preventDefault();  // Annule la suppression si l'utilisateur annule
        }
    });

    // Fonction pour rendre les boutons plus interactifs
    $('.btn').on('mouseover', function() {
        $(this).css('opacity', '0.8');
    });

    $('.btn').on('mouseout', function() {
        $(this).css('opacity', '1');
    });
});
