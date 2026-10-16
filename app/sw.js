// Service worker del Lector: guarda la app y los estudios para usarlos sin conexión.
// Al agregar o cambiar estudios, sube el número de VERSION para que los celulares descarguen lo nuevo.
const VERSION = "lector-v12";
const BASE = ["./", "index.html", "manifest.webmanifest",
  "iconos/icono-192.png", "iconos/icono-512.png", "iconos/icono-maskable-512.png",
  "iconos/apple-touch-icon.png", "iconos/favicon-32.png", "comparaciones/notas.json",
  "estudio/indice.json", "estudio/libros.json", "estudio/atributos.json", "estudio/pericopas.json", "estudio/conteos.json"];

self.addEventListener("install", (e) => {
  e.waitUntil((async () => {
    const cache = await caches.open(VERSION);
    await cache.addAll(BASE.map((u) => new Request(u, { cache: "no-cache" })));
    self.skipWaiting();
  })());
});

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k !== VERSION) await caches.delete(k);
    await self.clients.claim();
  })());
});

// Primero la red (para ver siempre lo último); si no hay conexión, lo guardado.
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const fuentes = url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com" || url.hostname === "api.getbible.net" || url.hostname === "www.sefaria.org";
  if (url.origin !== location.origin && !fuentes) return;
  e.respondWith((async () => {
    const cache = await caches.open(VERSION);
    try {
      // "no-cache": revalida con GitHub en cada carga, así el celular ve lo último apenas se publica.
      const propio = url.origin === location.origin;
      const res = propio
        ? await fetch(req.mode === "navigate" ? req.url : req, { cache: "no-cache" })
        : await fetch(req);
      if (res && (res.ok || res.type === "opaque")) cache.put(req, res.clone());
      return res;
    } catch (err) {
      const hit = await cache.match(req, { ignoreSearch: url.origin === location.origin });
      if (hit) return hit;
      if (req.mode === "navigate") return (await cache.match("index.html")) || Response.error();
      return Response.error();
    }
  })());
});
