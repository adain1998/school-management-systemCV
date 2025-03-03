// filter_scripts.js

// Fonction pour afficher un message de succès ou d'erreur avec Toastr
function showNotification(type, message) {
    if (type === "success") {
        toastr.success(message, 'Succès', {
            positionClass: "toast-top-right",
            timeOut: 3000,
        });
    } else if (type === "error") {
        toastr.error(message, 'Erreur', {
            positionClass: "toast-top-right",
            timeOut: 3000,
        });
    }
}

// Attacher la soumission du formulaire
document.querySelector('form').addEventListener('submit', function(event) {
    event.preventDefault();  // Empêcher la soumission par défaut

    let form = event.target;
    let formData = new FormData(form);

    // Appel AJAX pour soumettre les données sans recharger la page
    fetch(form.action, {
        method: 'GET',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('success', 'Les étudiants ont été filtrés avec succès!');
        } else {
            showNotification('error', 'Une erreur s\'est produite lors du filtrage.');
        }
    })
    .catch(error => {
        showNotification('error', 'Une erreur s\'est produite.');
    });
});
