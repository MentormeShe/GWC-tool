// Navbar background change on scroll
document.addEventListener("DOMContentLoaded", function () {
    const navbar = document.querySelector(".navbar");
    window.addEventListener("scroll", function () {
        if (window.scrollY > 50) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }
    });
});

// Optional: confetti for cleared strikes
function launchConfetti() {
    const duration = 3*1000;
    const end = Date.now() + duration;
    (function frame(){
        confetti({particleCount:5, angle:60, spread:60, origin:{x:0}});
        confetti({particleCount:5, angle:120, spread:60, origin:{x:1}});
        if(Date.now() < end){requestAnimationFrame(frame);}
    })();
}
