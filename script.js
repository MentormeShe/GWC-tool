console.log("Mentor Me Collective Dashboard Loaded 🚀");

function confetti() {

    const container = document.createElement("div");
    container.style.position = "fixed";
    container.style.top = "0";
    container.style.left = "0";
    container.style.width = "100%";
    container.style.height = "100%";
    container.style.pointerEvents = "none";

    document.body.appendChild(container);

    for(let i=0;i<80;i++){

        const conf = document.createElement("div");

        conf.style.position = "absolute";
        conf.style.width = "8px";
        conf.style.height = "8px";
        conf.style.backgroundColor = `hsl(${Math.random()*360},100%,50%)`;

        conf.style.left = Math.random()*100 + "%";
        conf.style.top = "-10px";

        container.appendChild(conf);

        conf.animate(
        [
            {transform:"translateY(0px)"},
            {transform:`translateY(${window.innerHeight}px) rotate(360deg)`}
        ],
        {
            duration:2000 + Math.random()*2000,
            easing:"ease-out"
        });
    }

    setTimeout(()=>container.remove(),4000);
}}

// Example: Trigger confetti when page loads
window.addEventListener('load', () => {
    console.log("🎉 Mentor Me Collective App Loaded!");
});
