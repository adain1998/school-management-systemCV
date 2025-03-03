document.addEventListener("DOMContentLoaded", function () {
    toggleFields();

    document.getElementById("role").addEventListener("change", toggleFields);
    document.querySelector("form").addEventListener("submit", validateForm);

    function toggleFields() {
        let role = document.getElementById("role").value;

        document.getElementById("specialite_field").style.display = (role === "enseignant") ? "block" : "none";
        document.getElementById("niveau_field").style.display = (role === "eleve") ? "block" : "none";
        document.getElementById("role_admin_field").style.display = (role === "administrateur") ? "block" : "none";
    }

    function validateForm(event) {
        event.preventDefault(); // Empêche l'envoi du formulaire par défaut

        let username = document.getElementById("username").value.trim();
        let email = document.getElementById("email").value.trim();
        let password = document.getElementById("password").value;
        let confirmPassword = document.getElementById("confirm_password").value;

        if (username === "" || email === "" || password === "") {
            toastr.error("Tous les champs obligatoires doivent être remplis.", "Erreur de validation");
            return;
        }

        if (!validateEmail(email)) {
            toastr.warning("Veuillez entrer une adresse email valide.", "Format email incorrect");
            return;
        }

        if (password.length < 8) {
            toastr.warning("Le mot de passe doit contenir au moins 8 caractères.", "Mot de passe trop court");
            return;
        }

        if (password !== confirmPassword) {
            toastr.error("Les mots de passe ne correspondent pas.", "Erreur de validation");
            return;
        }

        toastr.success("Inscription en cours...", "Succès");
        setTimeout(() => event.target.submit(), 1500); // Soumission après validation
    }

    function validateEmail(email) {
        let re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
});
