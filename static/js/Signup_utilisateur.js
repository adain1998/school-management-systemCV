<script>
document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  const roleSelect = document.querySelector('select[name="role"]');
  const specialiteField = document.getElementById('specialite-field');
  const niveauField = document.getElementById('niveau-field');
  const roleAdminField = document.getElementById('role-admin-field');

  const emailInput = document.querySelector('input[name="email"]');
  const passwordInput = document.querySelector('input[name="password"]');
  const confirmPasswordInput = document.querySelector('input[name="confirm_password"]');

  function toggleFields(role) {
    const duration = 300;
    const allFields = [specialiteField, niveauField, roleAdminField];

    allFields.forEach(field => {
      if (field) {
        field.style.transition = `opacity ${duration}ms ease`;
        field.style.opacity = '0';
        setTimeout(() => field.style.display = 'none', duration);
      }
    });

    if (role === 'enseignant' && specialiteField) {
      specialiteField.style.display = 'block';
      setTimeout(() => specialiteField.style.opacity = '1', 10);
    } else if (role === 'eleve' && niveauField) {
      niveauField.style.display = 'block';
      setTimeout(() => niveauField.style.opacity = '1', 10);
    } else if (role === 'administrateur' && roleAdminField) {
      roleAdminField.style.display = 'block';
      setTimeout(() => roleAdminField.style.opacity = '1', 10);
    }
  }

  if (roleSelect) {
    toggleFields(roleSelect.value);
    roleSelect.addEventListener('change', () => toggleFields(roleSelect.value));
  }

  if (form) {
    form.addEventListener('submit', (e) => {
      let isValid = true;

      const email = emailInput?.value.trim() || '';
      const password = passwordInput?.value.trim() || '';
      const confirmPassword = confirmPasswordInput?.value.trim() || '';

      const errorSpans = form.querySelectorAll('.js-error');
      errorSpans.forEach(span => span.remove());

      if (!/^\S+@\S+\.\S+$/.test(email)) {
        if (emailInput) showError(emailInput, "Adresse email invalide.");
        isValid = false;
      }

      if (password.length < 6) {
        if (passwordInput) showError(passwordInput, "Le mot de passe doit contenir au moins 6 caractères.");
        isValid = false;
      }

      if (password !== confirmPassword) {
        if (confirmPasswordInput) showError(confirmPasswordInput, "Les mots de passe ne correspondent pas.");
        isValid = false;
      }

      if (!isValid) {
        e.preventDefault();
      }
    });
  }

  function showError(input, message) {
    const error = document.createElement('small');
    error.className = 'text-danger js-error';
    error.innerText = message;
    input.classList.add('is-invalid');
    input.parentNode.appendChild(error);
    setTimeout(() => {
      error.style.opacity = '1';
    }, 10);
  }

  [emailInput, passwordInput, confirmPasswordInput].forEach(input => {
    if (input) {
      input.addEventListener('input', () => {
        input.classList.remove('is-invalid');
        const error = input.parentNode.querySelector('.js-error');
        if (error) error.remove();
      });
    }
  });
});
</script>
