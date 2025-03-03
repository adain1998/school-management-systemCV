// detail_frais.js

$(document).ready(function() {
    // Initialisation de Toastr pour les notifications
    toastr.options = {
        "closeButton": true,   // Bouton de fermeture
        "progressBar": true,   // Barre de progression
        "positionClass": "toast-top-right",  // Position de la notification
        "timeOut": "5000",      // Temps d'affichage en ms
        "extendedTimeOut": "1000",  // Temps d'extension après survol
    };

    // Initialisation du calendrier avec FullCalendar
    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        dateClick: function(info) {
            // Action à effectuer lorsque l'on clique sur une date
            toastr.info('Vous avez sélectionné la date: ' + info.dateStr);  // Notification Toastr
            // Redirection ou autre action peut être ajoutée ici
        },
        events: [
            // Exemple d'événements dynamiques
            {
                title: 'Frais dûs',
                start: '2024-01-10',
                end: '2024-01-12',
                backgroundColor: 'red', // Vous pouvez personnaliser les couleurs
                textColor: 'white'
            },
            {
                title: 'Frais payés',
                start: '2024-01-15',
                end: '2024-01-17',
                backgroundColor: 'green',
                textColor: 'white'
            }
        ],
        eventClick: function(info) {
            // Exemple d'événement à cliquer pour notifier l'utilisateur
            toastr.success('Vous avez cliqué sur l\'événement: ' + info.event.title);
        }
    });

    calendar.render();

    // Exemple de Toastr pour un événement de chargement ou d'erreur
    toastr.success("Le calendrier a été chargé avec succès !");
});
