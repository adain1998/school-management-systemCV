// gestion_classe.js

document.addEventListener("DOMContentLoaded", function () {
    // Ajout d'un effet de surbrillance au passage de la souris sur les lignes du tableau
    document.querySelectorAll("table tbody tr").forEach(row => {
        row.addEventListener("mouseover", function () {
            this.style.backgroundColor = "#d1ecf1";
        });
        row.addEventListener("mouseout", function () {
            this.style.backgroundColor = "";
        });
    });

    // Confirmation avant la suppression d'une classe, section ou option
    document.querySelectorAll(".btn-danger").forEach(button => {
        button.addEventListener("click", function (event) {
            if (!confirm("Êtes-vous sûr de vouloir supprimer cet élément ?")) {
                event.preventDefault();
            }
        });
    });
});
