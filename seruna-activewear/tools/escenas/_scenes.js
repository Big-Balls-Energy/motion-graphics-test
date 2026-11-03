
/* ================= UTILIDADES (estilo Seruna: crema, serif, movimientos lentos) ================= */
const sm=x=>x*x*(3-2*x),es=x=>sm(clamp(x));                       // suavizado lento
function flashIn(t,a,k=.12){if(t>=a&&t<a+.5){ctx.fillStyle=`rgba(245,242,238,${(1-p(t,a,a+.5))*k})`;ctx.fillRect(0,0,W,H)}}
function sceneOut(t,b,d=.7){return 1-es(p(t,b-d,b-.05))}
function cream(){ctx.fillStyle=C.cream;ctx.fillRect(0,0,W,H)}
function photo(name,x,y,w,h,{z=1,fx=.5,fy=.5,alpha=1,r=0,arch=false,dx=0,dy=0}={}){const im=IMG[name];if(alpha<=0)return;ctx.save();ctx.globalAlpha*=alpha;ctx.beginPath();
 if(arch){ctx.moveTo(x,y+h);ctx.lineTo(x,y+w/2);ctx.arc(x+w/2,y+w/2,w/2,Math.PI,0);ctx.lineTo(x+w,y+h);ctx.closePath()}else if(r>0)ctx.roundRect(x,y,w,h,r);else ctx.rect(x,y,w,h);ctx.clip();
 if(!loaded(im)){ctx.fillStyle='#bfb8ae';ctx.fillRect(x,y,w,h);ctx.restore();return}
 const iw=im.naturalWidth,ih=im.naturalHeight,s=Math.max(w/iw,h/ih)*z,dw=iw*s,dh=ih*s;ctx.drawImage(im,x+(w-dw)*fx+dx,y+(h-dh)*fy+dy,dw,dh);ctx.restore()}
function full(name,o={}){photo(name,0,0,W,H,o)}
function veil(a,col='236,232,228'){if(a<=0)return;ctx.fillStyle=`rgba(${col},${a})`;ctx.fillRect(0,0,W,H)}
function gradV(y0,y1,c0,c1){const g=ctx.createLinearGradient(0,y0,0,y1);g.addColorStop(0,c0);g.addColorStop(1,c1);ctx.fillStyle=g;ctx.fillRect(0,y0,W,y1-y0)}
// texto elegante que aparece con desenfoque suave y leve subida
function soft(s,x,y,size,font,col,t,t0,{d=1.0,o=1,ls=0,align='center',rise=24}={}){const k=es(p(t,t0,t0+d))*o;if(k<=0)return;ctx.save();ctx.globalAlpha*=k;
 ctx.filter=`blur(${(1-k)*6}px)`;text(s,x,y+(1-k)*rise,size,font,col,align,ls);ctx.restore()}
// letras que aparecen una a una (para palabras protagonistas)
function letters(s,x,y,size,font,col,t,t0,{per=.06,d=.6,o=1,ls=0}={}){if(o<=0)return;ctx.save();ctx.font=`${size}px ${font}`;ctx.letterSpacing=ls+'px';const wt=ctx.measureText(s).width;let cx=x-wt/2;
 [...s].forEach((ch,i)=>{const w=ctx.measureText(ch).width,k=es(p(t,t0+i*per,t0+i*per+d))*o;if(k>0){ctx.save();ctx.globalAlpha*=k;ctx.filter=`blur(${(1-k)*5}px)`;text(ch,cx,y+(1-k)*14,size,font,col,'left',0);ctx.restore()}cx+=w+ls});ctx.letterSpacing='0px';ctx.restore()}
