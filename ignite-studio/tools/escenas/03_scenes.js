
/* ================= UTILIDADES DEL REEL ================= */
function darkPlate(x,y,w,h,a=.82,col=C.cyan){rr(x,y,w,h,30);ctx.fillStyle=`rgba(5,7,13,${a})`;ctx.fill();ctx.strokeStyle=rgba(col,.7);ctx.lineWidth=3;ctx.stroke()}
function flashIn(t,a,k=.12){if(t<a+.2){ctx.fillStyle=`rgba(230,250,255,${(1-p(t,a,a+.2))*k})`;ctx.fillRect(0,0,W,H)}}
function dim(a){ctx.fillStyle=`rgba(5,7,13,${a})`;ctx.fillRect(0,0,W,H)}
function bgDark(t,col='#0F2A3D'){const g=ctx.createRadialGradient(W*.5,H*.42,40,W*.5,H*.5,H*.8);g.addColorStop(0,col);g.addColorStop(.5,'#0A1222');g.addColorStop(1,C.bg);ctx.fillStyle=g;ctx.fillRect(0,0,W,H);godRays(t,.7);motes(t,.6)}
function person(x,y,s,col,a=1){if(a<=0)return;ctx.save();ctx.globalAlpha*=a;ctx.fillStyle=col;ctx.beginPath();ctx.arc(x,y-s*.42,s*.24,0,TAU);ctx.fill();ctx.beginPath();ctx.moveTo(x-s*.36,y+s*.5);ctx.quadraticCurveTo(x-s*.36,y-s*.1,x,y-s*.1);ctx.quadraticCurveTo(x+s*.36,y-s*.1,x+s*.36,y+s*.5);ctx.closePath();ctx.fill();ctx.restore()}
// encabezado de cada cambio: número en círculo + título
function tipHeader(t,a,b,[n,label]){const k=eback(p(t,a+.1,a+.4))*(1-eo(p(t,b-.5,b-.1)));if(k<=0)return;ctx.save();ctx.globalAlpha*=Math.min(1,k);
 const w=tw(label,fitSize(label,'SGB',58,640,2),'SGB',2),x0=CX-(w+130)/2;ctx.translate((1-k)*-40,0);
 circle(x0+50,420,50,C.cyan);text(n,x0+50,424,62,'SGB',C.ink);text(label,x0+130,424,fitSize(label,'SGB',58,640,2),'SGB',C.white,'left',2);ctx.restore()}






/* ================= PANTALLA DEL CELULAR (reproductor genérico, sin interfaz real) ================= */
let SCRN='hook';const SW=464,SH=992;
function screenChat(t){const g=ctx.createLinearGradient(0,0,SW,SH);g.addColorStop(0,'#3B0764');g.addColorStop(.5,'#9D174D');g.addColorStop(1,'#F59E0B');ctx.fillStyle=g;ctx.fillRect(0,0,SW,SH);
 const r=mulberry(3);for(let i=0;i<14;i++){ctx.fillStyle=`rgba(255,255,255,${.05+r()*.08})`;ctx.beginPath();ctx.arc(r()*SW,(r()*SH+t*40*(1+r()))%SH,20+r()*60,0,TAU);ctx.fill()}
 circle(SW/2,SH*.42,62,'rgba(255,255,255,.25)');ctx.fillStyle=C.white;ctx.beginPath();ctx.moveTo(SW/2-18,SH*.42-28);ctx.lineTo(SW/2+30,SH*.42);ctx.lineTo(SW/2-18,SH*.42+28);ctx.closePath();ctx.fill();
 ['heart','send','star'].forEach((ic,i)=>icon(ctx,ic,SW-46,SH*.55+i*86,38,C.white));
 circle(46,SH-170,22,'rgba(255,255,255,.85)');bar(ctx,80,SH-180,150,14,'rgba(255,255,255,.85)');bar(ctx,30,SH-130,300,12,'rgba(255,255,255,.6)');
 const st=eio(p(t,2.4,3.4)),bw=SW-60;ctx.fillStyle='rgba(255,255,255,.3)';ctx.fillRect(30,SH-70,bw,8);ctx.fillStyle=st>0?C.amber:C.white;ctx.fillRect(30,SH-70,bw*(st>0?.08:(t*.2)%1),8);
 const lab=st<=0?T.corto:st<1?['0:15','2:40','11:20','37:05','58:30','1:30:00'][Math.floor(st*6)%6]:T.largo;rr(SW-170,SH-110,140,36,10);ctx.fillStyle='rgba(5,7,13,.7)';ctx.fill();text(lab,SW-100,SH-91,22,'JBM',st>0?C.amber:C.white)}
