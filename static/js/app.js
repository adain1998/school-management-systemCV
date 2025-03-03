document.getElementById('add-student').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    const studentData = {};
    formData.forEach((value, key) => {
        studentData[key] = value;
    });

    await fetch('/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(studentData),
    });

    location.reload();  // Recharge la page pour afficher le nouvel élève ajouté.
});
