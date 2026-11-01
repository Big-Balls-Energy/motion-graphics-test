
/* ================= UTILIDADES DE IGNITE ================= */
function flashIn(t,a,k=.12){if(t>=a&&t<a+.2){ctx.fillStyle=`rgba(234,243,253,${(1-p(t,a,a+.2))*k})`;ctx.fillRect(0,0,W,H)}}
function dim(a){ctx.fillStyle=`rgba(3,8,23,${a})`;ctx.fillRect(0,0,W,H)}
function bgBlue(t,{k=1,core='#123a9e'}={}){const g=ctx.createRadialGradient(W*.5,H*.4,40,W*.5,H*.5,H*.85);g.addColorStop(0,core);g.addColorStop(.45,'#071233');g.addColorStop(1,C.bg);ctx.fillStyle=g;ctx.fillRect(0,0,W,H);godRays(t,.7*k,-160,-240,'120,170,255');motes(t,.6*k)}
// líneas de velocidad (ritmo de pedaleo)
function speedLines(t,k=1,col='120,170,255'){if(k<=0)return;ctx.save();ctx.globalCompositeOperation='lighter';for(let i=0;i<26;i++){const y=(rnd(i*3.1)*H+(t*(500+rnd(i)*900)))%(H+400)-200,x=rnd(i*7.7)*W,l=120+rnd(i*1.3)*260;
 ctx.strokeStyle=`rgba(${col},${(.05+.12*rnd(i*5.1))*k})`;ctx.lineWidth=2+rnd(i)*3;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x,y+l);ctx.stroke()}ctx.restore()}
// foto a pantalla completa o en un recuadro (recorte tipo «cover»)
function photo(name,x,y,w,h,{z=1,fx=.5,fy=.5,alpha=1,r=0,src}={}){const im=src||DUO[name]||IMG[name];if(alpha<=0)return;ctx.save();ctx.globalAlpha*=alpha;
 if(r>0){rr(x,y,w,h,r);ctx.clip()}else{ctx.beginPath();ctx.rect(x,y,w,h);ctx.clip()}
 const iw=im.naturalWidth||im.width,ih=im.naturalHeight||im.height;if(!iw){ctx.fillStyle='#3a3f4a';ctx.fillRect(x,y,w,h);text(name,x+w/2,y+h/2,26,'JBM','#e2e8f0');ctx.restore();return}
 const s=Math.max(w/iw,h/ih)*z,dw=iw*s,dh=ih*s;ctx.drawImage(im,x+(w-dw)*fx,y+(h-dh)*fy,dw,dh);ctx.restore()}
function full(name,o={}){photo(name,0,0,W,H,o)}
// duotono azul de Ignite para las fotos en blanco y negro (de su sitio y la silueta conceptual)
const DUO={};
function buildDuo(name,stops=[[0,[2,6,23]],[.45,[10,42,138]],[.8,[31,107,255]],[1,[234,243,253]]]){const im=IMG[name];if(!loaded(im))return;const[c,g]=mkCanvas(im.naturalWidth,im.naturalHeight);g.drawImage(im,0,0);
 const d=g.getImageData(0,0,c.width,c.height),a=d.data;const lut=[];for(let v=0;v<256;v++){const x=v/255;let i=0;while(i<stops.length-2&&x>stops[i+1][0])i++;const[x0,c0]=stops[i],[x1,c1]=stops[i+1],k=clamp((x-x0)/(x1-x0));lut.push(c0.map((q,j)=>q+(c1[j]-q)*k))}
 for(let i=0;i<a.length;i+=4){const l=Math.round(.3*a[i]+.59*a[i+1]+.11*a[i+2]);const q=lut[l];a[i]=q[0];a[i+1]=q[1];a[i+2]=q[2]}g.putImageData(d,0,0);c.naturalWidth=c.width;c.naturalHeight=c.height;DUO[name]=c}
// logo de perfil de Ignite: círculo azul con el ala blanca (archivo oficial)
function avatar(x,y,r,k=1,{ring=true,t=0}={}){if(k<=0)return;ctx.save();ctx.translate(x,y);ctx.scale(k,k);
 if(ring){const pr=(t*.8)%1;ctx.beginPath();ctx.arc(0,0,r*(1.05+pr*.3),0,TAU);ctx.strokeStyle=rgba(C.cyan,.7*(1-pr));ctx.lineWidth=6;ctx.stroke()}
 ctx.shadowColor=rgba(C.blue,.8);ctx.shadowBlur=60;circle(0,0,r,C.blue);ctx.shadowBlur=0;
 const im=MARCA.ala_blanca;if(loaded(im)){const h=r*1.12,w=h*im.naturalWidth/im.naturalHeight;ctx.drawImage(im,-w/2-r*.02,-h/2,w,h)}ctx.restore()}
function wordmark(x,y,w,k=1,{col='blanco',reveal=1}={}){const im=MARCA['ignite_'+col];if(!loaded(im)||k<=0)return;const h=w*im.naturalHeight/im.naturalWidth;ctx.save();ctx.globalAlpha*=Math.min(1,k);
 ctx.beginPath();ctx.rect(x-w/2-10,y-h/2-10,(w+20)*reveal,h+20);ctx.clip();ctx.drawImage(im,x-w/2,y-h/2,w,h);ctx.restore()}
// texto grande condensado (Anton) que entra con golpe
function slam(s,x,y,size,t,t0,{col=C.white,glow=false,from=1.5,dx=0,dy=0,maxW=860,o=1}={}){const k=p(t,t0,t0+.22);if(k<=0||o<=0)return;const e=eo(k),fs=fitSize(s,'ANT',size,maxW,2);
 ctx.save();ctx.globalAlpha*=Math.min(1,k*2)*o;ctx.translate(x+dx*(1-e),y+dy*(1-e));const sc=lerp(from,1,e);ctx.scale(sc,sc);
 if(glow)glowText(s,0,0,fs,col,'ANT',2,46,0);else text(s,0,0,fs,'ANT',col,'center',2);ctx.restore()}
