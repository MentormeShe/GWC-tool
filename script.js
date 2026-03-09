// ===== Fun JS for Streamlit =====

// Confetti effect on success
function triggerConfetti() {
    const confettiContainer = document.createElement('div');
    confettiContainer.style.position = 'fixed';
    confettiContainer.style.top = '0';
    confettiContainer.style.left = '0';
    confettiContainer.style.width = '100%';
    confettiContainer.style.height = '100%';
    confettiContainer.style.pointerEvents = 'none';
    confettiContainer.style.zIndex = '9999';
    document.body.appendChild(confettiContainer);

    for(let i=0; i<100; i++) {
        const confetti = document.createElement('div');
        confetti.style.position = 'absolute';
        confetti.style.width = '10px';
        confetti.style.height = '10px';
        confetti.style.backgroundColor = `hsl(${Math.random()*360}, 100%, 50%)`;
        confetti.style.top = '-10px';
        confetti.style.left = Math.random()*100 + '%';
        confetti.style.opacity = Math.random();
        confetti.style.borderRadius = '50%';
        confettiContainer.appendChild(confetti);

        // Animate falling
        let duration = 2 + Math.random()*2;
        confetti.animate([
            { transform: 'translateY(0px)', opacity: confetti.style.opacity },
            { transform: `translateY(${window.innerHeight + 20}px) rotate(${Math.random()*360}deg)`, opacity: 0 }
        ], { duration: duration*1000, iterations: 1, easing: 'ease-out' });
    }

    // Remove confetti after animation
    setTimeout(() => { confettiContainer.remove(); }, 4000);
}

// Example: Trigger confetti when page loads
window.addEventListener('load', () => {
    console.log("🎉 Mentor Me Collective App Loaded!");
});
