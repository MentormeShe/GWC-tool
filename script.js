// ---------- POPUP GREETINGS ----------
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(() => {
        const popup = document.createElement("div");
        popup.innerHTML = "✨ Welcome to Mentor Me Collective Dashboard! 🚀";
        popup.style.position = "fixed";
        popup.style.bottom = "20px";
        popup.style.right = "20px";
        popup.style.padding = "15px 25px";
        popup.style.background = "linear-gradient(90deg, #ff9966, #ff5e62)";
        popup.style.color = "white";
        popup.style.fontSize = "1em";
        popup.style.borderRadius = "12px";
        popup.style.boxShadow = "0 4px 12px rgba(0,0,0,0.3)";
        popup.style.zIndex = 1000;
        popup.style.animation = "fadeIn 1s ease-in-out";
        document.body.appendChild(popup);

        setTimeout(() => {
            popup.style.transition = "all 1s ease";
            popup.style.opacity = 0;
            setTimeout(() => { popup.remove(); }, 1000);
        }, 4000);
    }, 1500);
});

// ---------- RANDOM EMOJIS FOR AI SCORE ----------
function addScoreEmojis() {
    const cells = document.querySelectorAll("td");
    cells.forEach(cell => {
        let value = parseInt(cell.innerText);
        if (!isNaN(value)) {
            if (value > 500) {
                cell.innerText += " 🚀";
            } else if (value > 300) {
                cell.innerText += " 🌟";
            } else {
                cell.innerText += " ⚡";
            }
        }
    });
}

// Run after 2s delay to ensure table loaded
setTimeout(addScoreEmojis, 2000);

// ---------- CARD HOVER EFFECT ----------
const cards = document.querySelectorAll(".track-card");
cards.forEach(card => {
    card.addEventListener("mouseenter", () => {
        card.style.transform = "translateY(-10px) scale(1.05)";
        card.style.boxShadow = "0 12px 30px rgba(0,0,0,0.4)";
    });
    card.addEventListener("mouseleave", () => {
        card.style.transform = "translateY(0px) scale(1)";
        card.style.boxShadow = "0 4px 8px rgba(0,0,0,0.15)";
    });
});