function hline(x0,x1,y,k,col=C.char,lw=2){if(k<=0)return;ctx.save();ctx.strokeStyle=col;ctx.lineWidth=lw;ctx.globalAlpha*=.7;const m=(x0+x1)/2,h=(x1-x0)/2*k;ctx.beginPath();ctx.moveTo(m-h,y);ctx.lineTo(m+h,y);ctx.stroke();ctx.restore()}
// polvo en la luz
function dust(t,k=1,col='255,250,240'){if(k<=0)return;ctx.save();ctx.globalCompositeOperation='lighter';for(let i=0;i<40;i++){const x=(rnd(i*3.3)*W+Math.sin(t*.2+i)*40+t*8*(rnd(i)-.3))%W,y=(rnd(i*7.1)*H-t*(10+rnd(i*2)*18)+H*4)%H,r=1.5+rnd(i*5)*3.5,a=(.15+.35*rnd(i*9))*(.5+.5*Math.sin(t*.8+i))*k;
 ctx.fillStyle=`rgba(${col},${a})`;ctx.beginPath();ctx.arc(x,y,r,0,TAU);ctx.fill()}ctx.restore()}
// logo «se» oficial; tint opcional (blanco sobre fotos)
const TINT={};function logoTint(col){if(TINT[col])return TINT[col];if(!loaded(logo))return null;const[c,g]=mkCanvas(logo.naturalWidth,logo.naturalHeight);g.drawImage(logo,0,0);g.globalCompositeOperation='source-in';g.fillStyle=col;g.fillRect(0,0,c.width,c.height);return TINT[col]=c}
function logoSe(x,y,w,k=1,{col=null,blur=true}={}){if(k<=0)return;const im=col?logoTint(col):logo;if(!im||!(im.width||im.naturalWidth))return;const iw=im.naturalWidth||im.width,ih=im.naturalHeight||im.height,h=w*ih/iw;
 ctx.save();ctx.globalAlpha*=k;if(blur)ctx.filter=`blur(${(1-k)*8}px)`;ctx.drawImage(im,x-w/2,y-h/2,w,h);ctx.restore()}
// prenda real (recorte del catálogo) con sombra suave
function prenda(n,x,y,h,k=1,{fx=0}={}){const im=IMG[n];if(!loaded(im)||k<=0)return;const w=h*im.naturalWidth/im.naturalHeight;ctx.save();ctx.globalAlpha*=k;
 ctx.save();ctx.globalAlpha*=.25;ctx.fillStyle='#3f3a33';ctx.beginPath();ctx.ellipse(x,y+h/2-6,w*.32,18,0,0,TAU);ctx.filter='blur(14px)';ctx.fill();ctx.restore();
 ctx.drawImage(im,x-w/2+fx,y-h/2,w,h);ctx.restore()}
function pillSoft(s,x,y,k,{bg='rgba(245,242,238,.9)',fg=C.char,size=28,font='PP4',ls=4}={}){if(k<=0)return;ctx.save();ctx.globalAlpha*=k;const w=tw(s,size,font,ls)+size*1.8,h=size*2;rr(x-w/2,y-h/2,w,h,h/2);ctx.fillStyle=bg;ctx.fill();text(s,x,y+2,size,font,fg,'center',ls);ctx.restore()}

/* ================= 1 · RESPIRA ================= */
function hookFrame(t,{titles=true}={}){cream();const z=1.08-.06*es(p(t,0,8.6));
 full('N09_luz_hojas',{z,fx:.5,dx:Math.sin(t*.35)*10});veil(.12);dust(t,.6);
 if(!titles)return;
 const o1=1-es(p(t,5.2,6.0)),br=.5+.5*Math.sin((t+.6)*TAU/4.2);
 // anillo que respira
 ctx.save();ctx.globalAlpha=o1*.55;ctx.strokeStyle=C.char;ctx.lineWidth=2;ctx.beginPath();ctx.arc(CX,820,170+br*70,0,TAU);ctx.stroke();ctx.globalAlpha=o1*.25;ctx.beginPath();ctx.arc(CX,820,120+br*50,0,TAU);ctx.stroke();ctx.restore();
 ctx.save();ctx.globalAlpha=o1;const s=1+.025*br;ctx.translate(CX,820);ctx.scale(s,s);text(T.respira,0,0,150,'CGI3',C.char,'center',1);ctx.restore();
 // logo y nombre
 const kl=es(p(t,5.8,7.2));logoSe(CX,780,360,kl);
 if(kl>0){letters(T.marca,CX,1010,64,'PP3',C.char,t,6.4,{per:.07,ls:22});soft(T.sub,CX,1080,24,'PP4',C.sage,t,7.2,{ls:12});hline(380,620,1130,es(p(t,7.4,8.2)))}}