const PH={x:500,y:940},PS=.86;
function silhouette(x,y,s,a){if(a<=0)return;ctx.save();ctx.globalAlpha*=a;ctx.translate(x,y);ctx.scale(s,s);
 const g=ctx.createLinearGradient(0,-300,0,300);g.addColorStop(0,'#111827');g.addColorStop(1,'#020408');ctx.fillStyle=g;
 ctx.beginPath();ctx.arc(0,-210,95,0,TAU);ctx.fill();ctx.beginPath();ctx.moveTo(-260,300);ctx.quadraticCurveTo(-250,-40,-90,-90);ctx.lineTo(90,-90);ctx.quadraticCurveTo(250,-40,260,300);ctx.closePath();ctx.fill();
 ctx.strokeStyle=rgba(C.cyan,.85);ctx.lineWidth=5;ctx.beginPath();ctx.arc(0,-210,95,-1.2,.6);ctx.stroke();ctx.beginPath();ctx.moveTo(90,-90);ctx.quadraticCurveTo(250,-40,260,300);ctx.stroke();ctx.restore()}
function stamp(label,x,y,k,col,rot=-7,w=560){if(k<=0)return;ctx.save();ctx.translate(x,y);ctx.rotate(rot*DEG);const sc=1.6-.6*Math.min(1,k);ctx.scale(sc,sc);ctx.globalAlpha*=Math.min(1,k);
 rr(-w/2,-58,w,116,16);ctx.fillStyle='rgba(5,7,13,.85)';ctx.fill();ctx.fillStyle=rgba(col,.15);ctx.fill();ctx.strokeStyle=col;ctx.lineWidth=9;ctx.stroke();text(label,0,4,fitSize(label,'SGB',58,w-60,6),'SGB',col,'center',6);ctx.restore()}
function reelCard(x,y,s,k,col,i){if(k<=0)return;ctx.save();ctx.translate(x,y);ctx.scale(s*k,s*k);rr(-60,-105,120,210,16);const g=ctx.createLinearGradient(0,-105,0,105);g.addColorStop(0,col);g.addColorStop(1,'#0B1222');ctx.fillStyle=g;ctx.fill();ctx.strokeStyle='rgba(255,255,255,.5)';ctx.lineWidth=3;ctx.stroke();
 ctx.fillStyle=C.white;ctx.beginPath();ctx.moveTo(-12,-20);ctx.lineTo(18,0);ctx.lineTo(-12,20);ctx.closePath();ctx.fill();text(String(i),0,80,22,'SGB',C.white);ctx.restore()}

/* ================= 1 · HOOK ================= */
function hookFrame(t,{titles=true}={}){bgDark(t,'#2A1030');const k=eback(p(t,0,.45));if(k>0){SCRN='hook';drawPhone({x:PH.x,y:PH.y+(1-k)*400},PS,(-1.5+1*Math.sin(t*.7))*DEG,titles?t:0,'chat',{glow:.6})}
 if(!titles)return;const out=eo(p(t,5.6,6.1));const kv=eback(p(t,H90.a,H90.a+.3))*(1-out);if(kv>0){ctx.save();ctx.globalAlpha=Math.min(1,kv);glowText(T.m90,500,430,170,C.amber,'SGB',4,60,8);ctx.restore()}}
