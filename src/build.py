# Construit l'appli installable (dossier pwa/) à partir de carnet-scores.html
import re, json, pathlib
SRC = (pathlib.Path(__file__).parent/'carnet-scores.html').read_text()
OUT = pathlib.Path(__file__).parent.parent
FB_VER = '10.12.2'
CFG = {
  "apiKey": "AIzaSyDrEE1r9YbUTE607SEWKPd_vPXX1PaFyTY",
  "authDomain": "carnet-des-scores.firebaseapp.com",
  "projectId": "carnet-des-scores",
  "storageBucket": "carnet-des-scores.firebasestorage.app",
  "messagingSenderId": "1094194182327",
  "appId": "1:1094194182327:web:4f74dd9bf1539e13e6b532"
}
s = SRC
def rep(a, b):
    global s
    assert a in s, 'introuvable: ' + a[:90]
    s = s.replace(a, b, 1)

# ---------- couche de synchro (script classique) ----------
rep("function save(){try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}}", r"""function save(){try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}pushChanges()}
/* ---------- Synchronisation de groupe ---------- */
const GROUP_KEY='carnet-group',SYNC_KEY='carnet-sync-v1';
const SYNC={state:'off',gid:null};
try{const gr=JSON.parse(localStorage.getItem(GROUP_KEY)||'null');if(gr&&gr.gid)SYNC.gid=gr.gid}catch(e){}
let synced=(()=>{try{return JSON.parse(localStorage.getItem(SYNC_KEY))}catch(e){return null}})()||{players:{},games:{}};
function saveSynced(){try{localStorage.setItem(SYNC_KEY,JSON.stringify(synced))}catch(e){}}
const strip=e=>{const{u,...r}=e;return JSON.stringify(r)};
function pushChanges(){
  if(!window.FB||!FB.ready()||!SYNC.gid)return;
  ['players','games'].forEach(col=>{const cur={};
    S[col].forEach(e=>{const j=strip(e);cur[e.id]=1;if(synced[col][e.id]!==j){e.u=Date.now();FB.put(col,e.id,{j:JSON.stringify(e),u:e.u,deleted:false});synced[col][e.id]=j}});
    Object.keys(synced[col]).forEach(id=>{if(!cur[id]){FB.put(col,id,{j:'',u:Date.now(),deleted:true});delete synced[col][id]}})});
  try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}
  saveSynced();
}
window.pushChanges=pushChanges;
let renderPending=false;
function softRender(){const busy=['round','wheel','reveal','chooser'].includes(UI.view)||(document.activeElement&&/INPUT|TEXTAREA/.test(document.activeElement.tagName));if(busy){renderPending=true;return}render()}
window.onRemote=(col,docs)=>{let changed=false;
  docs.forEach(d=>{const i=S[col].findIndex(e=>e.id===d.id);
    if(d.deleted){if(i>=0&&(S[col][i].u||0)<=(d.u||0)){S[col].splice(i,1);changed=true}delete synced[col][d.id];return}
    let e;try{e=JSON.parse(d.j)}catch(_){return}
    if(i<0){S[col].push(e);changed=true}
    else if((S[col][i].u||0)<(d.u||0)){S[col][i]=e;changed=true}
    else return;
    synced[col][d.id]=strip(e)});
  if(changed){try{localStorage.setItem(KEY,JSON.stringify(S))}catch(_){}saveSynced();softRender()}};
const SYNC_LABEL={off:'Non connecté',connecting:'Connexion…',online:'Synchronisé',offline:'Hors ligne, envoi au retour du réseau',error:'Erreur de synchronisation'};
window.syncStatus=st=>{SYNC.state=st;document.querySelectorAll('[data-sync-pill]').forEach(el=>{el.textContent=SYNC_LABEL[st]||st;el.dataset.state=st})};
function syncPill(){return `<span class="sync-pill" data-sync-pill data-state="${SYNC.state}">${SYNC_LABEL[SYNC.state]}</span>`}
async function groupId(code){const data=new TextEncoder().encode('carnet-scores:'+code.trim().toLowerCase());const h=await crypto.subtle.digest('SHA-256',data);return [...new Uint8Array(h)].map(b=>b.toString(16).padStart(2,'0')).join('')}
function startSync(){if(!SYNC.gid)return;const go=()=>window.FB&&FB.start(SYNC.gid);if(window.FB)go();else addEventListener('fb-ready',go,{once:true})}""")

