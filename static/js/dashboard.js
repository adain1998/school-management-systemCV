document.addEventListener('DOMContentLoaded', () => {
    // Boutons avec redirection
    document.querySelectorAll('[data-redirect]').forEach(btn => {
        btn.addEventListener('click', () => {
            const url = btn.getAttribute('data-redirect');
            window.location.href = url;
        });
    });

    // Boutons pour ouvrir des modales
    const enseignantBtn = document.getElementById('btn-add-enseignant');
    const eleveBtn = document.getElementById('btn-add-eleve');

    if (enseignantBtn) {
        enseignantBtn.addEventListener('click', () => {
            const modal = new bootstrap.Modal(document.getElementById('modalAddEnseignant'));
            modal.show();
        });
    }

    if (eleveBtn) {
        eleveBtn.addEventListener('click', () => {
            const modal = new bootstrap.Modal(document.getElementById('modalAddEleve'));
            modal.show();
        });
    }
});
