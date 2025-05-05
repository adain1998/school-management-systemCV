// app.js

document.addEventListener('DOMContentLoaded', () => {
    // Initialisation de Select2 pour le menu déroulant des langues
    $('.select2').select2({
        width: '100%',
        minimumResultsForSearch: Infinity
    });

    // Redirection lors du changement de langue
    const languageSelect = document.getElementById('language');
    if (languageSelect) {
        languageSelect.addEventListener('change', function () {
            const selectedLang = this.value;
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('language', selectedLang);
            window.location.href = currentUrl.toString();
        });
    }

    // Validation du formulaire avec SweetAlert2
    const loginForm = document.querySelector('form[name="loginform"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function (e) {
            const username = loginForm.querySelector('input[name="username"]');
            const password = loginForm.querySelector('input[name="password"]');

            if (!username.value.trim() || !password.value.trim()) {
                e.preventDefault();
                Swal.fire({
                    icon: 'warning',
                    title: 'Champs requis',
                    text: 'Veuillez remplir tous les champs obligatoires.',
                    confirmButtonText: 'OK'
                });
            }
        });
    }

    // Initialisation des animations AOS
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true
    });
});
