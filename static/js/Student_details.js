document.addEventListener('DOMContentLoaded', () => {
    const mainForm = document.querySelector('form');  // Formulaire principal
    const contactForm = document.querySelector('form[action*="contact_student"]'); // Formulaire de contact

    if (mainForm) {
        const inputs = mainForm.querySelectorAll('input');
        const submitBtn = mainForm.querySelector('button[type="submit"]');

        const initialValues = {};
        inputs.forEach(input => {
            initialValues[input.name] = input.value;
        });

        function hasChanged() {
            return Array.from(inputs).some(input => input.value !== initialValues[input.name]);
        }

        mainForm.addEventListener('input', () => {
            submitBtn.disabled = !hasChanged();
        });

        mainForm.addEventListener('submit', (e) => {
            let errors = [];

            const firstName = mainForm.first_name.value.trim();
            const lastName = mainForm.last_name.value.trim();
            const paiement = mainForm.paiement.value;
            const debt = mainForm.debt.value;

            if (!firstName || !lastName) {
                errors.push("Le prénom et le nom sont requis.");
            }

            if (paiement && parseFloat(paiement) < 0) {
                errors.push("Le montant payé ne peut pas être négatif.");
            }

            if (debt && parseFloat(debt) < 0) {
                errors.push("La dette ne peut pas être négative.");
            }

            if (errors.length > 0) {
                e.preventDefault();
                alert(errors.join("\n"));
                return false;
            }

            const confirmed = confirm("Êtes-vous sûr de vouloir mettre à jour les informations ?");
            if (!confirmed) {
                e.preventDefault();
                return false;
            }
        });

        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                if (input.required && !input.value.trim()) {
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });
        });
    }

    if (contactForm) {
        const emailInput = contactForm.querySelector('input[name="email"]');
        const messageInput = contactForm.querySelector('textarea[name="message"]');
        const contactBtn = contactForm.querySelector('button[type="submit"]');

        contactForm.addEventListener('submit', (e) => {
            const email = emailInput.value.trim();
            const message = messageInput.value.trim();
            let errors = [];

            // Validation simple de l'email
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!email || !emailPattern.test(email)) {
                errors.push("Veuillez entrer une adresse email valide.");
            }

            if (!message) {
                errors.push("Le message ne peut pas être vide.");
            }

            if (errors.length > 0) {
                e.preventDefault();
                alert(errors.join("\n"));
                return false;
            }

            const confirmed = confirm("Voulez-vous vraiment envoyer ce message ?");
            if (!confirmed) {
                e.preventDefault();
                return false;
            }
        });

        [emailInput, messageInput].forEach(input => {
            input.addEventListener('blur', () => {
                if (input.required && !input.value.trim()) {
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });
        });
    }
});
