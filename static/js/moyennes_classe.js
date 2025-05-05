// Activer DataTables pour améliorer l'affichage du tableau
$(document).ready(function () {
    $('#table-moyennes').DataTable({
        "paging": true,
        "searching": true,
        "ordering": true,
        "info": true,
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.11.5/i18n/French.json"
        }
    });

    // Afficher un message de succès avec Toastr après le chargement de la page
    toastr.options = {
        "closeButton": true,
        "progressBar": true,
        "positionClass": "toast-top-right",
        "timeOut": "3000"
    };

    toastr.success("Les moyennes ont été chargées avec succès !");
});

// Fonction pour rafraîchir la page avec effet animé
function rafraichirPage() {
    $("body").fadeOut(300, function () {
        location.reload();
    });
}

// Gérer le changement de classe dynamiquement
$("#classe").change(function () {
    let selectedClass = $(this).val();
    if (selectedClass) {
        window.location.href = `/moyennes/${selectedClass}`;
    }
});

// Bouton pour télécharger les moyennes sous format CSV
$("#export-csv").click(function () {
    let table = $("#table-moyennes").DataTable();
    let csv = [];

    table.rows().every(function () {
        let row = this.data();
        csv.push(row.join(","));
    });

    let csvContent = "data:text/csv;charset=utf-8," + csv.join("\n");
    let encodedUri = encodeURI(csvContent);
    let link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "moyennes_classe.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    toastr.info("Le fichier CSV a été téléchargé.");
});