function sHook(t){hookFrame(t);flashIn(t,8.1,0)}

/* ================= 2 · BIENESTAR SIN PERFECCIÓN ================= */
function sOrigen(t){const a=8.6,b=17.2,o=sceneOut(t,b);cream();
 full('S01_tarjetas',{z:1.12-.08*es(p(t,a,b)),fy:.55,alpha:es(p(t,a,a+1.2))});
 {const g=ctx.createLinearGradient(0,0,0,1100);g.addColorStop(0,'rgba(236,232,228,.98)');g.addColorStop(.62,'rgba(236,232,228,.94)');g.addColorStop(1,'rgba(236,232,228,0)');ctx.fillStyle=g;ctx.fillRect(0,0,W,1100)}
 ctx.save();ctx.globalAlpha=o;
 soft(T.lugar,CX,350,24,'PP4',C.sage,t,9.1,{ls:10});hline(400,600,390,es(p(t,9.4,10.2)),C.sage);
 soft(T.bien[0],CX,510,130,'CGI3',C.char,t,12.3,{d:1.2});soft(T.bien[1],CX,630,84,'CG3',C.char,t,13.3,{d:1.1});
 soft(T.bienEn,CX,710,22,'PP4',C.sage,t,14.2,{ls:8});
 ctx.restore();flashIn(t,a,.6)}

/* ================= 3 · MOVE · REST · LIVE ================= */
function sMRL(t){const a=17.2,b=26.9,o=sceneOut(t,b);cream();dust(t,.3,'200,190,175');
 const fotos=['S05_puente','S02_comfy','S08_dos_espaldas'],t0s=[17.6,19.1,20.2],fx=[.55,.4,.5],fy=[.5,.25,.35];
 const mg=es(p(t,22.2,23.6));
 ctx.save();ctx.globalAlpha=o;
 if(mg<1)fotos.forEach((f,i)=>{const k=es(p(t,t0s[i],t0s[i]+1.1));if(k<=0)return;const x=80+i*285,w=270,y=470,h=780;ctx.save();ctx.globalAlpha*=k*(1-mg);
  photo(f,x,y+(1-k)*60,w,h,{arch:true,fx:fx[i],fy:fy[i],z:1.05});ctx.restore();
  ctx.save();ctx.globalAlpha*=(1-mg);soft(T.mrl[i][0],x+w/2,1300,40,'PP3',C.char,t,t0s[i]+.2,{ls:14});soft(T.mrl[i][1],x+w/2,410,48,'CGI4',C.char,t,t0s[i]+.3);ctx.restore()});
 if(mg>0){photo('S06_abrazo_dos',80+ (1-mg)*285,470-(1-mg)*0,840-(1-mg)*570,780,{arch:true,fy:.45,z:1.06+.04*p(t,22.2,26.9),alpha:mg});
  soft('Move · Rest · Live',CX,400,74,'CGI3',C.char,t,23.2,{d:1.2});}
 ctx.restore();flashIn(t,a,.5)}

/* ================= 4 · INSPIRED BY NATURE ================= */
function sInspirada(t){const a=26.9,b=31.6,o=sceneOut(t,b,.5);cream();
 ctx.save();ctx.globalAlpha=o;
 soft(T.inspired,CX,470,96,'CG3',C.char,t,27.3,{d:1.2});soft(T.inspiredEs,CX,560,28,'PP3',C.sage,t,28.0,{ls:4});
 const k=es(p(t,27.6,28.8));photo('N12_telas',250,660+(1-k)*60,500,640,{arch:true,z:1.12-.06*p(t,a,b),alpha:k});
 ctx.restore();flashIn(t,a,.5)}