function sceneOut(t,b){return 1-eio(p(t,b-.45,b-.08))}
// número de sección: grande al centro y luego sube como encabezado
function secHeader(t,a,b,[n,label]){const k=eback(p(t,a+.05,a+.35)),m=eio(p(t,a+.95,a+1.4)),o=sceneOut(t,b);if(k<=0||o<=0)return;
 ctx.save();ctx.globalAlpha=o;const y=lerp(860,410,m),sc=lerp(1,.36,m)*k;ctx.translate(CX,y);ctx.scale(sc,sc);
 const fl=fitSize(label,'ANT',190,560,4),wn=tw(n,360,'ANT',4),wl=tw(label,fl,'ANT',4),x0=-(wn+40+wl)/2;
 glowText(n,x0+wn/2,0,360,C.blue,'ANT',4,60,0);text(label,x0+wn+40,10,fl,'ANT',C.white,'left',4);ctx.restore();
 if(m<1){ctx.save();ctx.globalAlpha=(1-m)*o;speedLines(t,1.2);ctx.restore()}}
function chip(s,x,y,k,{col=C.blue,fg=C.white,size=34}={}){pill(s,x,y,k,col,size,fg,'SGB')}
// íconos dibujados
function heartPath(g,s){g.beginPath();g.moveTo(0,s*.35);g.bezierCurveTo(-s*1.1,-s*.35,-s*.55,-s*1.05,0,-s*.5);g.bezierCurveTo(s*.55,-s*1.05,s*1.1,-s*.35,0,s*.35);g.closePath()}
function lungs(x,y,s,k,col){ctx.save();ctx.translate(x,y);ctx.scale(s*k,s*k);ctx.strokeStyle=col;ctx.lineWidth=.06;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(0,-.9);ctx.lineTo(0,-.25);ctx.moveTo(0,-.25);ctx.quadraticCurveTo(-.18,-.1,-.3,0);ctx.moveTo(0,-.25);ctx.quadraticCurveTo(.18,-.1,.3,0);ctx.stroke();
 for(const sd of [-1,1]){ctx.beginPath();ctx.moveTo(sd*.12,-.55);ctx.bezierCurveTo(sd*.75,-.75,sd*.95,.2,sd*.75,.75);ctx.quadraticCurveTo(sd*.4,.9,sd*.15,.55);ctx.closePath();ctx.fillStyle=rgba(col,.22);ctx.fill();ctx.stroke()}ctx.restore()}
function moon(x,y,s,col){ctx.save();ctx.translate(x,y);ctx.beginPath();ctx.arc(0,0,s,0,TAU);ctx.arc(s*.45,-s*.3,s*.85,0,TAU,true);ctx.fillStyle=col;ctx.fill('evenodd');ctx.restore()}
function battery(x,y,w,h,f,col){ctx.save();ctx.translate(x,y);rr(-w/2,-h/2,w,h,h*.2);ctx.strokeStyle=col;ctx.lineWidth=5;ctx.stroke();rr(w/2+2,-h*.2,8,h*.4,3);ctx.fillStyle=col;ctx.fill();
 if(f>0){rr(-w/2+8,-h/2+8,(w-16)*f,h-16,h*.12);ctx.fillStyle=col;ctx.fill()}ctx.restore()}
function arrowUD(x,y,s,up,col){ctx.save();ctx.translate(x,y);if(!up)ctx.rotate(Math.PI);ctx.fillStyle=col;ctx.beginPath();ctx.moveTo(0,-s);ctx.lineTo(s*.8,0);ctx.lineTo(s*.3,0);ctx.lineTo(s*.3,s);ctx.lineTo(-s*.3,s);ctx.lineTo(-s*.3,0);ctx.lineTo(-s*.8,0);ctx.closePath();ctx.fill();ctx.restore()}

/* ================= 1 · HOOK ================= */
function hookFrame(t,{titles=true}={}){bgBase();const z=1.12-.1*eo(p(t,0,4.1));
 full('C03_silueta_ciclista',{z,fx:.5,fy:.5});dim(.3);
 {const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'rgba(3,8,23,.75)');g.addColorStop(.35,'rgba(3,8,23,.15)');g.addColorStop(.65,'rgba(3,8,23,.25)');g.addColorStop(1,'rgba(3,8,23,.85)');ctx.fillStyle=g;ctx.fillRect(0,0,W,H)}
 speedLines(t,.6);
 if(!titles)return;
 const o=1-eo(p(t,3.55,3.95)),s0=1+.06*(1-eo(p(t,0,.5)));
 ctx.save();ctx.globalAlpha=o;ctx.translate(CX,560);ctx.scale(s0,s0);text(T.hook[0],0,-70,fitSize(T.hook[0],'ANT',120,820,2),'ANT',C.white,'center',2);
 glowText(T.hook[1],0,70,fitSize(T.hook[1],'ANT',150,860,2),C.cyan,'ANT',2,46,0);ctx.restore();
 slam(T.hook[2],CX,1060,100,t,1.75,{o,from:1.3});slam(T.hook[3],CX,1180,120,t,2.15,{o,glow:true,col:C.white,from:1.6});
 // el ala se enciende y abre el video
 const kw=bell(t,3.25,4.1);if(kw>0){ctx.save();ctx.globalAlpha=kw;avatar(CX,860,170*(.6+.8*eo(p(t,3.25,4.1))),1,{ring:false});ctx.restore();lensFlare(CX,860,kw*1.2,C.cyan)}
 flashIn(t,3.32,.5)}
function sHook(t){hookFrame(t)}

