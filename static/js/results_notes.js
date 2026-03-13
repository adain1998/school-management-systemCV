document.addEventListener('DOMContentLoaded', function () {
  // Récupération des données JSON
  const dataContainer = document.getElementById('results-data');
  if (!dataContainer) return;

  const data = JSON.parse(dataContainer.textContent || dataContainer.innerText);
  const labels = data.map(d => d.name);
  const values = data.map(d => d.average);

  // Remplir le champ caché pour l'export CSV
  const hiddenField = document.getElementById('results');
  if (hiddenField) {
    hiddenField.value = JSON.stringify(data);
  }

  // Génération du graphique avec Chart.js
  const ctx = document.getElementById('noteChart');
  if (ctx && window.Chart) {
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Moyennes par élève',
          data: values,
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            max: 20
          }
        }
      }
    });
  }

  // Fonction Export PDF
  const exportPdfBtn = document.getElementById('exportPdfBtn');
  if (exportPdfBtn) {
    exportPdfBtn.addEventListener('click', async (e) => {
      e.preventDefault();

      const { jsPDF } = window.jspdf;
      const doc = new jsPDF();

      // 1. Capturer le tableau HTML (les résultats)
      const table = document.querySelector('table');
      const canvasTable = await html2canvas(table, { scale: 2 });
      const imgDataTable = canvasTable.toDataURL('image/png');

      // 2. Capturer le canvas Chart.js
      const canvasChart = document.getElementById('noteChart');
      const imgDataChart = canvasChart.toDataURL('image/png');

      const pageWidth = doc.internal.pageSize.getWidth();
      let y = 10;

      // Titre
      doc.setFontSize(18);
      doc.text("Résultats des Notes", pageWidth / 2, y, { align: 'center' });
      y += 10;

      // Moyenne générale
      const generalAverage = document.querySelector('.alert-info strong')?.textContent || '';
      doc.setFontSize(12);
      doc.text(`Moyenne générale de la classe : ${generalAverage} / 20`, 10, y);
      y += 10;

      // Ajouter tableau image au PDF
      const imgPropsTable = doc.getImageProperties(imgDataTable);
      const tableWidth = pageWidth - 20; // marges 10 + 10
      const tableHeight = (imgPropsTable.height * tableWidth) / imgPropsTable.width;
      doc.addImage(imgDataTable, 'PNG', 10, y, tableWidth, tableHeight);
      y += tableHeight + 10;

      // Ajouter graphique image au PDF
      const imgPropsChart = doc.getImageProperties(imgDataChart);
      const chartWidth = pageWidth - 20;
      const chartHeight = (imgPropsChart.height * chartWidth) / imgPropsChart.width;
      doc.addImage(imgDataChart, 'PNG', 10, y, chartWidth, chartHeight);

      // Sauvegarder PDF
      doc.save('resultats_notes.pdf');
    });
  }
});
