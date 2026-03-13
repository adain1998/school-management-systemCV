<script>
  document.addEventListener('DOMContentLoaded', () => {
    // --- Variables DOM ---
    const filterForm = document.getElementById('filter-form');
    const filterButton = document.getElementById('filter-button');
    const postsContainer = document.querySelector('.row.row-cols-1, #posts-container'); // supporte les 2 cas
    const gridBtn = document.getElementById('grid-view-btn');
    const listBtn = document.getElementById('list-view-btn');

    // --- Sécurité : vérifier que les éléments existent ---
    if (!filterForm || !filterButton) {
      console.warn('filtered_forum.js : formulaire ou bouton non trouvé.');
    } else {
      // --- Gestion soumission formulaire : désactiver bouton + texte chargement ---
      filterForm.addEventListener('submit', () => {
        filterButton.classList.add('disabled-button');
        filterButton.disabled = true;
        filterButton.innerText = '⏳ Chargement...';
      });
    }

    if (!postsContainer) {
      console.warn('filtered_forum.js : container des posts non trouvé.');
    }

    if (!gridBtn || !listBtn) {
      console.warn('filtered_forum.js : boutons de mode grille/liste non trouvés.');
    }

    // --- Scroll vers le haut si page présente dans l'URL (pagination) ---
    if (window.location.search.includes("page=")) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // --- Fonction bascule mode affichage ---
    function setView(view) {
      if (!postsContainer) return;

      if (view === 'list') {
        postsContainer.classList.remove('row', 'row-cols-md-2', 'posts-grid');
        postsContainer.classList.add('posts-list');

        if (gridBtn && listBtn) {
          gridBtn.setAttribute('aria-pressed', 'false');
          listBtn.setAttribute('aria-pressed', 'true');
          gridBtn.classList.remove('active');
          listBtn.classList.add('active');
        }
      } else {
        postsContainer.classList.remove('posts-list');
        postsContainer.classList.add('row', 'row-cols-md-2', 'posts-grid');

        if (gridBtn && listBtn) {
          gridBtn.setAttribute('aria-pressed', 'true');
          listBtn.setAttribute('aria-pressed', 'false');
          gridBtn.classList.add('active');
          listBtn.classList.remove('active');
        }
      }

      // Sauvegarde du choix utilisateur
      localStorage.setItem('forumViewMode', view);
    }

    // --- Écouteurs boutons grille/liste ---
    if (gridBtn) gridBtn.addEventListener('click', () => setView('grid'));
    if (listBtn) listBtn.addEventListener('click', () => setView('list'));

    // --- Chargement du mode sauvegardé ---
    const savedView = localStorage.getItem('forumViewMode') || 'grid';
    setView(savedView);
  });
</script>
