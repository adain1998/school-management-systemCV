document.addEventListener('DOMContentLoaded', function () {
    // Affichage des toasts
    document.querySelectorAll('.toast').forEach(t => new bootstrap.Toast(t).show());

    // Activation de DataTables
    if ($('#resultsTable').length) {
        $('#resultsTable').DataTable({
            language: {
                url: "//cdn.datatables.net/plug-ins/1.13.5/i18n/fr-FR.json"
            }
        });
    }

    // Liens AJAX classiques
    $('.ajax-link').on('click', function (e) {
        e.preventDefault();
        const url = $(this).data('url');
        $.get(url, function (data) {
            $('#admin-section').html(data);
        }).fail(function () {
            alert("Erreur de chargement.");
        });
    });

    // Liens avec modal
    $('.modal-link').on('click', function (e) {
        e.preventDefault();
        const url = $(this).data('url');
        const title = $(this).data('title') || 'Chargement';
        $('#modalTitle').text(title);
        $('#modalBody').html(`
          <div class="text-center p-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Chargement...</span>
            </div>
            <p class="mt-3">Veuillez patienter</p>
          </div>
        `);
        $('#dynamicModal').modal('show');

        $.get(url, function (data) {
            $('#modalBody').html(data);
        }).fail(function () {
            $('#modalBody').html('<div class="alert alert-danger">Impossible de charger le contenu.</div>');
        });
    });
});
