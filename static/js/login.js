document.addEventListener('DOMContentLoaded', function() {
    // Afficher les notifications Toastr pour les messages flash
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                if ('{{ category }}' === 'success') {
                    toastr.success('{{ message }}', 'Succès');
                } else if ('{{ category }}' === 'danger') {
                    toastr.error('{{ message }}', 'Erreur');
                } else if ('{{ category }}' === 'info') {
                    toastr.info('{{ message }}', 'Information');
                } else if ('{{ category }}' === 'warning') {
                    toastr.warning('{{ message }}', 'Avertissement');
                }
            {% endfor %}
        {% endif %}
    {% endwith %}
});
