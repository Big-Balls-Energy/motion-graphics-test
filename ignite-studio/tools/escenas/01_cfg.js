
/* =====================================================================
   VIDEO PROMOCIONAL · IGNITE STUDIO (Xalapa) · 90 s · 1080×1920 · 30 fps
   · Colores: C · Textos en pantalla: T · Escenas: SCENES · Subtítulos: SUBS_RAW
   · Sin marca de agua ni créditos de Atlas Path (pedido del usuario): el cierre es de Ignite.
   · Logos y fotos de coaches: archivos oficiales de su sitio (ignite.cyclingboost.com).
   · Fotos C01–C06: tomas conceptuales generadas con IA (Higgsfield) con su estilo de luz y color;
     no muestran su estudio real.
   ===================================================================== */
const W=1080,H=1920,CX=500,DUR=90,TAU=Math.PI*2,DEG=Math.PI/180;
// paleta Ignite: azul eléctrico del logo (#1F6BFF), azul marino profundo, hielo (#EAF3FD) y blanco
const C={bg:'#030817',navy:'#071233',blue:'#1F6BFF',cyan:'#3D8BFF',ice:'#EAF3FD',white:'#FFFFFF',gray:'#9FB0CC',amber:'#FFD23F',ink:'#030817',green:'#2EE59D',pink:'#8EC5FF',red:'#FF4D5E',deep:'#0A2A8A'};
const T={
 hook:['¿Y SI TU','MEJOR VERSIÓN…','EMPIEZA CON','UNA SOLA CLASE?'],
 chips:['CYCLING','TRAIN','XALAPA'],
 sudar:['NO VIENES','SOLO A SUDAR…'],encender:['VIENES A','ENCENDERTE'],
 sec:[['01','SALUD'],['02','CUERPO'],['03','RENDIMIENTO'],['04','COMUNIDAD']],
 corazon:'CORAZÓN',pulmones:'PULMONES',salud3:[['ESTRÉS','down'],['SUEÑO','up'],['ENERGÍA','up']],
 cuerpo1:['PIERNAS','GLÚTEOS'],pedaladas:'PEDALADAS',cuerpo2:['BRAZOS','ESPALDA','ABDOMEN'],fuerza:'CLASES DE FUERZA',
 rend:['RESISTENCIA','FUERZA','POTENCIA'],
 clases:[['TRAIN','FULL LOWER BODY'],['TRAIN','PUSH'],['TRAIN','PULL + ABS'],['TRAIN','FULL BODY'],['CYCLE','JUST RIDE']],
 espejo:'LO MEJOR NO SE VE EN EL ESPEJO…',gente:'ES LA GENTE',
 coaches:['Emilio','Isa','Ivana','Jorge','Julius','Mime','Montse','Rebeca','Sebastian','Vale','Zamora'],
 coachLabel:'COACHES QUE TE CONOCEN POR TU NOMBRE',
 nadie:['NADIE','ENTRENA','SOLO'],juntos:'CADA META SE CELEBRA JUNTOS',
 dias:[['LUN','6:00'],['MAR','7:00'],['MIÉ','6:00'],['JUE','7:00'],['VIE','6:00'],['SÁB','8:30'],['DOM','9:00']],
 horarios:'CLASES DESDE LAS',seis:'6:00 AM',semana:'TODA LA SEMANA',
 app:{titulo:'IGNITE',clase:'CYCLE · JUST RIDE',hora:'7:30 PM',coach:'con Julius',btn:'RESERVAR',ok:'¡RESERVADO!'},
 etiqueta:['ETIQUETA A QUIEN','VENDRÍA CONTIGO'],tag:'@tu_compa ¿vamos el lunes?',
 lugar:'PLAZA XANAT · XALAPA',enciendete:'ENCIÉNDETE',usuario:'@_ignitestudiomx',
 nota:{salud:['Beneficios del ejercicio regular según la OMS (2020).','Los resultados varían de persona a persona.'],
  horarios:['Primera clase de cada día, semana del 26 oct al 1 nov 2026.','Consulta los horarios vigentes en su app.'],
  ia:['Tomas de la bici: imágenes conceptuales.']},
 portada:['¿TU MEJOR','VERSIÓN?','ENCIÉNDETE']};
const cv=document.getElementById('c'),ctx=cv.getContext('2d');
const logo=new Image();logo.src='assets/marca/ala_blanca.png';
const MARCA={};for(const n of ['ala_blanca','ala_azul','ignite_blanco','ignite_azul']){MARCA[n]=new Image();MARCA[n].src=`assets/marca/${n}.png`}
// fotos: I01–I04 de su sitio (blanco y negro), C01–C06 conceptuales con IA, coaches de su sitio
const FOTOS=['I01_strength','I02_movement','I03_getting_started','I04_we_are_ignite','C01_bici_estudio','C02_volante','C03_silueta_ciclista','C04_piernas_pedaleo','C05_manos_manubrio','C06_bici_azul'];
const FONDOS={};const RECORTES={W01_mano_celular:1536/1024};
const IMG={};
for(const n of FOTOS){IMG[n]=new Image();IMG[n].src=`assets/fotos/${n}.jpg`}
for(const n of T.coaches){IMG['co_'+n]=new Image();IMG['co_'+n].src=`assets/coaches/${n}.jpg`}
for(const n of Object.keys(RECORTES)){IMG[n]=new Image();IMG[n].src=`assets/fotos/${n}.png`}
const loaded=i=>i&&i.complete&&i.naturalWidth>0;
const GRADE='contrast(1.1)';
