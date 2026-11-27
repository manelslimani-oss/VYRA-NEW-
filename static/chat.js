(function(){
const pageMode=document.body.dataset.page==="chat";
const QUESTIONS=[["VIH ou sida ?","Quelle est la différence entre le VIH et le sida ?"],["Transmission","Comment le VIH se transmet-il ?"],["Prévention","Quels sont les moyens de prévention ?"],["Dépistage","Quand faire un test de dépistage ?"]];
const panelHTML=`<div class="chat-header"><img src="/static/logo-vyra.svg" alt=""><div><strong>VYRA</strong><small>Assistant d’information sur le VIH</small></div>${pageMode?"":'<button type="button" class="chat-close" aria-label="Fermer">×</button>'}</div>
<div id="chat-messages" aria-live="polite"><div class="bot-message">Bonjour, je suis VYRA. Posez-moi vos questions sur le VIH, le sida, la transmission, la prévention, le dépistage ou les traitements. Sans jugement, sans donnée personnelle.</div></div>
<div class="chat-chips" id="chat-chips">${QUESTIONS.map(q=>`<button type="button" data-ask="${q[1]}">${q[0]}</button>`).join("")}</div>
<form id="chat-form" class="chat-input"><input id="user-message" type="text" maxlength="1500" placeholder="Écrivez votre question…" autocomplete="off" aria-label="Votre question"><button id="chat-send" type="submit" aria-label="Envoyer">➤</button></form>
<p class="chat-warning">Informations générales uniquement : VYRA ne pose pas de diagnostic et ne remplace pas un professionnel de santé. Après une exposition possible, consultez sans attendre (PPE dans les 72 h).</p>`;
let win;
if(pageMode){win=document.getElementById("chat-root");win.className="chat-panel";win.setAttribute("aria-label","Discussion avec VYRA");}
else{
  const t=document.createElement("button");t.id="chat-toggle";t.type="button";t.setAttribute("aria-label","Ouvrir l’assistant VYRA");
  t.innerHTML='<i><img src="/static/ruban-rouge.svg" alt=""></i>Poser une question';
  win=document.createElement("section");win.id="chat-window";win.className="chat-panel";win.setAttribute("aria-label","Discussion avec VYRA");
  document.body.append(t,win);t.onclick=toggle;
}
win.insertAdjacentHTML("beforeend",panelHTML);
const form=win.querySelector("#chat-form"),input=win.querySelector("#user-message"),messages=win.querySelector("#chat-messages"),send=win.querySelector("#chat-send"),chips=win.querySelector("#chat-chips");
function toggle(){win.classList.toggle("chat-open");if(win.classList.contains("chat-open"))input.focus();}
function openChat(){if(!pageMode)win.classList.add("chat-open");input.focus();}
const close=win.querySelector(".chat-close");if(close)close.onclick=toggle;
chips.addEventListener("click",e=>{const b=e.target.closest("[data-ask]");if(b)sendQuestion(b.dataset.ask);});
function add(txt,cls){const el=document.createElement("div");el.className=cls;el.textContent=txt;messages.appendChild(el);messages.scrollTop=messages.scrollHeight;return el;}
async function sendQuestion(message){
  if(!message||send.disabled)return;openChat();chips.remove();
  add(message,"user-message");input.value="";send.disabled=true;
  const waiting=add("","bot-message");waiting.innerHTML='<span class="typing"><i></i><i></i><i></i></span>';
  try{const r=await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message})});const d=await r.json();if(!r.ok)throw new Error(d.error||"L’assistant est indisponible.");waiting.textContent=d.response;}
  catch(err){waiting.textContent=err.message||"Une erreur est survenue. Veuillez réessayer.";}
  finally{send.disabled=false;input.focus();messages.scrollTop=messages.scrollHeight;}
}
window.sendQuestion=sendQuestion;window.openChat=openChat;
form.addEventListener("submit",e=>{e.preventDefault();sendQuestion(input.value.trim());});
})();
