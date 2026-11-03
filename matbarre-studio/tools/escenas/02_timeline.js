/* ================= LÍNEA DE TIEMPO ================= */
const SCENES=[
 {id:'hook',name:'HOOK: 10 · 20 · 30 SESIONES',a:0,b:11.5,vis:'«10 sesiones: lo sientes · 20: lo ves · 30: un cuerpo nuevo» con números grandes y fotos en arco; firma de Joseph Pilates (frase atribuida).'},
 {id:'marca',name:'MATBARRE STUDIO · ORIZABA',a:11.5,b:19.7,vis:'Su foto de tres alumnas en plancha; logo oficial rosa; «More than movement» → «Más que movimiento, es tu momento».'},
 {id:'barre',name:'CLASE 01 · BARRE',a:19.7,b:25.6,vis:'Su foto de Barre en óvalo (como en su sitio), relevé conceptual y beneficios: resistencia, equilibrio, postura; dato: Londres, 1959.'},
 {id:'pilates',name:'CLASE 02 · PILATES',a:25.6,b:31.6,vis:'Su foto de Pilates en óvalo, aro y mat conceptuales; fuerza desde tu centro, precisión, cuerpo y mente.'},
 {id:'sculpt',name:'CLASE 03 · SCULPT',a:31.6,b:36.9,vis:'Su foto de Sculpt en óvalo, mancuernas conceptuales; tonifica, fuerza, ritmo.'},
 {id:'ciencia',name:'LA CIENCIA LO RESPALDA',a:36.9,b:46.0,vis:'Espalda en blanco y negro (conceptual); contador 10 estudios · 510 personas; alivio del dolor de espalda baja (Cochrane 2015).'},
 {id:'mujeres',name:'EN MUJERES: FUERZA · FLEXIBILIDAD · EQUILIBRIO',a:46.0,b:51.2,vis:'Estiramiento conceptual con tres anillos ilustrativos (sin cifras).'},
 {id:'oms',name:'OMS: FUERZA 2+ DÍAS POR SEMANA',a:51.2,b:56.9,vis:'«2+» grande y semana con dos días marcados.'},
 {id:'coaches',name:'SUS COACHES: PAO · MIREILLE · ANA · LIZ',a:56.9,b:68.2,vis:'Sus 4 retratos oficiales en óvalos, cada nombre al decirlo; luego una por una: «Cuidan tu técnica en cada movimiento».'},
 {id:'clases',name:PRECIO?'TU PRIMERA CLASE: $150 MXN':'LUNES A SÁBADO · CENTRO DE ORIZABA',a:68.2,b:73.8,vis:PRECIO?'Tarjeta ovalada como en su sitio: FIRST TIMERS $150 MXN, 1 clase, vigencia 7 días.':'Horarios de la semana (7:00 a 20:10) y dirección: Plaza Sur 17, Centro, Orizaba.'},
 {id:'reserva',name:'RESERVA EN LÍNEA · COMPÁRTELO',a:73.8,b:78.5,vis:'Tarjeta de su sitio con botón BOOK NOW; su foto de tres alumnas: compártelo con tu amiga de pilates.'},
 {id:'cierre',name:'CIERRE: @matbarre_mx',a:78.5,b:90,vis:'Perfil con su avatar «M», MATBARRE STUDIO, su bio; @matbarre_mx 3 s sola; «Bienvenida a tu era de bienestar» y botón Seguir con toque; el último medio segundo regresa al primer cuadro (loop).'},
];
// [entra, sale, texto, palabras clave, [voz desde, voz hasta]]
const SUBS_RAW=[
 [0.6,2.6,'Diez sesiones: lo sientes.',['sientes.'],[0.64,2.53]],
 [2.6,4.4,'Veinte: lo ves.',['ves.'],[2.85,4.19]],
 [4.4,6.95,'Treinta: un cuerpo nuevo.',['nuevo.'],[4.48,6.85]],
 [7.45,9.25,'Eso decía Joseph Pilates,',['Pilates,'],[7.53,9.25]],
 [9.25,11.0,'hace casi cien años.',['cien'],[9.42,10.91]],
 [11.6,13.9,'Hoy, en Orizaba, esa filosofía',['Orizaba,'],[11.64,13.6]],
 [13.9,16.2,'tiene nombre: Matbarre Studio.',['Matbarre'],[13.95,16.12]],
 [16.7,19.2,'Más que movimiento: tu momento.',['momento.'],[16.74,19.17]],
 [20.0,22.1,'Barre: inspirado en ballet.',['ballet.'],[20.04,21.89]],
 [22.1,25.1,'Resistencia, equilibrio y postura.',['postura.'],[22.14,24.99]],
 [26.0,28.4,'Pilates: fuerza desde tu centro,',['centro,'],[26.04,28.29]],
 [28.4,31.1,'precisión y conexión cuerpo-mente.',['cuerpo-mente.'],[28.52,31.07]],
 [32.0,34.65,'Sculpt: tonifica todo tu cuerpo,',['tonifica'],[32.04,34.62]],
 [34.65,36.4,'con fuerza y ritmo.',['ritmo.'],[34.84,36.25]],
 [37.35,38.85,'Y lo mejor…',['mejor…'],[37.43,38.21]],
 [38.85,40.6,'la ciencia lo respalda.',['ciencia'],[38.9,39.88]],
 [40.6,42.7,'Revisión de 10 estudios:',['10'],[40.62,42.4]],
 [42.7,45.5,'puede aliviar el dolor lumbar.',['lumbar.'],[42.75,45.4]],
 [46.4,48.3,'En mujeres: más fuerza,',['fuerza,'],[46.44,48.2]],
 [48.3,50.7,'flexibilidad y equilibrio.',['equilibrio.'],[48.35,50.6]],
 [51.5,53.8,'La OMS recomienda fuerza',['OMS'],[51.54,53.7]],
 [53.8,56.4,'dos días por semana, mínimo.',['dos'],[53.85,56.3]],
 [57.2,60.1,'Te guían instructoras especializadas:',['especializadas:'],[57.24,59.98]],
 [60.1,62.6,'Pao, Mireille, Ana, Liz.',['Liz.'],[60.28,62.4]],
 [63.1,65.4,'Cuidan tu técnica,',['técnica,'],[63.14,65.3]],
 [65.4,67.7,'avanzas segura, a tu ritmo.',['segura,'],[65.56,67.54]],
 ...(PRECIO?[
 [68.6,70.1,'Tu primera clase…',['primera'],[68.64,69.75]],
 [70.1,72.4,'cuesta solo $150 MXN.',['$150'],[70.15,72.11]]]:[
 [68.6,70.9,'Barre, pilates y sculpt,',['sculpt,'],[68.63,70.81]],
 [70.9,73.3,'lunes a sábado, en Orizaba.',['sábado,'],[70.95,73.25]]]),
 [74.2,75.8,'Reserva en línea…',['Reserva'],[74.24,75.63]],
 [75.8,78.0,'comparte con tu amiga.',['amiga.'],[75.86,77.92]],
 [78.9,80.4,'Síguenos en Instagram:',['Instagram:'],[78.95,80.09]],
 [84.0,85.6,'Matbarre Studio: bienvenida',['bienvenida'],[84.05,85.5]],
 [85.6,87.8,'a tu era de bienestar.',['bienestar.'],[85.65,87.39]],
];
const HOLDS=[{a:80.4,b:83.6,text:'@matbarre_mx',sola:true,min:3}];
const HKEY=HOLDS[0];
const norm=s=>s.toLowerCase().replace(/[«»¿?¡!.,:;…"]/g,'');
const SUBS=SUBS_RAW.map(([a,b,text,keys,[va,vb]])=>{
 const ws=text.split(/\s+/),chars=ws.map(w=>w.length),tot=chars.reduce((s,v)=>s+v,0);let acc=0;
 const v0=Math.max(a+.05,va),v1=Math.min(b-.1,Math.max(v0+.4,vb));
 const words=ws.map((w,i)=>{const t0=v0+(acc/tot)*(v1-v0);acc+=chars[i];return{w,key:keys.map(norm).includes(norm(w)),num:false,t0}});
 return{a,b,text,keys,words}});
const sceneAt=t=>{let i=0;SCENES.forEach((s,j)=>{if(t>=s.a)i=j});return i};
const SOURCES=[[0.3,11.0,[T.nota.frase]],[19.9,36.4,[T.nota.ia]],[40.6,45.6,T.nota.cochrane],[46.2,50.8,T.nota.mujeres],[51.5,56.5,T.nota.oms],
 [68.6,73.4,PRECIO?T.nota.precio:T.nota.horario]];
const TAGS=[];

const SFX=[];
const sfx=(t,type,v=1,pitch=1)=>SFX.push({t:+t.toFixed(3),type,v,pitch});
// efectos suaves y femeninos: campanas, aire, toques
sfx(.6,'chime',.35,.9);sfx(2.85,'chime',.35,1.0);sfx(4.5,'chime',.4,1.12);sfx(7.45,'whoosh',.16,.6);
[11.5,19.7,25.6,31.6,36.9,46.0,51.2,56.9,68.2,73.8,78.5].forEach(t0=>sfx(t0,'whoosh',.16,.55));
sfx(14.95,'chime',.45,1.0);sfx(16.8,'sweep',.12,.7);
[[20.74,22.2,23.4,24.3],[26.99,28.6,29.9],[32.9,34.9,35.6]].forEach((g,j)=>g.forEach((x,i)=>sfx(x,i?'pop':'ding',i?.16:.18,.85+i*.06+j*.04)));
sfx(38.9,'chime',.35,1.05);sfx(40.7,'ding',.2,.8);sfx(41.2,'ding',.2,.9);
sfx(46.5,'sweep',.12,.6);[47.0,48.4,49.4].forEach((x,i)=>sfx(x,'pop',.16,.9+i*.06));
sfx(51.6,'chime',.35,.95);sfx(54.0,'ding',.18,.85);sfx(54.4,'ding',.18,.95);
[60.28,60.77,61.42,61.9].forEach((x,i)=>sfx(x,'pop',.18,.9+i*.05));sfx(63.15,'sweep',.12,.7);
if(PRECIO){sfx(70.15,'chime',.45,1.1)}else{[70.95,71.3,71.65].forEach((x,i)=>sfx(x,'pop',.15,.95+i*.05))}
sfx(74.9,'click',.5);sfx(76.6,'send',.25,.8);sfx(79.0,'chime',.4,1.0);sfx(80.45,'ding',.25,.8);
sfx(88.3,'click',.6);sfx(88.32,'pop',.25,1.1);sfx(89.45,'whoosh',.2,.55);

window.TL={W,H,fps:30,duration:DUR,scenes:SCENES.map(s=>({id:s.id,name:s.name,a:s.a,b:s.b,vis:s.vis})),subs:SUBS.map(s=>({a:s.a,b:s.b,text:s.text,keys:s.keys})),holds:HOLDS,sfx:SFX,sources:SOURCES,
 musicDips:[],musicBoost:[[6.9,7.5,1.15],[16.3,19.6,1.15],[87.5,89.5,1.2]]};