/* ================= 5 · LOS 8 COLORES ================= */
function sColores(t){const a=31.6,b=44.9,o=sceneOut(t,b);cream();
 const gridK=es(p(t,39.5,40.4));
 // cada color: su naturaleza a pantalla completa + su prenda real
 let idx=-1;COLORES.forEach((c,i)=>{if(t>=c.t-.25)idx=i});
 if(gridK<1){if(idx<0)idx=0;
  for(let j=Math.max(0,idx-1);j<=idx;j++){const c=COLORES[j],k=j===idx?es(p(t,c.t-.25,c.t+.2)):1;if(k<=0)continue;ctx.save();ctx.globalAlpha*=k*(1-gridK);
   full(c.foto,{z:1.15-.05*p(t,c.t,c.t+1.5)});gradV(980,1920,'rgba(0,0,0,0)','rgba(20,18,16,.55)');gradV(0,560,'rgba(20,18,16,.45)','rgba(0,0,0,0)');
   prenda(c.prod,CX,945,740,1);
   text(c.n,CX,380,120,'CGI3',C.white,'center',1);
   ctx.save();ctx.translate(CX,470);circle(0,0,22,c.hex);ctx.strokeStyle='rgba(255,255,255,.9)';ctx.lineWidth=3;ctx.stroke();ctx.restore();
   ctx.restore()}}
 // paleta completa
 if(gridK>0){ctx.save();ctx.globalAlpha*=gridK*o;cream();
  soft(T.colores,CX,500,64,'CGI3',C.char,t,39.7,{d:1});
  COLORES.forEach((c,i)=>{const col=i%4,row=Math.floor(i/4),x=170+col*220,y=760+row*290,k=es(p(t,39.9+i*.12,40.5+i*.12));if(k<=0)return;ctx.save();ctx.globalAlpha*=k;
   photo(c.foto,x-80,y-110,160,160,{r:80,z:1.2});ctx.beginPath();ctx.arc(x,y-30,80,0,TAU);ctx.strokeStyle=c.hex;ctx.lineWidth=8;ctx.stroke();
   text(c.n,x,y+100,34,'CGI4',C.char,'center');ctx.restore()});
  logoSe(CX,1300,120,es(p(t,41.5,42.5)));ctx.restore()}
 flashIn(t,a,.4)}

/* ================= 6 · TELAS · DEL MAT A TU DÍA ================= */
function waves(t,k,col){if(k<=0)return;ctx.save();ctx.globalAlpha*=k;for(let j=0;j<6;j++){ctx.strokeStyle=col;ctx.globalAlpha=k*(.18+.08*j);ctx.lineWidth=2;ctx.beginPath();
 for(let x=-20;x<=W+20;x+=12){const y=1180+j*26+Math.sin(x*.006+t*1.1+j*.6)*(30+j*6)+Math.sin(x*.013-t*.7)*10;x>-20?ctx.lineTo(x,y):ctx.moveTo(x,y)}ctx.stroke()}ctx.restore()}
function sTelas(t){const a=44.9,b=54.0,o=sceneOut(t,b);cream();dust(t,.3,'200,190,175');
 const sw=es(p(t,48.6,49.4));
 ctx.save();ctx.globalAlpha=o;
 if(sw<1){ctx.save();ctx.globalAlpha*=1-sw;waves(t,es(p(t,45.2,46.2)),C.sage);
  const k=es(p(t,45.3,46.3));prenda('p12',CX+Math.sin(t*.8)*6,860,800,k);
  soft(T.telas[0],CX,400,84,'CGI3',C.char,t,45.6,{d:1});soft(T.telas[1],CX,480,32,'PP3',C.sage,t,46.6,{ls:4});ctx.restore()}
 if(sw>0){ctx.save();ctx.globalAlpha*=sw;
  photo('S03_estudio_estocada',80,560,840,470,{r:28,z:1.08-.05*p(t,48.6,54),fx:.5});
  const k2=es(p(t,50.3,51.2));photo('S07_espalda_espalda',80,1060+(1-k2)*40,840,260,{r:28,fy:.35,alpha:k2});
  soft(T.mat[0],CX,400,76,'CGI3',C.char,t,48.9,{d:1});soft(T.mat[1],CX,480,32,'PP3',C.sage,t,50.4,{ls:4});ctx.restore()}
 ctx.restore();flashIn(t,a,.4)}