/* ================= 2 · ESTO ES IGNITE STUDIO ================= */
function sIntro(t){const a=4.1,b=10.0,o=sceneOut(t,b);bgBlue(t,{core:'#1546c4'});speedLines(t,.5);
 ctx.save();ctx.globalAlpha=o;
 // bici conceptual de estudio, al fondo y difuminada en los bordes
 const kb=eo(p(t,7.9,8.6));if(kb>0){ctx.save();ctx.globalAlpha*=kb*.9;photo('C01_bici_estudio',CX-260,1110,520,215,{z:1.0,fy:.62,r:28});ctx.restore()}
 const k=eback(p(t,a+.1,a+.55)),zr=1+.05*Math.sin((t-a)*1.4);avatar(CX,640,210*zr,k,{t});
 lensFlare(CX,640,bell(t,a+.1,a+.8)*1.1,C.cyan);sparks(CX,640,t,a+.2,40,401,{spd:900,g:200,life:1,kind:'spark',cols:[C.white,C.cyan,C.pink],spread:3.1});
 wordmark(CX,935,620,eo(p(t,4.9,5.2)),{reveal:eio(p(t,4.9,5.6))});
 const ks=eo(p(t,5.4,5.8));if(ks>0){ctx.save();ctx.globalAlpha*=ks;text('STUDIO',CX,1015,30,'JBM',C.ice,'center',18);ctx.restore()}
 const kc=[6.1,7.0,8.1].map(x=>eback(p(t,x,x+.3)));const xs=[300,500,700];
 if(kb<=0)T.chips.forEach((c2,i)=>chip(c2,xs[i],1120,kc[i],{col:i===2?C.white:C.blue,fg:i===2?C.ink:C.white}));
 else T.chips.forEach((c2,i)=>chip(c2,xs[i],1060,kc[i],{col:i===2?C.white:C.blue,fg:i===2?C.ink:C.white}));
 if(kc[2]>0){ctx.save();ctx.globalAlpha*=kc[2];icon(ctx,'pin',700,980,44,C.white);ctx.restore()}
 ctx.restore();flashIn(t,a,.35)}

/* ================= 3 · VIENES A ENCENDERTE ================= */
function sEncender(t){const a=10.0,b=15.1;bgBase();
 ctx.save();ctx.translate(CX,960);ctx.rotate((t-a)*.04);ctx.translate(-CX,-960);full('C02_volante',{z:1.18+.06*p(t,a,b),fx:.4});ctx.restore();dim(.45+.15*bell(t,11.6,12.2));
 const out=eio(p(t,13.7,14.6));
 // NO VIENES SOLO A SUDAR… (se tacha)
 const os=1-eo(p(t,11.8,12.1))*.75;
 slam(T.sudar[0],CX,500,110,t,10.12,{dx:-300,from:1,o:os*(1-out)});slam(T.sudar[1],CX,630,120,t,10.45,{dx:300,from:1,o:os*(1-out)});
 const kst=eio(p(t,11.75,11.95));if(kst>0&&out<1){ctx.save();ctx.globalAlpha=1-out;ctx.strokeStyle=C.red;ctx.lineWidth=12;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(130,640);ctx.lineTo(130+740*kst,620);ctx.stroke();ctx.restore()}
 // VIENES A ENCENDERTE
 const ke=p(t,11.95,12.2);if(ke>0){const sc=1+.6*out,o=1-eo(p(t,14.5,14.95));ctx.save();ctx.globalAlpha=o;ctx.translate(CX,950);ctx.scale(sc,sc);
  slam(T.encender[0],0,-90,96,t,11.95,{from:1.4});slam(T.encender[1],0,60,200,t,12.05,{glow:true,col:C.cyan,from:2.2,maxW:900});ctx.restore()}
 lensFlare(CX,1010,bell(t,12.0,12.8)*1.3,C.cyan);
 for(let q=0;q<4;q++)sparks(CX+(q-1.5)*180,1080,t,12.1+q*.25,26,500+q*31,{spd:700,g:-300,life:1.4,kind:'spark',cols:[C.cyan,C.white,C.amber],spread:.6});
 // transición: el ala crece hacia la cámara
 const kw=p(t,13.75,14.95);if(kw>0){const s=lerp(.4,9,ei(kw));ctx.save();ctx.globalAlpha=Math.min(1,kw*3);const im=MARCA.ala_blanca;if(loaded(im)){const h=300*s,w=h*im.naturalWidth/im.naturalHeight;ctx.drawImage(im,CX-w/2,960-h/2,w,h)}ctx.restore()}
 if(t>14.8){ctx.fillStyle=`rgba(234,243,253,${eo(p(t,14.8,15.1))})`;ctx.fillRect(0,0,W,H)}
 flashIn(t,a,.25)}

/* ================= 4 · 01 SALUD ================= */
function ecg(x0,y,w,t,t0,col){const k=clamp((t-t0)/3.6);if(k<=0)return;ctx.save();ctx.strokeStyle=col;ctx.lineWidth=7;ctx.lineJoin='round';ctx.shadowColor=col;ctx.shadowBlur=24;ctx.beginPath();
 const n=Math.floor(w*k);for(let i=0;i<=n;i+=3){const u=i/w,ph=(u*3.2)%1;let v=0;if(ph>.42&&ph<.46)v=-.25;else if(ph>.46&&ph<.5)v=1.6;else if(ph>.5&&ph<.54)v=-.9;else if(ph>.6&&ph<.7)v=.25*Math.sin((ph-.6)/.1*Math.PI);
  const yy=y-v*80;i?ctx.lineTo(x0+i,yy):ctx.moveTo(x0+i,yy)}ctx.stroke();ctx.shadowBlur=0;circle(x0+n,y-0,9,C.white);ctx.restore()}
