// Línea de tiempo única: la usan la animación, el audio y el guion.
// Subtítulos: [inicio, fin, texto]. Las palabras entre *asteriscos* son la palabra clave (naranja).
window.TIMELINE = {
  duration: 60,
  fps: 30,
  scenes: [
    { id: 'hook',       start: 0,  end: 3,  title: 'HOOK' },
    { id: 'giro',       start: 3,  end: 8,  title: 'GIRO' },
    { id: 'experimento',start: 8,  end: 20, title: 'EL EXPERIMENTO' },
    { id: 'resultado',  start: 20, end: 30, title: 'EL RESULTADO' },
    { id: 'porque',     start: 30, end: 42, title: 'POR QUÉ FUNCIONA' },
    { id: 'donde',      start: 42, end: 52, title: 'DÓNDE LO VES' },
    { id: 'aplicacion', start: 52, end: 57, title: 'APLICACIÓN' },
    { id: 'cta',        start: 57, end: 60, title: 'CTA' },
  ],
  subs: [
    [0.00, 1.50, 'En este menú hay una opción'],
    [1.50, 3.00, 'que existe para que *NADIE* la compre.'],

    [3.00, 4.25, 'Y aun así,'],
    [4.25, 5.50, 'te hace gastar *más*.'],
    [5.50, 6.75, 'Se llama:'],
    [6.75, 8.00, 'el efecto *señuelo*.'],

    [8.00, 10.00, 'Una *revista* ofreció tres suscripciones:'],
    [10.00, 11.20, 'solo *digital*,'],
    [11.20, 12.60, '*59* dólares.'],
    [12.60, 13.90, 'Solo *impresa*,'],
    [13.90, 15.30, '*125*.'],
    [15.30, 17.00, 'Impresa más *digital*…'],
    [17.00, 20.00, '*también* *125*.'],

    [20.00, 21.60, '*Nadie* eligió la impresa sola.'],
    [21.60, 23.00, 'Pero el *84%*'],
    [23.00, 24.40, 'eligió el *paquete*.'],
    [24.40, 25.80, 'Cuando *quitaron* esa opción'],
    [25.80, 27.00, '“inútil”…'],
    [27.00, 28.60, 'solo el *32%*'],
    [28.60, 30.00, 'lo eligió.'],

    [30.00, 31.50, 'Tu *cerebro* no sabe'],
    [31.50, 33.00, 'cuánto vale algo'],
    [33.00, 34.40, 'por sí solo:'],
    [34.40, 36.00, 'lo *compara*.'],
    [36.00, 37.60, 'El *señuelo* hace que'],
    [37.60, 39.20, 'la opción cara'],
    [39.20, 42.00, 'parezca una *ganga*.'],

    [42.00, 43.60, 'Está en las *palomitas* medianas'],
    [43.60, 44.90, 'casi al precio'],
    [44.90, 46.20, 'de las grandes,'],
    [46.20, 48.00, 'en planes de *streaming*'],
    [48.00, 49.60, 'y en *cafés*'],
    [49.60, 52.00, 'de tres tamaños.'],

    [52.00, 53.20, '¿Tienes un *negocio*?'],
    [53.20, 54.40, '*No* bajes tu precio.'],
    [54.40, 55.60, '*Agrega* una opción'],
    [55.60, 57.00, 'que haga *brillar* la que quieres vender.'],

    [57.00, 58.40, '*Síguenos* para más trucos'],
    [58.40, 60.00, 'de *psicología* que usan las marcas contigo.'],
  ],
  // Efectos de sonido: [tiempo, tipo]. Tipos: pop, whoosh, ding, poof, click, drop, thud, sparkle, tick
  sfx: [
    [0.06, 'thud'], [0.12, 'pop'], [0.18, 'pop'], [0.24, 'pop'], [0.30, 'pop'], [0.75, 'pop'],
    [3.00, 'whoosh'], [3.40, 'pop'], [4.30, 'pop'], [5.50, 'whoosh'], [6.75, 'thud'], [7.25, 'sparkle'],
    [7.88, 'whoosh'], [8.15, 'pop'], [8.95, 'pop'], [10.00, 'pop'], [11.25, 'tick'], [11.85, 'ding'],
    [12.60, 'pop'], [13.95, 'tick'], [14.55, 'ding'], [15.30, 'pop'], [17.05, 'tick'], [17.60, 'ding'], [18.15, 'pop'],
    [19.88, 'whoosh'], [20.40, 'pop'], [20.70, 'pop'], [21.65, 'tick'], [22.25, 'ding'], [23.00, 'whoosh'], [23.80, 'ding'],
    [25.85, 'poof'], [27.05, 'drop'], [27.70, 'ding'], [28.05, 'drop'],
    [29.88, 'whoosh'], [31.50, 'pop'], [33.00, 'whoosh'], [34.40, 'pop'], [36.10, 'pop'], [37.70, 'pop'], [37.80, 'whoosh'], [39.20, 'ding'], [39.25, 'sparkle'],
    [41.88, 'whoosh'], [42.25, 'pop'], [42.35, 'pop'], [42.45, 'pop'], [43.60, 'pop'], [44.90, 'ding'],
    [46.20, 'whoosh'], [46.45, 'pop'], [47.00, 'pop'], [47.60, 'ding'],
    [49.00, 'whoosh'], [49.25, 'pop'], [49.80, 'pop'], [50.40, 'ding'],
    [51.88, 'whoosh'], [52.15, 'pop'], [53.20, 'pop'], [53.70, 'whoosh'], [54.45, 'pop'], [54.60, 'pop'], [54.75, 'pop'], [55.60, 'ding'], [55.65, 'sparkle'],
    [56.88, 'whoosh'], [57.15, 'pop'], [58.30, 'click'], [58.40, 'ding'], [59.20, 'whoosh'],
  ],
  // Volumen de la música (ganancia lineal sobre la pista normalizada): [inicio, fin, ganancia]
  musicGain: [
    [0, 3, 0.12],    // hook: mucho texto en 3 s
    [3, 8, 0.17],    // giro / título
    [8, 42, 0.12],   // experimento, resultado y explicación (más texto y cifras)
    [42, 52, 0.15],  // ejemplos en carrusel
    [52, 60, 0.12],  // aplicación + CTA
  ],
};
