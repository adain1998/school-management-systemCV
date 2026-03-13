document.addEventListener("DOMContentLoaded", function () {
    // Animation de fade-in sur la carte
    const card = document.querySelector(".card");
    if (card) {
        card.classList.add("fade-in");
    }

    // Affichage toast de bienvenue
    const userName = document.querySelector("h1").textContent;
    showToast(`👋 Bienvenue ${userName}`);

    // Affichage heure dynamique (si souhaité)
    const datePara = document.querySelector("p strong + text");
    const currentTime = document.createElement("p");
    currentTime.classList.add("text-muted", "mt-2");
    document.querySelector(".card-body").appendChild(currentTime);

    setInterval(() => {
        const now = new Date();
        const timeStr = now.toLocaleTimeString("fr-FR", { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        currentTime.textContent = "Heure actuelle : " + timeStr;
    }, 1000);

    // Animation au survol du bouton
    const button = document.querySelector(".btn-primary");
    if (button) {
        button.addEventListener("mouseenter", () => {
            button.classList.add("shadow-lg");
        });
        button.addEventListener("mouseleave", () => {
            button.classList.remove("shadow-lg");
        });
    }
});

// Fonction d'affichage de toast simple
function showToast(message) {
    const toast = document.createElement("div");
    toast.textContent = message;
    toast.style.position = "fixed";
    toast.style.bottom = "20px";
    toast.style.right = "20px";
    toast.style.backgroundColor = "#333";
    toast.style.color = "#fff";
    toast.style.padding = "12px 18px";
    toast.style.borderRadius = "6px";
    toast.style.boxShadow = "0 0 10px rgba(0,0,0,0.3)";
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.5s";

    document.body.appendChild(toast);

    setTimeout(() => toast.style.opacity = "1", 100);
    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 500);
    }, 4000);
}
