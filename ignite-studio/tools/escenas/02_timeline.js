/* ================= LÍNEA DE TIEMPO ================= */
const SCENES=[
 {id:'hook',name:'HOOK: ¿Y SI TU MEJOR VERSIÓN EMPIEZA CON UNA SOLA CLASE?',a:0,b:4.1,vis:'Silueta de ciclista en blanco y negro (toma conceptual con IA) teñida de azul; tipografía cinética y el ala del logo que se enciende.'},
 {id:'intro',name:'ESTO ES IGNITE STUDIO',a:4.1,b:10.0,vis:'Círculo azul con el ala blanca (logo oficial) y «IGNITE»; chips CYCLING · TRAIN · XALAPA; bici conceptual de estudio.'},
 {id:'encender',name:'NO VIENES SOLO A SUDAR: VIENES A ENCENDERTE',a:10.0,b:15.1,vis:'Volante de la bici girando (toma conceptual), texto que se enciende con chispas azules.'},
 {id:'salud',name:'01 · SALUD',a:15.1,b:26.2,vis:'Corazón con línea de pulso, pulmones que respiran; tarjetas ESTRÉS ↓ · SUEÑO ↑ · ENERGÍA ↑ con fuente OMS.'},
 {id:'cuerpo',name:'02 · CUERPO',a:26.2,b:37.6,vis:'Piernas pedaleando (toma conceptual) con PIERNAS y GLÚTEOS y contador de pedaladas; foto de su sitio «MOVEMENT» con BRAZOS · ESPALDA · ABDOMEN.'},
 {id:'rend',name:'03 · RENDIMIENTO',a:37.6,b:50.9,vis:'Barras RESISTENCIA · FUERZA · POTENCIA que se llenan sobre manos en el manubrio; tarjetas de sus clases reales (TRAIN y CYCLE).'},
 {id:'comunidad',name:'04 · COMUNIDAD: COACHES',a:50.9,b:61.9,vis:'Espejo que se rompe en «ES LA GENTE»; muro con los 11 coaches (fotos oficiales, sin repetir) y montaje con los 11, uno por uno, con su nombre.'},
 {id:'juntos',name:'NADIE ENTRENA SOLO',a:61.9,b:67.5,vis:'Foto «STRENGTH» de su sitio teñida de azul, confeti azul y blanco.'},
 {id:'horarios',name:'CLASES DESDE LAS 6:00 AM',a:67.5,b:72.2,vis:'Semana LUN–DOM con la primera clase de cada día según su app.'},
 {id:'reserva',name:'RESERVA EN LA APP Y ETIQUETA A TU COMPA',a:72.2,b:80.3,vis:'Celular con app genérica: clase CYCLE · JUST RIDE → RESERVAR → ¡RESERVADO! ✓; comentario que etiqueta a un amigo.'},
 {id:'cierre',name:'CIERRE: IGNITE STUDIO · ENCIÉNDETE',a:80.3,b:90,vis:'Logo en avatar (círculo azul y ala blanca), «IGNITE», Plaza Xanat · Xalapa, «ENCIÉNDETE» 3 s sola, @_ignitestudiomx y botón SEGUIR con cursor y clic; el último medio segundo regresa al primer cuadro (loop).'},
];
// [entra, sale, texto, palabras clave, [voz desde, voz hasta]]
const SUBS_RAW=[
 [0.2,1.75,'¿Tu mejor versión…',['versión…'],[0.24,1.45]],
 [1.75,3.6,'empieza con una clase?',['clase?'],[1.7,3.33]],
 [4.15,6.0,'Esto es Ignite Studio:',['Ignite'],[4.24,5.82]],
 [6.0,8.0,'cycling y entrenamiento funcional…',['cycling'],[6.09,7.9]],
 [8.0,9.5,'aquí en Xalapa.',['Xalapa'],[8.1,9.28]],
 [10.05,11.85,'No solo a sudar…',['sudar…'],[10.14,11.67]],
 [11.85,13.8,'vienes a encenderte.',['encenderte'],[11.95,13.4]],
 [15.3,17.0,'Uno: tu salud.',['salud'],[15.34,16.45]],
 [17.0,18.7,'fortalece tu corazón…',['corazón…'],[16.64,18.57]],
 [18.7,20.3,'y tus pulmones.',['pulmones'],[18.79,19.71]],
 [20.3,23.0,'Bajas estrés, duermes mejor…',['mejor…'],[20.42,22.63]],
 [23.0,25.6,'sales con más energía.',['energía'],[22.92,25.12]],
 [26.5,28.1,'Dos: tu cuerpo.',['cuerpo'],[26.61,27.93]],
 [28.1,30.3,'Piernas y glúteos…',['glúteos…'],[28.17,30.24]],
 [30.3,32.2,'pedalada tras pedalada.',['pedalada.'],[30.49,31.96]],
 [32.6,34.5,'clases de fuerza:',['fuerza:'],[32.74,34.3]],
 [34.5,36.9,'brazos, espalda y abdomen.',['abdomen'],[34.3,36.53]],
 [37.95,39.7,'Tres: tu rendimiento.',['rendimiento'],[38.04,39.59]],
 [39.7,43.6,'Resistencia, fuerza, potencia.',['potencia'],[39.83,43.46]],
 [44.1,46.4,'Pierna, empuje, jalón,',['jalón'],[44.24,46.2]],
 [46.4,50.3,'cuerpo completo y rodadas.',['rodadas'],[46.3,49.95]],
 [51.35,53.6,'Lo mejor no se ve…',['mejor'],[51.44,53.51]],
 [53.6,55.2,'es la gente.',['gente'],[53.76,54.54]],
 [55.2,57.2,'Coaches que te conocen…',['Coaches'],[55.33,57.05]],
 [57.2,59.7,'te empujan a dar más.',['más'],[57.27,59.52]],
 [62.35,64.1,'Nadie entrena solo.',['solo'],[62.44,63.91]],
 [64.1,66.95,'Cada meta se celebra juntos.',['juntos'],[64.2,66.88]],
 [67.6,69.6,'Desde las 6 AM…',['6'],[67.74,69.53]],
 [69.6,71.7,'toda la semana.',['semana'],[69.75,71.6]],
 [72.3,74.2,'Reserva desde la app…',['app…'],[72.43,74.04]],
 [74.2,76.2,'vive tu primera clase.',['primera'],[74.36,75.92]],
 [76.5,79.8,'Etiqueta a quien vendría contigo.',['Etiqueta'],[76.64,79.63]],
 [80.5,83.6,'Ignite Studio, Plaza Xanat, Xalapa.',['Ignite'],[80.64,83.4]],
];
// frases que se quedan solas en pantalla (sola = sin subtítulo encima)
const HOLDS=[{a:83.6,b:86.8,text:'ENCIÉNDETE',sola:true,min:3},{a:12.0,b:15.0,text:'VIENES A ENCENDERTE'}];
const HKEY=HOLDS[0];
const norm=s=>s.toLowerCase().replace(/[«»¿?¡!.,:;…"]/g,'');
const SUBS=SUBS_RAW.map(([a,b,text,keys,[va,vb]])=>{
 const ws=text.split(/\s+/),chars=ws.map(w=>w.length),tot=chars.reduce((s,v)=>s+v,0);let acc=0;
 const v0=Math.max(a+.05,va),v1=Math.min(b-.1,Math.max(v0+.4,vb));
 const words=ws.map((w,i)=>{const t0=v0+(acc/tot)*(v1-v0);acc+=chars[i];return{w,key:keys.map(norm).includes(norm(w)),num:/\d/.test(w),t0}});
 return{a,b,text,keys,words}});
const sceneAt=t=>{let i=0;SCENES.forEach((s,j)=>{if(t>=s.a)i=j});return i};
const SOURCES=[[15.3,25.7,T.nota.salud],[67.6,71.7,T.nota.horarios],[0.2,3.6,T.nota.ia],[26.6,32.2,T.nota.ia]];
const TAGS=[[15.3,25.7,'01 · SALUD'],[26.6,37.1,'02 · CUERPO'],[38.0,50.4,'03 · RENDIMIENTO'],[51.4,67.0,'04 · COMUNIDAD']];

const SFX=[];
const sfx=(t,type,v=1,pitch=1)=>SFX.push({t:+t.toFixed(3),type,v,pitch});
// gancho
sfx(.02,'drone',.5);sfx(.25,'hit',.5);sfx(1.75,'hit',.55,1.1);sfx(2.4,'rise',.4);sfx(3.3,'impact',.8);sfx(3.32,'flash',.4);
// intro y logo
sfx(4.1,'whoosh',.8);sfx(4.3,'chord',.55,1.0);sfx(4.5,'chime',.45);[6.1,7.0,8.1].forEach((x,i)=>sfx(x,'pop',.5,1+i*.08));sfx(9.6,'whoosh',.6);
// encenderte
sfx(10.1,'sweep',.5);sfx(11.95,'impact',.8);sfx(11.97,'chord',.5,1.12);sfx(12.1,'assemble',.35);sfx(13.7,'rise',.45);
// secciones
[15.1,26.2,37.6,50.9].forEach(t0=>{sfx(t0,'flash',.3);sfx(t0+.12,'number',.7)});
sfx(16.7,'pulse',.6);sfx(17.5,'pulse',.6);sfx(18.3,'pulse',.6);sfx(18.9,'whoosh',.35,1.3);
sfx(20.45,'select',.5);sfx(21.7,'select',.5,1.06);sfx(22.95,'ding',.55);sfx(24.6,'meter',.5);sfx(25.6,'whoosh',.6);
sfx(28.2,'pop',.5);sfx(28.9,'pop',.5,1.08);sfx(30.5,'count',.35);sfx(32.4,'whoosh',.6);[34.4,35.2,35.9].forEach((x,i)=>sfx(x,'pop',.5,1+i*.08));sfx(37.1,'whoosh',.6);
sfx(39.85,'meter',.5);sfx(41.3,'meter',.5,1.08);sfx(42.4,'meter',.55,1.16);sfx(43.1,'impact',.6);
[44.3,44.95,45.55,46.2,48.0].forEach((x,i)=>sfx(x,'lock',.5,1+i*.04));sfx(50.3,'whoosh',.6);
sfx(51.6,'scan',.4);sfx(53.75,'impact',.9);sfx(53.77,'dissolve',.5);sfx(55.35,'whoosh',.5);
for(let i=0;i<11;i++)sfx(55.6+i*.17,'tick',.35,1+i*.03);sfx(57.55,'sweep',.5);for(let i=0;i<11;i++)sfx(57.75+i*(61.4-57.75)/11,'hit',.3,1+i*.03);
sfx(61.9,'flash',.3);sfx(62.45,'impact',.7);sfx(64.2,'chime',.5);sfx(66.3,'chord',.5,1.0);
sfx(67.5,'whoosh',.6);for(let i=0;i<7;i++)sfx(68.0+i*.25,'blip',.45,1+i*.05);sfx(69.8,'ding',.5);
sfx(72.2,'whoosh',.6);sfx(73.6,'click',.8);sfx(73.7,'select',.55);sfx(76.5,'whoosh',.5);for(let i=0;i<10;i++)sfx(77.2+i*.11,'key',.5,1+i*.02);sfx(78.6,'send',.6);
// cierre
sfx(80.3,'flash',.4);sfx(80.35,'impact',.9);sfx(80.4,'chord',.6,1.0);sfx(81.9,'pop',.5);sfx(83.6,'impact',1);sfx(83.62,'chord',.8,1.12);
sfx(86.8,'whoosh',.4,1.3);sfx(87.1,'pop',.5);sfx(87.35,'pop',.5,1.1);sfx(88.2,'click',1);sfx(88.22,'pop',.5,1.3);sfx(89.45,'whoosh',.5,.8);

window.TL={W,H,fps:30,duration:DUR,scenes:SCENES.map(s=>({id:s.id,name:s.name,a:s.a,b:s.b,vis:s.vis})),subs:SUBS.map(s=>({a:s.a,b:s.b,text:s.text,keys:s.keys})),holds:HOLDS,sfx:SFX,sources:SOURCES,
 musicDips:[[11.6,11.95],[53.45,53.75],[83.25,83.6]],
 musicBoost:[[3.6,4.1,1.2],[13.6,15.1,1.25],[25.6,26.5,1.15],[37.0,38.0,1.15],[50.3,51.35,1.15],[57.6,62.3,1.25],[86.8,89.5,1.2]]};
