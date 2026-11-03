
/* ================= UTILIDADES (estilo Matbarre: blush, rosa empolvado, óvalos, Poppins ligera) ================= */
const sm=x=>x*x*(3-2*x),es=x=>sm(clamp(x));
function flashIn(t,a,k=.12){if(t>=a&&t<a+.5){ctx.fillStyle=`rgba(251,247,245,${(1-p(t,a,a+.5))*k})`;ctx.fillRect(0,0,W,H)}}
function sceneOut(t,b,d=.3){return 1-es(p(t,b-d,b-.02))}
function blush(){ctx.fillStyle=C.blush;ctx.fillRect(0,0,W,H);const g=ctx.createRadialGradient(W*.7,H*.25,50,W*.7,H*.25,H*.8);g.addColorStop(0,'rgba(255,255,255,.55)');g.addColorStop(1,'rgba(234,220,215,.35)');ctx.fillStyle=g;ctx.fillRect(0,0,W,H)}
const cream=blush;
function photo(name,x,y,w,h,{z=1,fx=.5,fy=.5,alpha=1,r=0,arch=false,oval=false,dx=0,dy=0,gray=false}={}){const im=IMG[name];if(alpha<=0)return;ctx.save();ctx.globalAlpha*=alpha;ctx.beginPath();
 if(oval)ctx.ellipse(x+w/2,y+h/2,w/2,h/2,0,0,TAU);else if(arch){ctx.moveTo(x,y+h);ctx.lineTo(x,y+w/2);ctx.arc(x+w/2,y+w/2,w/2,Math.PI,0);ctx.lineTo(x+w,y+h);ctx.closePath()}else if(r>0)ctx.roundRect(x,y,w,h,r);else ctx.rect(x,y,w,h);ctx.clip();
 if(!loaded(im)){ctx.fillStyle='#d9c9c4';ctx.fillRect(x,y,w,h);ctx.restore();return}
 if(gray)ctx.filter='grayscale(1)';
 const iw=im.naturalWidth,ih=im.naturalHeight,s=Math.max(w/iw,h/ih)*z,dw=iw*s,dh=ih*s;ctx.drawImage(im,x+(w-dw)*fx+dx,y+(h-dh)*fy+dy,dw,dh);ctx.restore()}
function full(name,o={}){photo(name,0,0,W,H,o)}
function veil(a,col='246,239,236'){if(a<=0)return;ctx.fillStyle=`rgba(${col},${a})`;ctx.fillRect(0,0,W,H)}
function gradV(y0,y1,c0,c1){const g=ctx.createLinearGradient(0,y0,0,y1);g.addColorStop(0,c0);g.addColorStop(1,c1);ctx.fillStyle=g;ctx.fillRect(0,y0,W,y1-y0)}
function topVeil(y1,a=.97,hold=.6){const g=ctx.createLinearGradient(0,0,0,y1);g.addColorStop(0,`rgba(246,239,236,${a})`);g.addColorStop(hold,`rgba(246,239,236,${a*.93})`);g.addColorStop(1,'rgba(246,239,236,0)');ctx.fillStyle=g;ctx.fillRect(0,0,W,y1)}
function soft(s,x,y,size,font,col,t,t0,{d=1.0,o=1,ls=0,align='center',rise=24}={}){const k=es(p(t,t0,t0+d))*o;if(k<=0)return;ctx.save();ctx.globalAlpha*=k;
 ctx.filter=`blur(${(1-k)*6}px)`;text(s,x,y+(1-k)*rise,size,font,col,align,ls);ctx.restore()}
function letters(s,x,y,size,font,col,t,t0,{per=.06,d=.6,o=1,ls=0}={}){if(o<=0)return;ctx.save();ctx.font=`${size}px ${font}`;ctx.letterSpacing=ls+'px';const wt=ctx.measureText(s).width;let cx=x-wt/2;
 [...s].forEach((ch,i)=>{const w=ctx.measureText(ch).width,k=es(p(t,t0+i*per,t0+i*per+d))*o;if(k>0){ctx.save();ctx.globalAlpha*=k;ctx.filter=`blur(${(1-k)*5}px)`;text(ch,cx,y+(1-k)*14,size,font,col,'left',0);ctx.restore()}cx+=w+ls});ctx.letterSpacing='0px';ctx.restore()}