# carte de synchro dans l'onglet Joueurs
rep('  <div class="card"><div><h3>Sauvegarde</h3>', r"""  <div class="card"><div class="row between"><h3>Groupe partagé</h3>${SYNC.gid?syncPill():''}</div>
    ${SYNC.gid?(UI.confirmLeave?`<p>Quitter le groupe ? Les parties restent sur ce téléphone mais ne seront plus partagées.</p><div class="row"><button class="btn danger" data-a="sync-leave">Quitter</button><button class="btn" data-a="sync-cancel">Rester</button></div>`
      :`<p class="muted small">Les joueurs et les parties sont partagés avec les téléphones du groupe.</p><div class="row"><button class="btn ghost" data-a="sync-ask-leave">Quitter le groupe</button></div>`)
    :`<p class="muted small">Entre le même code sur chaque téléphone pour partager joueurs et parties.</p><form class="row" data-f="sync-join" style="flex-wrap:nowrap"><input type="text" id="sync-code" placeholder="Code de groupe" autocomplete="off" autocapitalize="none" spellcheck="false"><button class="btn primary" type="submit">Rejoindre</button></form>${UI.syncErr?`<p class="err">${esc(UI.syncErr)}</p>`:''}`}
  </div>
  <div class="card"><div><h3>Sauvegarde</h3>""")
rep("document.addEventListener('submit',e=>{e.preventDefault();const f=e.target.dataset.f;", r"""document.addEventListener('submit',async e=>{e.preventDefault();const f=e.target.dataset.f;
  if(f==='sync-join'){const code=document.getElementById('sync-code').value;if(code.trim().length<6){UI.syncErr='Le code doit faire au moins 6 caractères.';render();return}
    try{SYNC.gid=await groupId(code)}catch(_){UI.syncErr='Impossible de créer le code sur ce navigateur.';render();return}
    try{localStorage.setItem(GROUP_KEY,JSON.stringify({gid:SYNC.gid}))}catch(_){}
    synced={players:{},games:{}};saveSynced();UI.syncErr='';window.syncStatus('connecting');startSync();render();return}""")
rep("A['setup-exp']=", """A['sync-ask-leave']=()=>{UI.confirmLeave=true;render()};
A['sync-cancel']=()=>{UI.confirmLeave=false;render()};
A['sync-leave']=()=>{window.FB&&FB.start(null);SYNC.gid=null;UI.confirmLeave=false;try{localStorage.removeItem(GROUP_KEY);localStorage.removeItem(SYNC_KEY)}catch(_){}synced={players:{},games:{}};window.syncStatus('off');render()};
A['setup-exp']=""")
rep("L'import remplace toutes les données actuelles.", "L'import remplace toutes les données actuelles${SYNC.gid?', pour tout le groupe':''}.")
# rendu différé après navigation
rep("function go(view,extra){", "function go(view,extra){renderPending=false;navPush(view,extra||{});")
# ---------- bouton retour Android ----------
rep("let renderPending=false;", r"""let renderPending=false;
const NAV=[],TRANSIENT=['round','reveal','wheel','chooser','setup'];let navRestoring=false,ignorePop=0;
function navSnap(){return{view:UI.view,gameId:UI.gameId,setup:UI.setup,draft:UI.draft,statGame:UI.statGame,statVar:UI.statVar,ch:UI.ch,wheel:UI.wheel,wheelBack:UI.wheelBack,revealStep:UI.revealStep,duel:0}}
function navPush(view,extra){if(navRestoring)return;
  if(view===UI.view&&(extra.gameId===undefined||extra.gameId===UI.gameId))return;
  if(TRANSIENT.includes(UI.view)&&!TRANSIENT.includes(view)){const top=NAV[NAV.length-1];
    if(top&&top.view===view&&(extra.gameId===undefined||top.gameId===extra.gameId)){NAV.pop();ignorePop++;history.back()}
    return}
  NAV.push(navSnap());history.pushState({n:NAV.length},'')}
addEventListener('popstate',()=>{if(ignorePop){ignorePop--;return}const prev=NAV.pop();if(!prev)return;
  try{clearTimeout(duelTimer);clearInterval(teamTimer)}catch(_){}
  if(UI.view==='chooser')resetChooser(true);
  navRestoring=true;const{view,...rest}=prev;go(view,rest);navRestoring=false});""")
# démarrage
rep("const boot=d=>{if(d&&d.UI)UI=d.UI;render()};", "const boot=d=>{if(d&&d.UI)UI=d.UI;render();startSync()};")
rep(".swconv{", """.sync-pill{font-size:.78rem;font-weight:700;padding:3px 10px;border-radius:99px;background:var(--surface-2);color:var(--ink-soft)}
.sync-pill[data-state="online"]{background:var(--good-soft);color:var(--good)}
.sync-pill[data-state="error"]{background:var(--danger-soft);color:var(--danger)}
.swconv{""")

