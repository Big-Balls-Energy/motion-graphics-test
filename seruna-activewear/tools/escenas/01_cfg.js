
/* =====================================================================
   VIDEO PROMOCIONAL · SERUNA ACTIVE WEAR (Xalapa) · 90 s · 1080×1920 · 30 fps
   Estilo: elegante, tranquilo, natural. Sin marca de agua ni menciones de la agencia.
   · Logo «se» y fotos de producto: archivos oficiales (Linktree y catálogo de lanzamiento, oct 2026)
   · Fotos S01–S08: de su Instagram @serunabalance (recortadas, sin la interfaz de la app)
   · N01–N12: imágenes de naturaleza generadas con IA (Higgsfield) en la paleta de sus 8 colores
   ===================================================================== */
const W=1080,H=1920,CX=500,DUR=90,TAU=Math.PI*2,DEG=Math.PI/180;
// paleta: crema de sus publicaciones (#ECE8E4), carbón del logo (#4A515A), salvia del catálogo (#6E806B)
const C={bg:'#ECE8E4',cream:'#ECE8E4',paper:'#F5F2EE',stone:'#D8D0C6',ink:'#3F454C',char:'#4A515A',sage:'#6E806B',sand:'#B9A68E',
 white:'#FFFFFF',gray:'#8C8F92',cyan:'#6E806B',blue:'#6E806B',amber:'#9C7A4E',pink:'#6E806B',green:'#6E806B',red:'#9A4B4B',navy:'#24344F'};
// sus 8 colores (muestras tomadas de su publicación «The color of seruna»)
const COLORES=[
 {n:'Obsidiana',hex:'#0C0C0A',foto:'N01_obsidiana',prod:'p15',t:31.83},
 {n:'Laurel',hex:'#3C6325',foto:'N02_laurel',prod:'p19',t:33.03},
 {n:'Marea',hex:'#24344F',foto:'N03_marea',prod:'p09',t:33.90},
 {n:'Duna',hex:'#724A16',foto:'N04_duna',prod:'p07',t:34.74},
 {n:'Índigo',hex:'#061A3B',foto:'N05_indigo',prod:'p21',t:36.34},
 {n:'Cacao',hex:'#381904',foto:'N06_cacao',prod:'p23',t:37.28},
 {n:'Piedra',hex:'#4A5058',foto:'N07_piedra',prod:'p11',t:38.23},
 {n:'Merlot',hex:'#492E30',foto:'N08_merlot',prod:'p13',t:38.95}];
// sus sets (catálogo «Colección de lanzamiento», octubre 2026)
const SETS=[{n:'Daily Set',l:'LIVE',p:'p07'},{n:'Flex Set',l:'MOVE',p:'p13'},{n:'Top Twist',l:'MOVE',p:'p17'},{n:'Set Active',l:'MOVE',p:'p19'},{n:'Set Comfy',l:'REST',p:'p23'}];
const T={
 respira:'Respira.',marca:'SERUNA',sub:'ACTIVE WEAR',lugar:'XALAPA, VERACRUZ',
 bien:['bienestar','sin perfección.'],bienEn:'WELLNESS WITHOUT PERFECTION',
 mrl:[['MOVE','moverte'],['REST','descansar'],['LIVE','vivir']],
 inspired:'Inspired by nature.',inspiredEs:'Inspirada en la naturaleza',colores:'8 colores, una sola esencia',
 telas:['Telas flexibles','que se adaptan a ti'],mat:['Del mat de pilates','a tu día a día'],
 sets3:[['Set Active','para entrenar','p15'],['Flex Set','para fluir','p11'],['Set Comfy','para descansar','p21']],
 volver:['Moverte no es exigirte…','es volver a ti.'],
 ritmo:['Cada una a su ritmo.','Todas a nuestra manera.'],comparte:['Compártelo con tu','compañera de pilates'],
 usuario:'@serunabalance',cierre:'Vuelve a tu cuerpo.',claim:'Wellness without perfection · Move · Rest · Live',
 nota:{ia:'Imágenes de naturaleza: conceptuales.'},
 portada:['Respira.','Vuelve a tu cuerpo.']};
const cv=document.getElementById('c'),ctx=cv.getContext('2d');
const logo=new Image();logo.src='assets/marca/logo_se.png';
const FOTOS=['S01_tarjetas','S02_comfy','S03_estudio_estocada','S04_abrazo_espaldas','S05_puente','S06_abrazo_dos','S07_espalda_espalda','S08_dos_espaldas',
 'N01_obsidiana','N02_laurel','N03_marea','N04_duna','N05_indigo','N06_cacao','N07_piedra','N08_merlot','N09_luz_hojas','N10_rincon_pilates','N11_bosque','N12_telas'];
const PRODS=['p07','p09','p11','p13','p15','p17','p19','p21','p23','p12','p16'];
const FONDOS={};const RECORTES={};const MARCA={};
const IMG={};
for(const n of FOTOS){IMG[n]=new Image();IMG[n].src=`assets/fotos/${n}.jpg`}
for(const n of PRODS){IMG[n]=new Image();IMG[n].src=`assets/productos/${n}.png`}
const loaded=i=>i&&i.complete&&i.naturalWidth>0;
const GRADE='none';
