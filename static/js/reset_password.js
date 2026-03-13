document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const email = form.querySelector('input[name="email"]');

    form.addEventListener('submit', (event) => {
        if (!email.value.trim()) {
            event.preventDefault();
            toastr.error("Veuillez entrer votre adresse email.");
            email.focus();
        }
    });
});