function sSalud(t){const a=15.1,b=26.2,o=sceneOut(t,b);bgBlue(t);flashIn(t,a,.6);secHeader(t,a,b,T.sec[0]);
 ctx.save();ctx.globalAlpha=o;
 const o1=1-eo(p(t,20.0,20.35));
 if(o1>0){ctx.save();ctx.globalAlpha*=o1;
  const kh=eback(p(t,16.1,16.5)),beat=[16.7,17.5,18.3,19.1,19.9].reduce((m,x)=>Math.max(m,bell(t,x,x+.3)),0),hx=lerp(CX,330,eio(p(t,18.6,19.0)));
  if(kh>0){ctx.save();ctx.translate(hx,740);const s=150*kh*(1+.12*beat);ctx.shadowColor=C.blue;ctx.shadowBlur=60;heartPath(ctx,s);ctx.fillStyle=C.blue;ctx.fill();ctx.shadowBlur=0;ctx.lineWidth=8;ctx.strokeStyle=C.ice;ctx.stroke();ctx.restore();
   text(T.corazon,hx,940,40,'ANT',C.white,'center',4)}
  const kl=eback(p(t,18.8,19.2));if(kl>0){const br=1+.08*Math.sin((t-18.8)*3.2);lungs(690,740,190*br,kl,C.pink);ctx.save();ctx.globalAlpha*=Math.min(1,kl);text(T.pulmones,690,940,40,'ANT',C.white,'center',4);ctx.restore()}
  ecg(100,1130,800,t,16.3,C.cyan);ctx.restore()}
 // ESTRÉS ↓ · SUEÑO ↑ · ENERGÍA ↑
 [[20.45,'ESTRÉS'],[21.7,'SUEÑO'],[22.95,'ENERGÍA']].forEach(([t0,lab],i)=>{const k=eback(p(t,t0,t0+.35));if(k<=0)return;const y=620+i*210;ctx.save();ctx.translate((1-Math.min(1,k))*-200,0);ctx.globalAlpha*=Math.min(1,k);
  rr(120,y-80,760,160,32);ctx.fillStyle='rgba(7,18,51,.88)';ctx.fill();ctx.strokeStyle=rgba(C.cyan,.6);ctx.lineWidth=3;ctx.stroke();
  if(i===0){const lv=1-.75*eio(p(t,t0+.3,t0+1.4));for(let j=0;j<6;j++){const on=j<Math.round(lv*6);rr(190+j*26,y+30-j*12,18,12+j*12,4);ctx.fillStyle=on?C.red:'rgba(255,255,255,.15)';ctx.fill()}}
  if(i===1)moon(240,y,46,C.pink);
  if(i===2)battery(240,y,110,58,eo(p(t,t0+.3,25.0)),C.green);
  text(lab,340,y+4,64,'ANT',C.white,'left',3);arrowUD(800,y,38,i>0,i===0?C.cyan:C.green);ctx.restore()});
 ctx.restore()}

/* ================= 5 · 02 CUERPO ================= */
function pinLabel(s,px,py,lx,ly,k,col=C.white){if(k<=0)return;ctx.save();ctx.globalAlpha*=Math.min(1,k);const pr=(performanceT*1.2)%1;circle(px,py,12,col);ctx.beginPath();ctx.arc(px,py,12+pr*26,0,TAU);ctx.strokeStyle=rgba(C.cyan,1-pr);ctx.lineWidth=4;ctx.stroke();
 ctx.strokeStyle=col;ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(px,py);ctx.lineTo(lerp(px,lx,k),lerp(py,ly,k));ctx.stroke();if(k>.6)chip(s,lx,ly,eback(clamp((k-.6)/.4)),{col:C.blue,size:36});ctx.restore()}
let performanceT=0;
function sCuerpo(t){performanceT=t;const a=26.2,b=37.6,o=sceneOut(t,b);bgBlue(t);flashIn(t,a,.6);secHeader(t,a,b,T.sec[1]);
 ctx.save();ctx.globalAlpha=o;
 const swap=eio(p(t,32.25,32.7));
 // piernas en la bici (toma conceptual)
 const k1=eo(p(t,27.0,27.5))*(1-swap);if(k1>0){ctx.save();ctx.globalAlpha*=k1;const y=540+(1-k1)*80;ctx.shadowColor=rgba(C.blue,.6);ctx.shadowBlur=50;rr(150,y,700,760,36);ctx.fillStyle=C.ice;ctx.fill();ctx.shadowBlur=0;
  photo('C04_piernas_pedaleo',150,y,700,760,{z:1.05+.05*p(t,27,32.5),fy:.35,r:36});
  pinLabel(T.cuerpo1[0],560,y+260,330,y+120,eo(p(t,28.2,28.6)));pinLabel(T.cuerpo1[1],470,y+120,700,y+60,eo(p(t,28.9,29.3)));
  const kc=eo(p(t,30.4,30.7));if(kc>0){const n=Math.floor(clamp((t-30.45)/1.7)*60);ctx.save();ctx.globalAlpha*=kc;rr(250,y+600,500,130,30);ctx.fillStyle='rgba(3,8,23,.85)';ctx.fill();
   text(String(n).padStart(3,'0'),400,y+668,92,'ANT',C.white,'center',4);text(T.pedaladas,610,y+668,30,'JBM',C.pink,'center',3);ctx.restore()}
  ctx.restore()}
 // clases de fuerza: foto «MOVEMENT» de su sitio con duotono azul
 if(swap>0){ctx.save();ctx.globalAlpha*=swap;slam(T.fuerza,CX,520,70,t,32.7,{from:1.2});
  photo('I02_movement',190,600,620,760,{z:1.08-.05*p(t,32.3,37),fy:.3,r:36});
  [[34.4,T.cuerpo2[0],330,760],[35.2,T.cuerpo2[1],640,960],[35.9,T.cuerpo2[2],380,1160]].forEach(([t0,s,x,y])=>chip(s,x,y,eback(p(t,t0,t0+.3)),{col:C.blue,size:40}));
  ctx.restore()}
 ctx.restore()}

