document.addEventListener('DOMContentLoaded', () => {
  // 🔔 Animation douce pour les alertes Bootstrap (auto-dismiss après 5s)
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    // Show alert if not visible
    alert.classList.add('show');
    // Après 5 secondes, fade out doucement puis suppression du node
    setTimeout(() => {
      alert.classList.remove('show');
      alert.classList.add('fade');
      // Après la transition Bootstrap (300ms), on enlève l'alerte du DOM
      alert.addEventListener('transitionend', () => alert.remove(), { once: true });
    }, 5000);
  });

  // 🗑️ Confirmation SweetAlert pour les suppressions (fonctionne pour formulaire standard et en modal)
  const deleteForms = document.querySelectorAll('form[action*="delete_section"]');
  deleteForms.forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();

      Swal.fire({
        title: 'Êtes-vous sûr ?',
        text: "Cette action est irréversible.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Oui, supprimer',
        cancelButtonText: 'Annuler',
        focusCancel: true,
        reverseButtons: true,
      }).then(result => {
        if (result.isConfirmed) {
          form.submit();
        }
      });
    });
  });

  // 🌟 Animation de survol légère sur les lignes du tableau
  const rows = document.querySelectorAll('table tbody tr');
  rows.forEach(row => {
    row.addEventListener('mouseenter', () => {
      row.classList.add('table-hover-highlight');
    });
    row.addEventListener('mouseleave', () => {
      row.classList.remove('table-hover-highlight');
    });
  });

  // ✅ Animation rapide au clic sur boutons et liens btn
  const clickableElements = document.querySelectorAll('button, a.btn');
  clickableElements.forEach(el => {
    el.addEventListener('click', () => {
      el.classList.add('active');
      setTimeout(() => el.classList.remove('active'), 150);
    });
  });
});
