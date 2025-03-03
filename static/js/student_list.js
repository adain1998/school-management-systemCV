document.addEventListener("DOMContentLoaded", function() {
    // Gestion du menu responsive
    const navbarToggler = document.querySelector(".navbar-toggler");
    const navbarCollapse = document.querySelector("#navbarNav");

    if (navbarToggler) {
        navbarToggler.addEventListener("click", function() {
            navbarCollapse.classList.toggle("show");
        });
    }

    // Fermeture automatique des messages flash
    const flashMessages = document.querySelectorAll(".alert");
    setTimeout(() => {
        flashMessages.forEach(message => {
            message.style.transition = "opacity 0.5s";
            message.style.opacity = "0";
            setTimeout(() => message.remove(), 500);
        });
    }, 5000);

    // Initialisation du calendrier FullCalendar
    if (document.getElementById("calendar")) {
        let calendarEl = document.getElementById("calendar");
        let calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: "dayGridMonth",
            locale: "fr",
            events: "/api/get_events" // Endpoint pour récupérer les événements
        });
        calendar.render();
    }

    // Gestion des actions sur les étudiants
    document.querySelectorAll(".delete-student").forEach(button => {
        button.addEventListener("click", function(event) {
            event.preventDefault();
            let studentId = this.getAttribute("data-id");
            if (confirm("Êtes-vous sûr de vouloir supprimer cet étudiant ?")) {
                fetch(`/delete_student/${studentId}`, {
                    method: "DELETE",
                    headers: { "Content-Type": "application/json" }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert("Étudiant supprimé avec succès.");
                        location.reload();
                    } else {
                        alert("Erreur lors de la suppression de l'étudiant.");
                    }
                })
                .catch(error => console.error("Erreur :", error));
            }
        });
    });

    // Pré-remplissage du formulaire de modification d'élève
    const editForm = document.querySelector("#edit-student-form");
    if (editForm) {
        editForm.addEventListener("submit", function(event) {
            const nom = document.querySelector("#nom").value.trim();
            const prenom = document.querySelector("#prenom").value.trim();
            const classe = document.querySelector("#classe").value.trim();

            if (!nom || !prenom || !classe) {
                event.preventDefault();
                alert("Veuillez remplir tous les champs avant de soumettre le formulaire.");
            }
        });
    }

    // Filtrage des étudiants
    const filterForm = document.querySelector("#filter-student-form");
    if (filterForm) {
        filterForm.addEventListener("submit", function(event) {
            event.preventDefault();
            const filterData = new FormData(filterForm);
            const queryString = new URLSearchParams(filterData).toString();
            fetch(`/filter?${queryString}`)
                .then(response => response.text())
                .then(html => {
                    document.querySelector("#student-list").innerHTML = html;
                })
                .catch(error => console.error("Erreur lors du filtrage :", error));
        });
    }

    // Recherche dynamique d'étudiants
    const searchInput = document.querySelector("#search-student");
    if (searchInput) {
        searchInput.addEventListener("input", function() {
            const query = searchInput.value.trim();
            fetch(`/students?search=${query}`)
                .then(response => response.text())
                .then(html => {
                    document.querySelector("#student-list").innerHTML = html;
                })
                .catch(error => console.error("Erreur lors de la recherche :", error));
        });
    }
});