/* ================= 6 · 03 RENDIMIENTO ================= */
function sRend(t){const a=37.6,b=50.9,o=sceneOut(t,b);bgBase();
 const sw=eio(p(t,43.7,44.1));
 full('C05_manos_manubrio',{z:1.12-.06*p(t,a,44),alpha:1-sw});full('C06_bici_azul',{z:1.15-.08*p(t,44,b),fy:.6,alpha:sw});dim(.5+.15*sw);flashIn(t,a,.6);secHeader(t,a,b,T.sec[2]);
 ctx.save();ctx.globalAlpha=o;
 const ob=1-sw;if(ob>0){ctx.save();ctx.globalAlpha*=ob;
  [[39.85,T.rend[0]],[41.3,T.rend[1]],[42.4,T.rend[2]]].forEach(([t0,s],i)=>{const k=eo(p(t,t0-.25,t0));if(k<=0)return;const y=700+i*190,f=eio(p(t,t0,t0+.9)),fl=bell(t,43.1,43.5);ctx.save();ctx.globalAlpha*=k;
   text(s,140,y-50,54,'ANT',C.white,'left',4);rr(140,y,740,46,23);ctx.fillStyle='rgba(255,255,255,.14)';ctx.fill();
   const g=ctx.createLinearGradient(140,0,880,0);g.addColorStop(0,C.blue);g.addColorStop(1,C.pink);rr(140,y,Math.max(46,740*f),46,23);ctx.fillStyle=g;ctx.shadowColor=C.cyan;ctx.shadowBlur=30+40*fl;ctx.fill();ctx.shadowBlur=0;
   if(f>.02)sparks(140+740*f,y+23,t,t0+.9,16,700+i*13,{spd:500,g:600,life:.6,kind:'spark',cols:[C.white,C.cyan]});ctx.restore()});ctx.restore()}
 // sus clases reales (tomadas de su horario)
 if(sw>0){T.clases.forEach(([tipo,nom],i)=>{const t0=[44.3,44.95,45.55,46.2,48.0][i],k=eback(p(t,t0,t0+.3));if(k<=0)return;const y=560+i*150;ctx.save();ctx.globalAlpha*=Math.min(1,k);ctx.translate((1-Math.min(1,k))*260,0);
  rr(130,y-58,740,116,26);ctx.fillStyle=i===4?'rgba(31,107,255,.92)':'rgba(7,18,51,.9)';ctx.fill();ctx.strokeStyle=rgba(i===4?C.white:C.cyan,.7);ctx.lineWidth=3;ctx.stroke();
  rr(160,y-26,150,52,14);ctx.fillStyle=i===4?C.white:C.blue;ctx.fill();text(tipo,235,y+2,28,'JBM',i===4?C.blue:C.white,'center',3);
  text(nom,340,y+4,fitSize(nom,'ANT',58,500,2),'ANT',C.white,'left',2);ctx.restore()})}
 ctx.restore()}

/* ================= 7 · 04 COMUNIDAD ================= */
const SHARDS=(()=>{const out=[],cols=4,rows=6,w=540/cols,h=680/rows,pts=[];for(let j=0;j<=rows;j++)for(let i=0;i<=cols;i++){const jx=(i>0&&i<cols)?(rnd(i*7+j*13)-.5)*w*.6:0,jy=(j>0&&j<rows)?(rnd(i*3+j*17)-.5)*h*.6:0;pts.push([i*w+jx,j*h+jy])}
 const P=(i,j)=>pts[j*(cols+1)+i];for(let j=0;j<rows;j++)for(let i=0;i<cols;i++){const A=P(i,j),B=P(i+1,j),Cc=P(i+1,j+1),D=P(i,j+1);out.push([A,B,Cc],[A,Cc,D])}return out})();
function coachCard(n,x,y,w,h,k=1,{label=true,z=1}={}){if(k<=0)return;ctx.save();ctx.globalAlpha*=Math.min(1,k);ctx.shadowColor='rgba(0,0,0,.45)';ctx.shadowBlur=30;rr(x,y,w,h,24);ctx.fillStyle=C.ice;ctx.fill();ctx.shadowBlur=0;
 photo('co_'+n,x,y,w,h,{fy:.25,r:24,z,src:IMG['co_'+n]});if(label){const g=ctx.createLinearGradient(0,y+h*.62,0,y+h);g.addColorStop(0,'rgba(3,8,23,0)');g.addColorStop(1,'rgba(3,8,23,.85)');ctx.fillStyle=g;rr(x,y,w,h,24);ctx.fill();
  text(n==='Sebastian'?'SEBASTIÁN':n.toUpperCase(),x+w/2,y+h-34,fitSize(n.toUpperCase(),'ANT',44,w-30,3),'ANT',C.white,'center',3)}
 rr(x,y,w,h,24);ctx.strokeStyle=rgba(C.cyan,.55);ctx.lineWidth=3;ctx.stroke();ctx.restore()}
