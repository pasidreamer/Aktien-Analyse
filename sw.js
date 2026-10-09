// Offline-Unterstützung: App-Hülle aus dem Cache, Daten immer zuerst frisch aus dem Netz.
const V = "ampel-v1";
const SHELL = ["./", "index.html", "app.css", "app.js", "manifest.webmanifest", "icons/icon-192.png", "icons/apple-touch-icon.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(V).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET") return;
  const fresh = u.pathname.includes("/data/") || u.pathname.includes("/analysen/") || u.pathname.endsWith("app.js") || u.pathname.endsWith("app.css") || u.pathname.endsWith("/") || u.pathname.endsWith("index.html");
  if (fresh) {
    // Netz zuerst, bei Funkloch der letzte Stand
    e.respondWith(fetch(e.request).then(r => { const c = r.clone(); caches.open(V).then(x => x.put(e.request, c)); return r; })
      .catch(() => caches.match(e.request, { ignoreSearch: true })));
  } else {
    e.respondWith(caches.match(e.request).then(m => m || fetch(e.request).then(r => { if (r.ok || r.type === "opaque") { const c = r.clone(); caches.open(V).then(x => x.put(e.request, c)); } return r; })));
  }
});
