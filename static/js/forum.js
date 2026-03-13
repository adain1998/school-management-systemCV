document.addEventListener("DOMContentLoaded", () => {
    const reactionButtons = document.querySelectorAll(".reaction-btn");

    reactionButtons.forEach(button => {
        button.addEventListener("click", async () => {
            const postCard = button.closest("[data-post-id]");
            const postId = postCard?.dataset.postId;
            const reactionType = button.dataset.reaction;

            if (!postId || !reactionType) {
                console.warn("Post ID ou type de réaction manquant.");
                return;
            }

            try {
                const response = await fetch(`/api/reactions/${postId}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: JSON.stringify({ reaction: reactionType }),
                });

                if (!response.ok) {
                    throw new Error(`Erreur serveur (${response.status})`);
                }

                const data = await response.json();
                updateReactionStats(postCard, data.reactions);
            } catch (error) {
                console.error("Erreur lors de l'envoi de la réaction :", error);
                alert("Une erreur est survenue lors de l’enregistrement de votre réaction.");
            }
        });
    });

    /**
     * Met à jour l'affichage des statistiques de réactions pour un post.
     */
    function updateReactionStats(postElement, reactions) {
        const statsDiv = postElement.querySelector(".reaction-stats");
        if (!statsDiv) return;

        // Compter les types de réactions
        const counts = {
            like: 0,
            love: 0,
            haha: 0,
            wow: 0,
            sad: 0,
            angry: 0,
        };

        reactions.forEach(r => {
            if (counts.hasOwnProperty(r.reaction_type)) {
                counts[r.reaction_type]++;
            }
        });

        // Réinitialiser le HTML
        statsDiv.innerHTML = "";

        for (const [type, count] of Object.entries(counts)) {
            if (count > 0) {
                const emoji = getEmojiForReaction(type);
                const span = document.createElement("span");
                span.className = "reaction-count me-2";
                span.textContent = `${count} ${emoji}`;
                statsDiv.appendChild(span);
            }
        }
    }

    /**
     * Retourne l’emoji associé à un type de réaction.
     */
    function getEmojiForReaction(type) {
        switch (type) {
            case "like": return "👍";
            case "love": return "❤️";
            case "haha": return "😂";
            case "wow": return "😮";
            case "sad": return "😢";
            case "angry": return "😡";
            default: return "";
        }
    }

    /**
     * Récupère le token CSRF depuis les cookies (Flask-WTF).
     */
    function getCSRFToken() {
        const match = document.cookie.match(/csrf_token=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : "";
    }
});