function hline(x0,x1,y,k,col=C.rose,lw=2){if(k<=0)return;ctx.save();ctx.strokeStyle=col;ctx.lineWidth=lw;ctx.globalAlpha*=.8;const m=(x0+x1)/2,h=(x1-x0)/2*k;ctx.beginPath();ctx.moveTo(m-h,y);ctx.lineTo(m+h,y);ctx.stroke();ctx.restore()}
// título en dos tonos como en su sitio («Class» + «es» en rosa)
function two(a,b,x,y,size,font,t,t0,{d=1,ca=C.ink,cb=C.rose,o=1}={}){const k=es(p(t,t0,t0+d))*o;if(k<=0)return;ctx.save();ctx.globalAlpha*=k;ctx.filter=`blur(${(1-k)*6}px)`;
 const wa=tw(a,size,font,0),wb=tw(b,size,font,0),x0=x-(wa+wb)/2,yy=y+(1-k)*24;text(a,x0,yy,size,font,ca,'left',0);text(b,x0+wa,yy,size,font,cb,'left',0);ctx.restore()}
function dust(t,k=1,col='186,126,117'){if(k<=0)return;ctx.save();for(let i=0;i<34;i++){const x=(rnd(i*3.3)*W+Math.sin(t*.2+i)*40+t*8*(rnd(i)-.3)+W*4)%W,y=(rnd(i*7.1)*H-t*(10+rnd(i*2)*18)+H*4)%H,r=1.5+rnd(i*5)*3,a=(.08+.22*rnd(i*9))*(.5+.5*Math.sin(t*.8+i))*k;
 ctx.fillStyle=`rgba(${col},${a})`;ctx.beginPath();ctx.arc(x,y,r,0,TAU);ctx.fill()}ctx.restore()}
function mark(name,x,y,w,k=1,{blur=true}={}){const im=MARCA[name];if(k<=0||!loaded(im))return;const h=w*im.naturalHeight/im.naturalWidth;ctx.save();ctx.globalAlpha*=k;if(blur)ctx.filter=`blur(${(1-k)*8}px)`;ctx.drawImage(im,x-w/2,y-h/2,w,h);ctx.restore()}
// óvalo con la mancha rosa detrás (como sus tarjetas de clases y coaches)
function ovalCard(name,cx,cy,w,h,k,{z=1.05,fy=.5,fx=.5,blob=true,gray=false,bob=0}={}){if(k<=0)return;ctx.save();ctx.globalAlpha*=k;
 if(blob){ctx.fillStyle='rgba(186,126,117,.22)';ctx.beginPath();ctx.ellipse(cx-w*.18,cy+h*.12,w*.46,h*.4,0,0,TAU);ctx.fill()}
 const s=.94+.06*k;ctx.translate(cx,cy+bob);ctx.scale(s,s);photo(name,-w/2,-h/2,w,h,{oval:true,z,fy,fx,gray});ctx.restore()}
function chip(s,x,y,k,{size=30,dot=true,bg='rgba(251,247,245,.94)',fg=C.ink,align='left'}={}){if(k<=0)return;ctx.save();ctx.globalAlpha*=k;const w=tw(s,size,'PP4',1)+size*1.6+(dot?26:0),h=size*2.1;const x0=align==='left'?x+(1-k)*-30:x-w/2;
 ctx.shadowColor='rgba(126,74,70,.18)';ctx.shadowBlur=24;ctx.shadowOffsetY=8;rr(x0,y-h/2,w,h,h/2);ctx.fillStyle=bg;ctx.fill();ctx.shadowColor='transparent';
 if(dot)circle(x0+size*.8+6,y,8,C.rose);text(s,x0+size*.8+(dot?26:0),y+2,size,'PP4',fg,'left',1);ctx.restore()}
function ring(x,y,r,k,col=C.rose,lw=10){ctx.save();ctx.lineCap='round';ctx.strokeStyle='rgba(186,126,117,.18)';ctx.lineWidth=lw;ctx.beginPath();ctx.arc(x,y,r,0,TAU);ctx.stroke();
 if(k>0){ctx.strokeStyle=col;ctx.beginPath();ctx.arc(x,y,r,-Math.PI/2,-Math.PI/2+TAU*k);ctx.stroke()}ctx.restore()}
