document.addEventListener('DOMContentLoaded', function () {
    // Initialisation des animations AOS
    AOS.init();

    // Fonction pour charger plus d'élèves via AJAX
    const loadMoreButton = document.getElementById('load-more-btn');
    if (loadMoreButton) {
        loadMoreButton.addEventListener('click', function () {
            loadMoreButton.disabled = true; // Désactive le bouton pendant le chargement

            // Requête AJAX pour charger plus d'élèves (page 2 par exemple)
            fetch('/api/students?page=2')
                .then(response => response.json())
                .then(data => {
                    const studentsList = document.getElementById('students');
                    const students = data.students;

                    // Ajout des élèves à la liste existante
                    students.forEach(student => {
                        const li = document.createElement('li');
                        li.classList.add('list-group-item', 'd-flex', 'justify-content-between');
                        li.setAttribute('data-aos', 'fade-up');
                        li.innerHTML = `<span>${student.first_name} ${student.last_name}</span>
                                       <span class="badge bg-secondary">Classe: ${student.class_name}</span>`;
                        studentsList.appendChild(li);
                    });

                    loadMoreButton.disabled = false; // Réactive le bouton après le chargement
                })
                .catch(err => {
                    console.error('Erreur lors du chargement des étudiants :', err);
                    loadMoreButton.disabled = false; // Réactive le bouton en cas d'erreur
                });
        });
    }
});