const MONT=['Mime','Julius','Montse','Zamora','Vale'];
function sComunidad(t){const a=50.9,b=61.9,o=sceneOut(t,b);bgBlue(t);flashIn(t,a,.6);secHeader(t,a,b,T.sec[3]);
 ctx.save();ctx.globalAlpha=o;
 // espejo
 const km=eo(p(t,51.6,52.1)),br=p(t,53.75,54.6),mx=230,my=560;
 if(km>0&&br<1){ctx.save();ctx.globalAlpha*=km;
  const drawMirror=g=>{const gr=g.createLinearGradient(mx,my,mx+540,my+680);gr.addColorStop(0,'#cfe0ff');gr.addColorStop(.5,'#7da2e6');gr.addColorStop(1,'#2a4fa8');g.fillStyle=gr;g.fillRect(mx,my,540,680);
   g.save();g.globalAlpha=.55;photo('I03_getting_started',mx,my,540,680,{z:1.3,fy:.2});g.restore();g.fillStyle='rgba(255,255,255,.18)';g.beginPath();g.moveTo(mx+60,my);g.lineTo(mx+200,my);g.lineTo(mx+40,my+680);g.lineTo(mx-100,my+680);g.closePath();g.fill()};
  if(br<=0){ctx.save();rr(mx,my,540,680,30);ctx.clip();drawMirror(ctx);ctx.restore();rr(mx-10,my-10,560,700,36);ctx.strokeStyle=C.ice;ctx.lineWidth=10;ctx.stroke()}
  else SHARDS.forEach((s,i)=>{const cxs=(s[0][0]+s[1][0]+s[2][0])/3,cys=(s[0][1]+s[1][1]+s[2][1])/3,dx=(cxs-270)*(1.6+rnd(i)*1.6),dy=(cys-340)*(1.4+rnd(i*3)*1.2)+900*br*br,rot=(rnd(i*5)-.5)*4*br,e=eo(br);
   ctx.save();ctx.globalAlpha*=1-br;ctx.translate(mx+cxs+dx*e,my+cys+dy*e);ctx.rotate(rot);ctx.translate(-(mx+cxs),-(my+cys));ctx.beginPath();s.forEach(([x,y],j)=>j?ctx.lineTo(mx+x,my+y):ctx.moveTo(mx+x,my+y));ctx.closePath();ctx.save();ctx.clip();drawMirror(ctx);ctx.restore();ctx.strokeStyle='rgba(255,255,255,.8)';ctx.lineWidth=2;ctx.stroke();ctx.restore()});
  ctx.restore();const kt=eo(p(t,51.9,52.3))*(1-eo(p(t,53.6,53.8)));if(kt>0){ctx.save();ctx.globalAlpha*=kt;text(T.espejo,CX,1310,fitSize(T.espejo,'ANT',52,840,2),'ANT',C.white,'center',2);ctx.restore()}}
 // ES LA GENTE
 const kg=p(t,53.75,54.0),og=1-eo(p(t,55.1,55.4));if(kg>0&&og>0){ctx.save();ctx.globalAlpha*=og;slam(T.gente,CX,880,190,t,53.75,{glow:true,col:C.white,from:2});ctx.restore();lensFlare(CX,880,bell(t,53.75,54.4)*1.2,C.cyan)}
 // muro de coaches (11, sin repetir)
 const kw=eo(p(t,55.25,55.7)),ow=1-eo(p(t,59.6,59.9));if(kw>0&&ow>0){ctx.save();ctx.globalAlpha*=kw*ow;
  text(T.coachLabel,CX,470,fitSize(T.coachLabel,'JBM',28,840,3),'JBM',C.pink,'center',3);
  const cw=200,ch=245,dy=-30*eio(p(t,55.25,59.9));
  for(let ix=0;ix<12;ix++){const c=ix%4,r=Math.floor(ix/4),x=75+c*(cw+16),y=520+r*(ch+12)+dy,k=eback(p(t,55.4+ix*.3,55.4+ix*.3+.35));
   if(ix<11)coachCard(T.coaches[ix],x,y,cw,ch,k);
   else if(k>0){ctx.save();ctx.globalAlpha*=Math.min(1,k);rr(x,y,cw,ch,24);ctx.fillStyle=C.blue;ctx.fill();ctx.restore();avatar(x+cw/2,y+ch/2-20,62,k,{ring:false});ctx.save();ctx.globalAlpha*=Math.min(1,k);text('Y TÚ',x+cw/2,y+ch-40,40,'ANT',C.white,'center',3);ctx.restore()}}
  ctx.restore()}
 // montaje rápido
 if(t>=59.9){const i=Math.min(MONT.length-1,Math.floor((t-59.9)/.4)),t0=59.9+i*.4,k=eo(p(t,t0,t0+.12)),z=1.08-.08*p(t,t0,t0+.4);
  ctx.save();ctx.translate(CX,900);ctx.scale(z,z);ctx.translate(-CX,-900);coachCard(MONT[i],CX-290,540,580,740,k);ctx.restore();flashIn(t,t0,.35)}
 ctx.restore()}

/* ================= 8 · NADIE ENTRENA SOLO ================= */
function sJuntos(t){const a=61.9,b=67.5,o=sceneOut(t,b);bgBase();full('I01_strength',{z:1.18-.07*p(t,a,b),fy:.3});dim(.35);flashIn(t,a,.7);
 ctx.save();ctx.globalAlpha=o;const up=eio(p(t,64.0,64.4));
 T.nadie.forEach((s,i)=>{const y=lerp(560+i*180,450+i*70,up),sz=lerp(170,64,up);slam(s,CX,y,sz,t,62.45+i*.35,{from:1.8,col:i===2?C.cyan:C.white,glow:i===2})});
 const kj=p(t,64.2,64.5);if(kj>0){slam('CADA META',CX,880,110,t,64.2,{from:1.3});slam('SE CELEBRA',CX,1010,110,t,64.55,{from:1.3});slam('JUNTOS',CX,1170,170,t,66.25,{glow:true,col:C.cyan,from:2.2})}
 for(let q=0;q<3;q++)sparks(250+q*250,1200,t,66.3+q*.08,40,900+q*41,{spd:1100,g:1300,life:1.2,size:12,cols:[C.white,C.cyan,C.blue,C.amber],spread:.7});
 ctx.restore()}