/* ================= 7 · UN SET PARA CADA MOMENTO ================= */
function sSets(t){const a=54.0,b=62.9,o=sceneOut(t,b);cream();dust(t,.25,'200,190,175');
 const all=es(p(t,59.3,60.2)),t0s=[54.5,56.06,57.84];
 ctx.save();ctx.globalAlpha=o;
 if(all<1){let i=0;t0s.forEach((x,j)=>{if(t>=x-.2)i=j});const [n,d,pr]=T.sets3[i],k=es(p(t,t0s[i]-.2,t0s[i]+.6));
  ctx.save();ctx.globalAlpha*=(1-all);
  if(i>0){const [n0,d0,p0]=T.sets3[i-1],ko=1-k;if(ko>0){ctx.save();ctx.globalAlpha*=ko;prenda(p0,CX-120*k,935,760,1);ctx.restore()}}
  ctx.save();ctx.translate((1-k)*120,0);prenda(pr,CX,935,760,k);ctx.restore();
  ctx.save();ctx.globalAlpha*=k;text(n,CX,370,96,'CGI3',C.char,'center',1);text(d,CX,440,32,'PP3',C.sage,'center',4);ctx.restore();
  // indicador de los 3 momentos
  t0s.forEach((x,j)=>{circle(CX-40+j*40,1345,j===i?8:5,j<=i?C.char:'rgba(74,81,90,.3)')});ctx.restore()}
 if(all>0){ctx.save();ctx.globalAlpha*=all;soft('Un set para cada momento',CX,420,64,'CGI3',C.char,t,59.4,{d:1});
  SETS.forEach((s,i)=>{const x=150+i*175,k=es(p(t,59.6+i*.15,60.4+i*.15));if(k<=0)return;ctx.save();ctx.globalAlpha*=k;prenda(s.p,x,850+(1-k)*30,520,1);
   text(s.l,x,1150,18,'PP4',C.sage,'center',6);text(s.n,x,1195,32,'CGI4',C.char,'center');ctx.restore()});ctx.restore()}
 ctx.restore();flashIn(t,a,.4)}

/* ================= 8 · VOLVER A TI ================= */
function sVolver(t){const a=62.9,b=67.8,o=sceneOut(t,b);cream();
 full('N11_bosque',{z:1.12-.07*es(p(t,a,b)),alpha:es(p(t,a,a+1))});{const g=ctx.createLinearGradient(0,0,0,1000);g.addColorStop(0,'rgba(236,232,228,.92)');g.addColorStop(.6,'rgba(236,232,228,.82)');g.addColorStop(1,'rgba(236,232,228,0)');ctx.fillStyle=g;ctx.fillRect(0,0,W,1000)}dust(t,.7);
 ctx.save();ctx.globalAlpha=o;soft(T.volver[0],CX,500,66,'CGI4',C.ink,t,63.6,{d:1.1});soft(T.volver[1],CX,640,120,'CG4',C.ink,t,65.7,{d:1.2});ctx.restore();flashIn(t,a,.4)}

/* ================= 9 · CADA UNA A SU RITMO · COMPÁRTELO ================= */
function planeIcon(x,y,s,k,col){if(k<=0)return;ctx.save();ctx.globalAlpha*=k;ctx.translate(x,y);ctx.scale(s,s);ctx.strokeStyle=col;ctx.lineWidth=2.4/s*1.2;ctx.lineJoin='round';
 ctx.beginPath();ctx.moveTo(-40,0);ctx.lineTo(44,-36);ctx.lineTo(18,40);ctx.lineTo(4,12);ctx.closePath();ctx.moveTo(4,12);ctx.lineTo(44,-36);ctx.stroke();ctx.restore()}