function sparkle(x,y,s,col=C.rose){ctx.save();ctx.translate(x,y);ctx.fillStyle=col;ctx.beginPath();for(let i=0;i<8;i++){const a=i*Math.PI/4,r=i%2?s*.28:s;ctx.lineTo(Math.cos(a-Math.PI/2)*r,Math.sin(a-Math.PI/2)*r)}ctx.closePath();ctx.fill();ctx.restore()}
function planeIcon(x,y,s,k,col){if(k<=0)return;ctx.save();ctx.globalAlpha*=k;ctx.translate(x,y);ctx.scale(s,s);ctx.strokeStyle=col;ctx.lineWidth=3;ctx.lineJoin='round';
 ctx.beginPath();ctx.moveTo(-40,0);ctx.lineTo(44,-36);ctx.lineTo(18,40);ctx.lineTo(4,12);ctx.closePath();ctx.moveTo(4,12);ctx.lineTo(44,-36);ctx.stroke();ctx.restore()}
function tapDot(x,y,k){if(k<=0)return;ctx.save();ctx.globalAlpha*=k;circle(x,y,30,'rgba(46,38,38,.18)');circle(x,y,15,'rgba(46,38,38,.42)');ctx.restore()}

/* ================= 1 · 10 · 20 · 30 ================= */
const HK=[{t:0,foto:'N3_espalda',fy:.35,gray:true},{t:2.75,foto:'F05_sculpt',fy:.3},{t:4.4,foto:'F02_tres_pierna',fy:.5}];
function hookFrame(t,{titles=true}={}){blush();dust(t,.5);
 const jp=es(p(t,7.25,7.95));
 if(jp<1){ctx.save();ctx.globalAlpha*=1-jp;
  let idx=0;HK.forEach((h,i)=>{if(t>=h.t)idx=i});
  for(let j=Math.max(0,idx-1);j<=idx;j++){const h=HK[j],k=j===idx?(j===0?1:es(p(t,h.t,h.t+.45))):1;if(k<=0)continue;
   ovalCard(h.foto,CX,995,560,680,k,{z:1.08-.04*p(t,h.t,h.t+3),fy:h.fy,gray:h.gray,blob:j===0||k<1?true:false})}
  if(titles){const [n,l,ph]=T.hook[idx],kn=idx===0?1:es(p(t,HK[idx].t,HK[idx].t+.4));
   // número grande: el anterior se va hacia arriba
   if(idx>0){const ko=1-kn;if(ko>0){ctx.save();ctx.globalAlpha*=ko;text(T.hook[idx-1][0],CX,390-60*kn,250,'PP3',C.rose,'center',0);ctx.restore()}}
   ctx.save();ctx.globalAlpha*=kn;ctx.filter=`blur(${(1-kn)*8}px)`;text(n,CX,390+(1-kn)*60,250,'PP3',C.rose,'center',0);ctx.restore();
   ctx.save();ctx.globalAlpha*=kn;text(l.toUpperCase(),CX,555,24,'PP4',C.ink,'center',12);ctx.restore();
   soft(ph,CX,618,64,'CGI4',C.ink,t,HK[idx].t+(idx===0?.9:.35),{d:.6});
   // tres puntitos de avance
   [0,1,2].forEach(i=>circle(CX-26+i*26,1355,i===idx?6:4,i<=idx?C.rose:'rgba(186,126,117,.3)'))}
  ctx.restore()}
 if(jp>0){ctx.save();ctx.globalAlpha*=jp;full('N4_luz_barra',{z:1.12-.06*p(t,7.25,11.5)});veil(.45);
  soft('“10 · 20 · 30”',CX,520,54,'CGI4',C.roseD,t,7.4,{d:.8});
  soft(T.jp,CX,680,120,'CGI3',C.ink,t,7.6,{d:1});hline(370,630,760,es(p(t,8.2,9.0)));
  soft(T.jpSub,CX,815,22,'PP4',C.ink,t,8.4,{ls:9});
  two('casi ','100 años',CX,980,84,'PP3',t,9.45,{d:.9});
  ctx.restore()}}
function sHook(t){hookFrame(t)}