/* ================= 9 · HORARIOS ================= */
function sHorarios(t){const a=67.5,b=72.2,o=sceneOut(t,b);bgBlue(t,{core:'#0f3fb8'});flashIn(t,a,.5);
 ctx.save();ctx.globalAlpha=o;
 slam(T.horarios,CX,500,78,t,67.75,{from:1.2});slam(T.seis,CX,670,230,t,68.0,{glow:true,col:C.amber,from:1.8});
 T.dias.forEach(([d,h],i)=>{const t0=68.4+i*.25,k=eback(p(t,t0,t0+.3));if(k<=0)return;const x=95+i*123,y=900;ctx.save();ctx.globalAlpha*=Math.min(1,k);ctx.translate(x+55,y+80);ctx.scale(k,k);ctx.translate(-x-55,-y-80);
  rr(x,y,110,160,22);ctx.fillStyle=i===0?C.blue:'rgba(7,18,51,.9)';ctx.fill();ctx.strokeStyle=rgba(C.cyan,.7);ctx.lineWidth=3;ctx.stroke();
  text(d,x+55,y+48,28,'JBM',C.pink,'center',2);text(h,x+55,y+102,38,'ANT',C.white,'center',1);text('AM',x+55,y+138,20,'JBM',C.gray,'center',2);ctx.restore()});
 chip(T.semana,CX,1170,eback(p(t,69.8,70.1)),{col:C.white,fg:C.blue,size:38});
 ctx.restore()}

/* ================= 10 · RESERVA Y ETIQUETA ================= */
const TAP=73.6,SEND2=78.6,TY2=77.2;
// pantalla de una app de reservas genérica (no es la app real)
function screenChat(t){const Ws=SCR.w,Hs=SCR.h;ctx.fillStyle='#F4F8FF';ctx.fillRect(0,0,Ws,Hs);
 ctx.fillStyle=C.blue;ctx.fillRect(0,0,Ws,150);const im=MARCA.ignite_blanco;if(loaded(im)){const w=210,h=w*im.naturalHeight/im.naturalWidth;ctx.drawImage(im,Ws/2-w/2,95-h/2,w,h)}
 text('Reserva tu clase',36,200,26,'SGB','#0B1A3A','left');
 ['LUN','MAR','MIÉ','JUE','VIE'].forEach((d,i)=>{const x=36+i*80;rr(x,232,68,74,14);ctx.fillStyle=i===0?C.blue:'#E3ECFB';ctx.fill();text(d,x+34,256,16,'JBM',i===0?C.white:'#43537a','center');text(String(26+i<=31?26+i:1),x+34,286,24,'SGB',i===0?C.white:'#0B1A3A','center')});
 rr(24,336,Ws-48,250,24);ctx.fillStyle=C.white;ctx.shadowColor='rgba(15,40,100,.18)';ctx.shadowBlur=24;ctx.fill();ctx.shadowBlur=0;
 const ok=t>=TAP+.1;rr(24,336,10,250,5);ctx.fillStyle=C.blue;ctx.fill();
 text(T.app.clase,56,384,24,'SGB','#0B1A3A','left');text(T.app.hora,56,424,34,'ANT',C.blue,'left',1);
 const jim=IMG.co_Julius;ctx.save();ctx.beginPath();ctx.arc(80,500,34,0,TAU);ctx.clip();if(loaded(jim))ctx.drawImage(jim,46,466,68,68);ctx.restore();text(T.app.coach,128,502,22,'SGM','#43537a','left');
 const pr=1-.08*bell(t,TAP-.05,TAP+.15);ctx.save();ctx.translate(Ws/2,650);ctx.scale(pr,pr);rr(-180,-38,360,76,38);ctx.fillStyle=ok?C.green:C.blue;ctx.fill();
 if(ok){text(T.app.ok,-18,3,28,'SGB',C.white,'center',2);check(118,0,22,C.white,6)}else text(T.app.btn,0,3,28,'SGB',C.white,'center',3);ctx.restore();
 const kr=bell(t,TAP,TAP+.5);if(kr>0){ctx.beginPath();ctx.arc(Ws/2,650,40+kr*120,0,TAU);ctx.strokeStyle=rgba(C.blue,kr);ctx.lineWidth=5;ctx.stroke()}
 if(t<TAP+.2){const e=eio(p(t,72.9,TAP));circle(lerp(Ws*.8,Ws/2+30,e),lerp(Hs*.85,668,e),26,'rgba(31,107,255,.35)')}}
function screenComments(t){const Ws=SCR.w,Hs=SCR.h;ctx.fillStyle='#0B1222';ctx.fillRect(0,0,Ws,Hs);
 text('Comentarios',Ws/2,100,24,'SGB',C.white);ctx.fillStyle='rgba(255,255,255,.12)';ctx.fillRect(0,134,Ws,2);
 for(let k=0;k<3;k++){const y=170+k*120;circle(46,y+24,22,['#334155','#1E3A8A','#4C1D95'][k]);bar(ctx,82,y+6,100+k*24,13,'#94A3B8');bar(ctx,82,y+32,270-k*40,13,'#E2E8F0',.8);bar(ctx,82,y+54,180+k*20,13,'#E2E8F0',.58)}
 const kn=eback(p(t,SEND2+.15,SEND2+.4));if(kn>0){ctx.save();ctx.translate(46,560);ctx.scale(kn,kn);ctx.translate(-46,-560);rr(16,516,Ws-32,96,20);ctx.fillStyle=rgba(C.cyan,.16);ctx.fill();ctx.strokeStyle=rgba(C.cyan,.7);ctx.lineWidth=2;ctx.stroke();
  circle(59,560,22,C.cyan);text('tú',82,540,17,'SGM','#94A3B8','left');text(T.tag,82,578,fitSize(T.tag,'SGB',26,Ws-110),'SGB',C.white,'left');ctx.restore()}
 rr(18,Hs-90,Ws-110,60,30);ctx.fillStyle='#1E293B';ctx.fill();
 const n=t>=SEND2?0:clamp(Math.floor((t-TY2)/.06)+1,0,T.tag.length),typed=T.tag.slice(0,n),fs=fitSize(T.tag,'SGB',24,Ws-160);
 if(typed)text(typed,40,Hs-59,fs,'SGB',C.white,'left');else if(t<SEND2)text('Añade un comentario…',40,Hs-59,19,'SGM','#64748B','left');
 const pr=1-.15*bell(t,SEND2-.1,SEND2+.05);ctx.save();ctx.translate(Ws-59,Hs-59);ctx.scale(pr,pr);circle(0,0,28,C.cyan);icon(ctx,'send',2,0,28,C.ink);ctx.restore()}
