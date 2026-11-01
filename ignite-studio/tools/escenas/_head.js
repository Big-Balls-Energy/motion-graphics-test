
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





