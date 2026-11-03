
/* =====================================================================
   VIDEO PROMOCIONAL · MATBARRE STUDIO (Orizaba) · 90 s · 1080×1920 · 30 fps
   Estilo: femenino, elegante, rosa empolvado de su marca. Sin marca de agua ni menciones de la agencia.
   Dos versiones: sin precios (por defecto) y con la clase de prueba ($150) → ?precio
   · Logo, fotos de clases y de coaches: archivos oficiales de matbarrestudio.com.mx
   · Avatar «M»: su foto de perfil de Instagram (captura enviada por el usuario)
   · N1–N6: imágenes conceptuales generadas con IA (Higgsfield) en su estilo de luz
   ===================================================================== */
const W=1080,H=1920,CX=500,DUR=90,TAU=Math.PI*2,DEG=Math.PI/180;
const PRECIO=new URLSearchParams(location.search).has('precio');
// paleta: rosa del logo (#BA7E75), vino de sus botones, blush de su sitio
const C={bg:'#F6EFEC',blush:'#F6EFEC',paper:'#FBF7F5',mist:'#EADCD7',rose:'#BA7E75',roseD:'#9C5F57',wine:'#7E4A46',ink:'#2E2626',char:'#3A3030',gray:'#8C8282',white:'#FFFFFF',
 cream:'#F6EFEC',sage:'#9C5F57',cyan:'#BA7E75',blue:'#BA7E75',amber:'#BA7E75',pink:'#BA7E75',green:'#BA7E75',red:'#9A4B4B',navy:'#2E2626'};
const T={
 hook:[['10','sesiones','lo sientes'],['20','sesiones','lo ves'],['30','sesiones','un cuerpo nuevo']],
 jp:'Joseph Pilates',jpSub:'CREADOR DEL MÉTODO PILATES',jpAnios:'casi 100 años',
 lugar:'ORIZABA, VERACRUZ',mtm:'MORE THAN MOVEMENT',momento:['Más que movimiento,','es tu momento.'],
 clases:[{n:['Bar','re'],num:'01',foto:'F03_barre',ins:'N1_releve',chips:['Resistencia','Equilibrio','Postura'],dato:'Inspirado en el ballet · Londres, 1959'},
         {n:['Pila','tes'],num:'02',foto:'F04_pilates',ins:'N2_aro_mat',chips:['Fuerza desde tu centro','Precisión','Cuerpo y mente'],dato:'El método de Joseph Pilates'},
         {n:['Scul','pt'],num:'03',foto:'F05_sculpt',ins:'N5_mancuernas',chips:['Tonifica','Fuerza','Ritmo'],dato:'Fuerza y resistencia de cuerpo completo'}],
 ciencia:['La ciencia','lo respalda.'],cochrane:{n1:'10',l1:'estudios',n2:'510',l2:'personas',txt:['El pilates puede aliviar','el dolor de espalda baja']},
 mujeres:['En mujeres, se asocia con','más fuerza, flexibilidad y equilibrio'],metr:['Fuerza','Flexibilidad','Equilibrio'],
 oms:['días por semana','de fuerza, como mínimo'],dias:['L','M','M','J','V','S','D'],
 coaches:{h:['Nuestras Coach','es'],sub:'INSTRUCTORAS ESPECIALIZADAS',lista:[['Pao','C1_pao'],['Mireille','C2_mireille'],['Ana','C3_ana'],['Liz','C4_liz']],tec:['Cuidan tu técnica','en cada movimiento']},
 horario:{h:['Nuestras Clas','es'],dias:'Lunes a sábado',horas:['7:00','8:10','9:10','18:10','19:10','20:10'],dir:['Plaza Sur 17 · Centro','Orizaba, Veracruz']},
 precio:{pk:'FIRST TIMERS',sym:'$',n:'150',mxn:'MXN',l1:'1 clase',l2:'Vigencia de 7 días',h:'Tu primera clase'},
 reserva:{url:'matbarrestudio.com.mx',btn:'BOOK NOW',h:['Reserva','en línea'],comparte:['Compártelo con','tu amiga de pilates']},
 perfil:{nom:'MATBARRE STUDIO',bio1:'Welcome to your wellness era',bio2:'Barre · Pilates · Sculpt'},
 usuario:'@matbarre_mx',cierre:['Bienvenida a tu','era de bienestar.'],
 nota:{ia:'Imágenes conceptuales (IA), salvo fotos de Matbarre.',
  frase:'Frase atribuida a Joseph Pilates, creador del método (n. 1883).',
  cochrane:['Cochrane (2015): 10 ensayos, 510 personas con dolor lumbar; frente a intervención mínima.','Evidencia de calidad baja a moderada.'],
  mujeres:['Revisión sistemática en mujeres (Bull. Fac. Phys. Ther., 2023).','Gráfico ilustrativo, sin cifras.'],
  oms:['OMS (2020): actividades de fortalecimiento muscular 2 o más días a la semana.'],
  horario:['Horario de la semana del 2 al 8 nov 2026; consulta el vigente en su sitio.'],
  precio:['Precio publicado en matbarrestudio.com.mx al 2 nov 2026.']},
 portada:['Diez sesiones','para sentirlo.']};
const cv=document.getElementById('c'),ctx=cv.getContext('2d');
const logo=new Image();logo.src='assets/marca/logo_rosa.png';
const MARCA={};for(const n of ['logo_rosa','logo_blanco','avatar_m','m_blanca']){MARCA[n]=new Image();MARCA[n].src=`assets/marca/${n}.png`}
const FOTOS=['F01_tres_plancha','F02_tres_pierna','F03_barre','F04_pilates','F05_sculpt','C1_pao','C2_mireille','C3_ana','C4_liz',
 'N1_releve','N2_aro_mat','N3_espalda','N4_luz_barra','N5_mancuernas','N6_estiramiento'];
const FONDOS={};const RECORTES={};const IMG={};
for(const n of FOTOS){IMG[n]=new Image();IMG[n].src=`assets/fotos/${n}.jpg`}
const loaded=i=>i&&i.complete&&i.naturalWidth>0;
const GRADE='none';