function sReserva(t){const a=72.2,b=80.3,o=sceneOut(t,b);bgBlue(t,{core:'#123a9e'});flashIn(t,a,.5);
 ctx.save();ctx.globalAlpha=o;const mode=t<76.45?'chat':'comments',sw=bell(t,76.25,76.65);
 const ph=eo(p(t,72.25,72.7)),P={x:500,y:960+(1-ph)*800},s=.78,rot=(-2+1*Math.sin(t*.8))*DEG;
 drawPhone(P,s,rot,t,mode,{glow:1});if(sw>0){ctx.fillStyle=`rgba(234,243,253,${sw*.5})`;ctx.fillRect(0,0,W,H)}
 const kt=eo(p(t,72.4,72.8))*(1-eo(p(t,76.2,76.45)));if(kt>0){ctx.save();ctx.globalAlpha*=kt;text('RESERVA DESDE LA APP',CX,430,fitSize('RESERVA DESDE LA APP','ANT',74,820,3),'ANT',C.white,'center',3);ctx.restore()}
 if(t>=76.45){slam(T.etiqueta[0],CX,400,70,t,76.55,{from:1.2});slam(T.etiqueta[1],CX,490,82,t,76.85,{glow:true,col:C.cyan,from:1.4})}
 ctx.restore()}

/* ================= 11 · CIERRE ================= */
function sCierre(t){const a=80.3,b=90;bgBlue(t,{core:'#1f5fe0'});speedLines(t,.35);flashIn(t,a,.7);
 const m=eio(p(t,83.45,83.85)),f=eio(p(t,86.6,87.0));
 // logo en avatar
 const ka=eback(p(t,80.35,80.8)),ay=lerp(lerp(650,500,m),430,f),ar=lerp(lerp(220,130,m),120,f);avatar(CX,ay,ar,ka,{t});lensFlare(CX,ay,bell(t,80.35,81.0)*1.2,C.cyan);
 sparks(CX,ay,t,80.4,44,1201,{spd:950,g:250,life:1,kind:'spark',cols:[C.white,C.cyan,C.pink],spread:3.1});
 const ow=1-m;wordmark(CX,950,600,eo(p(t,80.6,80.9))*ow,{reveal:eio(p(t,80.6,81.3))});
 if(ow>0){const ks=eo(p(t,81.0,81.3))*ow;ctx.save();ctx.globalAlpha=ks;text('STUDIO',CX,1028,30,'JBM',C.ice,'center',18);ctx.restore();chip(T.lugar,CX,1130,eback(p(t,81.9,82.2))*ow,{col:C.white,fg:C.blue,size:32})}
 // ENCIÉNDETE (3 s sola)
 const ke=p(t,83.6,83.85);if(ke>0){const y=lerp(830,690,f),sz=lerp(250,140,f);slam(T.enciendete,CX,y,sz,t,83.6,{glow:true,col:C.white,from:2.4,maxW:lerp(880,760,f)});lensFlare(CX,y,bell(t,83.6,84.3)*1.3,C.cyan);
  for(let q=0;q<4;q++)sparks(CX+(q-1.5)*200,y+60,t,83.7+q*.2,30,1300+q*17,{spd:800,g:-200,life:1.3,kind:'spark',cols:[C.cyan,C.white,C.amber],spread:.7})}
 // usuario y botón SEGUIR con cursor y clic
 const ku=eback(p(t,87.1,87.4));if(ku>0){ctx.save();ctx.translate(CX,860);ctx.scale(ku,ku);text(T.usuario,0,0,fitSize(T.usuario,'SGB',62,820),'SGB',C.white);ctx.restore()}
 const kbt=eback(p(t,87.35,87.7)),clicked=t>=88.2,press=1-.08*Math.sin(Math.PI*p(t,88.15,88.35));
 if(kbt>0){ctx.save();ctx.translate(CX,1020);ctx.scale(kbt*press,kbt*press);rr(-250,-59,500,116,59);ctx.fillStyle=clicked?C.white:C.blue;ctx.shadowColor=rgba(C.cyan,.7);ctx.shadowBlur=40;ctx.fill();ctx.shadowBlur=0;
  if(clicked){text('SIGUIENDO',-40,4,56,'SGB',C.blue,'center',2);check(180,0,36,C.blue,10)}else text('SEGUIR',0,4,59,'SGB',C.white,'center',4);ctx.restore();
  const kr=bell(t,88.2,88.8);if(kr>0){ctx.save();ctx.globalAlpha=kr;rr(CX-250-60*kr,1020-59-30*kr,500+120*kr,116+60*kr,90);ctx.strokeStyle=C.ice;ctx.lineWidth=4;ctx.stroke();ctx.restore()}}
 const kc=p(t,87.4,88.15);if(kc>0&&t<89.3){const e=eio(kc),x=lerp(880,610,e),y=lerp(1330,1050,e);ctx.save();ctx.globalAlpha=1-p(t,88.9,89.3);cursorArrow(x,y,1.3);ctx.restore()}}
