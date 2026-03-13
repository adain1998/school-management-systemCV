document.addEventListener('DOMContentLoaded', () => {
  const filterForm = document.getElementById('filter-form');
  const filterBySelect = document.getElementById('filter_by');
  const filterValueInput = document.getElementById('filter_value');

  // Préremplir avec les valeurs précédentes si disponibles (optionnel)
  if (localStorage.getItem('filter_by')) {
    filterBySelect.value = localStorage.getItem('filter_by');
  }
  if (localStorage.getItem('filter_value')) {
    filterValueInput.value = localStorage.getItem('filter_value');
  }

  filterForm.addEventListener('submit', (e) => {
    // Validation des champs
    const filterBy = filterBySelect.value.trim();
    const filterValue = filterValueInput.value.trim();

    if (!filterBy) {
      alert("Veuillez sélectionner un champ pour filtrer.");
      filterBySelect.focus();
      e.preventDefault();
      return;
    }

    if (!filterValue) {
      alert("Veuillez saisir une valeur de filtre.");
      filterValueInput.focus();
      e.preventDefault();
      return;
    }

    // Sauvegarde dans le localStorage (optionnel)
    localStorage.setItem('filter_by', filterBy);
    localStorage.setItem('filter_value', filterValue);
  });

  // Nettoyage du message flash après quelques secondes
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.classList.remove('show');
      alert.classList.add('fade');
    }, 5000); // 5 secondes
  });
});
