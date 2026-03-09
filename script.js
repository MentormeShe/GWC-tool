// Confetti 🎉 function
function launchConfetti() {
    const duration = 3 * 1000;
    const end = Date.now() + duration;

    (function frame() {
        confetti({
            particleCount: 5,
            angle: 60,
            spread: 60,
            origin: { x: 0 }
        });
        confetti({
            particleCount: 5,
            angle: 120,
            spread: 60,
            origin: { x: 1 }
        });
        if (Date.now() < end) {
            requestAnimationFrame(frame);
        }
    }());
}

// Trigger confetti for cleared users
document.addEventListener("DOMContentLoaded", function() {
    const clearedUsers = document.querySelectorAll(".strike-cleared");
    clearedUsers.forEach(user => {
        user.addEventListener("click", launchConfetti);
    });
});            } else {
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
