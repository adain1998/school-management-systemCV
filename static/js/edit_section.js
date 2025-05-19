document.addEventListener("DOMContentLoaded", function () {
    // Focus sur le champ quand on clique sur l’icône de crayon
    document.querySelectorAll(".input-group-text").forEach(span => {
        span.style.cursor = "pointer";
        span.addEventListener("click", () => {
            const input = span.previousElementSibling;
            if (input) input.focus();
        });
    });

    // Ajoute une classe visuelle lors du focus
    document.querySelectorAll("input, select").forEach(field => {
        field.addEventListener("focus", () => {
            field.classList.add("border-primary", "shadow");
        });
        field.addEventListener("blur", () => {
            field.classList.remove("border-primary", "shadow");
        });
    });

    // Exemple de compteur de caractères pour le champ nom
    const nameInput = document.getElementById("name");
    if (nameInput) {
        const counter = document.createElement("div");
        counter.className = "form-text text-end";
        nameInput.parentElement.parentElement.appendChild(counter);

        const updateCounter = () => {
            counter.textContent = `${nameInput.value.length} / 100 caractères`;
        };

        nameInput.maxLength = 100;
        nameInput.addEventListener("input", updateCounter);
        updateCounter(); // Initialisation
    }

    // Validation légère côté client avant soumission
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", (e) => {
            const name = document.getElementById("name").value.trim();
            const classe = document.getElementById("classe_id").value;

            if (!name || !classe) {
                e.preventDefault();
                alert("Veuillez remplir tous les champs obligatoires.");
            }
        });
    }
});
