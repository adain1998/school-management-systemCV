document.addEventListener("DOMContentLoaded", function () {
    // Configuration avancée de Toastr
    toastr.options = {
        closeButton: true,
        progressBar: true,
        positionClass: "toast-bottom-right",
        timeOut: "5000",
        extendedTimeOut: "2000",
        showMethod: "fadeIn",
        hideMethod: "fadeOut",
        preventDuplicates: true
    };

    // Gestion des messages flash via Toastr
    let flashMessages = JSON.parse('{{ messages | tojson | safe }}');
    if (flashMessages) {
        flashMessages.forEach(([category, message]) => {
            toastr[category](message);
        });
    }

    // Confirmation avant suppression d’un utilisateur
    document.querySelectorAll(".delete-user-form").forEach(form => {
        form.addEventListener("submit", function (event) {
            event.preventDefault();
            let userName = this.dataset.username;
            let confirmed = confirm(`Voulez-vous vraiment supprimer l'utilisateur ${userName} ?`);
            if (confirmed) {
                this.submit();
            }
        });
    });

    // Ajout d’un effet de hover sur les boutons
    document.querySelectorAll(".btn").forEach(button => {
        button.addEventListener("mouseenter", () => {
            button.classList.add("shadow-lg");
        });
        button.addEventListener("mouseleave", () => {
            button.classList.remove("shadow-lg");
        });
    });
});