/* ================= 2 · MATBARRE STUDIO ================= */
function sMarca(t){const a=11.5,b=19.7,o=sceneOut(t,b);blush();
 full('F01_tres_plancha',{z:1.16+.06*es(p(t,a,b)),fx:.58,fy:.5,dy:230,alpha:es(p(t,a,a+1))});
 topVeil(1280,.99,.72);
 ctx.save();ctx.globalAlpha=o;
 soft(T.lugar,CX,330,24,'PP4',C.roseD,t,11.8,{ls:10});hline(400,600,370,es(p(t,12.1,12.9)));
 const kq=es(p(t,13.1,13.8))*(1-es(p(t,14.6,15.0)));if(kq>0){ctx.save();ctx.globalAlpha*=kq;text('esa filosofía',CX,520,90,'CGI3',C.ink,'center',0);text('tiene un nombre',CX,610,56,'CGI4',C.roseD,'center',0);ctx.restore()}
 const kl=es(p(t,14.85,15.9));mark('logo_rosa',CX,500,lerp(560,640,kl),kl);
 soft(T.mtm,CX,640,24,'PP4',C.ink,t,15.7,{ls:14});
 soft(T.momento[0],CX,760,72,'CGI3',C.ink,t,16.75,{d:.9});soft(T.momento[1],CX,845,72,'CGI4',C.roseD,t,18.15,{d:.9});
 ctx.restore();flashIn(t,a,.16)}

/* ================= 3–5 · CLASES ================= */
const CLT=[{a:19.7,b:25.6,chips:[22.15,23.3,24.2],dato:20.6},{a:25.6,b:31.6,chips:[26.95,28.55,29.6],dato:26.5},{a:31.6,b:36.9,chips:[32.9,34.85,35.6],dato:32.4}];
function sClase(t,i){const c=T.clases[i],tt=CLT[i],a=tt.a,b=tt.b,o=sceneOut(t,b);blush();dust(t,.35);
 ctx.save();ctx.globalAlpha=o;
 soft(c.num,CX,330,26,'PP4',C.rose,t,a+.15,{ls:8});
 two(c.n[0],c.n[1],CX,445,140,'PP3',t,a+.05,{d:.6});
 soft(c.dato,CX,535,34,'CGI4',C.roseD,t,tt.dato,{d:.8});
 const k=es(p(t,a,a+.55));ovalCard(c.foto,CX+(1-k)*120,990,560,720,k,{z:1.1-.06*p(t,a,b),fy:.35});
 // imagen conceptual en círculo
 const ki=es(p(t,a+1.2,a+2.0));if(ki>0){ctx.save();ctx.globalAlpha*=ki;const r=125,x=820,y=1185-(1-ki)*30;ctx.beginPath();ctx.arc(x,y,r+8,0,TAU);ctx.fillStyle=C.paper;ctx.fill();photo(c.ins,x-r,y-r,2*r,2*r,{oval:true,z:1.15,fy:.5});ctx.restore()}
 c.chips.forEach((s,j)=>chip(s,90,720+j*96,es(p(t,tt.chips[j]-.1,tt.chips[j]+.45)),{size:28}));
 ctx.restore();flashIn(t,a,.16)}
const sBarre=t=>sClase(t,0),sPilates=t=>sClase(t,1),sSculpt=t=>sClase(t,2);

/* ================= 6 · LA CIENCIA LO RESPALDA ================= */
function counter(n,t,t0,d=1.2){const k=es(p(t,t0,t0+d));return Math.round(+n*k)+''}
function sCiencia(t){const a=36.9,b=46.0,o=sceneOut(t,b);blush();dust(t,.3);
 const sw=es(p(t,40.2,41.1));
 ctx.save();ctx.globalAlpha=o;
 // la espalda: arco central → a la izquierda
 const x=lerp(250,90,sw),w=lerp(500,400,sw),y=lerp(640,620,sw),h=lerp(700,640,sw),k0=es(p(t,a,a+.55));
 photo('N3_espalda',x,y+(1-k0)*50,w,h,{arch:true,z:1.08-.04*p(t,a,b),fy:.4,alpha:k0});
 if(sw<1){ctx.save();ctx.globalAlpha*=1-sw;soft(T.ciencia[0],CX,400,112,'CGI3',C.ink,t,37.45,{d:.9});soft(T.ciencia[1],CX,510,112,'CGI4',C.roseD,t,38.9,{d:.9});ctx.restore()}
 if(sw>0){ctx.save();ctx.globalAlpha*=sw;const cc=T.cochrane;
  text(counter(cc.n1,t,40.6),735,760,170,'PP3',C.rose,'center',0);text(cc.l1.toUpperCase(),735,870,24,'PP4',C.ink,'center',10);
  hline(620,850,935,es(p(t,41.4,42)));
  text(counter(cc.n2,t,41.1,1.4),735,1060,150,'PP3',C.rose,'center',0);text(cc.l2.toUpperCase(),735,1165,24,'PP4',C.ink,'center',10);
  soft(cc.txt[0],CX,390,62,'CGI3',C.ink,t,42.7,{d:.8});soft(cc.txt[1],CX,465,62,'CGI4',C.roseD,t,43.3,{d:.8});
  ctx.restore()}
 ctx.restore();flashIn(t,a,.16)}