# ---------- module Firebase ----------
base = f'https://www.gstatic.com/firebasejs/{FB_VER}'
module = f"""<script type="module">
import {{initializeApp}} from '{base}/firebase-app.js';
import {{getAuth,signInAnonymously,onAuthStateChanged}} from '{base}/firebase-auth.js';
import {{initializeFirestore,persistentLocalCache,persistentMultipleTabManager,doc,setDoc,collection,onSnapshot}} from '{base}/firebase-firestore.js';
const app=initializeApp({json.dumps(CFG)});
const auth=getAuth(app);
let db;try{{db=initializeFirestore(app,{{localCache:persistentLocalCache({{tabManager:persistentMultipleTabManager()}})}})}}catch(e){{db=initializeFirestore(app,{{}})}}
let user=null,gid=null,unsubs=[];
const status=s=>window.syncStatus&&window.syncStatus(s);
function stop(){{unsubs.forEach(u=>u());unsubs=[]}}
function subscribe(){{stop();if(!user||!gid)return;const seen={{}};
  ['players','games'].forEach(col=>unsubs.push(onSnapshot(collection(db,'groups',gid,col),{{includeMetadataChanges:true}},snap=>{{
    const docs=snap.docChanges().filter(c=>c.type!=='removed').map(c=>({{id:c.doc.id,...c.doc.data()}}));
    if(docs.length)window.onRemote(col,docs);
    status(snap.metadata.fromCache?(navigator.onLine?'connecting':'offline'):(snap.metadata.hasPendingWrites?'connecting':'online'));
    if(!seen[col]){{seen[col]=1;if(seen.players&&seen.games)window.pushChanges()}}
  }},err=>{{console.warn(err);status('error')}})))}}
window.FB={{
  ready:()=>!!user&&!!gid,
  put:(col,id,data)=>setDoc(doc(db,'groups',gid,col,id),data).catch(e=>{{console.warn(e);status('error')}}),
  start(g){{gid=g;stop();if(!gid){{status('off');return}}status(navigator.onLine?'connecting':'offline');
    if(user)subscribe();else signInAnonymously(auth).catch(()=>status(navigator.onLine?'error':'offline'))}}
}};
onAuthStateChanged(auth,u=>{{user=u;if(u&&gid)subscribe()}});
addEventListener('online',()=>{{if(gid){{status('connecting');if(!user)signInAnonymously(auth).catch(()=>status('error'))}}}});
addEventListener('offline',()=>{{if(gid)status('offline')}});
window.dispatchEvent(new Event('fb-ready'));
</script>
<script>if('serviceWorker' in navigator)addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{{}}));</script>"""

head = """<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#2541b2">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="icon-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Scores">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}*{-webkit-tap-highlight-color:transparent}</style>
"""
# séparer le contenu head (title/link/style) du body
i = s.index('<div class="wrap" id="app"></div>')
html = head + s[:i] + '</head><body>\n' + s[i:] + '\n' + module + '\n</body></html>\n'
OUT.mkdir(exist_ok=True)
(OUT / 'index.html').write_text(html)

(OUT / 'manifest.webmanifest').write_text(json.dumps({
  "name": "Carnet de Scores", "short_name": "Scores", "lang": "fr",
  "start_url": "./", "scope": "./", "display": "standalone", "orientation": "portrait",
  "background_color": "#f4f6fb", "theme_color": "#2541b2",
  "icons": [
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]}, ensure_ascii=False, indent=2))

import hashlib
ver = hashlib.sha1(html.encode()).hexdigest()[:8]
(OUT / 'sw.js').write_text(f"""// Carnet de Scores — fonctionnement hors ligne
const V='carnet-{ver}';
const SHELL=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./icon-180.png'];
const EXT=['www.gstatic.com','fonts.googleapis.com','fonts.gstatic.com'];
self.addEventListener('install',e=>{{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))}});
self.addEventListener('activate',e=>{{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('carnet-')&&k!==V&&k!=='carnet-ext').map(k=>caches.delete(k)))).then(()=>self.clients.claim()))}});
const timeout=(p,ms)=>new Promise((res,rej)=>{{const t=setTimeout(()=>rej(new Error('timeout')),ms);p.then(r=>{{clearTimeout(t);res(r)}},e=>{{clearTimeout(t);rej(e)}})}});
self.addEventListener('fetch',e=>{{
  const req=e.request;if(req.method!=='GET')return;const u=new URL(req.url);
  if(req.mode==='navigate'){{
    e.respondWith(timeout(fetch(req),3500).then(r=>{{const cp=r.clone();caches.open(V).then(c=>c.put('./index.html',cp));return r}}).catch(()=>caches.match('./index.html')));return}}
  const same=u.origin===location.origin,ext=EXT.includes(u.hostname);
  if(!same&&!ext)return;
  const store=ext?'carnet-ext':V;
  e.respondWith(caches.match(req).then(hit=>{{
    const net=fetch(req).then(r=>{{if(r.ok||r.type==='opaque'){{const cp=r.clone();caches.open(store).then(c=>c.put(req,cp))}}return r}}).catch(()=>hit);
    return hit||net}}));
}});
""")
print('ok', ver, len(html))
