// historique.js

document.addEventListener('DOMContentLoaded', () => {
  const table = document.querySelector('table');
  if (!table) return;

  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const headers = Array.from(table.querySelectorAll('thead th'));

  // Création de la barre de recherche
  const container = table.parentElement;
  const searchInput = document.createElement('input');
  searchInput.type = 'search';
  searchInput.placeholder = 'Rechercher...';
  searchInput.className = 'form-control mb-3';
  container.insertBefore(searchInput, table);

  // Fonction de filtrage des lignes
  searchInput.addEventListener('input', () => {
    const query = searchInput.value.toLowerCase();
    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(query) ? '' : 'none';
    });
  });

  // Fonction de tri
  headers.forEach((header, index) => {
    header.style.cursor = 'pointer';
    header.title = 'Cliquez pour trier';

    let asc = true;

    header.addEventListener('click', () => {
      const compare = (a, b) => {
        const cellA = a.children[index].textContent.trim();
        const cellB = b.children[index].textContent.trim();

        // Gestion des nombres (ex: montants)
        const numA = parseFloat(cellA.replace(/[^\d.-]/g, ''));
        const numB = parseFloat(cellB.replace(/[^\d.-]/g, ''));

        if (!isNaN(numA) && !isNaN(numB)) {
          return asc ? numA - numB : numB - numA;
        }

        // Sinon, comparaison lexicographique
        return asc
          ? cellA.localeCompare(cellB, 'fr', { sensitivity: 'base' })
          : cellB.localeCompare(cellA, 'fr', { sensitivity: 'base' });
      };

      rows.sort(compare);
      asc = !asc;

      // Ré-insertion des lignes triées dans le tbody
      rows.forEach(row => tbody.appendChild(row));
    });
  });
});
