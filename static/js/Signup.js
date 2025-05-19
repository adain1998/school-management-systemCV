document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  const roleSelect = document.querySelector('select[name="role"]');
  const specialiteField = document.getElementById('specialite-field');
  const niveauField = document.getElementById('niveau-field');
  const roleAdminField = document.getElementById('role-admin-field');

  const emailInput = document.querySelector('input[name="email"]');
  const passwordInput = document.querySelector('input[name="password"]');
  const confirmPasswordInput = document.querySelector('input[name="confirm_password"]');

  // Affiche ou masque les champs selon le rôle avec animation
  function toggleFields(role) {
    const duration = 300; // Durée de l'animation en ms
    // Cache tous les champs
    [specialiteField, niveauField, roleAdminField].forEach(field => {
      field.style.transition = `opacity ${duration}ms ease`;
      field.style.opacity = '0';
      setTimeout(() => field.style.display = 'none', duration);
    });

    // Affiche les champs appropriés
    if (role === 'enseignant') {
      specialiteField.style.display = 'block';
      setTimeout(() => specialiteField.style.opacity = '1', 10);
    } else if (role === 'eleve') {
      niveauField.style.display = 'block';
      setTimeout(() => niveauField.style.opacity = '1', 10);
    } else if (role === 'administrateur') {
      roleAdminField.style.display = 'block';
      setTimeout(() => roleAdminField.style.opacity = '1', 10);
    }
  }

  if (roleSelect) {
    toggleFields(roleSelect.value);
    roleSelect.addEventListener('change', () => toggleFields(roleSelect.value));
  }

  // Validation frontale du formulaire avec animations d'erreur
  form.addEventListener('submit', (e) => {
    let isValid = true;
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    const confirmPassword = confirmPasswordInput.value.trim();

    // Réinitialise les messages d'erreurs
    const errorSpans = form.querySelectorAll('.js-error');
    errorSpans.forEach(span => span.remove());

    // Vérifie l'email
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      showError(emailInput, "Adresse email invalide.");
      isValid = false;
    }

    // Vérifie les mots de passe
    if (password.length < 6) {
      showError(passwordInput, "Le mot de passe doit contenir au moins 6 caractères.");
      isValid = false;
    }

    if (password !== confirmPassword) {
      showError(confirmPasswordInput, "Les mots de passe ne correspondent pas.");
      isValid = false;
    }

    // Empêche l'envoi si le formulaire est invalide
    if (!isValid) {
      e.preventDefault();
    }
  });

  // Affiche une erreur sous un champ avec une animation
  function showError(input, message) {
    const error = document.createElement('small');
    error.className = 'text-danger js-error';
    error.innerText = message;
    input.classList.add('is-invalid');
    input.parentNode.appendChild(error);

    // Animation d'apparition de l'erreur
    setTimeout(() => {
      error.style.opacity = '1';
    }, 10);
  }

  // Enlève l'indicateur d'erreur dès que l'utilisateur modifie le champ
  [emailInput, passwordInput, confirmPasswordInput].forEach(input => {
    input.addEventListener('input', () => {
      input.classList.remove('is-invalid');
      const error = input.parentNode.querySelector('.js-error');
      if (error) error.remove();
    });
  });
});
