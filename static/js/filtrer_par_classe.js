document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const filterStatus = document.getElementById('filterStatus');
    const rows = [...document.querySelectorAll('#paiementTable tbody .paiement-row')];
    const tableBody = document.getElementById('tableBody');
    const pagination = document.getElementById('pagination');
    const itemsPerPage = 10;
    let currentPage = 1;

    function filterAndPaginate() {
        const query = searchInput.value.toLowerCase();
        const status = filterStatus.value;

        const filtered = rows.filter(row => {
            const name = row.dataset.nom.toLowerCase();
            const stat = row.dataset.statut;
            return name.includes(query) && (!status || stat === status);
        });

        // Masquer toutes les lignes
        rows.forEach(row => row.style.display = 'none');
        document.querySelectorAll('.collapse').forEach(el => el.style.display = 'none');

        const totalPages = Math.ceil(filtered.length / itemsPerPage);
        pagination.innerHTML = '';

        // Génération des boutons de pagination
        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement('li');
            li.className = 'page-item' + (i === currentPage ? ' active' : '');
            li.innerHTML = `<button class="page-link">${i}</button>`;
            li.addEventListener('click', () => {
                currentPage = i;
                filterAndPaginate();
            });
            pagination.appendChild(li);
        }

        const start = (currentPage - 1) * itemsPerPage;
        const end = start + itemsPerPage;

        // Affichage des lignes filtrées et paginées
        filtered.slice(start, end).forEach(row => {
            row.style.display = '';
            const detailsRow = row.nextElementSibling;
            if (detailsRow && detailsRow.classList.contains('collapse')) {
                detailsRow.style.display = '';
            }
        });
    }

    searchInput.addEventListener('input', () => {
        currentPage = 1;
        filterAndPaginate();
    });

    filterStatus.addEventListener('change', () => {
        currentPage = 1;
        filterAndPaginate();
    });

    filterAndPaginate();

    // Export PDF
    const exportBtn = document.getElementById('exportPdfBtn');
    exportBtn.addEventListener('click', () => {
        import('https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js').then(jsPDFModule => {
            const { jsPDF } = jsPDFModule;
            const doc = new jsPDF();
            const title = document.querySelector('h2')?.textContent || 'Liste des paiements';
            doc.text(title, 10, 10);
            let y = 20;

            rows.forEach(row => {
                if (row.style.display !== 'none') {
                    const name = row.cells[0].textContent.trim();
                    const total = row.cells[1].textContent.trim();
                    const statut = row.cells[2].textContent.trim();
                    doc.text(`${name} | ${total} | ${statut}`, 10, y);
                    y += 10;
                }
            });

            const filename = title.replace(/\s+/g, '_').toLowerCase() + '.pdf';
            doc.save(filename);
        });
    });
});
