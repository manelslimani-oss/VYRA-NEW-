(function(){
  document.documentElement.classList.add("js");
  const reduce=matchMedia("(prefers-reduced-motion: reduce)").matches;
  const bar=document.getElementById("scrollbar"),links=[...document.querySelectorAll('nav a[href^="#"]')];
  addEventListener("scroll",()=>{const m=document.documentElement.scrollHeight-innerHeight;if(bar)bar.style.setProperty("--p",m>0?(scrollY/m).toFixed(3):0);},{passive:true});
  const map=new Map();links.forEach(a=>{const s=document.getElementById(a.getAttribute("href").slice(1));if(s)map.set(s,a);});
  if(map.size&&"IntersectionObserver" in window){
    const spy=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){links.forEach(l=>l.classList.remove("active"));map.get(e.target).classList.add("active");}}),{rootMargin:"-45% 0px -50% 0px"});
    map.forEach((_,s)=>spy.observe(s));
  }
  /* Apparition au défilement */
  const items=document.querySelectorAll(".band h2,.band .lead,.col,.tile,.card,.ii,details,.checklist li,.note,.cta");
  if(!reduce&&"IntersectionObserver" in window){
    items.forEach(el=>{el.classList.add("reveal");el.style.setProperty("--i",Math.min([...el.parentElement.children].indexOf(el),5));});
    const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){const el=e.target;el.classList.add("in");io.unobserve(el);setTimeout(()=>el.classList.remove("reveal","in"),1500);}}),{threshold:.12,rootMargin:"0px 0px -40px 0px"});
    items.forEach(el=>io.observe(el));
  }
  document.querySelectorAll("[data-q]").forEach(b=>b.addEventListener("click",()=>window.sendQuestion&&window.sendQuestion(b.dataset.q)));
})();
