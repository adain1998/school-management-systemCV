document.addEventListener("DOMContentLoaded", function () {
  const table = document.querySelector("#paiementsTable");
  if (!table) return;

  // 💡 Init DataTables avec options FR
  const dataTable = $(table).DataTable({
    responsive: true,
    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/fr-FR.json"
    },
    pageLength: 10,
    lengthMenu: [5, 10, 25, 50],
    columnDefs: [
      { orderable: false, targets: -1 }
    ]
  });

  // ✅ Confirmation douce pour suppression
  document.querySelectorAll("a.btn-outline-danger").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      if (!confirm("⚠️ Confirmez-vous la suppression de ce paiement ?")) {
        e.preventDefault();
      }
    });
  });

  // ✨ Mise en surbrillance d’une ligne lors du clic
  document.querySelectorAll("tbody tr").forEach((row) => {
    row.addEventListener("click", () => {
      row.classList.add("table-primary");
      setTimeout(() => row.classList.remove("table-primary"), 800);
    });
  });

  // 🎯 Filtre par statut
  const filter = document.createElement("div");
  filter.className = "d-flex justify-content-end align-items-center gap-2 mb-3";
  filter.innerHTML = `
    <label for="statutFilter" class="form-label m-0">Filtrer par statut :</label>
    <select id="statutFilter" class="form-select form-select-sm w-auto">
      <option value="">Tous</option>
      <option value="payé">Payé</option>
      <option value="en attente">En attente</option>
      <option value="autre">Autre</option>
    </select>
    <button id="toggleTheme" class="btn btn-sm btn-outline-dark" title="Changer le thème">
      <i class="bi bi-circle-half"></i>
    </button>
  `;
  table.parentElement.parentElement.insertBefore(filter, table.parentElement);

  document.getElementById("statutFilter").addEventListener("change", function () {
    const value = this.value.toLowerCase();
    dataTable.rows().every(function () {
      const statut = this.data()[6].toLowerCase();
      this.nodes().to$().toggle(
        value === "" || statut.includes(value)
      );
    });
  });

  // 🌗 Thème clair/sombre dynamique
  const toggleTheme = document.getElementById("toggleTheme");
  toggleTheme.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
    localStorage.setItem("theme", document.body.classList.contains("dark-mode") ? "dark" : "light");
  });
  if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark-mode");
  }

  // 📊 Intégration graphique des paiements
  const statsContainer = document.createElement("div");
  statsContainer.className = "my-4";
  statsContainer.innerHTML = `<canvas id="paiementChart" height="100"></canvas>`;
  table.parentElement.after(statsContainer);

  const counts = { payé: 0, "en attente": 0, autre: 0 };
  dataTable.rows().every(function () {
    const statut = this.data()[6].toLowerCase();
    if (statut.includes("payé")) counts.payé++;
    else if (statut.includes("en attente")) counts["en attente"]++;
    else counts.autre++;
  });

  new Chart(document.getElementById("paiementChart").getContext("2d"), {
    type: 'doughnut',
    data: {
      labels: ['Payé', 'En attente', 'Autre'],
      datasets: [{
        data: [counts.payé, counts["en attente"], counts.autre],
        backgroundColor: ['#198754', '#ffc107', '#6c757d']
      }]
    },
    options: {
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  });
});
