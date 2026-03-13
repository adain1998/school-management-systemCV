document.addEventListener('DOMContentLoaded', () => {
  const scoreInput = document.getElementById('score');
  const studentInput = document.getElementById('student_name');
  const subjectInput = document.getElementById('subject');
  const form = document.querySelector('form');

  // Validation en temps réel du champ score
  scoreInput.addEventListener('input', () => {
    const score = parseFloat(scoreInput.value);
    if (isNaN(score) || score < 0 || score > 100) {
      scoreInput.classList.add('is-invalid');
      scoreInput.setCustomValidity("Le score doit être compris entre 0 et 100.");
    } else {
      scoreInput.classList.remove('is-invalid');
      scoreInput.setCustomValidity("");
    }
  });

  // Ajout d’un avertissement visuel sur les champs vides
  form.addEventListener('submit', (e) => {
    let valid = true;

    [studentInput, subjectInput, scoreInput].forEach(input => {
      if (!input.value.trim()) {
        input.classList.add('is-invalid');
        valid = false;
      } else {
        input.classList.remove('is-invalid');
      }
    });

    if (!valid) {
      e.preventDefault();
      alert("Tous les champs sont requis et doivent être valides.");
    }
  });

  // Animation douce sur focus
  [studentInput, subjectInput, scoreInput].forEach(input => {
    input.addEventListener('focus', () => {
      input.style.boxShadow = '0 0 5px rgba(255,193,7,0.5)';
    });
    input.addEventListener('blur', () => {
      input.style.boxShadow = 'none';
    });
  });
});
