document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const email = form.querySelector('input[name="email"]');

    form.addEventListener('submit', (e) => {
        if (!email.value.trim()) {
            e.preventDefault();
            toastr.error("Veuillez saisir une adresse email valide.");
            email.focus();
        }
    });
});
