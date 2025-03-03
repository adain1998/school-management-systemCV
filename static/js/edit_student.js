document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const inputs = form.querySelectorAll(".form-control");
    const submitButton = form.querySelector(".btn-primary");

    // Fonction pour afficher un message d'erreur
    function showError(input, message) {
        let errorDiv = input.nextElementSibling;
        if (!errorDiv || !errorDiv.classList.contains("error-message")) {
            errorDiv = document.createElement("div");
            errorDiv.className = "error-message";
            input.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = message;
        input.classList.add("input-error");
    }

    // Fonction pour supprimer un message d'erreur
    function clearError(input) {
        let errorDiv = input.nextElementSibling;
        if (errorDiv && errorDiv.classList.contains("error-message")) {
            errorDiv.remove();
        }
        input.classList.remove("input-error");
    }

    // Validation en temps réel
    inputs.forEach(input => {
        input.addEventListener("input", function () {
            if (input.value.trim() === "") {
                showError(input, "Ce champ est requis.");
            } else {
                clearError(input);
            }
        });
    });

    // Vérification avant soumission
    form.addEventListener("submit", function (event) {
        let isValid = true;

        inputs.forEach(input => {
            if (input.value.trim() === "") {
                showError(input, "Ce champ est requis.");
                isValid = false;
            }
        });

        if (!isValid) {
            event.preventDefault();
        } else {
            // Confirmation avant l'envoi
            if (!confirm("Êtes-vous sûr de vouloir enregistrer ces modifications ?")) {
                event.preventDefault();
            }
        }
    });

});