/* ================= 7 · EN MUJERES ================= */
function sMujeres(t){const a=46.0,b=51.2,o=sceneOut(t,b);blush();
 full('N6_estiramiento',{z:1.1-.05*p(t,a,b),fx:.5,alpha:es(p(t,a-.05,a+.4))});topVeil(1000,.95,.7);
 ctx.save();ctx.globalAlpha=o;
 soft(T.mujeres[0],CX,380,40,'PP3',C.ink,t,46.3,{d:.8});
 T.metr.forEach((m,i)=>{const t0=[47.0,48.4,49.4][i],k=es(p(t,t0-.1,t0+.5));if(k<=0)return;const x=230+i*270,y=620;ctx.save();ctx.globalAlpha*=k;
  circle(x,y,108,'rgba(251,247,245,.85)');ring(x,y,92,es(p(t,t0,t0+1.2)),C.rose,9);
  if(i===0){ctx.strokeStyle=C.roseD;ctx.lineWidth=5;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(x-30,y);ctx.lineTo(x+30,y);ctx.moveTo(x-30,y-16);ctx.lineTo(x-30,y+16);ctx.moveTo(x+30,y-16);ctx.lineTo(x+30,y+16);ctx.stroke()}
  if(i===1){ctx.strokeStyle=C.roseD;ctx.lineWidth=5;ctx.lineCap='round';ctx.beginPath();for(let q=0;q<=40;q++){const xx=x-36+q*1.8,yy=y+Math.sin(q*.32+t*3)*14;q?ctx.lineTo(xx,yy):ctx.moveTo(xx,yy)}ctx.stroke()}
  if(i===2){ctx.strokeStyle=C.roseD;ctx.lineWidth=5;ctx.lineCap='round';const tl=Math.sin(t*2)*.12;ctx.save();ctx.translate(x,y+6);ctx.rotate(tl);ctx.beginPath();ctx.moveTo(-36,0);ctx.lineTo(36,0);ctx.stroke();ctx.restore();ctx.beginPath();ctx.moveTo(x,y+6);ctx.lineTo(x-12,y+30);ctx.lineTo(x+12,y+30);ctx.closePath();ctx.stroke()}
  text(m,x,y+160,46,'CGI4',C.ink,'center',0);ctx.restore()});
 ctx.restore();flashIn(t,a,.16)}

/* ================= 8 · OMS ================= */
function sOMS(t){const a=51.2,b=56.9,o=sceneOut(t,b);blush();dust(t,.3);
 ctx.save();ctx.globalAlpha=o;
 const kb=es(p(t,a,a+.6));if(kb>0){ctx.save();ctx.globalAlpha*=kb;photo('N5_mancuernas',640,430,300,520,{arch:true,z:1.05,fy:.35,alpha:.95});ctx.restore()}
 chip('OMS · 2020',CX,350,es(p(t,51.5,52.1)),{size:24,dot:false,align:'center'});
 const k2=es(p(t,51.3,52.1));if(k2>0){ctx.save();ctx.globalAlpha*=k2;ctx.filter=`blur(${(1-k2)*8}px)`;text('2+',350,640+(1-k2)*40,330,'PP3',C.rose,'center',0);ctx.restore()}
 soft(T.oms[0],350,840,64,'CGI4',C.ink,t,53.0,{d:.8});soft(T.oms[1],350,910,28,'PP3',C.ink,t,53.6,{d:.8,ls:2});
 T.dias.forEach((d,i)=>{const x=140+i*120,y=1120,on=(i===1&&t>=54.0)||(i===3&&t>=54.4),k=es(p(t,52.6+i*.08,53.2+i*.08));if(k<=0)return;ctx.save();ctx.globalAlpha*=k;
  const pk=on?bell(t,i===1?54.0:54.4,(i===1?54.0:54.4)+.5):0;ctx.translate(x,y);ctx.scale(1+.15*pk,1+.15*pk);
  ctx.beginPath();ctx.arc(0,0,44,0,TAU);ctx.fillStyle=on?C.rose:'rgba(251,247,245,.9)';ctx.fill();ctx.strokeStyle='rgba(186,126,117,.5)';ctx.lineWidth=2;ctx.stroke();
  text(d,0,3,30,'PP4',on?C.white:C.ink,'center',0);ctx.restore()});
 ctx.restore();flashIn(t,a,.16)}

