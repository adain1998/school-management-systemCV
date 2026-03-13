// custom_notifications.js

document.addEventListener('DOMContentLoaded', () => {
  try {
    const filterForm = document.getElementById('filter-form');
    const filterBySelect = document.getElementById('filter_by');
    const orderSelect = document.getElementById('order');
    const notificationsTable = document.querySelector('table.table');
    const notificationRows = document.querySelectorAll('.notification-row');

    // 1. Amélioration accessibilité des lignes (cliquables + focus)
    notificationRows.forEach(row => {
      row.style.cursor = 'pointer';

      // Permettre navigation clavier + focus visible
      row.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          row.click();
        }
      });

      // Exemple d’action au clic : affichage d’un détail (peut être adapté)
      row.addEventListener('click', () => {
        const title = row.querySelector('td').textContent.trim();
        alert(`Détails de la notification :\n${title}`);
      });
    });

    // 2. Gestion sécurisée du formulaire de filtre
    if (filterForm) {
      filterForm.addEventListener('submit', e => {
        // On peut ajouter ici des validations custom si besoin
        // Exemples : vérifier que les valeurs sont valides
        const validFilters = ['due_date', 'title', 'description'];
        const validOrders = ['asc', 'desc'];

        if (!validFilters.includes(filterBySelect.value)) {
          e.preventDefault();
          alert('Filtre invalide sélectionné.');
          filterBySelect.focus();
          return false;
        }

        if (!validOrders.includes(orderSelect.value)) {
          e.preventDefault();
          alert('Ordre de tri invalide.');
          orderSelect.focus();
          return false;
        }
        // Le formulaire peut être soumis normalement si validé
      });
    }

    // 3. Amélioration UX : focus sur le premier champ après chargement
    if (filterBySelect) {
      filterBySelect.focus();
    }

    // 4. Gestion des messages flash avec auto-fermeture progressive
    const flashAlerts = document.querySelectorAll('.alert-dismissible');

    flashAlerts.forEach(alert => {
      // Durée avant disparition en ms
      const dismissAfter = 7000;

      setTimeout(() => {
        // Bootstrap 5: on peut utiliser l’événement 'close.bs.alert' mais on fait un fade-out custom
        alert.classList.remove('show');
        alert.classList.add('fade');

        // Supprimer l’alerte du DOM après transition (350ms)
        setTimeout(() => {
          alert.remove();
        }, 350);
      }, dismissAfter);
    });

  } catch (error) {
    console.error('Erreur dans le script notifications :', error);
  }
});
