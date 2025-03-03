// edit_assignment.js

// Attendre que le DOM soit entièrement chargé
document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const titleInput = document.getElementById('title');
    const descriptionInput = document.getElementById('description');
    const dueDateInput = document.getElementById('due_date');

    // Configuration globale de Toastr
    toastr.options = {
        "closeButton": true,
        "progressBar": true,
        "positionClass": "toast-top-right",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    };

    // Fonction pour afficher les messages d'erreur
    function showError(input, message) {
        input.classList.add('is-invalid');
        toastr.error(message, 'Erreur');
    }

    // Fonction pour supprimer les messages d'erreur
    function clearError(input) {
        input.classList.remove('is-invalid');
    }

    // Validation du champ titre
    titleInput.addEventListener('input', function () {
        if (titleInput.value.trim() === '') {
            showError(titleInput, 'Le titre est obligatoire.');
        } else {
            clearError(titleInput);
        }
    });

    // Validation du champ description
    descriptionInput.addEventListener('input', function () {
        if (descriptionInput.value.trim() === '') {
            showError(descriptionInput, 'La description est obligatoire.');
        } else {
            clearError(descriptionInput);
        }
    });

    // Validation du champ date d'échéance
    dueDateInput.addEventListener('input', function () {
        if (dueDateInput.value.trim() === '') {
            showError(dueDateInput, "La date d'échéance est obligatoire.");
        } else {
            clearError(dueDateInput);
        }
    });

    // Validation du formulaire avant soumission
    form.addEventListener('submit', function (event) {
        let isValid = true;

        if (titleInput.value.trim() === '') {
            showError(titleInput, 'Le titre est obligatoire.');
            isValid = false;
        }

        if (descriptionInput.value.trim() === '') {
            showError(descriptionInput, 'La description est obligatoire.');
            isValid = false;
        }

        if (dueDateInput.value.trim() === '') {
            showError(dueDateInput, "La date d'échéance est obligatoire.");
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault();
        } else {
            toastr.success('Le devoir a été mis à jour avec succès.', 'Succès');
        }
    });
});
