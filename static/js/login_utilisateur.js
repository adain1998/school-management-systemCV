document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  const emailInput = form.querySelector('input[name="email"]');
  const passwordInput = form.querySelector('input[name="password"]');

  // Fonction simple de validation email
  function isValidEmail(email) {
    // Regex basique pour vérifier la forme email
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  form.addEventListener('submit', (event) => {
    let hasError = false;

    // Nettoyer les notifications précédentes
    toastr.clear();

    // Validation email
    if (!emailInput.value.trim()) {
      toastr.error("Veuillez saisir votre adresse email.");
      emailInput.focus();
      hasError = true;
    } else if (!isValidEmail(emailInput.value.trim())) {
      toastr.error("L'adresse email saisie n'est pas valide.");
      emailInput.focus();
      hasError = true;
    }

    // Validation mot de passe
    else if (!passwordInput.value.trim()) {
      toastr.error("Veuillez saisir votre mot de passe.");
      passwordInput.focus();
      hasError = true;
    }

    // Si erreur, empêcher l'envoi du formulaire
    if (hasError) {
      event.preventDefault();
    }
  });
});
