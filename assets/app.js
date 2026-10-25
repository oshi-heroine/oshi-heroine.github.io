document.querySelectorAll(".pv").forEach(function(b){var bt=b.querySelector("button");if(bt)bt.onclick=function(){
b.innerHTML='<iframe src="https://www.youtube-nocookie.com/embed/'+b.dataset.id+'?autoplay=1&rel=0" title="公式PV" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';};});
(function(){var f="all",q=document.getElementById("q");if(!q)return;
function apply(){var s=q.value.trim().toLowerCase();document.querySelectorAll(".work").forEach(function(w){var n=0;
w.querySelectorAll(".hcard").forEach(function(c){var ok=(f=="all"||c.dataset.role==f)&&(!s||c.dataset.q.toLowerCase().indexOf(s)>=0);c.classList.toggle("hide",!ok);if(ok)n++;});
w.classList.toggle("hide",n==0);});}
document.querySelectorAll(".chips button").forEach(function(b){b.onclick=function(){document.querySelectorAll(".chips button").forEach(function(x){x.classList.remove("on")});b.classList.add("on");f=b.dataset.f;apply();};});
q.oninput=apply;})();
(function(){var g=document.getElementById("gacha"),o=document.getElementById("gacha-out");if(!g||!window.PICKS)return;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
g.onclick=function(){var p=PICKS[Math.floor(Math.random()*PICKS.length)];o.hidden=false;
o.innerHTML='<a class="hcard" href="heroine/'+p.id+'.html"><div class="tile" style="--c:'+p.c+'"><span>'+esc(p.n.charAt(0))+'</span></div><div class="hc-b"><b>'+esc(p.n)+'</b><span class="muted">'+esc(p.w)+'</span><p>'+esc(p.p)+'</p><span class="fav">この子に会いに行く →</span></div></a>';
g.textContent="もう1回引く";};})();
