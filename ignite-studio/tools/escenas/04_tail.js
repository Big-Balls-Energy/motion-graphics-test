
/* ================= HUD / SUBTÍTULOS / POST ================= */
function tag(t){const g=TAGS.find(([a,b])=>t>=a-.05&&t<b+.3);if(!g)return;const[a,b,s]=g,k=eo(p(t,a,a+.3))*(1-p(t,b,b+.3));if(k<=0)return;
 ctx.save();ctx.globalAlpha=k;const w=tw(s,19,'JBM',2)+46;rr(60,282,w,42,10);ctx.fillStyle='rgba(3,8,23,.75)';ctx.fill();ctx.strokeStyle=rgba(C.cyan,.75);ctx.lineWidth=2;ctx.stroke();
 circle(80,303,5,Math.floor(t*2)%2?C.cyan:rgba(C.cyan,.4));text(s,94,304,19,'JBM',C.white,'left',2);ctx.restore()}
// sin marca de agua (video para Ignite): solo barra de progreso y etiqueta de sección
function hud(t){
 ctx.fillStyle='rgba(255,255,255,.1)';ctx.fillRect(0,0,W,6);ctx.fillStyle=C.blue;ctx.fillRect(0,0,W*clamp(t/DUR),6);
 tag(t)}
function sources(t){const s=SOURCES.find(([a,b])=>t>=a&&t<b+.3);if(!s)return;const[a,b,lines2]=s,k=eo(p(t,a,a+.3))*(1-p(t,b,b+.3));if(k<=0)return;
 ctx.save();ctx.globalAlpha=k*.8;lines2.forEach((l,i)=>text(l,CX,1502-(lines2.length-1-i)*26,fitSize(l,'SGM',20,900),'SGM',C.white));ctx.restore()}
const SUB_FS=52,SUB_MAXW=850;
// corte de línea equilibrado: si no cabe en una, elige el corte con líneas más parejas y nunca deja «y», «un», «de»… al final
function subLines(ws,sp){const wid=a=>a.reduce((s,w,i)=>s+w.ww+(i?sp:0),0);if(wid(ws)<=SUB_MAXW)return[{ws,w:wid(ws)}];let best=null;
 for(let k=1;k<ws.length;k++){const a=ws.slice(0,k),b=ws.slice(k),wa=wid(a),wb=wid(b);if(wa>SUB_MAXW||wb>SUB_MAXW)continue;const sc=Math.max(wa,wb)+(norm(a[a.length-1].w).length<=2?1e4:0);if(!best||sc<best.sc)best={sc,a,b,wa,wb}}
 return best?[{ws:best.a,w:best.wa},{ws:best.b,w:best.wb}]:[{ws,w:wid(ws)}]}
function subs(t){
 const s=SUBS.find(s=>t>=s.a&&t<s.b);if(!s)return;
 ctx.font=`${SUB_FS}px SGM`;const sp=ctx.measureText(' ').width;
 const lines2=subLines(s.words.map(w=>({...w,ww:ctx.measureText(w.w).width})),sp);
 const lh=SUB_FS*1.28,pad=34,pv=20,bw=Math.max(...lines2.map(l=>l.w))+pad*2,bh=lines2.length*lh+pv*2;
 const kin=eo(p(t,s.a,s.a+.18)),kout=1-p(t,s.b-.12,s.b),Y=s.a>=HKEY.b?1300:1395;
 ctx.save();ctx.translate(CX,Y);const sc=.92+.08*kin;ctx.scale(sc,sc);ctx.globalAlpha=Math.min(kin,kout);
 rr(-bw/2,-bh/2,bw,bh,20);ctx.fillStyle='rgba(7,7,11,.8)';ctx.fill();ctx.strokeStyle=rgba(C.cyan,.35);ctx.lineWidth=2;ctx.stroke();
 ctx.fillStyle=C.cyan;ctx.fillRect(-bw/2,-bh/2+16,5,bh-32);
 ctx.textBaseline='middle';ctx.textAlign='left';
 lines2.forEach((l,li)=>{let x=-l.w/2;const y=-bh/2+pv+lh*(li+.5);
  l.ws.forEach(w=>{const reached=t>=w.t0;ctx.fillStyle=reached?(w.num?C.amber:w.key?C.pink:C.white):'rgba(255,255,255,.42)';
   const e=reached?1-eo(p(t,w.t0,w.t0+.28)):0;
   ctx.save();ctx.translate(x+w.ww/2,y-7*e);ctx.scale(1+.03*e,1+.03*e);ctx.fillText(w.w,-w.ww/2,0);ctx.restore();x+=w.ww+sp})});
 ctx.restore()}
