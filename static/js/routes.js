document.addEventListener("DOMContentLoaded", function () {
    // Afficher un toast de bienvenue lorsque la page des routes est chargée
    toastr.success("Toutes les routes sont chargées avec succès !", "Bienvenue", {
        positionClass: "toast-top-right",
        closeButton: true,
        progressBar: true
    });

    // Ajouter un gestionnaire d'événements pour les éléments de la liste des routes
    const routeItems = document.querySelectorAll(".route-item");
    routeItems.forEach(function (item) {
        item.addEventListener("click", function () {
            toastr.info(`Vous avez cliqué sur la route: ${item.innerText}`, "Détail de la Route", {
                positionClass: "toast-top-left",
                closeButton: true,
                progressBar: true
            });
        });
    });
});
