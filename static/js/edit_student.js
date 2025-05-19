document.addEventListener("DOMContentLoaded", function () {
    const editableFields = [
        'last_name',
        'first_name',
        'class_name',
        'date_naissance',
        'registration_date',
        'numero_matricule',
        'fees_paid',
        'class_id',
        'debt',
        'religion'
    ];

    const form = document.querySelector("form");
    const submitButton = form.querySelector(".btn-primary");

    // Fonction pour afficher un message d'erreur
    function showError(input, message) {
        let errorDiv = input.nextElementSibling;
        if (!errorDiv || !errorDiv.classList.contains("error-message")) {
            errorDiv = document.createElement("div");
            errorDiv.className = "error-message text-danger mt-1";
            input.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = message;
        input.classList.add("input-error", "is-invalid");
    }

    // Fonction pour supprimer le message d'erreur
    function clearError(input) {
        let errorDiv = input.nextElementSibling;
        if (errorDiv && errorDiv.classList.contains("error-message")) {
            errorDiv.remove();
        }
        input.classList.remove("input-error", "is-invalid");
    }

    // Active un champ pour l'édition
    function enableEdit(input) {
        input.readOnly = false;
        input.classList.add("editable");
        input.focus();
    }

    // Attacher les boutons d'édition
    editableFields.forEach(fieldId => {
        const button = document.querySelector(`button[onclick="enableEdit('${fieldId}')"]`);
        const input = document.getElementById(fieldId);

        if (button && input) {
            button.addEventListener('click', function () {
                enableEdit(input);
            });
        }

        // Validation en temps réel
        if (input) {
            input.addEventListener("input", function () {
                if (input.value.trim() === "") {
                    showError(input, "Ce champ est requis.");
                } else {
                    clearError(input);

                    // Validation spécifique pour les champs numériques
                    if (['fees_paid', 'debt'].includes(fieldId) && isNaN(parseFloat(input.value))) {
                        showError(input, "Entrez un nombre valide.");
                    }
                }
            });
        }
    });

    // Validation avant soumission
    form.addEventListener("submit", function (e) {
        let isValid = true;

        editableFields.forEach(fieldId => {
            const input = document.getElementById(fieldId);
            if (!input) return;

            const value = input.value.trim();
            clearError(input);

            if (value === "") {
                showError(input, "Ce champ est requis.");
                isValid = false;
            }

            if (['fees_paid', 'debt'].includes(fieldId) && isNaN(parseFloat(value))) {
                showError(input, "Entrez un nombre valide.");
                isValid = false;
            }
        });

        if (!isValid) {
            e.preventDefault();
            alert("Veuillez corriger les erreurs dans le formulaire.");
            return;
        }

        // Confirmation finale
        if (!confirm("Êtes-vous sûr de vouloir enregistrer ces modifications ?")) {
            e.preventDefault();
        }
    });
});
