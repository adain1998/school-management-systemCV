// scripts.js

document.addEventListener('DOMContentLoaded', function() {
    // Exemple : Afficher une alerte lors du clic sur une classe
    const classItems = document.querySelectorAll('.list-group-item');
    classItems.forEach(item => {
        item.addEventListener('click', function() {
            alert(`Vous avez sélectionné la classe : ${this.textContent}`);
        });
    });
});
