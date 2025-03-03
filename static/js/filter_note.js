// Assurez-vous que le DOM est complètement chargé avant d'exécuter le script
document.addEventListener("DOMContentLoaded", function () {
    // Initialisation des messages flash (si on utilise Toastr pour les notifications)
    const messages = {{ get_flashed_messages(with_categories=true)|tojson }};
    if (messages.length > 0) {
        messages.forEach((message) => {
            // Chaque message a une catégorie et un texte
            const [category, text] = message;
            toastr.options = {
                closeButton: true,  // Permet de fermer le message via un bouton
                progressBar: true,  // Affiche une barre de progression
                positionClass: 'toast-top-center',  // Position du toast
                timeOut: 5000,  // Durée d'affichage du message
            };

            // Affichage du toast selon la catégorie
            if (category === 'error') {
                toastr.error(text);
            } else if (category === 'success') {
                toastr.success(text);
            } else {
                toastr.info(text);
            }
        });
    }

    // Validation du formulaire avant envoi
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function (event) {
            // Récupérer les valeurs des champs du formulaire
            const filterBy = document.querySelector('[name="filter_by"]');
            const filterValue = document.querySelector('[name="filter_value"]');
            const order = document.querySelector('[name="order"]');

            // Validation simple des champs
            if (!filterBy.value) {
                event.preventDefault();
                toastr.error("Veuillez sélectionner un filtre.");
                return;
            }

            if (!filterValue.value.trim()) {
                event.preventDefault();
                toastr.error("Veuillez entrer une valeur pour le filtre.");
                return;
            }

            if (!order.value) {
                event.preventDefault();
                toastr.error("Veuillez sélectionner un ordre de tri.");
                return;
            }
        });
    }

    // Exemple de manipulation dynamique de données (par exemple, ajustement de l'affichage)
    const filterBy = document.querySelector('[name="filter_by"]');
    const filterValue = document.querySelector('[name="filter_value"]');

    // Dynamique pour ajuster les options en fonction du filtre
    if (filterBy) {
        filterBy.addEventListener('change', function () {
            if (filterBy.value === 'note') {
                filterValue.setAttribute('type', 'number');  // Si le filtre est par note, utiliser un champ numérique
            } else {
                filterValue.setAttribute('type', 'text');  // Sinon, un champ texte
            }
        });
    }
});
