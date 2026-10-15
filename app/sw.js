// Guarda la app y los estudios para usarlos sin conexión.
// Al publicar cambios, sube la versión (lector-v2 → lector-v3) para que los celulares descarguen lo nuevo.
var CACHE = "lector-v6";
var BASE = ["./", "index.html", "manifest.webmanifest", "config.js", "estudios/index.json", "comparaciones/notas.json",
  "iconos/icono-192.png", "iconos/apple-touch-icon.png", "iconos/favicon-32.png"];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(BASE.map(function (u) { return new Request(u, { cache: "reload" }); })); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (ks) {
    return Promise.all(ks.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

// Archivos propios: primero la red (para tener lo último) y, sin conexión, la copia guardada.
// "no-cache" obliga a preguntar al servidor si hay versión nueva (GitHub Pages deja copias de 10 minutos).
self.addEventListener("fetch", function (e) {
  var u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;
  e.respondWith(fetch(e.request, { cache: "no-cache" }).then(function (r) {
    if (r.ok) { var copia = r.clone(); caches.open(CACHE).then(function (c) { c.put(e.request, copia); }); }
    return r;
  }).catch(function () { return caches.match(e.request); }));
});