function sHook(t){hookFrame(t);if(t>3.2&&t<3.5){ctx.fillStyle=`rgba(250,204,21,${(1-p(t,3.2,3.5))*.15})`;ctx.fillRect(0,0,W,H)}}

/* ================= 2 · FEATURES ================= */
function sAnuncio(t){bgDark(t,'#2A1030');const out=eio(p(t,12.3,12.8));
 pill(T.fecha,500,430,eback(p(t,6.5,6.8))*(1-out),C.cyan,30,C.ink);
 const kf=eback(p(t,7.7,8.0))*(1-out);if(kf>0){ctx.save();ctx.globalAlpha=Math.min(1,kf);glowText(T.features,500,600,fitSize(T.features,'SGB',130,880,4),C.white,'SGB',4,40,6);text(T.nuevo,500,690,30,'JBM',C.gray,'center',6);ctx.restore()}
 const kb=eo(p(t,8.8,9.2))*(1-out);if(kb>0){ctx.save();ctx.globalAlpha=kb;text(T.reel,140,870,30,'SGB',C.white,'left',4);rr(140,900,90*eo(p(t,8.8,9.4)),56,28);ctx.fillStyle=C.cyan;ctx.fill();
  const kl=eio(p(t,10.3,11.4));text(T.hasta,140,1040,30,'SGB',C.amber,'left',4);rr(140,1070,Math.max(56,800*kl),56,28);ctx.fillStyle=C.amber;ctx.fill();ctx.restore()}
 flashIn(t,6.2)}

/* ================= 3 · PRUEBA ================= */
function sPrueba(t){fondo('G10_personas_celular',{z:1.1-.05*p(t,12.8,18.4),alpha:eo(p(t,12.8,13.0))});dim(.62);const out=eio(p(t,17.9,18.4));
 stamp(T.prueba,500,460,eback(p(t,13.2,13.45))*(1-out),C.amber,-6,400);
 const P=[{x:300,y:1050},{x:720,y:760}];
 const ka=eo(p(t,15.6,16.3))*(1-out);if(ka>0){ctx.save();ctx.globalAlpha=ka;ctx.setLineDash([14,12]);ctx.strokeStyle=rgba(C.white,.8);ctx.lineWidth=6;ctx.beginPath();ctx.moveTo(P[0].x,P[0].y);ctx.quadraticCurveTo(420,700,P[0].x+(P[1].x-P[0].x)*ka,P[0].y+(P[1].y-P[0].y)*ka);ctx.stroke();ctx.setLineDash([]);ctx.restore()}
 T.paises.forEach(([n,l],i)=>{const k=eback(p(t,[14.4,16.2][i],[14.4,16.2][i]+.3))*(1-out);if(k<=0)return;ctx.save();ctx.translate(P[i].x,P[i].y);ctx.scale(k,k);darkPlate(-170,-70,340,140,.9,i?C.cyan:C.green);icon(ctx,'pin',-120,0,46,i?C.cyan:C.green);text(n,25,-14,40,'SGB',C.white,'center',3);text(l,25,32,22,'SGM',C.gray);ctx.restore()});
 flashIn(t,12.8)}

/* ================= 4 · MOSSERI ================= */
function sMosseri(t){bgDark(t,'#14203A');const out=eio(p(t,25.7,26.2)),sw=eio(p(t,22.2,22.6));
 silhouette(500,820,.9,eo(p(t,18.5,19.0))*(1-sw));
 const kn=eo(p(t,20.8,21.2))*(1-sw);if(kn>0){ctx.save();ctx.globalAlpha=kn;darkPlate(170,1050,660,170,.88,C.amber);text(T.mosseri[0],500,1110,56,'SGB',C.white,'center',6);text(T.mosseri[1],500,1180,26,'JBM',C.amber,'center',4);ctx.restore()}
 const kq=eo(p(t,22.6,23.0))*(1-out);if(kq>0){ctx.save();ctx.globalAlpha=kq;ctx.translate(0,(1-kq)*50);darkPlate(100,480,800,640,.9,C.amber);ctx.font='260px SGB';ctx.fillStyle=rgba(C.amber,.35);ctx.textAlign='left';ctx.fillText('“',120,650);
  const tt=[22.7,23.4,24.0,24.7];T.cita.forEach((l,i)=>{const kk=eo(p(t,tt[i],tt[i]+.3));ctx.globalAlpha=kq*kk;text(l,500,640+i*100,fitSize(l,'SGB',66,720,2),'SGB',i===1?C.amber:C.white,'center',2)});
  ctx.globalAlpha=kq;text(T.citaB,500,1060,22,'SGM',C.gray);ctx.restore()}
 flashIn(t,18.4)}

