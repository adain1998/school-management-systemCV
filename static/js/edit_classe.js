// edit_classe.js

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("editClassForm");

    form.addEventListener("submit", function (event) {
        const nameInput = document.getElementById("name").value.trim();

        if (nameInput === "") {
            event.preventDefault();
            alert("Le nom de la classe ne peut pas être vide.");
        } else {
            if (!confirm("Êtes-vous sûr de vouloir enregistrer les modifications ?")) {
                event.preventDefault();
            }
        }
    });
});
