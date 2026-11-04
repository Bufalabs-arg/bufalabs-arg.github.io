// Mando de BufaLabs: se instala como app. Siempre pide lo último a la red; sin internet, abre la última copia.
const C='mando-3';
self.addEventListener('install', e=>{ e.waitUntil(caches.open(C).then(c=>c.addAll(['./'])).then(()=>self.skipWaiting())); });
self.addEventListener('activate', e=>{ e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('mando-')&&k!==C).map(k=>caches.delete(k)))).then(()=>self.clients.claim())); });
self.addEventListener('fetch', e=>{ const u=new URL(e.request.url); if(e.request.method!=='GET'||u.origin!==location.origin||!u.pathname.startsWith('/mando/')) return;
  e.respondWith(fetch(e.request).then(r=>{ if(r.ok){ const cp=r.clone(); caches.open(C).then(c=>c.put(e.request,cp)); } return r; }).catch(()=>caches.match(e.request).then(r=>r||caches.match('./')))); });
