document.addEventListener("DOMContentLoaded", function () {
  const passwordInput = document.getElementById("password");
  const toggleButton = document.querySelector(".toggle-password");

  // 🎯 Afficher/Masquer le mot de passe
  if (toggleButton && passwordInput) {
    toggleButton.addEventListener("click", function () {
      const isPassword = passwordInput.type === "password";
      passwordInput.type = isPassword ? "text" : "password";
      toggleButton.innerText = isPassword ? "🙈" : "👁️";
    });
  }

  // ✅ Validation visuelle dynamique des champs
  const form = document.querySelector("form");
  if (form) {
    form.addEventListener("submit", function (e) {
      const email = form.querySelector("[name='email']");
      const password = form.querySelector("[name='password']");
      let valid = true;

      if (!email.value.trim()) {
        showError(email, "Veuillez entrer une adresse email.");
        valid = false;
      } else {
        clearError(email);
      }

      if (!password.value.trim()) {
        showError(password, "Veuillez entrer votre mot de passe.");
        valid = false;
      } else {
        clearError(password);
      }

      if (!valid) {
        e.preventDefault();
      }
    });
  }

  function showError(input, message) {
    clearError(input);
    const error = document.createElement("div");
    error.className = "text-danger mt-1";
    error.innerText = message;
    input.classList.add("is-invalid");
    input.parentNode.appendChild(error);
  }

  function clearError(input) {
    input.classList.remove("is-invalid");
    const errors = input.parentNode.querySelectorAll(".text-danger");
    errors.forEach(el => el.remove());
  }
});
