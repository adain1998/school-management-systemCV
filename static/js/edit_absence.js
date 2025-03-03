// edit_absence.js

document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const dateInput = document.getElementById('date');
    const reasonInput = document.getElementById('reason');

    // Fonction pour afficher les messages d'erreur
    function showError(input, message) {
        let errorElement = input.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('error-message')) {
            errorElement = document.createElement('div');
            errorElement.classList.add('error-message');
            input.parentNode.insertBefore(errorElement, input.nextSibling);
        }
        errorElement.textContent = message;
        input.classList.add('is-invalid');
    }

    // Fonction pour supprimer les messages d'erreur
    function clearError(input) {
        const errorElement = input.nextElementSibling;
        if (errorElement && errorElement.classList.contains('error-message')) {
            errorElement.remove();
        }
        input.classList.remove('is-invalid');
    }

    // Validation du champ date
    dateInput.addEventListener('input', function () {
        if (!dateInput.value) {
            showError(dateInput, 'La date est obligatoire.');
        } else {
            clearError(dateInput);
        }
    });

    // Validation du champ raison
    reasonInput.addEventListener('input', function () {
        if (reasonInput.value.trim().length < 5) {
            showError(reasonInput, 'La raison doit comporter au moins 5 caractères.');
        } else {
            clearError(reasonInput);
        }
    });

    // Validation du formulaire avant soumission
    form.addEventListener('submit', function (event) {
        let isValid = true;

        if (!dateInput.value) {
            showError(dateInput, 'La date est obligatoire.');
            isValid = false;
        }

        if (reasonInput.value.trim().length < 5) {
            showError(reasonInput, 'La raison doit comporter au moins 5 caractères.');
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault();
        }
    });
});