/* ================= 5 · CLIPS COMO REELS ================= */
function sClips(t){bgDark(t,'#2A1030');const out=eio(p(t,31.7,32.1));
 const kt=eback(p(t,26.4,26.7))*(1-out);if(kt>0){ctx.save();ctx.globalAlpha=Math.min(1,kt);text(T.clips,500,430,fitSize(T.clips,'SGB',70,880,3),'SGB',C.white,'center',3);ctx.restore()}
 const kb=eo(p(t,26.6,27.1))*(1-out),sp=eio(p(t,27.4,28.4));if(kb>0){ctx.save();ctx.globalAlpha=kb;for(let i=0;i<3;i++){const x0=140+i*(800/3),w=800/3-6,x=lerp(x0,[180,410,640][i]-60+0*i,sp),y=lerp(640,760,sp);
  if(sp<1){rr(x,y-28,lerp(w,120,sp),lerp(56,210,sp),lerp(28,16,sp));ctx.fillStyle=lerp(0,1,sp)>.5?'#9D174D':C.amber;ctx.fill()}}
  if(t<27.4){ctx.strokeStyle=C.white;ctx.lineWidth=4;[1,2].forEach(i=>{const x=140+i*800/3;ctx.setLineDash([8,8]);ctx.beginPath();ctx.moveTo(x,590);ctx.lineTo(x,690);ctx.stroke();ctx.setLineDash([])})}
  ctx.restore()}
 if(sp>=1)for(let i=0;i<3;i++)reelCard([240,500,760][i],860,1.2,eback(p(t,28.4+i*.2,28.7+i*.2))*(1-out),['#9D174D','#7C3AED','#B45309'][i],i+1);
 const kc=eback(p(t,29.8,30.1))*(1-out);if(kc>0){ctx.save();ctx.translate(500,1150);ctx.scale(kc,kc);rr(-260,-40,520,80,40);ctx.fillStyle=C.amber;ctx.fill();text(T.completo,0,3,36,'SGB',C.ink,'center',2);ctx.restore()}
 flashIn(t,26.2)}

/* ================= 6 · ¿CÓMO VAN A PAGAR? ================= */
function coin(x,y,s,col){ctx.save();ctx.translate(x,y);ctx.scale(s,s);ctx.beginPath();ctx.ellipse(0,0,60,60,0,0,TAU);ctx.fillStyle=col;ctx.fill();ctx.strokeStyle='rgba(0,0,0,.25)';ctx.lineWidth=6;ctx.stroke();text('$',0,4,64,'SGB','rgba(5,7,13,.6)');ctx.restore()}
function sPago(t){bgDark(t,'#1F1608');const out=eio(p(t,37.5,38.0));
 const kt=eback(p(t,32.3,32.6))*(1-out);if(kt>0){ctx.save();ctx.globalAlpha=Math.min(1,kt);text(T.pago,500,430,fitSize(T.pago,'SGB',70,880,2),'SGB',C.white,'center',2);ctx.restore()}
 for(let i=0;i<5;i++){const k=eback(p(t,32.4+i*.12,32.7+i*.12))*(1-out);if(k<=0||i===2)continue;coin(260+i*120,640+Math.sin(t*3+i)*12,.9*k,C.amber)}
 const kq=eback(p(t,33.0,33.3))*(1-out);if(kq>0){ctx.save();ctx.globalAlpha=Math.min(1,kq);glowText('?',500,640,160,C.white,'SGB',0,40,6);ctx.restore()}
 const kc=eo(p(t,34.5,34.9))*(1-out);if(kc>0){ctx.save();ctx.globalAlpha=kc;darkPlate(110,800,780,380,.9,C.amber);T.pagoCita.forEach((l,i)=>text(l,500,890+i*80,fitSize(l,'SGB',52,700,1),'SGB',i===2?C.amber:C.white,'center',1));text(T.pagoB,500,1140,22,'SGM',C.gray);ctx.restore()}
 flashIn(t,32.1)}

