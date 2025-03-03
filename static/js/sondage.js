<script>
    // Fonction pour ajouter un nouveau choix
    function addChoice() {
        const choicesDiv = document.getElementById('choices');
        const index = choicesDiv.children.length;

        // Créer un conteneur pour le nouveau choix
        const newChoice = document.createElement('div');
        newChoice.classList.add('input-group', 'mb-2');
        newChoice.setAttribute('id', `choice-${index}`);

        // Créer le champ de saisie pour le choix
        const input = document.createElement('input');
        input.type = 'text';
        input.name = `choices-${index}-choice_text`;
        input.classList.add('form-control');
        input.placeholder = 'Entrez un choix';

        // Créer le bouton de suppression
        const button = document.createElement('button');
        button.type = 'button';
        button.classList.add('btn', 'btn-danger');
        button.textContent = 'Supprimer';
        button.onclick = function() {
            removeChoice(index);
        };

        // Ajouter le champ de saisie et le bouton au conteneur
        newChoice.appendChild(input);
        newChoice.appendChild(button);

        // Ajouter le nouveau choix au div 'choices'
        choicesDiv.appendChild(newChoice);
    }

    // Fonction pour supprimer un choix
    function removeChoice(index) {
        const choice = document.getElementById(`choice-${index}`);
        if (choice) {
            choice.remove();
        }
    }
</script>
