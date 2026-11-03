/* ================= LÍNEA DE TIEMPO ================= */
const SCENES=[
 {id:'hook',name:'HOOK: RESPIRA',a:0,b:8.6,vis:'Luz de mañana y sombras de hojas sobre muro crema (IA); «Respira.» en serif; anillo que respira; aparece el logo «se», SERUNA · ACTIVE WEAR.'},
 {id:'origen',name:'BIENESTAR SIN PERFECCIÓN',a:8.6,b:17.2,vis:'Su foto de tarjetas en círculo; Xalapa, Veracruz; «bienestar sin perfección» (Wellness without perfection).'},
 {id:'mrl',name:'MOVE · REST · LIVE',a:17.2,b:26.9,vis:'Tríptico con sus fotos: MOVE (pilates), REST (Set Comfy), LIVE (Daily Set); se funde en su foto de dos amigas abrazadas.'},
 {id:'inspirada',name:'INSPIRED BY NATURE',a:26.9,b:31.6,vis:'«Inspired by nature.» y telas en sus colores dentro de un arco (IA).'},
 {id:'colores',name:'SUS 8 COLORES',a:31.6,b:44.9,vis:'Obsidiana, Laurel, Marea, Duna, Índigo, Cacao, Piedra y Merlot: naturaleza (IA) + su prenda real de ese color; cierra con la paleta de 8.'},
 {id:'telas',name:'TELAS FLEXIBLES · DEL MAT A TU DÍA',a:44.9,b:54.0,vis:'Prenda real con líneas que fluyen; sus fotos de pilates y de día a día.'},
 {id:'sets',name:'UN SET PARA CADA MOMENTO',a:54.0,b:62.9,vis:'Set Active, Flex Set y Set Comfy con su intención; después los 5 sets del catálogo.'},
 {id:'volver',name:'VOLVER A TI',a:62.9,b:67.8,vis:'Bosque con neblina (IA); «Moverte no es exigirte… es volver a ti.»'},
 {id:'juntas',name:'CADA UNA A SU RITMO · COMPÁRTELO',a:67.8,b:75.0,vis:'Sus fotos de comunidad; invitación a compartir con tu compañera de pilates.'},
 {id:'cierre',name:'CIERRE: @serunabalance',a:75.0,b:90,vis:'Logo «se», SERUNA · ACTIVE WEAR, @serunabalance 3 s sola, «Vuelve a tu cuerpo.» y botón Seguir con toque; el último medio segundo regresa al primer cuadro (loop).'},
];
// [entra, sale, texto, palabras clave, [voz desde, voz hasta]]
const SUBS_RAW=[
 [0.9,2.9,'Respira hondo… ¿hace cuánto',['Respira'],[1.03,2.9]],
 [2.9,4.7,'no te mueves… solo',['mueves…'],[2.9,4.3]],
 [4.7,6.4,'para sentirte bien?',['bien?'],[4.4,5.27]],
 [8.95,10.75,'Seruna nace en Xalapa',['Seruna'],[9.02,10.4]],
 [10.75,12.5,'con una idea sencilla:',['idea'],[10.4,11.72]],
 [12.5,14.8,'bienestar sin perfección.',['perfección'],[12.34,14.15]],
 [17.55,19.2,'Ropa para moverte…',['moverte…'],[17.62,18.91]],
 [19.2,21.0,'para descansar y vivir.',['vivir'],[19.07,21.16]],
 [27.35,29.2,'Inspirada en la naturaleza,',['naturaleza'],[27.41,28.97]],
 [29.2,31.1,'cada color, una historia.',['historia'],[29.26,31.09]],
 [31.75,35.0,'Obsidiana, laurel, marea, duna…',['duna…'],[31.83,35.25]],
 [36.25,39.4,'Índigo, cacao, piedra, merlot.',['merlot'],[36.34,39.53]],
 [45.45,47.3,'Telas que se adaptan',['adaptan'],[45.53,47.25]],
 [47.3,48.9,'a cada movimiento…',['movimiento…'],[47.38,48.40]],
 [48.9,50.7,'del mat de pilates',['pilates'],[48.94,50.2]],
 [50.7,52.9,'a tu día a día.',['día.'],[50.42,51.38]],
 [54.45,56.3,'Un set para entrenar…',['entrenar…'],[54.51,55.89]],
 [56.3,57.8,'otro para fluir…',['fluir…'],[56.06,57.02]],
 [57.8,61.2,'y otro para descansar.',['descansar'],[57.84,60.99]],
 [63.45,65.6,'Moverte no es exigirte…',['exigirte…'],[63.54,65.5]],
 [65.6,67.3,'volver a ti.',['ti'],[65.70,66.61]],
 [67.95,69.7,'Cada una, su ritmo…',['ritmo…'],[68.04,69.2]],
 [69.7,71.95,'todas a nuestra manera.',['manera'],[69.44,70.83]],
 [71.95,74.5,'Compártelo con tu compañera…',['Compártelo'],[72.04,74.07]],
 [75.05,76.6,'Síguenos en Instagram:',['Instagram'],[75.23,76.45]],
 [79.6,81.9,'Seruna. Vuelve a tu cuerpo.',['cuerpo'],[79.53,81.45]],
];
const HOLDS=[{a:76.6,b:79.6,text:'@serunabalance',sola:true,min:3}];
const HKEY=HOLDS[0];
const norm=s=>s.toLowerCase().replace(/[«»¿?¡!.,:;…"]/g,'');
const SUBS=SUBS_RAW.map(([a,b,text,keys,[va,vb]])=>{
 const ws=text.split(/\s+/),chars=ws.map(w=>w.length),tot=chars.reduce((s,v)=>s+v,0);let acc=0;
 const v0=Math.max(a+.05,va),v1=Math.min(b-.1,Math.max(v0+.4,vb));
 const words=ws.map((w,i)=>{const t0=v0+(acc/tot)*(v1-v0);acc+=chars[i];return{w,key:keys.map(norm).includes(norm(w)),num:false,t0}});
 return{a,b,text,keys,words}});
const sceneAt=t=>{let i=0;SCENES.forEach((s,j)=>{if(t>=s.a)i=j});return i};
const SOURCES=[[0.3,8.2,[T.nota.ia]],[26.9,44.4,[T.nota.ia]],[62.9,67.4,[T.nota.ia]]];
const TAGS=[];

const SFX=[];
const sfx=(t,type,v=1,pitch=1)=>SFX.push({t:+t.toFixed(3),type,v,pitch});
// efectos suaves: campanas, aire, toques
sfx(.05,'chime',.35,.8);sfx(5.8,'chime',.4,1.0);sfx(6.4,'whoosh',.18,.6);
[8.6,17.2,26.9,44.9,54.0,62.9,67.8,75.0].forEach(t0=>sfx(t0,'whoosh',.16,.55));
sfx(12.3,'chime',.3,1.2);[17.6,19.1,20.2].forEach((x,i)=>sfx(x,'pop',.18,.8+i*.06));sfx(27.4,'chime',.3,.9);
COLORES.forEach((c,i)=>sfx(c.t,'ding',.16,.7+i*.04));sfx(39.6,'chime',.35,1.1);
sfx(45.5,'sweep',.12,.6);[54.5,56.06,57.84].forEach((x,i)=>sfx(x,'pop',.18,.85+i*.06));sfx(59.6,'chime',.3,1.0);
sfx(65.7,'chime',.35,.8);sfx(72.0,'send',.25,.8);sfx(75.3,'chime',.4,1.0);sfx(76.6,'ding',.25,.8);
sfx(85.0,'click',.6);sfx(85.02,'pop',.25,1.1);sfx(89.45,'whoosh',.2,.55);

window.TL={W,H,fps:30,duration:DUR,scenes:SCENES.map(s=>({id:s.id,name:s.name,a:s.a,b:s.b,vis:s.vis})),subs:SUBS.map(s=>({a:s.a,b:s.b,text:s.text,keys:s.keys})),holds:HOLDS,sfx:SFX,sources:SOURCES,
 musicDips:[],musicBoost:[[5.6,8.6,1.15],[39.4,44.9,1.2],[82,89.5,1.2]]};
