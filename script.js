console.log("Mentor Me Collective Dashboard Loaded 🚀")

function celebration(){

const emoji = document.createElement("div")

emoji.innerHTML = "🎉 🎉 🎉"

emoji.style.position="fixed"
emoji.style.top="40%"
emoji.style.left="45%"
emoji.style.fontSize="50px"

document.body.appendChild(emoji)

setTimeout(()=>{
emoji.remove()
},2000)

}

setTimeout(()=>{
celebration()
},3000)
