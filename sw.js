// Carnet de Scores — fonctionnement hors ligne
const V='carnet-ba71c96a';
const SHELL=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./icon-180.png'];
const EXT=['www.gstatic.com','fonts.googleapis.com','fonts.gstatic.com'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('carnet-')&&k!==V&&k!=='carnet-ext').map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
const timeout=(p,ms)=>new Promise((res,rej)=>{const t=setTimeout(()=>rej(new Error('timeout')),ms);p.then(r=>{clearTimeout(t);res(r)},e=>{clearTimeout(t);rej(e)})});
self.addEventListener('fetch',e=>{
  const req=e.request;if(req.method!=='GET')return;const u=new URL(req.url);
  if(req.mode==='navigate'){
    e.respondWith(timeout(fetch(req),3500).then(r=>{const cp=r.clone();caches.open(V).then(c=>c.put('./index.html',cp));return r}).catch(()=>caches.match('./index.html')));return}
  const same=u.origin===location.origin,ext=EXT.includes(u.hostname);
  if(!same&&!ext)return;
  const store=ext?'carnet-ext':V;
  e.respondWith(caches.match(req).then(hit=>{
    const net=fetch(req).then(r=>{if(r.ok||r.type==='opaque'){const cp=r.clone();caches.open(store).then(c=>c.put(req,cp))}return r}).catch(()=>hit);
    return hit||net}));
});