/* ================= 7 · LA SEÑAL ================= */
function tvIcon(x,y,s,col){ctx.save();ctx.translate(x,y);ctx.scale(s,s);rr(-170,-110,340,210,20);ctx.fillStyle='#0B1222';ctx.fill();ctx.strokeStyle=col;ctx.lineWidth=8;ctx.stroke();ctx.fillStyle=col;ctx.fillRect(-60,110,120,14);ctx.fillRect(-12,96,24,20);
 ctx.beginPath();ctx.moveTo(-20,-40);ctx.lineTo(40,0);ctx.lineTo(-20,40);ctx.closePath();ctx.fill();ctx.restore()}
function sSenal(t){bgDark(t,'#14203A');const out=eio(p(t,43.2,43.7));
 const V=T.vs;[[V[0],460,38.4,C.white],[V[1],580,39.5,C.amber],[V[2],700,39.6,C.white]].forEach(([s,y,a,col],i)=>{const k=eback(p(t,a,a+.3))*(1-out);if(k<=0)return;ctx.save();ctx.globalAlpha=Math.min(1,k);ctx.translate((1-k)*(i===0?-80:i===2?80:0),0);
  if(i===1)glowText(s,500,y,100,col,'SGB',8,40,6);else text(s,500,y,fitSize(s,'SGB',96,860,6),'SGB',col,'center',6);ctx.restore()});
 const kv=eback(p(t,41.6,41.9))*(1-out);if(kv>0){ctx.save();ctx.globalAlpha=Math.min(1,kv);tvIcon(500,940,kv,C.cyan);text(T.tv,500,1160,44,'SGB',C.cyan,'center',4);ctx.restore()}
 flashIn(t,38.0)}

/* ================= 8 · TU NEGOCIO ================= */
function sNegocio(t){fondo('D01_grabando_video',{z:1.1-.05*p(t,43.7,49.8),alpha:eo(p(t,43.7,43.9))});dim(.6);const out=eio(p(t,49.3,49.8));
 const kt=eback(p(t,44.7,45.0))*(1-out);if(kt>0){ctx.save();ctx.globalAlpha=Math.min(1,kt);text(T.negocio,500,430,80,'SGB',C.white,'center',4);ctx.restore()}
 const kb=eo(p(t,44.8,45.6))*(1-out),sp=eio(p(t,46.3,46.6));if(kb>0&&sp<1){ctx.save();ctx.globalAlpha=kb*(1-sp);rr(110,640,780*kb,70,35);ctx.fillStyle=C.amber;ctx.fill();text('1:30:00',130+760*kb-20,676,30,'JBM',C.ink,'right');ctx.restore()}
 for(let i=0;i<5;i++)reelCard(180+i*160,820,1.1,eback(p(t,46.6+i*.2,46.9+i*.2))*(1-out),['#9D174D','#7C3AED','#B45309','#0E7490','#15803D'][i],i+1);
 const ks=eback(p(t,47.6,47.9))*(1-out);if(ks>0){ctx.save();ctx.globalAlpha=Math.min(1,ks);glowText(T.saca,500,1120,fitSize(T.saca,'SGB',90,880,4),C.amber,'SGB',4,40,6);ctx.restore()}
 flashIn(t,43.7)}

