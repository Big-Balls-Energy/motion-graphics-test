// Todo el texto y los colores del video viven aquí.
// Edita este archivo y vuelve a renderizar (ver promo/README.md).
//
// PROVISIONAL: art.bigballsenergy.com no fue accesible al crear esta versión,
// así que los textos de abajo son genéricos. Sustitúyelos por los del sitio.
window.PROMO = {
  brand: {
    line1: "BIG BALLS",
    line2: "ENERGY",
    tag: "ART",
    url: "art.bigballsenergy.com",
  },

  colors: {
    bg: "#0B0614",
    bg2: "#1A0B2E",
    orange: "#FF5A1F",
    magenta: "#FF2E88",
    yellow: "#FFD60A",
    cyan: "#2EF2FF",
    white: "#FFF6EC",
    muted: "#7D7390",
  },

  // Escena 2 (4–8 s): gancho. La última línea es la que la bola rompe.
  hook: ["¿TU MARCA", "SE VE", "ABURRIDA?"],
  answer: ["¡DALE", "ENERGÍA!"],

  // Escena 3 (8–14 s): servicios. Exactamente 4.
  servicesTitle: "LO QUE HACEMOS",
  services: [
    { title: "ILUSTRACIÓN", sub: "Piezas únicas hechas a mano" },
    { title: "BRANDING", sub: "Logos e identidad que se recuerdan" },
    { title: "MOTION GRAPHICS", sub: "Animación que frena el scroll" },
    { title: "DISEÑO PARA REDES", sub: "Contenido que se comparte" },
  ],
  servicesFooter: "…y todo con energía de sobra.",

  // Escena 4 (14–20 s): portafolio.
  portfolioTitle: ["ARTE QUE", "SE NOTA"],
  portfolioCaption: "ILUSTRACIÓN · BRANDING · MOTION",
  // Rutas de imágenes reales del portafolio (relativas a promo/), p. ej.
  // ["assets/obra1.jpg", "assets/obra2.jpg"]. Vacío = arte generativo.
  portfolioImages: [],

  // Escena 5 (20–25 s): tres razones. "\n" separa líneas.
  valuesTitle: "POR QUÉ NOSOTROS",
  values: ["IDEAS\nAUDACES", "ARTE 100%\nORIGINAL", "HECHO PARA\nDESTACAR"],

  // Escena 6 (25–30 s): llamada a la acción.
  ctaTitle: ["¿LISTO PARA", "DESTACAR?"],
  ctaButton: "COTIZA TU PROYECTO",
};
