document.addEventListener("DOMContentLoaded", function () {
  const choicesContainer = document.getElementById("choicesContainer");
  const questionInput = document.getElementById("questionInput");
  let choiceIndex = document.querySelectorAll("#choicesContainer .choice-item").length;

  // Mise à jour du compteur de caractères
  questionInput.addEventListener("input", (e) => {
    document.getElementById("charCount").textContent = e.target.value.length;
  });

  // Ajouter un nouveau champ de choix
  window.addChoice = function () {
    const div = document.createElement("div");
    div.className = "choice-item input-group mb-2";
    div.setAttribute("data-index", choiceIndex);

    const input = document.createElement("input");
    input.type = "text";
    input.name = `choices-${choiceIndex}-choice_text`;
    input.className = "form-control";
    input.placeholder = "Texte du choix";

    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "btn btn-outline-danger";
    removeBtn.innerHTML = "&times;";
    removeBtn.onclick = () => div.remove();

    div.appendChild(input);
    div.appendChild(removeBtn);
    choicesContainer.appendChild(div);

    choiceIndex++;
  };

  // Supprimer un champ de choix
  window.removeChoice = function (btn) {
    const parent = btn.closest(".choice-item");
    if (parent) parent.remove();
  };

  // Validation du formulaire avant soumission
  window.validatePollForm = function () {
    const endDateInput = document.getElementById("endDateInput");
    const endDate = endDateInput.value;
    const endDateObj = new Date(endDate);
    const now = new Date();

    if (!endDate || isNaN(endDateObj.getTime())) {
      alert("Veuillez entrer une date de fin valide.");
      endDateInput.focus();
      return false;
    }

    if (endDateObj < now) {
      alert("La date de fin ne peut pas être dans le passé.");
      endDateInput.focus();
      return false;
    }

    const inputs = choicesContainer.querySelectorAll("input");
    const values = new Set();

    for (const input of inputs) {
      const val = input.value.trim();
      if (!val) {
        alert("Tous les choix doivent être remplis.");
        input.focus();
        return false;
      }
      if (values.has(val)) {
        alert(`Le choix '${val}' est dupliqué.`);
        input.focus();
        return false;
      }
      values.add(val);
    }

    if (values.size === 0) {
      alert("Veuillez ajouter au moins un choix.");
      return false;
    }

    return true;
  };
});
