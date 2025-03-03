// student_details.js

document.addEventListener('DOMContentLoaded', function() {
    // Formulaire de modification : validation simple
    const formUpdateStudent = document.querySelector('.form-update-student');
    if (formUpdateStudent) {
        formUpdateStudent.addEventListener('submit', function(event) {
            const nom = document.getElementById('nom').value;
            const prenom = document.getElementById('prenom').value;
            const paiement = document.getElementById('paiement').value;

            if (!nom || !prenom || !paiement) {
                event.preventDefault();
                alert('Tous les champs doivent être remplis!');
            }
        });
    }

    // Formulaire de contact : validation simple
    const formContact = document.querySelector('.contact-form');
    if (formContact) {
        formContact.addEventListener('submit', function(event) {
            const email = document.getElementById('email').value;
            const message = document.getElementById('message').value;

            if (!email || !message) {
                event.preventDefault();
                alert('Veuillez remplir tous les champs du formulaire!');
            }
        });
    }
});
