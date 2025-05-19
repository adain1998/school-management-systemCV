<script>
document.addEventListener('DOMContentLoaded', () => {
    const students = {{ students | tojson }};
    if (!Array.isArray(students) || students.length === 0) {
        console.warn("Aucune donnée étudiant disponible.");
        document.querySelectorAll('canvas').forEach(canvas => {
            canvas.insertAdjacentHTML('beforebegin', "<p class='text-danger'>Données indisponibles pour ce graphique.</p>");
            canvas.remove();
        });
        return;
    }

    const fullNames = students.map(s => `${s.first_name || ''} ${s.last_name || ''}`.trim());
    const avgGrades = students.map(s => s.avg_grade ?? 0);
    const attendanceRates = students.map(s => s.attendance_rate ?? 0);
    const absencesCounts = students.map(s => s.absences_count ?? 0);
    const completedAssignments = students.map(s => s.completed_assignments ?? 0);
    const totalAssignments = students.map(s => s.total_assignments ?? 0);

    const getColorPalette = (count, base = 'rgba(75, 192, 192,') => {
        return Array.from({ length: count }, (_, i) => `${base} ${0.2 + 0.1 * (i % 5)})`);
    };

    function createChart({ id, type, label, data, colors, borderColors = null, extraDataset = null }) {
        const canvas = document.getElementById(id);
        if (!canvas) {
            console.error(`Élément avec l'ID ${id} non trouvé.`);
            return;
        }

        const ctx = canvas.getContext('2d');
        new Chart(ctx, {
            type: type,
            data: {
                labels: fullNames,
                datasets: [
                    {
                        label: label,
                        data: data,
                        backgroundColor: colors,
                        borderColor: borderColors || colors.map(c => c.replace('0.2', '1')),
                        borderWidth: 1,
                        tension: type === 'line' ? 0.4 : 0
                    },
                    ...(extraDataset ? [extraDataset] : [])
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 800,
                    easing: 'easeInOutQuad'
                },
                plugins: {
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            label: context => `${context.dataset.label}: ${context.parsed.y ?? context.parsed}`
                        }
                    },
                    legend: {
                        display: type !== 'bar' || (extraDataset !== null),
                        position: 'bottom'
                    }
                },
                scales: ['bar', 'line'].includes(type) ? {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: label
                        }
                    }
                } : {}
            }
        });
    }

    // Moyenne des notes
    createChart({
        id: 'avgGradeChart',
        type: 'bar',
        label: 'Moyenne des notes',
        data: avgGrades,
        colors: getColorPalette(fullNames.length)
    });

    // Taux de présence
    createChart({
        id: 'attendanceChart',
        type: 'pie',
        label: 'Taux de présence (%)',
        data: attendanceRates,
        colors: getColorPalette(fullNames.length, 'rgba(255, 159, 64,')
    });

    // Devoirs
    createChart({
        id: 'assignmentsChart',
        type: 'line',
        label: 'Devoirs complétés',
        data: completedAssignments,
        colors: getColorPalette(fullNames.length, 'rgba(153, 102, 255,'),
        extraDataset: {
            label: 'Total des devoirs',
            data: totalAssignments,
            backgroundColor: 'rgba(255, 206, 86, 0.3)',
            borderColor: 'rgba(255, 206, 86, 1)',
            borderWidth: 1
        }
    });

    // Absences
    createChart({
        id: 'absencesChart',
        type: 'doughnut',
        label: 'Nombre d\'absences',
        data: absencesCounts,
        colors: getColorPalette(fullNames.length, 'rgba(255, 99, 132,')
    });
});
// Affichage du tableau
const tbody = document.getElementById('studentTableBody');
students.forEach((s, index) => {
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${s.first_name} ${s.last_name}</td>
        <td>${s.avg_grade ?? 0}</td>
        <td>${s.attendance_rate ?? 0}%</td>
        <td>${s.absences_count ?? 0}</td>
        <td>${s.completed_assignments ?? 0}</td>
        <td>${s.total_assignments ?? 0}</td>
    `;
    tbody.appendChild(row);
});

</script>
