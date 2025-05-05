// Assurez-vous que Toastr est inclus dans votre projet
// Vous pouvez le faire en ajoutant dans le fichier base.html :
/*
<link href="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.css" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js"></script>
*/

document.addEventListener('DOMContentLoaded', function () {
    // Affichage des messages Toastr
    const flashMessages = {{ get_flashed_messages(with_categories=true)|tojson }};

    if (flashMessages.length > 0) {
        flashMessages.forEach(message => {
            const [category, content] = message;
            // Choisir le type de Toastr en fonction de la catégorie
            switch (category) {
                case 'success':
                    toastr.success(content, "Succès");
                    break;
                case 'danger':
                    toastr.error(content, "Erreur");
                    break;
                case 'info':
                    toastr.info(content, "Information");
                    break;
                case 'warning':
                    toastr.warning(content, "Avertissement");
                    break;
                default:
                    toastr.info(content, "Message");
                    break;
            }
        });
    }

    // Initialiser des événements sur les formulaires
    const filterForm = document.querySelector('form#filter-form');
    const sortForm = document.querySelector('form#sort-form');

    // Exemple de logique pour rafraîchir la page après un filtre ou un tri
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            toastr.info("Les filtres sont appliqués, veuillez patienter...", "Chargement");
            this.submit();
        });
    }

    if (sortForm) {
        sortForm.addEventListener('submit', function(e) {
            e.preventDefault();
            toastr.info("Les paramètres de tri sont appliqués, veuillez patienter...", "Chargement");
            this.submit();
        });
    }
});
