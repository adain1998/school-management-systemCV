<script>
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const emailInput = document.querySelector("input[name='email']");
    const passwordInput = document.querySelector("input[name='password']");
    const confirmPasswordInput = document.querySelector("input[name='confirm_password']");
    const submitBtn = document.querySelector("button[type='submit']");

    // Fonction pour créer un champ avec icône œil
    function wrapWithPasswordToggle(input) {
        const formGroup = input.closest(".mb-3");

        const wrapper = document.createElement("div");
        wrapper.classList.add("position-relative");

        input.classList.add("pe-5"); // espace pour le bouton
        wrapper.appendChild(input.cloneNode(true));

        const toggleBtn = document.createElement("button");
        toggleBtn.type = "button";
        toggleBtn.innerHTML = `<i class="bi bi-eye-fill"></i>`;
        toggleBtn.classList.add("btn", "btn-sm", "position-absolute", "top-50", "end-0", "translate-middle-y", "me-2");
        toggleBtn.setAttribute("aria-label", "Afficher/masquer le mot de passe");

        toggleBtn.addEventListener("click", () => {
            const type = input.type === "password" ? "text" : "password";
            input.type = type;
            toggleBtn.innerHTML = type === "password"
                ? `<i class="bi bi-eye-fill"></i>`
                : `<i class="bi bi-eye-slash-fill"></i>`;
            input.focus();
        });

        // Remplacer l'ancien champ par le wrapper
        formGroup.replaceChild(wrapper, input);
        wrapper.appendChild(toggleBtn);
    }

    wrapWithPasswordToggle(passwordInput);
    wrapWithPasswordToggle(confirmPasswordInput);

    // === Barre de sécurité ===
    const strengthWrapper = document.createElement("div");
    strengthWrapper.className = "progress mt-2";
    strengthWrapper.style.height = "6px";
    const strengthBar = document.createElement("div");
    strengthBar.className = "progress-bar";
    strengthWrapper.appendChild(strengthBar);

    passwordInput.closest(".mb-3").appendChild(strengthWrapper);

    passwordInput.addEventListener("input", () => {
        const value = passwordInput.value;
        let strength = 0;
        if (value.length >= 8) strength++;
        if (/[A-Z]/.test(value)) strength++;
        if (/[0-9]/.test(value)) strength++;
        if (/[^A-Za-z0-9]/.test(value)) strength++;

        if (strength <= 1) {
            strengthBar.className = "progress-bar bg-danger";
            strengthBar.style.width = "33%";
        } else if (strength === 2 || strength === 3) {
            strengthBar.className = "progress-bar bg-warning";
            strengthBar.style.width = "66%";
        } else {
            strengthBar.className = "progress-bar bg-success";
            strengthBar.style.width = "100%";
        }
    });

    // === Validation email ===
    function isValidEmail(email) {
        const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return pattern.test(email.toLowerCase());
    }

    // === Erreurs dynamiques ===
    function showError(input, message) {
        removeError(input);
        const error = document.createElement("div");
        error.className = "text-danger small mt-1";
        error.textContent = message;
        input.classList.add("is-invalid");
        input.closest(".mb-3").appendChild(error);
    }

    function removeError(input) {
        input.classList.remove("is-invalid");
        const existing = input.closest(".mb-3").querySelector(".text-danger");
        if (existing) existing.remove();
    }

    emailInput.addEventListener("input", () => {
        removeError(emailInput);
        if (!isValidEmail(emailInput.value)) {
            showError(emailInput, "Veuillez entrer une adresse e-mail valide.");
        }
    });

    confirmPasswordInput.addEventListener("input", () => {
        removeError(confirmPasswordInput);
        if (confirmPasswordInput.value !== passwordInput.value) {
            showError(confirmPasswordInput, "Les mots de passe ne correspondent pas.");
        }
    });

    form.addEventListener("submit", function (e) {
        let isValid = true;

        removeError(emailInput);
        removeError(passwordInput);
        removeError(confirmPasswordInput);

        if (!isValidEmail(emailInput.value)) {
            showError(emailInput, "Adresse e-mail invalide.");
            isValid = false;
        }

        if (passwordInput.value.length < 8) {
            showError(passwordInput, "Le mot de passe doit contenir au moins 8 caractères.");
            isValid = false;
        }

        if (confirmPasswordInput.value !== passwordInput.value) {
            showError(confirmPasswordInput, "Les mots de passe ne correspondent pas.");
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
            return;
        }

        submitBtn.disabled = true;
        submitBtn.innerText = "Veuillez patienter...";
    });
});
</script>
