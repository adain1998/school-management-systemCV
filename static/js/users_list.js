document.addEventListener("DOMContentLoaded", function () {
    toastr.options = {
        "closeButton": true,
        "progressBar": true,
        "positionClass": "toast-top-right",
        "timeOut": "3000"
    };

    // Suppression d'un utilisateur
    document.querySelectorAll(".delete-user").forEach(button => {
        button.addEventListener("click", function () {
            let userId = this.getAttribute("data-id");
            if (confirm("Voulez-vous vraiment supprimer cet utilisateur ?")) {
                fetch(`/admin/users/delete/${userId}`, {
                    method: "DELETE",
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById(`user-${userId}`).remove();
                        toastr.success("Utilisateur supprimé avec succès.");
                    } else {
                        toastr.error("Erreur lors de la suppression.");
                    }
                })
                .catch(() => toastr.error("Erreur réseau."));
            }
        });
    });

    // Modification d'un utilisateur
    document.querySelectorAll(".edit-user").forEach(button => {
        button.addEventListener("click", function () {
            let userId = this.getAttribute("data-id");
            window.location.href = `/admin/users/edit/${userId}`;
        });
    });
});