const SCAN=document.createElement('canvas');SCAN.width=8;SCAN.height=4;{const g=SCAN.getContext('2d');g.fillStyle='rgba(0,0,0,.12)';g.fillRect(0,0,8,1)}
const GRN=document.createElement('canvas');GRN.width=GRN.height=256;
{const g=GRN.getContext('2d'),d=g.createImageData(256,256);for(let i=0;i<65536;i++){const v=rnd(i*.731+.1)>.5?255:0;d.data[i*4]=d.data[i*4+1]=d.data[i*4+2]=v;d.data[i*4+3]=rnd(i*1.37+9)*70}g.putImageData(d,0,0)}
function post(t){ctx.save();ctx.fillStyle=ctx.createPattern(SCAN,'repeat');ctx.globalAlpha=.35;ctx.fillRect(0,0,W,H);
 const f=Math.floor(t*8);ctx.globalAlpha=.035;const ox=-Math.floor(rnd(f)*256),oy=-Math.floor(rnd(f+.5)*256);for(let x=ox;x<W;x+=256)for(let y=oy;y<H;y+=256)ctx.drawImage(GRN,x,y);
 ctx.globalAlpha=1;const g=ctx.createRadialGradient(W/2,H*.45,H*.35,W/2,H*.45,H*.8);g.addColorStop(0,'rgba(0,0,0,0)');g.addColorStop(1,'rgba(0,0,0,.45)');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);ctx.restore()}
const SHAKES=[[3.3,8,.3],[11.95,8,.3],[43.1,6,.25],[53.75,10,.35],[62.45,6,.25],[80.35,6,.25],[83.6,10,.4]];
function shake(t){let x=0,y=0;SHAKES.forEach(([t0,a,d],i)=>{if(t<t0||t>t0+d)return;const k=1-(t-t0)/d,m=a*k*k;x+=Math.sin(t*97+i)*m;y+=Math.cos(t*83+i*2)*m});return[x,y]}

/* ================= COMPOSICIÓN ================= */
const DRAW=[sHook,sIntro,sEncender,sSalud,sCuerpo,sRend,sComunidad,sJuntos,sHorarios,sReserva,sCierre];
function renderFrame(t){
 bgBase();const i=sceneAt(t),sh=shake(t);
 ctx.save();ctx.translate(sh[0],sh[1]);DRAW[i](t);ctx.restore();
 if(t>DUR-.55){ctx.save();ctx.globalAlpha=eo(p(t,DUR-.55,DUR-.05));hookFrame(0);ctx.restore()}
 post(t);sources(t);subs(t);hud(t);
}

/* ================= PORTADA ================= */
function renderCover(){
 hookFrame(1.2,{titles:false});avatar(CX,930,125,1,{ring:false});
 text(T.portada[0],CX,470,fitSize(T.portada[0],'ANT',150,860,2),'ANT',C.white,'center',2);glowText(T.portada[1],CX,620,fitSize(T.portada[1],'ANT',170,860,2),C.cyan,'ANT',2,46,0);
 glowText(T.portada[2],CX,1260,fitSize(T.portada[2],'ANT',170,860,2),C.white,'ANT',2,46,0);wordmark(CX,1400,380,1);post(3)}
window.renderCover=renderCover;window.renderAsset=()=>[];window.assetNames=()=>[];

/* ================= CONSTRUCCIÓN ================= */
function build3D(){
 ENV=new THREE.PMREMGenerator(R).fromScene(new RoomEnvironment(),.04).texture;
 TX.glow=canvasTex(radialCanvas());
 MAT.cardBody=new THREE.MeshPhysicalMaterial({color:0x0b1424,metalness:.55,roughness:.22,clearcoat:1,clearcoatRoughness:.08,envMapIntensity:1.1});

}

/* ================= REPRODUCCIÓN ================= */
window.renderFrame=renderFrame;
const imgReady=im=>new Promise(r=>{if(im.complete)r();else{im.onload=r;im.onerror=r}});
window.ready=Promise.all([...['SGB','SGM','JBM','JBMm','ANT'].map(f=>document.fonts.load(`100px ${f}`)),imgReady(logo),...Object.values(MARCA).map(imgReady),...Object.values(IMG).map(imgReady)])
 .then(()=>{['I01_strength','I02_movement','I03_getting_started','I04_we_are_ignite'].forEach(n=>buildDuo(n));buildDuo('C03_silueta_ciclista',[[0,[2,6,23]],[.4,[6,22,80]],[.8,[18,70,190]],[1,[70,135,235]]]);Object.keys(RECORTES).forEach(buildCut);build3D();window.isReady=true});
const RENDER=new URLSearchParams(location.search).has('render');
const ui=document.getElementById('ui'),aud=document.getElementById('aud');
if(RENDER){ui.classList.add('hide');document.body.style.background=C.bg}
else{
 let playing=false,t0=0,useAudio=true;
 aud.addEventListener('error',()=>useAudio=false);
 const now=()=>useAudio&&!isNaN(aud.duration)?aud.currentTime:(performance.now()-t0)/1000;
 function loop(){if(!playing)return;let t=now();if(t>=DUR){if(useAudio){aud.currentTime=0;aud.play()}else t0=performance.now();t=0}renderFrame(Math.min(t,DUR-.001));requestAnimationFrame(loop)}
 function start(){ui.classList.add('hide');playing=true;t0=performance.now();aud.currentTime=0;aud.play().catch(()=>useAudio=false);loop()}
 ui.addEventListener('click',()=>window.ready.then(start));
 addEventListener('keydown',e=>{
  if(e.key==='f'||e.key==='F'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}
  if(e.key===' '){e.preventDefault();if(!playing){window.ready.then(start);return}if(aud.paused){aud.play()}else aud.pause()}
  if(e.key==='r'||e.key==='R'){aud.currentTime=0;t0=performance.now();if(!playing)window.ready.then(start)}
 });
 window.ready.then(()=>renderFrame(0));
}
</script>
</body>
</html>
