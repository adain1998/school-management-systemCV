// static/js/dashboard.js
document.addEventListener('DOMContentLoaded', () => {
    const chartCanvas = document.getElementById('statsChart');

    if (!chartCanvas) {
        console.warn('Élément canvas statsChart introuvable.');
        return;
    }

    const labels = [
        'Étudiants', 'Enseignants', 'Notes', 'Absences',
        'Présences', 'Messages', 'Forum', 'Rapports',
        'Infos école', 'Sondages'
    ];

    const chartData = {
        labels: labels,
        datasets: [{
            label: 'Total',
            data: JSON.parse(chartCanvas.dataset.counts || '[]'),
            backgroundColor: [
                '#007bff', '#28a745', '#17a2b8', '#ffc107',
                '#6f42c1', '#fd7e14', '#20c997', '#dc3545',
                '#6610f2', '#e83e8c'
            ],
        }]
    };

    const config = {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    };

    new Chart(chartCanvas.getContext('2d'), config);
});