/* ================= 9 · COACHES ================= */
const NOMT=[60.28,60.77,61.42,61.9],SOLO=[63.1,64.25,65.4,66.55];
function sCoaches(t){const a=56.9,b=68.2,o=sceneOut(t,b);blush();dust(t,.3);
 const sw=es(p(t,62.75,63.35));
 ctx.save();ctx.globalAlpha=o;
 if(sw<1){ctx.save();ctx.globalAlpha*=1-sw;
  two(T.coaches.h[0],T.coaches.h[1],CX,390,92,'PP3',t,a,{d:.6});soft(T.coaches.sub,CX,470,22,'PP4',C.roseD,t,57.9,{ls:9});
  T.coaches.lista.forEach(([n,f],i)=>{const cx=300+(i%2)*400,cy=760+Math.floor(i/2)*390,k=es(p(t,57.0+i*.15,57.6+i*.15));
   const on=t>=NOMT[i],hi=bell(t,NOMT[i],NOMT[i]+.6);
   ovalCard(f,cx,cy,330,350,k,{blob:false,z:1.06,fy:.2,bob:-8*hi});
   if(on){ctx.save();ctx.globalAlpha*=k;ctx.strokeStyle=C.rose;ctx.lineWidth=4;ctx.beginPath();ctx.ellipse(cx,cy-8*hi,172,182,0,0,TAU);ctx.stroke();ctx.restore();
    chip(n,cx,cy+165,es(p(t,NOMT[i],NOMT[i]+.35)),{size:30,dot:false,align:'center'})}});
  ctx.restore()}
 if(sw>0){ctx.save();ctx.globalAlpha*=sw;
  soft(T.coaches.tec[0],CX,380,84,'CGI3',C.ink,t,63.0,{d:.8});soft(T.coaches.tec[1],CX,470,64,'CGI4',C.roseD,t,63.6,{d:.8});
  let idx=0;SOLO.forEach((x,j)=>{if(t>=x)idx=j});
  for(let j=Math.max(0,idx-1);j<=idx;j++){const [n,f]=T.coaches.lista[j],k=j===idx?es(p(t,SOLO[j]-.05,SOLO[j]+.35)):1;
   ovalCard(f,CX+(1-k)*80,950,540,700,k,{z:1.08-.03*p(t,SOLO[j],SOLO[j]+1.2),fy:.15});
   if(j===idx){chip('Coach '+n,CX,1290,es(p(t,SOLO[j]+.1,SOLO[j]+.45)),{size:30,align:'center'})}}
  ctx.restore()}
 ctx.restore();flashIn(t,a,.16)}

