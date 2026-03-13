document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-student');
    const rows = document.querySelectorAll('#studentsTable tbody tr');

    searchInput.addEventListener('keyup', () => {
        const filter = searchInput.value.toLowerCase();
        rows.forEach(row => {
            const name = row.cells[1].textContent.toLowerCase();
            row.style.display = name.includes(filter) ? '' : 'none';
        });
    });
});
