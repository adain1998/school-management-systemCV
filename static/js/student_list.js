<script>
document.addEventListener('DOMContentLoaded', () => {
    // === MENU RESPONSIVE ===
    const navbarToggler = document.querySelector(".navbar-toggler");
    const navbarCollapse = document.querySelector("#navbarNav");
    if (navbarToggler) {
        navbarToggler.addEventListener("click", () => {
            navbarCollapse.classList.toggle("show");
        });
    }

    // === FERMETURE AUTOMATIQUE DES MESSAGES FLASH ===
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.classList.add('fade');
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });

    // === CHAMP DE RECHERCHE ===
    const searchBar = document.querySelector('.search-bar');
    if (searchBar) {
        const searchInput = searchBar.querySelector('input');
        const searchButton = searchBar.querySelector('button');
        searchButton.addEventListener('click', event => {
            event.preventDefault();
            const query = searchInput.value.trim();
            if (query.length < 3) {
                alert("Veuillez entrer au moins 3 caractères pour la recherche.");
            } else {
                searchBar.submit();
            }
        });

        searchInput.addEventListener('focus', () => {
            searchInput.classList.add('border-primary', 'shadow');
        });
        searchInput.addEventListener('blur', () => {
            searchInput.classList.remove('border-primary', 'shadow');
        });
    }

    // === CONFIRMATION SUPPRESSION ===
    const deleteButtons = document.querySelectorAll('.btn-danger, .delete-student');
    deleteButtons.forEach(button => {
        button.addEventListener('click', event => {
            const confirmed = confirm('Voulez-vous vraiment supprimer cet étudiant ? Cette action est irréversible.');
            if (!confirmed) {
                event.preventDefault();
                return;
            }

            const studentId = button.getAttribute("data-id");
            if (studentId) {
                fetch(`/delete_student/${studentId}`, {
                    method: "DELETE",
                    headers: { "Content-Type": "application/json" }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert("Étudiant supprimé avec succès.");
                        location.reload();
                    } else {
                        alert("Erreur lors de la suppression de l'étudiant.");
                    }
                })
                .catch(error => console.error("Erreur :", error));
            }
        });
    });

    // === PRÉREMPLISSAGE DU FORMULAIRE DE MODIFICATION ===
    const editForm = document.querySelector("#edit-student-form");
    if (editForm) {
        editForm.addEventListener("submit", event => {
            const nom = document.querySelector("#nom").value.trim();
            const prenom = document.querySelector("#prenom").value.trim();
            const classe = document.querySelector("#classe").value.trim();

            if (!nom || !prenom || !classe) {
                event.preventDefault();
                alert("Veuillez remplir tous les champs avant de soumettre le formulaire.");
            }
        });
    }

    // === PAGINATION : surbrillance et défilement fluide ===
    const paginationLinks = document.querySelectorAll('.pagination .page-link, .pagination a, .btn-outline-primary');
    paginationLinks.forEach(link => {
        link.addEventListener('mouseover', () => {
            link.style.backgroundColor = '#007bff';
            link.style.color = '#fff';
        });
        link.addEventListener('mouseout', () => {
            link.style.backgroundColor = '';
            link.style.color = '';
        });
        link.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });

    // === SURBRILLANCE DES LIGNES DE TABLE ===
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.classList.add('table-active');
        });
        row.addEventListener('mouseleave', () => {
            row.classList.remove('table-active');
        });
    });

    // === EFFETS SUR LES LISTES COMPACTES ===
    const compactListItems = document.querySelectorAll('.list-group-item');
    compactListItems.forEach(item => {
        item.addEventListener('mouseover', () => {
            item.style.backgroundColor = '#f8f9fa';
        });
        item.addEventListener('mouseout', () => {
            item.style.backgroundColor = '';
        });
    });

    // === BOUTON D’AJOUT D’ÉTUDIANT ===
    const addButton = document.querySelector('.btn-success');
    if (addButton) {
        addButton.addEventListener('mouseover', () => {
            addButton.style.transform = 'scale(1.05)';
        });
        addButton.addEventListener('mouseout', () => {
            addButton.style.transform = '';
        });
    }

    // === TÉLÉCHARGEMENT PDF & CSV ===
const downloadPDF = document.querySelector('#download-pdf');
const downloadCSV = document.querySelector('#download-csv');
const table = document.querySelector('table'); // adapte si nécessaire

if (downloadPDF) {
    downloadPDF.addEventListener('click', () => {
        import('https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js').then(jsPDFModule => {
            html2canvas(table).then(canvas => {
                const imgData = canvas.toDataURL('image/png');
                const { jsPDF } = jsPDFModule;
                const pdf = new jsPDF();
                const imgProps = pdf.getImageProperties(imgData);
                const pdfWidth = pdf.internal.pageSize.getWidth();
                const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
                pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
                pdf.save("tableau.pdf");
            });
        });
    });
}

if (downloadCSV) {
    downloadCSV.addEventListener('click', () => {
        let csvContent = '';
        const rows = table.querySelectorAll('tr');
        rows.forEach(row => {
            const cols = row.querySelectorAll('th, td');
            const rowData = Array.from(cols).map(cell => `"${cell.innerText.trim()}"`).join(',');
            csvContent += rowData + '\n';
        });

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "tableau.csv");
        link.style.display = "none";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
}
function deleteRow(row) {
  row.classList.add("fade-out");
  setTimeout(() => row.remove(), 500);
}
</script>
