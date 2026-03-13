document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-matiere');
    const tableRows = document.querySelectorAll('#noteTableBody tr');
    const resetBtn = document.getElementById('reset-filters');

    searchInput.addEventListener('keyup', function () {
        const filter = this.value.toLowerCase();
        tableRows.forEach(row => {
            const matiere = row.cells[1].textContent.toLowerCase();
            row.style.display = matiere.includes(filter) ? '' : 'none';
        });
    });

    resetBtn.addEventListener('click', () => {
        searchInput.value = '';
        tableRows.forEach(row => row.style.display = '');
    });

    // Export CSV
    document.getElementById('exportCSV').addEventListener('click', () => {
        let csv = 'N°,Matière,Score\n';
        tableRows.forEach((row, index) => {
            const cells = row.querySelectorAll('td');
            csv += `${index + 1},"${cells[1].textContent}","${cells[2].textContent}"\n`;
        });
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        saveAs(blob, `notes_${window.studentLastName}.csv`);
    });

    // Export PDF
    document.getElementById('exportPDF').addEventListener('click', () => {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        doc.text(`Liste des Notes - ${window.studentFirstName} ${window.studentLastName}`, 10, 10);
        let y = 20;
        tableRows.forEach((row, i) => {
            const cells = row.querySelectorAll('td');
            doc.text(`${i + 1}. ${cells[1].textContent} : ${cells[2].textContent}`, 10, y);
            y += 10;
        });
        doc.save(`notes_${window.studentLastName}.pdf`);
    });
});