/* ================= 10 · HORARIO o PRIMERA CLASE ================= */
function sClases(t){const a=68.2,b=73.8,o=sceneOut(t,b);blush();dust(t,.3);
 ctx.save();ctx.globalAlpha=o;
 if(!PRECIO){const hz=T.horario;
  two(hz.h[0],hz.h[1],CX,370,84,'PP3',t,a,{d:.6});
  soft('BARRE · PILATES · SCULPT',CX,450,24,'PP4',C.roseD,t,68.7,{ls:9});
  soft(hz.dias,CX,580,80,'CGI4',C.ink,t,70.9,{d:.8});
  hz.horas.forEach((h,i)=>chip(h,250+(i%3)*250,710+Math.floor(i/3)*104,es(p(t,71.0+i*.12,71.45+i*.12)),{size:30,dot:false,align:'center'}));
  const kd=es(p(t,68.4,69.1));if(kd>0){ctx.save();ctx.globalAlpha*=kd;
   photo('F01_tres_plancha',120,930,760,360,{r:180,z:1.1,fx:.55,fy:.5});
   ctx.restore();chip(hz.dir[0]+' · Orizaba',CX,1290,kd,{size:26,align:'center'})}}
 else{const pz=T.precio;
  soft(pz.h,CX,380,92,'CGI3',C.ink,t,68.2,{d:.6});
  const kc=es(p(t,68.4,69.2));if(kc>0){ctx.save();ctx.globalAlpha*=kc;const s=.92+.08*kc;ctx.translate(CX,860);ctx.scale(s,s);
   ctx.shadowColor='rgba(126,74,70,.2)';ctx.shadowBlur=50;ctx.shadowOffsetY=16;ctx.beginPath();ctx.ellipse(0,0,330,400,0,0,TAU);ctx.fillStyle=C.paper;ctx.fill();ctx.shadowColor='transparent';
   ctx.strokeStyle='rgba(186,126,117,.55)';ctx.lineWidth=2;ctx.stroke();
   circle(0,-270,42,'rgba(186,126,117,.18)');sparkle(0,-270,22,C.roseD);
   text(pz.pk,0,-185,28,'PP5',C.ink,'center',6);
   const kp=es(p(t,70.15,70.9));ctx.save();ctx.globalAlpha*=kp;ctx.filter=`blur(${(1-kp)*8}px)`;
    const wn=tw(pz.n,190,'PP5',0);text(pz.sym,-wn/2-28,-80,60,'PP4',C.rose,'center',0);text(pz.n,0,-30,190,'PP5',C.rose,'center',0);text(pz.mxn,wn/2+46,10,28,'PP4',C.rose,'center',2);ctx.restore();
   [pz.l1,pz.l2].forEach((l,j)=>{const y=110+j*62;circle(-140,y,13,'rgba(186,126,117,.25)');check(-140,y,9,C.roseD,3);text(l,-112,y+2,30,'PP4',C.ink,'left',0)});
   rr(-170,215,340,74,37);ctx.fillStyle=C.wine;ctx.fill();text('RESERVA',0,254,26,'PP5',C.white,'center',5);
   ctx.restore()}}
 ctx.restore();flashIn(t,a,.16)}

/* ================= 11 · RESERVA Y COMPARTE ================= */
function sReserva(t){const a=73.8,b=78.5,o=sceneOut(t,b);blush();dust(t,.3);
 const sw=es(p(t,75.5,76.2));
 ctx.save();ctx.globalAlpha=o;
 if(sw<1){ctx.save();ctx.globalAlpha*=1-sw;const rz=T.reserva;
  two(rz.h[0]+' ',rz.h[1],CX,390,92,'CGI3',t,a,{d:.6,cb:C.roseD});
  const k=es(p(t,a,a+.55));ctx.save();ctx.globalAlpha*=k;ctx.translate(0,(1-k)*60);
   ctx.shadowColor='rgba(126,74,70,.2)';ctx.shadowBlur=50;ctx.shadowOffsetY=16;rr(130,520,740,760,36);ctx.fillStyle=C.paper;ctx.fill();ctx.shadowColor='transparent';
   rr(170,555,660,56,28);ctx.fillStyle='rgba(186,126,117,.14)';ctx.fill();text(rz.url,CX,585,24,'PP4',C.ink,'center',1);
   photo('F01_tres_plancha',170,640,660,520,{r:22,z:1.05,fx:.55});
   ctx.save();ctx.globalAlpha*=.92;mark('logo_blanco',CX,760,380,1,{blur:false});ctx.restore();
   const pr=1-.06*bell(t,74.85,75.25);ctx.save();ctx.translate(CX,1210);ctx.scale(pr,pr);rr(-150,-36,300,72,36);ctx.fillStyle=t>=74.9?C.roseD:C.wine;ctx.fill();text(rz.btn,0,2,24,'PP5',C.white,'center',5);ctx.restore();
  ctx.restore();
  const kc=p(t,74.2,74.9);tapDot(lerp(780,520,es(kc)),lerp(1420,1220,es(kc)),es(p(t,74.2,74.5))*(1-p(t,75.2,75.5)));
  ctx.restore()}
 if(sw>0){ctx.save();ctx.globalAlpha*=sw;const rz=T.reserva;
  soft(rz.comparte[0],CX,380,72,'CGI3',C.ink,t,75.85,{d:.8});soft(rz.comparte[1],CX,465,72,'CGI4',C.roseD,t,76.3,{d:.8});
  photo('F02_tres_pierna',230,560,540,720,{arch:true,z:1.06-.03*p(t,75.5,78.5),fy:.4});
  const kp=es(p(t,76.4,76.9)),fl=p(t,76.9,78.0);planeIcon(CX+lerp(260,520,es(fl)),1240-lerp(0,300,es(fl)),1.1,kp*(1-fl*.9),C.roseD);
  ctx.restore()}
 ctx.restore();flashIn(t,a,.16)}