/* ================= 10 · CIERRE Y CTA ================= */
const TY0=50.15,TYS=.1,SEND=51.0;
function screenComments(t){const Ws=SCR.w,Hs=SCR.h;ctx.fillStyle='#0B1222';ctx.fillRect(0,0,Ws,Hs);
 text('Comentarios',Ws/2,100,24,'SGB',C.white);ctx.fillStyle='rgba(255,255,255,.12)';ctx.fillRect(0,134,Ws,2);
 for(let k=0;k<3;k++){const y=170+k*120;circle(46,y+24,22,['#334155','#1E3A8A','#4C1D95'][k]);bar(ctx,82,y+6,100+k*24,13,'#94A3B8');bar(ctx,82,y+32,270-k*40,13,'#E2E8F0',.8);bar(ctx,82,y+54,180+k*20,13,'#E2E8F0',.55)}
 const kn=eback(p(t,SEND+.15,SEND+.4));if(kn>0){ctx.save();ctx.translate(46,560);ctx.scale(kn,kn);ctx.translate(-46,-560);rr(16,516,Ws-32,96,20);ctx.fillStyle=rgba(C.cyan,.14);ctx.fill();ctx.strokeStyle=rgba(C.cyan,.7);ctx.lineWidth=2;ctx.stroke();
  circle(48,560,22,C.cyan);text('tú',82,540,17,'SGM','#94A3B8','left');text(T.keyword,82,578,36,'SGB',C.cyan,'left',3);ctx.restore()}
 rr(18,Hs-90,Ws-110,60,30);ctx.fillStyle='#1E293B';ctx.fill();
 const n=t>=SEND?0:clamp(Math.floor((t-TY0)/TYS)+1,0,T.keyword.length),typed=T.keyword.slice(0,n);
 if(typed)text(typed,42,Hs-59,34,'SGB',C.cyan,'left',3);else if(t<SEND)text('Añade un comentario…',40,Hs-59,19,'SGM','#64748B','left');
 if(t<SEND&&Math.floor(t*3)%2===0){ctx.fillStyle=C.cyan;ctx.fillRect(typed?46+tw(typed,34,'SGB',3):36,Hs-78,3,38)}
 const pr=1-.15*bell(t,SEND-.1,SEND+.05);ctx.save();ctx.translate(Ws-58,Hs-59);ctx.scale(pr,pr);circle(0,0,28,C.cyan);icon(ctx,'send',2,0,28,C.ink);ctx.restore()}
