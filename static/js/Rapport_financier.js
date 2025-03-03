// Fonction pour trier le tableau
function sortTable(columnIndex) {
    let table = document.getElementById("reportTable");
    let rows = Array.from(table.rows).slice(1);
    let ascending = table.dataset.sortDirection === "asc";

    rows.sort((rowA, rowB) => {
        let cellA = rowA.cells[columnIndex].textContent.trim();
        let cellB = rowB.cells[columnIndex].textContent.trim();

        let valueA = isNaN(cellA) ? cellA : parseFloat(cellA);
        let valueB = isNaN(cellB) ? cellB : parseFloat(cellB);

        return ascending ? valueA > valueB : valueA < valueB;
    });

    table.dataset.sortDirection = ascending ? "desc" : "asc";
    rows.forEach(row => table.appendChild(row));
}

// Fonction pour exporter en CSV
function exportToCSV() {
    let table = document.getElementById("reportTable");
    let csvContent = "data:text/csv;charset=utf-8,";

    for (let row of table.rows) {
        let rowData = Array.from(row.cells).map(cell => cell.textContent).join(",");
        csvContent += rowData + "\n";
    }

    let encodedUri = encodeURI(csvContent);
    let link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "rapport_financier.csv");
    document.body.appendChild(link);
    link.click();
}

// Fonction pour ajouter en-tête et pied de page
function addHeaderAndFooter(doc) {
    const pageCount = doc.internal.getNumberOfPages();

    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);

        // En-tête
        doc.setFontSize(10);
        doc.text("Nom de l'École", 15, 10);
        doc.text("Rapport Financier", 15, 20);

        // Pied de page
        doc.text(`Page ${i} sur ${pageCount}`, doc.internal.pageSize.getWidth() - 20, doc.internal.pageSize.getHeight() - 10, { align: 'right' });
    }
}

// Fonction pour exporter en PDF
function exportToPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    // Titre du document
    doc.setFontSize(16);
    doc.text("Rapport Financier", 14, 15);

    // Ajouter le tableau
    doc.autoTable({
        html: '#reportTable',
        startY: 25,
        theme: 'grid',
        headStyles: { fillColor: [22, 160, 133] },
        styles: { fontSize: 10 },
        didDrawPage: function (data) {
            addHeaderAndFooter(doc);
        }
    });

    doc.save("rapport_financier.pdf");
}

// Fonction pour exporter en Excel
function exportToExcel() {
    let table = document.getElementById("reportTable");
    let wb = XLSX.utils.book_new();
    let ws = XLSX.utils.table_to_sheet(table);

    XLSX.utils.book_append_sheet(wb, ws, "Rapport");
    XLSX.writeFile(wb, "rapport_financier.xlsx");
}
