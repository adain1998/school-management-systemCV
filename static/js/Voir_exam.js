// voir_exam.js

// Fonction de confirmation de suppression
document.querySelectorAll('.btn-danger').forEach((button) => {
    button.addEventListener('click', (event) => {
        if (!confirm("Êtes-vous sûr de vouloir supprimer cet examen ?")) {
            event.preventDefault(); // Annule l'action de suppression si l'utilisateur annule
        }
    });
});

// Validation du formulaire de filtrage (pour s'assurer que les entrées sont valides)
document.querySelector('form').addEventListener('submit', function(event) {
    let subject = document.getElementById('subject').value.trim();
    let score = document.getElementById('score').value.trim();

    if (subject === "" && score === "") {
        alert("Veuillez entrer au moins un critère de filtrage.");
        event.preventDefault();
    } else if (score !== "" && isNaN(score)) {
        alert("Veuillez entrer une note valide.");
        event.preventDefault();
    }
});