function sCta(t){
 const kW9=eo(p(t,54.2,54.8));
 if(kW9<1)bgDark(t);
 if(kW9>0)fondo('W09_equipo_estrategia',{z:1.08-.04*p(t,54.5,61),alpha:kW9});
 const ph=eo(p(t,49.8,50.15)),pd=eio(p(t,HKEY.a,HKEY.a+.4)),pout=eo(p(t,54.1,54.5));
 if(ph>0&&pout<1){const P={x:500,y:900+(1-ph)*760+pd*90+pout*400},s=.82-.08*pd,rot=(-2+1*Math.sin(t*.8))*DEG;drawPhone(P,s,rot,t,'comments',{alpha:1-pout,dim:.62*pd,glow:1-pd*.6});OBJ.ctaPhone={P,s,rot}}
 if(t>=HKEY.a-.02&&t<HKEY.b+.4){const ph2=OBJ.ctaPhone,from=ph2?phoneXf(ph2.P,ph2.s,ph2.rot)(SCR.x+82+70,SCR.y+578):{x:CX,y:900},k=eback(p(t,HKEY.a,HKEY.a+.3)),out=eio(p(t,HKEY.b,HKEY.b+.35));
  const x=lerp(from.x,CX,eo(p(t,HKEY.a,HKEY.a+.3))),y=lerp(lerp(from.y,760,eo(p(t,HKEY.a,HKEY.a+.3))),330,out),size=lerp(36,fitSize(T.keyword,'SGB',240,860,10),k)*(1-.7*out)*(1+.02*Math.sin(t*5));
  ctx.save();ctx.globalAlpha=1-out;const sh=ctx.createRadialGradient(x,y,40,x,y,560);sh.addColorStop(0,'rgba(5,7,13,.6)');sh.addColorStop(1,'rgba(5,7,13,0)');ctx.fillStyle=sh;ctx.fillRect(x-560,y-560,1120,1120);
  for(let q=0;q<3;q++){const rot=t*(.6+q*.25)+q*1.1;ring2D(x,y,(380+q*40)*k*(1-out),q===1?C.blue:C.cyan,.55*k*(1-out),4,.3,rot)}
  glowText(T.keyword,x,y,size,C.cyan,'SGB',10,70,size*.05);ctx.restore();lensFlare(x,y,bell(t,HKEY.a,HKEY.a+.5)*1.1,C.cyan);sparks(x,y,t,HKEY.a+.05,46,808,{spd:950,g:250,life:1,kind:'spark',cols:[C.cyan,C.amber,C.white],spread:3.1})}
 const out=1-eo(p(t,60.0,60.35));
 const ka=pop(t,54.55,.35);if(ka>0){ctx.save();ctx.globalAlpha=out;ctx.translate(CX,560);ctx.scale(ka,ka);const pr=(t*.9)%1;ctx.beginPath();ctx.arc(0,0,124+pr*50,0,TAU);ctx.strokeStyle=rgba(C.cyan,1-pr);ctx.lineWidth=5;ctx.stroke();
  circle(0,0,124,C.cyan);circle(0,0,113,C.white);if(loaded(logo)){const hh=172,ww=hh*logo.naturalWidth/logo.naturalHeight;ctx.drawImage(logo,-ww/2,-hh/2,ww,hh)}ctx.restore()}
 const kn=pop(t,54.8,.35);if(kn>0){ctx.save();ctx.globalAlpha=out;ctx.translate(CX,770);ctx.scale(kn,kn);text(T.marca,0,0,fitSize(T.marca,'SGB',112,820,4),'SGB',C.white,'center',4);text(T.claim,0,70,26,'JBM',C.gray,'center',4);text(T.usuario,0,128,46,'SGB',C.cyan);ctx.restore()}
 const kbt=pop(t,55.05,.35),clicked=t>=57.8,press=1-.08*Math.sin(Math.PI*p(t,57.75,57.95));
 if(kbt>0){ctx.save();ctx.globalAlpha=out;ctx.translate(CX,1060);ctx.scale(kbt*press,kbt*press);rr(-250,-58,500,116,58);ctx.fillStyle=clicked?C.white:C.cyan;ctx.shadowColor=rgba(C.cyan,.6);ctx.shadowBlur=40;ctx.fill();ctx.shadowBlur=0;
  if(clicked){text('SIGUIENDO',-40,4,48,'SGB',C.ink,'center',2);check(180,0,38,'#0891B2',10)}else text('SEGUIR',0,4,56,'SGB',C.ink,'center',4);ctx.restore()}
 const rk=p(t,57.8,58.3);if(rk>0&&rk<1){ctx.beginPath();ctx.arc(CX+120,1080,30+rk*110,0,TAU);ctx.strokeStyle=rgba(C.cyan,1-rk);ctx.lineWidth=8;ctx.stroke()}
 const mk=eio(p(t,57.1,57.7)),mo=eio(p(t,58.05,58.65));if(t>57.1&&t<59.05){ctx.save();ctx.globalAlpha=1-p(t,58.75,59.05);cursorArrow(lerp(900,CX+120,mk)+mo*110,lerp(1320,1080,mk)+mo*120,t>=57.75&&t<57.95?.88:1);ctx.restore()}
 const kd=eo(p(t,58.5,58.9))*out;if(kd>0){ctx.save();ctx.globalAlpha=kd*.85;text(T.nota[0],CX,1462,fitSize(T.nota[0],'SGM',22,900),'SGM',C.white);text(T.nota[1],CX,1492,fitSize(T.nota[1],'SGM',22,900),'SGM',C.white);ctx.restore()}
 flashIn(t,49.8,.15)}