function sJuntas(t){const a=67.8,b=75.0,o=sceneOut(t,b);cream();
 const sw=es(p(t,69.3,70.2)),sh=es(p(t,71.7,72.4));
 ctx.save();ctx.globalAlpha=o;
 photo('S04_abrazo_espaldas',80,560,840,520,{r:28,z:1.1-.05*p(t,a,71),fy:.5,alpha:(1-sw)*(1-sh)});
 photo('S06_abrazo_dos',80,560,840,700,{r:28,z:1.08-.04*p(t,69.3,73),fy:.45,alpha:sw*(1-sh)});
 if(sh<1){ctx.save();ctx.globalAlpha*=1-sh;soft(T.ritmo[0],CX,400,72,'CGI3',C.char,t,68.1,{d:1});soft(T.ritmo[1],CX,480,36,'PP3',C.sage,t,69.5,{ls:3});ctx.restore()}
 if(sh>0){ctx.save();ctx.globalAlpha*=sh;
  photo('S07_espalda_espalda',230,560,540,700,{arch:true,fy:.4,z:1.05});
  soft(T.comparte[0],CX,400,64,'CGI3',C.char,t,72.1,{d:.9});soft(T.comparte[1],CX,478,64,'CGI3',C.char,t,72.6,{d:.9});
  const kp=es(p(t,72.4,73.2)),fl=p(t,73.4,74.6);planeIcon(CX+lerp(0,260,es(fl)),1320-lerp(0,240,es(fl)),1,kp*(1-fl*.9),C.char);ctx.restore()}
 ctx.restore();flashIn(t,a,.4)}

/* ================= 10 · CIERRE ================= */
function sCierre(t){const a=75.0,b=90;cream();full('N09_luz_hojas',{z:1.04,alpha:.35,dx:Math.sin(t*.35)*10});dust(t,.5);
 const up=es(p(t,79.4,80.4));
 logoSe(CX,lerp(640,560,up),lerp(380,300,up),es(p(t,75.2,76.6)));
 letters(T.marca,CX,lerp(870,760,up),60,'PP3',C.char,t,75.6,{per:.06,ls:22});soft(T.sub,CX,lerp(935,820,up),22,'PP4',C.sage,t,76.2,{ls:12});
 // @serunabalance (3 s sola)
 const ku=es(p(t,76.6,77.4));if(ku>0){ctx.save();ctx.globalAlpha=ku;ctx.filter=`blur(${(1-ku)*6}px)`;const y=lerp(1070,930,up),sz=lerp(92,64,up);text(T.usuario,CX,y,sz,'CGI4',C.char,'center',1);ctx.restore();hline(340,660,lerp(1140,985,up),es(p(t,77.0,78.0)),C.sage)}
 soft(T.cierre,CX,1060,64,'CGI3',C.char,t,80.4,{d:1.1});
 // botón Seguir con toque
 const kb=es(p(t,82.6,83.4)),tapped=t>=85.0,pr=1-.06*Math.sin(Math.PI*p(t,84.95,85.2));
 if(kb>0){ctx.save();ctx.globalAlpha=kb;ctx.translate(CX,1200);ctx.scale(pr,pr);rr(-200,-50,400,100,50);ctx.fillStyle=tapped?C.paper:C.char;ctx.fill();if(tapped){ctx.strokeStyle=C.char;ctx.lineWidth=2;ctx.stroke()}
  text(tapped?'Siguiendo':'Seguir',tapped?-26:0,3,36,'PP4',tapped?C.char:C.paper,'center',2);if(tapped)check(112,0,20,C.char,4);ctx.restore();
  const kr=bell(t,85.0,85.8);if(kr>0){ctx.save();ctx.globalAlpha=kr*.6;rr(CX-200-40*kr,1150-20*kr,400+80*kr,100+40*kr,70);ctx.strokeStyle=C.sage;ctx.lineWidth=2;ctx.stroke();ctx.restore()}}
 const kc=p(t,83.6,84.95);if(kc>0&&t<86.4){const e=es(kc);ctx.save();ctx.globalAlpha=1-p(t,85.8,86.4);circle(lerp(820,560,e),lerp(1500,1215,e),28,'rgba(74,81,90,.22)');circle(lerp(820,560,e),lerp(1500,1215,e),14,'rgba(74,81,90,.45)');ctx.restore()}
 soft(T.claim,CX,1310,22,'PP3',C.sage,t,86.0,{ls:3});
 flashIn(t,a,.5)}