/* ================= 12 · CIERRE ================= */
function sCierre(t){const a=78.5,b=90;blush();full('N4_luz_barra',{z:1.04,alpha:.22});dust(t,.5);
 const up=es(p(t,83.6,84.4));
 const ka=es(p(t,78.5,79.2));if(ka>0){ctx.save();ctx.globalAlpha*=ka;const y=lerp(560,520,up),r=lerp(170,150,up)*(.92+.08*ka);
  const g=ctx.createLinearGradient(CX-r,y-r,CX+r,y+r);g.addColorStop(0,'#E8C3B9');g.addColorStop(1,C.roseD);ctx.strokeStyle=g;ctx.lineWidth=8;ctx.beginPath();ctx.arc(CX,y,r+16,0,TAU);ctx.stroke();
  mark('avatar_m',CX,y,2*r,1,{blur:false});ctx.restore()}
 const yN=lerp(800,730,up);
 letters(T.perfil.nom,CX,yN,44,'PP5',C.ink,t,79.0,{per:.04,ls:8});
 soft(T.perfil.bio1,CX-16,yN+66,34,'PP3',C.ink,t,79.6,{d:.8});if(t>79.9){const k=es(p(t,79.9,80.4));ctx.save();ctx.globalAlpha*=k;const w=tw(T.perfil.bio1,34,'PP3',0);sparkle(CX-16+w/2+26,yN+60,16,'#D9A441');ctx.restore()}
 soft(T.perfil.bio2,CX,yN+116,30,'PP3',C.roseD,t,79.9,{d:.8,ls:2});
 // @matbarre_mx (3 s sola)
 const ku=es(p(t,80.4,81.1));if(ku>0){ctx.save();ctx.globalAlpha=ku;ctx.filter=`blur(${(1-ku)*6}px)`;const y=lerp(1110,940,up),sz=lerp(100,62,up);text(T.usuario,CX,y,sz,'CGI4',C.ink,'center',1);ctx.restore();hline(320,680,lerp(1180,990,up),es(p(t,80.8,81.8)))}
 soft(T.cierre[0],CX,1060,66,'CGI3',C.ink,t,84.05,{d:.9});soft(T.cierre[1],CX,1135,66,'CGI4',C.roseD,t,85.6,{d:.9});
 // botón Seguir con toque
 const kb=es(p(t,87.5,87.95)),tapped=t>=88.3,pr=1-.06*Math.sin(Math.PI*p(t,88.25,88.5));
 if(kb>0){ctx.save();ctx.globalAlpha=kb;ctx.translate(CX,1235);ctx.scale(pr,pr);rr(-200,-48,400,96,48);ctx.fillStyle=tapped?C.paper:C.rose;ctx.fill();if(tapped){ctx.strokeStyle=C.rose;ctx.lineWidth=2;ctx.stroke()}
  text(tapped?'Siguiendo':'Seguir',tapped?-26:0,3,36,'PP5',tapped?C.roseD:C.white,'center',2);if(tapped)check(112,0,20,C.roseD,4);ctx.restore();
  const kr=bell(t,88.3,89.0);if(kr>0){ctx.save();ctx.globalAlpha=kr*.6;rr(CX-200-40*kr,1187-20*kr,400+80*kr,96+40*kr,70);ctx.strokeStyle=C.rose;ctx.lineWidth=2;ctx.stroke();ctx.restore()}}
 const kc=p(t,87.7,88.28);if(kc>0&&t<89.0){const e=es(kc);tapDot(lerp(820,560,e),lerp(1500,1250,e),1-p(t,88.6,89.0))}
 flashIn(t,a,.16)}
