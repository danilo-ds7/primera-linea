// Configuración opcional del Lector.
// API.Bible: versiones con derechos de autor (por ejemplo RVR1960, NVI, LBLA) leídas en vivo con tu cuenta de API.Bible.
// 1. Crea la cuenta y la clave en https://api.bible (plan Starter: hasta 3 Biblias con licencia, uso no comercial).
// 2. Publica el intermediario tools/apibible-worker.js (Cloudflare Workers, gratis) con tu clave como secreto,
//    para que la clave no quede a la vista en el sitio público. Pega aquí su dirección en «proxy».
// 3. Agrega en «biblias» el id de cada Biblia (lo muestra API.Bible), un nombre y el idioma (es, en).
window.LECTOR_CONFIG = {
  apibible: {
    proxy: "",            // por ejemplo "https://lector-apibible.TU-USUARIO.workers.dev"
    biblias: [
      // { id: "592420522e16049f-01", n: "Reina-Valera 1960", c: "es" }
    ]
  }
};
