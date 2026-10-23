/* ---------- ATLAS VIVO: MapLibre GL + relieve Copernicus + capas Escritura · Arqueología · Hoy ---------- */
/* Un solo mapa WebGL compartido: cada diapositiva con mapa lo toma al activarse; el atlas completo lo
   abre a pantalla completa. Si WebGL no está disponible, queda el mapa TikZ con sus puntos tocables. */
const ATL={p:null,ok:null,map:null,host:null,data:null,base:null,rel:null,mk:[],ev:null,capas:{relato:true,arq:true,hoy:false,rutas:false},fondo:'relieve',
  popup:null,full:false,tramo:0,play:0,lug:{}};
const ATL_BASE='abraham/';
/* íconos de trazo, sin emojis */
const ICO={
  relieve:'<svg viewBox="0 0 24 24"><path d="M3 18l5-8 4 6 3-4 6 6z"/><path d="M4 21h16"/></svg>',
  satelite:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M4 12h16M12 4c3 3 3 13 0 16M12 4c-3 3-3 13 0 16"/></svg>',
  calles:'<svg viewBox="0 0 24 24"><path d="M3 6l6-2 6 2 6-2v14l-6 2-6-2-6 2z"/><path d="M9 4v14M15 6v14"/></svg>',
  arq:'<svg viewBox="0 0 24 24"><path d="M4 20l7-7"/><path d="M11 13l2-2 4 4-2 2z"/><path d="M14 6l4 4"/><path d="M13 7l3-3 4 4-3 3"/></svg>',
  hoy:'<svg viewBox="0 0 24 24"><path d="M12 21s-6-5.3-6-11a6 6 0 0 1 12 0c0 5.7-6 11-6 11z"/><circle cx="12" cy="10" r="2.2"/></svg>',
  atlas:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/></svg>',
  libro:'<svg viewBox="0 0 24 24"><path d="M4 4h6a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4z"/><path d="M20 4h-6a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h7z"/></svg>',
  lista:'<svg viewBox="0 0 24 24"><path d="M5 7h14M5 12h14M5 17h14"/></svg>',
  tema:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 0 1 0 16z" fill="currentColor" stroke="none"/></svg>',
  full:'<svg viewBox="0 0 24 24"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>',
  cerrar:'<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  volver:'<svg viewBox="0 0 24 24"><path d="M14 6l-6 6 6 6"/></svg>',
  mas:'<svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>',
  menos:'<svg viewBox="0 0 24 24"><path d="M5 12h14"/></svg>',
  centrar:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="7"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/></svg>',
  altar:'<svg viewBox="0 0 24 24"><path d="M12 3c2 2.5 3 4.5 1.5 6.5a2 2 0 0 1-3 0C9 7.5 10 5.5 12 3z"/><path d="M8 13h8M6 17h12M4 21h16"/></svg>',
  mapa:'<svg viewBox="0 0 24 24"><path d="M3 6l6-2 6 2 6-2v14l-6 2-6-2-6 2z"/><path d="M9 4v14M15 6v14"/></svg>',
  texto:'<svg viewBox="0 0 24 24"><path d="M5 5h14M12 5v14M8 19h8"/></svg>',
  play:'<svg viewBox="0 0 24 24"><path d="M7 5l12 7-12 7z" fill="currentColor" stroke="none"/></svg>',
  pausa:'<svg viewBox="0 0 24 24"><path d="M8 5v14M16 5v14"/></svg>',
  ext:'<svg viewBox="0 0 24 24"><path d="M14 5h5v5M19 5l-8 8"/><path d="M19 14v5H5V5h5"/></svg>',
  gmaps:'<svg viewBox="0 0 24 24"><path d="M12 22s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="10" r="2.6"/></svg>',
  ruta:'<svg viewBox="0 0 24 24"><circle cx="5" cy="19" r="2"/><circle cx="19" cy="5" r="2"/><path d="M7 19h6a4 4 0 0 0 0-8h-2a4 4 0 0 1 0-8h6"/></svg>'};
/* Google Maps: URLs oficiales (Maps URLs), sin clave. Lugar, satélite y cómo llegar. */
const GM={lugar:L=>`https://www.google.com/maps/search/?api=1&query=${L.ll[0]},${L.ll[1]}`,
  sat:L=>`https://www.google.com/maps/@?api=1&map_action=map&center=${L.ll[0]},${L.ll[1]}&zoom=17&basemap=satellite`,
  street:L=>`https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${L.ll[0]},${L.ll[1]}`,
  dir:(a,b)=>`https://www.google.com/maps/dir/?api=1&origin=${a[0]},${a[1]}&destination=${b[0]},${b[1]}&travelmode=walking`};
const gmBtn=(href,txt,cls='')=>`<a class="gm ${cls}" href="${href}" target="_blank" rel="noopener">${ico('gmaps')} ${txt}</a>`;
const ico=k=>`<span class="ico" aria-hidden="true">${ICO[k]}</span>`;
const MLV='4.7.1';
function atlasCargar(){ if(ATL.p) return ATL.p;
  const tieneGL=(()=>{ try{ const c=document.createElement('canvas'); return !!(c.getContext('webgl2')||c.getContext('webgl')); }catch(_){ return false; } })();
  if(!tieneGL){ ATL.ok=false; return ATL.p=Promise.reject(new Error('sin WebGL')); }
  ATL.p=new Promise((res,rej)=>{ if(window.maplibregl) return res();
      const css=document.createElement('link'); css.rel='stylesheet'; css.href=ATL_BASE+'vendor/maplibre-gl.css'; document.head.append(css);
      const js=document.createElement('script'); js.src=ATL_BASE+'vendor/maplibre-gl.js'; js.onload=res; js.onerror=rej; document.head.append(js); })
    .then(()=>Promise.all(['mapa/base.json','mapa/atlas.json','relieve/indice.json'].map(u=>fetch(ATL_BASE+u).then(r=>{ if(!r.ok) throw new Error(u); return r.json(); }))))
    .then(([b,a,r])=>{ ATL.base=b; ATL.data=a; ATL.rel=r; a.lugares.forEach(l=>{ ATL.lug[l.id]=l; if(l.site) ATL.lug['s:'+l.site]=l; }); ATL.ok=true; })
    .catch(e=>{ ATL.ok=false; throw e; });
  return ATL.p; }

const km=(a,b)=>{ const R=6371,r=Math.PI/180,dl=(b[0]-a[0])*r,dg=(b[1]-a[1])*r; return 2*R*Math.asin(Math.sqrt(Math.sin(dl/2)**2+Math.cos(a[0]*r)*Math.cos(b[0]*r)*Math.sin(dg/2)**2)); };
const kmTramo=t=>t.pts.reduce((s,p,i)=>i?s+km(t.pts[i-1],p):0,0);
const fmtKm=v=>(v>=1000?Math.round(v/10)*10:Math.round(v)).toLocaleString('es-CL');
const lonlat=p=>[p[1],p[0]];
function curva(P,n=8){ /* Catmull-Rom: trazos suaves en lugar de quebrados */
  if(P.length<3) return P.map(lonlat); const o=[];
  for(let i=0;i<P.length-1;i++){ const p0=P[Math.max(i-1,0)],p1=P[i],p2=P[i+1],p3=P[Math.min(i+2,P.length-1)];
    for(let k=0;k<n;k++){ const t=k/n,t2=t*t,t3=t2*t; o.push([1,0].map(j=>.5*((2*p1[j])+(-p0[j]+p2[j])*t+(2*p0[j]-5*p1[j]+4*p2[j]-p3[j])*t2+(-p0[j]+3*p1[j]-3*p2[j]+p3[j])*t3))); } }
  o.push(lonlat(P[P.length-1])); return o; }

/* ficha del lugar: Escritura · Arqueología · Hoy */
function lugarDe(key){ return ATL.lug['s:'+key]||ATL.lug[key]||null; }
function datosLugar(key){ const L=lugarDe(key), S=sites[key];
  if(L) return L;
  return S?{id:key,site:key,n:S[2],ll:[S[0],S[1]],k:'biblico',actual:'',biblia:[],arq:[S[3]],hoy:''}:null; }
const KIND={biblico:'Lugar bíblico',arqueo:'Hallazgo arqueológico',hoy:'Hoy'};
function fichaHTML(L,tab){ const usa=L.site?SITEUSE[L.site]||[]:[];
  const B=(L.biblia||[]).map(([r,t])=>`<blockquote class="pp-q"><cite>${esc(r)}</cite>${esc(t)}</blockquote>`).join('')||'<p class="pp-v">Sin pasaje directo: es contexto para el relato.</p>';
  const A=(L.arq||[]).map(t=>`<p>${esc(t)}</p>`).join('')||'<p class="pp-v">—</p>';
  const H=L.hoy?`<p>${esc(L.hoy)}</p>`:'<p class="pp-v">—</p>';
  const Bb=(L.bib||[]).map(([f,t])=>`<p>${esc(t)}</p><p class="pp-cit">— ${esc(f)}</p>`).join('');
  const tabs=[['esc','Escritura',B],['arq','Arqueología',A],['hoy','Hoy',H+gmaps(L)],...(Bb?[['bib','Biblioteca',Bb]]:[])];
  const t0=tab||(L.k==='arqueo'?'arq':L.k==='hoy'?'hoy':'esc');
  return `<div class="pp k-${L.k}"><div class="pp-h"><span class="pp-k">${KIND[L.k]||'Lugar'}</span><b>${esc(L.n)}</b>${L.he?`<span class="pp-he" lang="he" dir="rtl">${esc(L.he)}</span>`:''}${L.actual?`<small>${esc(L.actual)}</small>`:''}</div>
    <div class="pp-tabs" role="tablist">${tabs.map(([k,t])=>`<button type="button" role="tab" data-t="${k}" aria-selected="${k===t0}">${t}</button>`).join('')}</div>
    ${tabs.map(([k,,c])=>`<div class="pp-p" data-p="${k}" ${k===t0?'':'hidden'}>${c}</div>`).join('')}
    <div class="pp-gmbar">${gmBtn(GM.lugar(L),'Visitar hoy en Google Maps','principal')}${gmBtn(GM.sat(L),'Satélite')}${gmBtn(GM.street(L),'Street View')}</div>
    <div class="pp-f"><button type="button" data-ficha="${esc(L.site||L.id)}">Ficha completa</button><button type="button" data-sat="${esc(L.site||L.id)}">${ico('hoy')} Ver hoy aquí</button>${usa.slice(0,3).map(u=>`<button type="button" data-goto="${u}">Hito ${u}</button>`).join('')}</div></div>`; }
/* enlaces oficiales de Google Maps (URLs públicas de Maps, sin API) */
function gmaps(L){ return `<div class="pp-gm">${gmBtn(GM.lugar(L),'Abrir en Google Maps')}${gmBtn(GM.sat(L),'Satélite en Google Maps')}${gmBtn(GM.street(L),'Street View')}</div>`; }
function tramoHTML(t){ const T=ATL.data.tramos, d=kmTramo(t);
  return `<div class="pp k-tramo"><div class="pp-h"><span class="pp-k">Tramo ${t.n} de ${T.length} · ≈ ${fmtKm(d)} km</span><b>${esc(t.de)} → ${esc(t.a)}</b></div>
    <blockquote class="pp-q"><cite>${esc(t.ref)}</cite>${esc(t.txt)}</blockquote><div class="pp-sub">Camino y arqueología</div><p>${esc(t.arq)}</p>
    ${(t.bib||[]).length?`<div class="pp-sub">Biblioteca de Primera Línea</div>${t.bib.map(([f,x])=>`<p>${esc(x)}</p><p class="pp-cit">— ${esc(f)}</p>`).join('')}`:''}
    <div class="pp-gmbar">${gmBtn(GM.dir(t.pts[0],t.pts[t.pts.length-1]),'Recorrer hoy en Google Maps (a pie)','principal')}</div>
    <div class="pp-f"><button type="button" data-tr="${t.n-1}" ${t.n>1?'':'disabled'}>← Estación ${t.n-1||''}</button><button type="button" data-lug="${esc(t.site)}">${esc(t.a)}</button>${t.hito?`<button type="button" data-goto="${t.hito}">Leer el hito ${t.hito}</button>`:''}<button type="button" data-tr="${t.n+1}" ${t.n<T.length?'':'disabled'}>Estación ${t.n<T.length?t.n+1:''} →</button></div></div>`; }
function cablear(root){ root.querySelectorAll('.pp-tabs button').forEach(b=>b.onclick=()=>{ const pp=b.closest('.pp'); pp.querySelectorAll('.pp-tabs button').forEach(x=>x.setAttribute('aria-selected',x===b)); pp.querySelectorAll('.pp-p').forEach(p=>p.hidden=p.dataset.p!==b.dataset.t); if(root.closest('.maplibregl-popup')) ajustarPopup(); });
  root.querySelectorAll('[data-ficha]').forEach(b=>b.onclick=()=>abrirLugar(b.dataset.ficha,b));
  root.querySelectorAll('[data-goto]').forEach(b=>b.onclick=()=>{ atlasCerrar(); closeDrawer(); go(+b.dataset.goto); });
  root.querySelectorAll('[data-tr]').forEach(b=>b.onclick=()=>atlasTramo(+b.dataset.tr));
  root.querySelectorAll('[data-lug]').forEach(b=>b.onclick=()=>atlasLugar(b.dataset.lug));
  root.querySelectorAll('[data-sat]').forEach(b=>b.onclick=()=>verHoy(b.dataset.sat)); }
/* «Ver hoy»: el mismo lugar en la imagen satelital actual, muy de cerca */
function verHoy(key){ const L=datosLugar(key); if(!L) return; closeDrawer(); const go_=()=>{ atlasFondo('satelite'); ATL.capas.hoy=true; atlasCapas();
    ATL.map.flyTo({center:lonlat(L.ll),zoom:15.2,duration:1600}); atlasPopLugar(key,'hoy'); };
  if(!ATL.full&&ATL.host&&ATL.host.clientWidth<700){ atlasAbrir(); }
  ATL.listo?go_():(atlasCargar().then(()=>{ atlasCrear(); ATL.map.once('load',go_); })); }
function abrirLugar(key,from){ const L=datosLugar(key); if(!L) return;
  const usa=L.site?SITEUSE[L.site]||[]:[], A=L.site?(DATA.altars||{})[L.site]:null;
  openDrawer(`<div class="era">${KIND[L.k]||'Lugar'}${A?` · altar ${A.n}`:''}</div><h3 class="ref" id="dref">${esc(L.n)}</h3>${L.he?`<div class="he" lang="he" dir="rtl">${esc(L.he)}</div>`:''}
    ${L.actual?`<div class="src">${esc(L.actual)} · ${L.ll[0].toFixed(3).replace('.',',')}° N, ${L.ll[1].toFixed(3).replace('.',',')}° E</div>`:''}
    <div class="lab">Escritura</div>${(L.biblia||[]).map(([r,t])=>`<blockquote><b>${esc(r)}</b> ${esc(t)}</blockquote>`).join('')||'<p>—</p>'}
    ${A?`<div class="lab">Altar ${A.n} · ${esc(A.ref)}</div><p><b>${esc(A.tr)}</b> — ${esc(A.mean)}</p><p><b>Atributo de Dios:</b> ${esc(A.attr)}</p>`:''}
    <div class="lab">Arqueología</div>${(L.arq||[]).map(t=>`<p>${esc(t)}</p>`).join('')}
    <div class="lab">Hoy</div><p>${esc(L.hoy||'—')}</p>${gmaps(L)}
    ${(L.bib||[]).length?`<div class="lab">Biblioteca de Primera Línea</div>${L.bib.map(([f,t])=>`<p>${esc(t)}</p><p class="src">${esc(f)}</p>`).join('')}`:''}${(L.fuentes||[]).length?`<div class="lab">Fuentes</div>${L.fuentes.map(f=>`<p class="src">${esc(f)}</p>`).join('')}`:''}
    <p class="pp-gmbar">${gmBtn(GM.lugar(L),'Visitar hoy en Google Maps','principal')}${gmBtn(GM.sat(L),'Satélite')}${gmBtn(GM.street(L),'Street View')}</p>
    <p><button type="button" class="vermapa" data-lug="${esc(L.site||L.id)}">Ver en el atlas</button></p>
    ${usa.length?`<div class="lab">Aparece en</div><div class="see" style="border:0;padding:0">${usa.map(u=>`<button type="button" data-goto="${u}"><span>${u}</span>${esc(events[u-1].title)}</button>`).join('')}</div>`:''}`,
    'c'+(events[cur-1]?events[cur-1].era:7),from);
  $('#dbody').querySelectorAll('[data-goto]').forEach(bt=>bt.onclick=()=>{ closeDrawer(); atlasCerrar(); go(+bt.dataset.goto); });
  $('#dbody').querySelectorAll('.vermapa').forEach(bt=>bt.onclick=()=>{ closeDrawer(); atlasLugar(bt.dataset.lug); }); }

/* ---------- construcción del mapa ---------- */
function atlasCrear(){ if(ATL.map) return ATL.map;
  const host=el('div',{class:'atl'}), cont=el('div',{class:'atl-map'});
  const bar=el('div',{class:'atl-capas',role:'group','aria-label':'Capas del mapa'});
  const fondo=el('div',{class:'atl-fondo',role:'radiogroup','aria-label':'Mapa base'});
  [['relieve','Relieve'],['satelite','Satélite'],['calles','Calles']].forEach(([k,t])=>{ const b=el('button',{type:'button','data-fondo':k,role:'radio','aria-checked':ATL.fondo===k,title:t}); b.innerHTML=`${ico(k)} ${t}`; b.onclick=()=>atlasFondo(k); fondo.append(b); });
  [['relato','Relato'],['arq','Arqueología'],['hoy','Hoy'],['rutas','Rutas']].forEach(([k,t])=>{ const b=el('button',{type:'button','data-capa':k,'aria-pressed':ATL.capas[k]}); b.textContent=t; b.onclick=()=>{ ATL.capas[k]=!ATL.capas[k]; b.setAttribute('aria-pressed',ATL.capas[k]); atlasCapas(); }; bar.append(b); });
  bar.prepend(fondo);
  const tools=el('div',{class:'atl-tools'});
  const mkb=(t,l,f)=>{ const b=el('button',{type:'button','aria-label':l,title:l}); b.innerHTML=t; b.onclick=f; tools.append(b); return b; };
  mkb(ICO.mas,'Acercar',()=>ATL.map.zoomIn()); mkb(ICO.menos,'Alejar',()=>ATL.map.zoomOut()); mkb(ICO.centrar,'Volver a la vista del hito',()=>atlasVista(ATL.ev,true));
  ATL.btnFull=mkb(ICO.full,'Abrir el atlas completo',()=>ATL.full?atlasCerrar():atlasAbrir());
  const leyenda=el('div',{class:'atl-ley'}); leyenda.innerHTML='<span><i class="lg-b"></i>Lugar bíblico</span><span><i class="lg-a"></i>Arqueología</span><span><i class="lg-h"></i>Hoy</span><span><i class="lg-r"></i>Camino</span><span><i class="lg-v"></i>Ruta antigua</span>';
  const cred=el('div',{class:'atl-cred'}); ATL.cred=cred;
  const paso=el('div',{class:'atl-paso',hidden:''}); paso.innerHTML=`<button type="button" data-p="-1" aria-label="Estación anterior">${ICO.volver}</button><span>Estación <b>— / —</b></span><button type="button" data-p="1" aria-label="Estación siguiente"><svg viewBox="0 0 24 24"><path d="M10 6l6 6-6 6"/></svg></button><button type="button" class="atl-play" aria-pressed="false">${ICO.play}</button>`;
  paso.querySelectorAll('[data-p]').forEach(b=>b.onclick=()=>{ atlasPlay(false); const T=ATL.data.tramos, n=Math.max(1,Math.min(T.length,(ATL.tramo||0)+(+b.dataset.p))); atlasTramo(n); });
  paso.querySelector('.atl-play').onclick=()=>atlasPlay(!ATL.play); ATL.paso=paso; host.append(paso);
  host.append(cont,bar,tools,leyenda,cred); ATL.host=host;
  const st={version:8,sources:{
      sat:{type:'raster',tiles:['https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2021_3857/default/g/{z}/{y}/{x}.jpg'],tileSize:256,maxzoom:15},
      osm:{type:'raster',tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,maxzoom:19}},
    layers:[{id:'mar',type:'background',paint:{'background-color':'#76a4c8'}},
      {id:'sat',type:'raster',source:'sat',layout:{visibility:'none'},paint:{'raster-fade-duration':200}},
      {id:'osm',type:'raster',source:'osm',layout:{visibility:'none'},paint:{'raster-fade-duration':200}}]};
  ATL.rel.forEach((r,k)=>{ st.sources['rel'+k]={type:'image',url:ATL_BASE+r.src.replace(/^abraham\//,''),coordinates:r.coords};
    st.layers.push({id:'rel'+k,type:'raster',source:'rel'+k,...(r.nivel==='levante'?{minzoom:5.6}:{}),paint:{'raster-fade-duration':180,'raster-contrast':.04}}); });
  const B=ATL.base, fc=f=>({type:'geojson',data:f});
  st.sources.lagos=fc(B.lagos); st.sources.rios=fc(B.rios); st.sources.costa=fc(B.costa); st.sources.fronteras=fc(B.fronteras);
  st.sources.ruta=fc({type:'FeatureCollection',features:ATL.data.tramos.map(t=>({type:'Feature',id:t.n,properties:{n:t.n,v:t.vuelta?1:0},geometry:{type:'LineString',coordinates:curva(t.pts)}}))});
  st.sources.trazo=fc({type:'FeatureCollection',features:[]});
  const RT=[...(ATL.data.rutas||[]),...ATL.data.tramos.filter(t=>t.alt).map(t=>({n:`Variante del tramo ${t.n}`,alt:1,nota:'Ruta alternativa por el Éufrates, Carquemis, Alepo y el valle del Orontes.',pts:t.alt}))];
  st.sources.rutas=fc({type:'FeatureCollection',features:RT.map((r,i)=>({type:'Feature',id:i+1,properties:{n:r.n,alt:r.alt?1:0},geometry:{type:'LineString',coordinates:curva(r.pts)}}))}); ATL.rutasL=RT;
  const cfx=[...B.ciudades.map(c=>({n:c.n,c:c.c})),...(ATL.data.ciudades_extra||[]).map(([n,la,lo])=>({n,c:[lo,la]}))];
  st.sources.ciudades=fc({type:'FeatureCollection',features:cfx.map(c=>({type:'Feature',properties:{n:c.n},geometry:{type:'Point',coordinates:c.c}}))});
  st.layers.push(
    {id:'lagos',type:'fill',source:'lagos',filter:['==',['get','hoy'],0],paint:{'fill-color':'#8dbadc','fill-outline-color':'#3d78a8'}},
    {id:'lagos-hoy',type:'fill',source:'lagos',filter:['==',['get','hoy'],1],layout:{visibility:'none'},paint:{'fill-color':'#7fb2dc','fill-opacity':.9}},
    {id:'costa',type:'line',source:'costa',paint:{'line-color':'#3f6f94','line-width':['interpolate',['linear'],['zoom'],4,.5,9,1.2],'line-opacity':.75}},
    {id:'rios',type:'line',source:'rios',filter:['==',['get','hoy'],0],layout:{'line-cap':'round','line-join':'round'},
      paint:{'line-color':'#2f7fc0','line-width':['interpolate',['linear'],['zoom'],4,['case',['<=',['get','r'],4],1.4,.7],9,['case',['<=',['get','r'],4],3,1.6]],'line-opacity':['case',['==',['get','esq'],1],.75,.95]}},
    {id:'rios-hoy',type:'line',source:'rios',filter:['==',['get','hoy'],1],layout:{visibility:'none'},paint:{'line-color':'#1f6fae','line-width':1.2,'line-dasharray':[2,1.5]}},
    {id:'fronteras',type:'line',source:'fronteras',layout:{visibility:'none','line-join':'round'},paint:{'line-color':'#7a2f3b','line-width':['interpolate',['linear'],['zoom'],4,.8,9,1.6],'line-dasharray':[4,2],'line-opacity':.8}},
    {id:'ciudades',type:'circle',source:'ciudades',layout:{visibility:'none'},paint:{'circle-radius':3.2,'circle-color':'#2f4f6f','circle-stroke-color':'#fff','circle-stroke-width':1.2}},
    {id:'rutas',type:'line',source:'rutas',layout:{visibility:'none','line-cap':'round','line-join':'round'},
      paint:{'line-color':['case',['==',['get','alt'],1],'#7a2f3b','#1f4e8c'],'line-width':['interpolate',['linear'],['zoom'],4,2.2,9,4],'line-dasharray':[1.2,1.4],'line-opacity':['case',['boolean',['feature-state','hov'],false],1,.85]}},
    {id:'rutas-toque',type:'line',source:'rutas',layout:{visibility:'none'},paint:{'line-color':'#000','line-opacity':0,'line-width':14}},
    {id:'ruta-casco',type:'line',source:'ruta',layout:{'line-cap':'round','line-join':'round'},paint:{'line-color':'#fff8e8','line-width':['interpolate',['linear'],['zoom'],4,4.5,9,8],'line-opacity':.75}},
    {id:'ruta',type:'line',source:'ruta',layout:{'line-cap':'round','line-join':'round'},
      paint:{'line-color':['case',['boolean',['feature-state','sel'],false],'#d6aa40',['boolean',['feature-state','hov'],false],'#c4612f','#9a4a2a'],
        'line-width':['interpolate',['linear'],['zoom'],4,['case',['boolean',['feature-state','sel'],false],4.5,2.4],9,['case',['boolean',['feature-state','sel'],false],8,4.2]]},filter:['==',['get','v'],0]},
    {id:'ruta-v',type:'line',source:'ruta',filter:['==',['get','v'],1],layout:{'line-join':'round'},
      paint:{'line-color':['case',['boolean',['feature-state','sel'],false],'#d6aa40',['boolean',['feature-state','hov'],false],'#c4612f','#9a4a2a'],
        'line-width':['interpolate',['linear'],['zoom'],4,['case',['boolean',['feature-state','sel'],false],4,2],9,['case',['boolean',['feature-state','sel'],false],7,3.6]],'line-dasharray':[1.4,1.2]}},
    {id:'ruta-toque',type:'line',source:'ruta',paint:{'line-color':'#000','line-opacity':0,'line-width':18}},
    {id:'trazo-casco',type:'line',source:'trazo',layout:{'line-cap':'round','line-join':'round'},paint:{'line-color':'#fff8e8','line-width':6,'line-opacity':.7}},
    {id:'trazo',type:'line',source:'trazo',layout:{'line-cap':'round','line-join':'round'},paint:{'line-color':['coalesce',['get','col'],'#9a4a2a'],'line-width':['case',['boolean',['feature-state','hov'],false],5,3.4]}},
    {id:'trazo-toque',type:'line',source:'trazo',paint:{'line-color':'#000','line-opacity':0,'line-width':18}});
  const map=new maplibregl.Map({container:cont,style:st,center:[38,33],zoom:5,minZoom:4.2,maxZoom:17,maxBounds:[[28.05,27.05],[50.95,39.95]],attributionControl:false,
    cooperativeGestures:false,dragRotate:false,pitchWithRotate:false,touchPitch:false,renderWorldCopies:false,fadeDuration:150,locale:{
      'CooperativeGesturesHandler.WindowsHelpText':'Usa Ctrl + rueda para acercar o alejar el mapa','CooperativeGesturesHandler.MacHelpText':'Usa ⌘ + rueda para acercar o alejar el mapa','CooperativeGesturesHandler.MobileHelpText':'Usa dos dedos para mover el mapa'}});
  map.touchZoomRotate.disableRotation();
  ATL.map=map;
  let hov=null;
  map.on('mousemove','ruta-toque',e=>{ const f=e.features[0]; if(hov!==f.id){ if(hov!==null) map.setFeatureState({source:'ruta',id:hov},{hov:false}); hov=f.id; map.setFeatureState({source:'ruta',id:hov},{hov:true}); } map.getCanvas().style.cursor='pointer';
    const t=ATL.data.tramos[f.id-1]; ATL.tip.innerHTML=`<b>Tramo ${t.n}</b> ${esc(t.de)} → ${esc(t.a)} · <i>${esc(t.ref)}</i>`; ATL.tip.style.left=e.point.x+'px'; ATL.tip.style.top=e.point.y+'px'; ATL.tip.hidden=false; });
  map.on('mouseleave','ruta-toque',()=>{ if(hov!==null) map.setFeatureState({source:'ruta',id:hov},{hov:false}); hov=null; map.getCanvas().style.cursor=''; ATL.tip.hidden=true; });
  map.on('click','ruta-toque',e=>{ ATL.tip.hidden=true; atlasTramo(e.features[0].id,e.lngLat); });
  /* caminos dibujados en el mapa de cada hito: al tocarlos se abre el tramo correspondiente o la nota del camino */
  let hovT=null;
  map.on('mousemove','trazo-toque',e=>{ const f=e.features[0]; if(hovT!==f.id){ if(hovT!==null) map.setFeatureState({source:'trazo',id:hovT},{hov:false}); hovT=f.id; map.setFeatureState({source:'trazo',id:hovT},{hov:true}); } map.getCanvas().style.cursor='pointer';
    ATL.tip.innerHTML=`<b>${esc(f.properties.lab||'Camino')}</b>${f.properties.tramo?` · tramo ${f.properties.tramo}`:''} · toca para ver`; ATL.tip.style.left=e.point.x+'px'; ATL.tip.style.top=e.point.y+'px'; ATL.tip.hidden=false; });
  map.on('mouseleave','trazo-toque',()=>{ if(hovT!==null) map.setFeatureState({source:'trazo',id:hovT},{hov:false}); hovT=null; map.getCanvas().style.cursor=''; ATL.tip.hidden=true; });
  map.on('click','trazo-toque',e=>{ ATL.tip.hidden=true; const f=e.features[0]; if(f.properties.tramo) return atlasTramo(f.properties.tramo,e.lngLat);
    const ev=events[cur-1]||{}; if(ATL.popup) ATL.popup.remove();
    const h=`<div class="pp k-tramo"><div class="pp-h"><span class="pp-k">Camino · hito ${cur}</span><b>${esc(f.properties.lab||ev.title||'Camino')}</b></div><p style="padding:10px 14px 4px">${esc(plain(ev.text||''))}</p>${(ev.refs||[]).length?`<div class="pp-f">${ev.refs.map(r=>`<button type="button" data-refpp="${r}">${esc(refs[r].label)}</button>`).join('')}</div>`:''}</div>`;
    if(ATL.host.clientWidth<560){ openDrawer(h,'c'+(ev.era||7)); $('#dbody').querySelectorAll('[data-refpp]').forEach(b=>b.onclick=()=>openRef(b.dataset.refpp,b)); return; }
    ATL.popup=new maplibregl.Popup(popupOpts(e.lngLat,{maxWidth:'360px'})).setLngLat(e.lngLat).setHTML(h).addTo(map); ATL.popup.getElement().querySelectorAll('[data-refpp]').forEach(b=>b.onclick=()=>openRef(b.dataset.refpp,b)); ajustarPopup(); });
  /* fondo del mapa: el lugar más cercano (hasta 30 px) se abre; si no hay ninguno, un aviso breve */
  map.on('click',e=>{ if(map.queryRenderedFeatures(e.point,{layers:['ruta-toque','trazo-toque','rutas-toque','ciudades'].filter(l=>map.getLayer(l))}).length) return;
    let best=null,bd=30; ATL.data.lugares.forEach(L=>{ if(L.k==='hoy'&&!ATL.capas.hoy) return; if(L.k==='arqueo'&&!ATL.capas.arq) return; const q=map.project(lonlat(L.ll)), d=Math.hypot(q.x-e.point.x,q.y-e.point.y); if(d<bd){ bd=d; best=L; } });
    if(best) atlasPopLugar(best.site||best.id); else if(ATL.popup){ ATL.popup.remove(); ATL.popup=null; } });
  /* teselas externas (satélite, calles) bloqueadas: avisar en vez de dejar el mapa en blanco */
  map.on('error',e=>{ const src=e&&e.sourceId; if(src==='sat'||src==='osm'){ if(!ATL.avisado){ ATL.avisado=true; const n=el('div',{class:'atl-aviso'}); n.innerHTML=`${ico('satelite')} ${src==='sat'?'La imagen satelital':'El mapa de calles'} no se puede cargar aquí (esta vista previa bloquea servidores externos). En el sitio publicado sí se ve. <button type="button">Volver al relieve</button>`; n.querySelector('button').onclick=()=>{ n.remove(); ATL.avisado=false; atlasFondo('relieve'); }; ATL.host.append(n); } } });
  map.on('mouseenter','rutas-toque',e=>{ map.getCanvas().style.cursor='pointer'; });
  map.on('mousemove','rutas-toque',e=>{ const r=ATL.rutasL[e.features[0].id-1]; ATL.tip.innerHTML=`<b>${esc(r.n)}</b>`; ATL.tip.style.left=e.point.x+'px'; ATL.tip.style.top=e.point.y+'px'; ATL.tip.hidden=false; });
  map.on('mouseleave','rutas-toque',()=>{ map.getCanvas().style.cursor=''; ATL.tip.hidden=true; });
  map.on('click','rutas-toque',e=>{ const r=ATL.rutasL[e.features[0].id-1]; if(ATL.popup) ATL.popup.remove();
    const h=`<div class="pp k-ruta"><div class="pp-h"><span class="pp-k">Ruta antigua</span><b>${esc(r.n)}</b>${r.he?`<span class="pp-he" lang="he" dir="rtl">${esc(r.he)}</span>`:''}</div><p style="padding:10px 14px 4px">${esc(r.nota)}</p><p class="pp-cit" style="padding:0 14px 12px">— Curso «Explorando la Tierra Bíblica de Israel»</p></div>`;
    if(ATL.host.clientWidth<560){ openDrawer(h,'c7'); return; } ATL.popup=new maplibregl.Popup(popupOpts(e.lngLat,{maxWidth:'340px'})).setLngLat(e.lngLat).setHTML(h).addTo(map); ajustarPopup(); });
  map.on('click','ciudades',e=>{ const f=e.features[0]; new maplibregl.Popup({closeButton:true,className:'atl-pop',maxWidth:'260px'}).setLngLat(f.geometry.coordinates).setHTML(`<div class="pp k-hoy"><div class="pp-h"><span class="pp-k">Ciudad actual</span><b>${esc(f.properties.n)}</b></div></div>`).addTo(map); });
  map.on('zoom',()=>atlasEtiquetas()); map.on('moveend',()=>atlasEtiquetas());
  ATL.tip=el('div',{class:'atl-tip',hidden:''}); host.append(ATL.tip);
  map.on('load',()=>{ ATL.listo=true; map.resize(); atlasCapas(); if(ATL.ev) atlasVista(ATL.ev,false); });
  let rw=0; new ResizeObserver(()=>{ const w=host.clientWidth; if(!w) return; map.resize(); if(Math.abs(w-rw)>40&&ATL.ev&&ATL.listo) atlasVista(ATL.ev,false); rw=w; }).observe(host);
  return map; }

function atlasCapas(){ const m=ATL.map; if(!m||!ATL.listo) return; const C=ATL.capas, vis=v=>v?'visible':'none';
  const F=ATL.fondo; ATL.rel.forEach((r,k)=>m.setLayoutProperty('rel'+k,'visibility',vis(F==='relieve')));
  m.setLayoutProperty('sat','visibility',vis(F==='satelite')); m.setLayoutProperty('osm','visibility',vis(F==='calles'));
  ['costa','lagos','rios'].forEach(id=>m.setLayoutProperty(id,'visibility',vis(F==='relieve')));
  ['rutas','rutas-toque'].forEach(id=>m.setLayoutProperty(id,'visibility',vis(C.rutas)));
  ATL.host.classList.toggle('f-sat',F==='satelite'); ATL.host.classList.toggle('f-osm',F==='calles');
  ATL.cred.innerHTML=F==='satelite'?'Satélite: <a href="https://s2maps.eu" target="_blank" rel="noopener">Sentinel-2 cloudless 2021 por EOX</a> (datos Copernicus Sentinel modificados)':F==='calles'?'© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">colaboradores de OpenStreetMap</a>':'Relieve: Copernicus DEM GLO-90 © ESA · Cartografía: Natural Earth';
  ATL.host.querySelectorAll('[data-fondo]').forEach(b=>b.setAttribute('aria-checked',b.dataset.fondo===F));
  ['fronteras','ciudades','lagos-hoy','rios-hoy'].forEach(id=>m.setLayoutProperty(id,'visibility',vis(C.hoy)));
  const verRuta=ATL.ev&&ATL.ev.viaje||ATL.full; ['ruta-casco','ruta','ruta-v','ruta-toque'].forEach(id=>m.setLayoutProperty(id,'visibility',vis(C.relato&&verRuta)));
  ['trazo','trazo-casco','trazo-toque'].forEach(id=>m.setLayoutProperty(id,'visibility',vis(C.relato&&!verRuta)));
  ATL.host.querySelectorAll('[data-capa]').forEach(b=>b.setAttribute('aria-pressed',C[b.dataset.capa]));
  atlasMarcadores(); }

/* marcadores HTML: lugares, altares, estaciones, países y ciudades actuales */
function atlasMarcadores(){ const m=ATL.map, C=ATL.capas, ev=ATL.ev||{}; ATL.mk.forEach(x=>x.remove()); ATL.mk=[];
  const add=(ll,node,minz)=>{ node.dataset.minz=minz||0; const k=new maplibregl.Marker({element:node,anchor:'bottom-left',offset:[-8,8]}).setLngLat(lonlat(ll)).addTo(m); ATL.mk.push(k); return node; };
  const verTodo=ev.viaje||ATL.full, hl=new Set(ev.hl||[]), alt=new Set(ev.altars||[]), foco=new Set(ev.focus||[]);
  if(C.relato){
    const keys=verTodo?ATL.data.lugares.filter(l=>l.k==='biblico').map(l=>l.site||l.id):[...new Set([...hl,...alt,...(ev.route||[]).flat()])];
    keys.forEach(key=>{ const L=datosLugar(key); if(!L) return; const A=(DATA.altars||{})[L.site||key], isA=A&&(verTodo||alt.has(key));
      const n=el('button',{type:'button',class:'atl-pin k-biblico'+(isA?' altar':'')+(isA&&foco.size&&!foco.has(key)?' tenue':''),'aria-label':`${L.n}: Escritura, arqueología y hoy`});
      n.innerHTML=isA?`<span class="atl-alt"><svg viewBox="-14 -26 28 30" aria-hidden="true"><path d="M0,-25 C4.5,-20 6.5,-16.5 4.6,-12.8 C3.5,-10.8 1.6,-10 0,-10 C-1.6,-10 -3.5,-10.8 -4.6,-12.8 C-6.5,-16.5 -3.5,-20 0,-25 Z" fill="#9a4a2a"/><path d="M0,-21 C1.6,-19 2.2,-17.4 1.4,-15.8 C.9,-15 -.9,-15 -1.4,-15.8 C-2.2,-17.4 -1.6,-19 0,-21 Z" fill="#d6aa40"/><rect x="-5" y="-10" width="10" height="4" rx="1" fill="#e9dcbc" stroke="#3a2f14"/><rect x="-8" y="-6" width="16" height="4" rx="1" fill="#e9dcbc" stroke="#3a2f14"/><rect x="-11" y="-2" width="22" height="4.5" rx="1" fill="#e9dcbc" stroke="#3a2f14"/></svg><i>${A.n}</i></span>`:'<span class="atl-dot"></span>';
      n.insertAdjacentHTML('beforeend',`<span class="atl-lab">${esc(L.n)}</span>`); n.onclick=e=>{ e.stopPropagation(); atlasPopLugar(L.site||L.id); }; add(L.ll,n,0); }); }
  (ev.stations||[]).length&&C.relato&&!verTodo&&(()=>{ const grp={}; ev.stations.forEach(([nn,key,ring,ov])=>{ const ll=ov||sites[key].slice(0,2), k=ll.map(v=>v.toFixed(2)).join(); (grp[k]=grp[k]||{ll,key,l:[]}).l.push([nn,ring]); });
    Object.values(grp).forEach(g=>{ const n=el('button',{type:'button',class:'atl-est','aria-label':`Estaciones ${g.l.map(x=>x[0]).join(', ')}: ${sites[g.key][2]}`}); n.innerHTML=g.l.map(([nn,r])=>`<i class="${r?'ring':''}">${nn}</i>`).join(''); n.onclick=e=>{ e.stopPropagation(); atlasPopLugar(g.key); }; add(g.ll,n,0).classList.add('est'); }); })();
  if(C.relato&&verTodo){ ATL.data.tramos.forEach(t=>{ const L=datosLugar(t.site); if(!L) return; const n=el('button',{type:'button',class:'atl-est camino'+(ATL.tramo===t.n?' activa':''),'data-n':t.n,'aria-label':`Estación ${t.n}: ${t.a}`}); n.innerHTML=`<i>${t.n}</i>`;
      n.onclick=e=>{ e.stopPropagation(); atlasPlay(false); atlasTramo(t.n); }; const k=new maplibregl.Marker({element:n,anchor:'bottom-right',offset:[-6,-4]}).setLngLat(lonlat(L.ll)).addTo(m); n.dataset.minz=0; ATL.mk.push(k); }); }
  if(C.arq) ATL.data.lugares.filter(l=>l.k==='arqueo').forEach(L=>{ const n=el('button',{type:'button',class:'atl-pin k-arqueo','aria-label':`${L.n}: hallazgo arqueológico`}); n.innerHTML=`<span class="atl-dot"></span><span class="atl-lab">${esc(L.n)}</span>`; n.onclick=e=>{ e.stopPropagation(); atlasPopLugar(L.id,'arq'); }; add(L.ll,n,verTodo?4.6:0); });
  if(C.hoy){ ATL.data.lugares.filter(l=>l.k==='hoy').forEach(L=>{ const n=el('button',{type:'button',class:'atl-pin k-hoy'}); n.innerHTML=`<span class="atl-dot"></span><span class="atl-lab">${esc(L.n)}</span>`; n.onclick=e=>{ e.stopPropagation(); atlasPopLugar(L.id,'hoy'); }; add(L.ll,n,0); });
    ATL.base.paises.forEach(p=>{ const n=el('div',{class:'atl-pais'}); n.textContent=p.n; const k=new maplibregl.Marker({element:n,anchor:'center'}).setLngLat(p.c).addTo(m); n.dataset.minz=0; n.dataset.maxz=8.5; ATL.mk.push(k); });
    [...ATL.base.ciudades.map(c=>[c.n,c.c]),...(ATL.data.ciudades_extra||[]).map(([n,la,lo])=>[n,[lo,la]])].forEach(([nm,c])=>{ const n=el('div',{class:'atl-ciu'}); n.textContent=nm; const k=new maplibregl.Marker({element:n,anchor:'left',offset:[6,0]}).setLngLat(c).addTo(m); n.dataset.minz=5.4; ATL.mk.push(k); }); }
  atlasEtiquetas(); }
function atlasFondo(k){ ATL.fondo=k; ATL.host.querySelectorAll('.atl-aviso').forEach(n=>n.remove()); ATL.avisado=false; if(k!=='relieve'&&!ATL.capas.hoy){ ATL.capas.hoy=true; } atlasCapas(); }
function atlasEtiquetas(){ const z=ATL.map.getZoom(); ATL.mk.forEach(k=>{ const n=k.getElement(); n.classList.toggle('zoculto',z<+(n.dataset.minz||0)||(!!n.dataset.maxz&&z>+n.dataset.maxz)); });
  cancelAnimationFrame(ATL.dcl); ATL.dcl=requestAnimationFrame(desamontonar); }
/* rótulos sin choques: prioridad altar > bíblico > arqueología > hoy > ciudades; los que chocan quedan solo con su punto */
function desamontonar(){ const pri=n=>n.classList.contains('altar')?5:n.classList.contains('atl-est')?6:n.classList.contains('k-biblico')?4:n.classList.contains('k-arqueo')?3:n.classList.contains('k-hoy')?2:n.classList.contains('atl-pais')?1:0;
  const L=ATL.mk.map(k=>k.getElement()).filter(n=>!n.classList.contains('zoculto')); L.forEach(n=>n.classList.remove('sinlab'));
  L.sort((a,b)=>pri(b)-pri(a)); const ok=[], hit=(r,q)=>r.left<q.right+2&&r.right>q.left-2&&r.top<q.bottom+1&&r.bottom>q.top-1;
  L.forEach(n=>{ const lab=n.querySelector('.atl-lab'), dot=n.querySelector('.atl-dot,.atl-alt')||n;
    const rd=dot.getBoundingClientRect(); const rl=lab?lab.getBoundingClientRect():n.getBoundingClientRect();
    if(ok.some(q=>hit(rl,q))){ n.classList.add('sinlab'); if(!lab) return; ok.push(rd); } else { ok.push(rl); if(lab) ok.push(rd); } }); }

/* la ficha siempre completa: se elige el lado con más espacio, se limita su alto a ese espacio (con desplazamiento interno)
   y, si el mapa puede moverse, se desplaza para dar más sitio */
function popupOpts(ll,extra={}){ const m=ATL.map, H=ATL.host.clientHeight, W=ATL.host.clientWidth; let q=m.project(ll);
  const arriba=q.y-60, abajo=H-q.y-36, ideal=Math.min(520,H-110);
  if(Math.max(arriba,abajo)<ideal){ const quiero=Math.min(ideal+60,H-70); m.panBy([0,q.y-quiero],{duration:0}); q=m.project(ll); }
  const ar=q.y-60, ab=H-q.y-36, lado=ar>=ab?'bottom':'top', room=Math.max(ar,ab);
  const anchor=lado+(q.x<W*.3?'-left':q.x>W*.7?'-right':'');
  ATL.popMax=Math.max(200,Math.min(ideal,room-16));
  return Object.assign({className:'atl-pop',anchor,offset:lado==='bottom'?[0,-14]:[0,14]},extra); }
function ajustarPopup(){ const P=ATL.popup; if(!P||!P.isOpen()) return; const pp=P.getElement().querySelector('.pp'); if(pp&&ATL.popMax) pp.style.maxHeight=ATL.popMax+'px';
  requestAnimationFrame(()=>{ if(!P.isOpen()) return; const host=ATL.host.getBoundingClientRect(), r=P.getElement().getBoundingClientRect(); let dx=0;
    if(r.left<host.left+10) dx=r.left-host.left-10; else if(r.right>host.right-10) dx=r.right-host.right+10; if(Math.abs(dx)>2) ATL.map.panBy([dx,0],{duration:300}); }); }
function atlasPopLugar(key,tab){ const L=datosLugar(key); if(!L) return; if(ATL.popup) ATL.popup.remove();
  const m_=ATL.map, ll_=lonlat(L.ll); if(!m_.getBounds().contains(ll_)) m_.easeTo({center:ll_,duration:600});
  if(ATL.host.clientWidth<560||(!ATL.full&&ATL.host.clientHeight<460)){ openDrawer(fichaHTML(L,tab),'c'+(events[cur-1]?events[cur-1].era:7)); cablear($('#dbody')); return; }
  ATL.popup=new maplibregl.Popup(popupOpts(lonlat(L.ll),{maxWidth:'360px',focusAfterOpen:true})).setLngLat(lonlat(L.ll)).setHTML(fichaHTML(L,tab)).addTo(ATL.map);
  cablear(ATL.popup.getElement()); ajustarPopup(); }
function atlasTramo(n,at){ const T=ATL.data.tramos, t=T[n-1]; if(!t) return; const m=ATL.map;
  if(ATL.full&&t.hito&&cur!==t.hito) irSinSalir(t.hito);
  ATL.host.querySelectorAll('.atl-est.camino').forEach(x=>x.classList.toggle('activa',+x.dataset.n===n));
  ATL.host.querySelectorAll('.atl-paso b').forEach(b=>b.textContent=`${n} / ${T.length}`);
  if(ATL.tramo) m.setFeatureState({source:'ruta',id:ATL.tramo},{sel:false}); ATL.tramo=n; m.setFeatureState({source:'ruta',id:n},{sel:true});
  const b=new maplibregl.LngLatBounds(); t.pts.forEach(p=>b.extend(lonlat(p)));
  const pad=ATL.host.clientWidth<560?{top:60,bottom:30,left:30,right:30}:{top:70,bottom:90,left:60,right:60};
  m.fitBounds(b,{padding:pad,maxZoom:t.pts.length<5?9.6:8.4,duration:matchMedia('(prefers-reduced-motion: reduce)').matches?0:1400});
  if(ATL.popup) ATL.popup.remove(); const mid=t.pts[Math.floor(t.pts.length/2)];
  if(ATL.host.clientWidth<560){ openDrawer(tramoHTML(t),'c7'); cablear($('#dbody')); document.querySelectorAll('.tramos button').forEach(x=>x.setAttribute('aria-current',+x.dataset.n===n)); return; }
  if(ATL.full){ const F=$('#atlasFull').querySelector('.af-ficha'); F.innerHTML=tramoHTML(t); F.hidden=false; cablear(F); F.scrollIntoView({block:'start',behavior:'smooth'}); }
  else m.once('moveend',()=>{ if(ATL.tramo!==n) return; const ll=at||lonlat(mid); ATL.popup=new maplibregl.Popup(popupOpts(ll,{maxWidth:'380px',focusAfterOpen:false})).setLngLat(ll).setHTML(tramoHTML(t)).addTo(m); cablear(ATL.popup.getElement()); ajustarPopup(); });
  document.querySelectorAll('.tramos button').forEach(x=>x.setAttribute('aria-current',+x.dataset.n===n)); }
function atlasLugar(key){ atlasAbrir(); const L=datosLugar(key); if(!L) return; const go_=()=>{ ATL.map.flyTo({center:lonlat(L.ll),zoom:Math.max(ATL.map.getZoom(),8.6),duration:1300}); atlasPopLugar(key); };
  ATL.listo?go_():ATL.map.once('load',go_); }

/* vista de cada hito */
function atlasVista(ev,anim){ ATL.ev=ev; const m=ATL.map; if(!m||!ATL.listo) return; m.resize();
  const B=ev.bbox; m.fitBounds([[B[2],B[0]],[B[3],B[1]]],{padding:ATL.full?{top:40,bottom:40,left:40,right:400}:14,duration:anim?900:0});
  const cs=getComputedStyle(document.querySelector('.slide.on')||document.body), col=c=>{ if(!c) return null; const v=/var\((--[\w-]+)\)/.exec(c); return v?(cs.getPropertyValue(v[1]).trim()||null):c; };
  const T=ATL.data.tramos, cerca=(a,b,d=25)=>km(a,b)<d, tramoDe=P=>{ const fin=P[P.length-1];
    const t=T.find(t=>cerca(t.pts[0],P[0],120)&&cerca(t.pts[t.pts.length-1],fin,60))||T.find(t=>cerca(t.pts[0],fin)&&cerca(t.pts[t.pts.length-1],P[0])); return t?t.n:0; };
  const feats=(ev.paths||[]).map((p,i)=>({type:'Feature',id:i+1,properties:{col:col(p.col),lab:p.lab||'',tramo:tramoDe(p.pts)},geometry:{type:'LineString',coordinates:curva(p.pts)}}));
  (ev.route||[]).forEach(([a,b],i)=>feats.push({type:'Feature',id:feats.length+1,properties:{lab:`${sites[a][2]} → ${sites[b][2]}`,tramo:tramoDe([sites[a].slice(0,2),sites[b].slice(0,2)])},geometry:{type:'LineString',coordinates:[lonlat(sites[a]),lonlat(sites[b])]}}));
  m.getSource('trazo').setData({type:'FeatureCollection',features:feats});
  if(ATL.popup){ ATL.popup.remove(); ATL.popup=null; } atlasCapas(); }

/* renderizador de los mapas de diapositiva: respaldo TikZ + mapa vivo */
function mVivo(m,label){ const w=el('div',{class:'vivo'+(m.viaje?' viaje':'')});
  const resp=m.tikz?mAtlas(m,label):el('div',{class:'vivo-vacio'}); resp.classList.add('respaldo'); w.append(resp);
  const slot=el('div',{class:'vivo-slot'}); w.append(slot);
  atlasCargar().then(()=>{ const map=atlasCrear(); if(ATL.full) return; slot.append(ATL.host); w.classList.add('listo'); ATL.ev=m; map.resize(); atlasVista(m,false); requestAnimationFrame(()=>map.resize()); })
    .catch(()=>{ w.classList.add('sin-gl'); });
  return w; }

/* atlas completo a pantalla completa, con la lista de tramos */
function atlasRecorrido(){ atlasAbrir('camino'); const f=()=>{ ATL.paso.hidden=false; atlasTramo(ATL.tramo||1); }; ATL.listo?setTimeout(f,350):atlasCargar().then(()=>{ atlasCrear(); ATL.map.once('load',()=>setTimeout(f,400)); }); }
function atlasAbrir(tab){ if(ATL.full){ if(tab&&ATL.panel) ATL.panel.show(tab); return; } atlasCargar().then(()=>{ const map=atlasCrear(); ATL.full=true; if(ATL.paso) ATL.paso.hidden=false;
    if(!ATL.panel){ ATL.panel=panelAtlas(); $('#atlasFull').querySelector('.af-lista').append(ATL.panel); }
    const ov=$('#atlasFull'); ov.hidden=false; ov.querySelector('.af-map').append(ATL.host); ATL.btnFull.innerHTML=ICO.cerrar; ATL.btnFull.setAttribute('aria-label','Cerrar el atlas'); ATL.btnFull.title='Cerrar el atlas';
    const prev=ATL.ev; ATL.ev={bbox:[29.4,37.6,30.8,47.2],viaje:1}; ATL.evPrev=prev; requestAnimationFrame(()=>{ map.resize(); atlasVista(ATL.ev,false); ATL.panel.show(tab||'camino'); }); ov.querySelector('.af-cerrar').focus(); })
  .catch(()=>{}); }
function atlasCerrar(){ if(!ATL.full) return; ATL.full=false; atlasPlay(false); if(ATL.paso) ATL.paso.hidden=true; $('#atlasFull').hidden=true; ATL.btnFull.innerHTML=ICO.full; ATL.btnFull.setAttribute('aria-label','Abrir el atlas completo'); ATL.btnFull.title='Abrir el atlas completo';
  if(ATL.popup){ ATL.popup.remove(); ATL.popup=null; } ATL.ev=ATL.evPrev||null; renderMedia(cur); }
/* panel del atlas: pestañas Camino · Arqueología · Hoy · Rutas */
function panelAtlas(){ const D=ATL.data, w=el('div',{class:'af-tabs-w'});
  const tabs=[['camino','Camino'],['arq','Arqueología'],['hoy','Hoy'],['rutas','Rutas']], bar=el('div',{class:'af-tabs',role:'tablist'}), cuerpo=el('div',{class:'af-cuerpo'});
  const tarjeta=(L,tab,extra='')=>{ const b=el('button',{type:'button',class:'af-card k-'+L.k}); b.innerHTML=`<b>${esc(L.n)}</b><small>${esc(L.actual||'')}</small>${extra}`; b.onclick=()=>{ atlasPlay(false); const go_=()=>{ ATL.map.flyTo({center:lonlat(L.ll),zoom:Math.max(8.4,ATL.map.getZoom()),duration:1200}); atlasPopLugar(L.site||L.id,tab); }; go_(); }; return b; };
  const pan={camino:()=>{ const [ol,tot]=listaTramos(); return [tot,ol]; },
    arq:()=>{ ATL.capas.arq=true; atlasCapas(); return D.lugares.filter(l=>l.k==='arqueo'||(l.arq||[]).length>1).map(L=>tarjeta(L,'arq',`<span>${esc(((L.arq||[])[0]||'').slice(0,110))}…</span>`)); },
    hoy:()=>{ return D.lugares.filter(l=>l.hoy).map(L=>{ const c=tarjeta(L,'hoy',`<span>${esc(L.hoy.slice(0,110))}…</span>`); const s=el('div',{class:'af-row'}); const sb=el('button',{type:'button',class:'af-sat'}); sb.innerHTML=`${ico('hoy')} Ver hoy`; sb.onclick=()=>verHoy(L.site||L.id);
      const ga=el('a',{class:'af-gm',href:GM.lugar(L),target:'_blank',rel:'noopener',title:'Visitar hoy en Google Maps'}); ga.innerHTML=`${ico('gmaps')} Google Maps`; s.append(c,sb,ga); return s; }); },
    rutas:()=>{ ATL.capas.rutas=true; atlasCapas(); return ATL.rutasL.map(r=>{ const b=el('button',{type:'button',class:'af-card k-ruta'}); b.innerHTML=`<b>${esc(r.n)}</b>${r.he?`<small lang="he" dir="rtl">${esc(r.he)}</small>`:''}<span>${esc(r.nota)}</span>`;
      b.onclick=()=>{ const bb=new maplibregl.LngLatBounds(); r.pts.forEach(p=>bb.extend(lonlat(p))); ATL.map.fitBounds(bb,{padding:{top:60,bottom:60,left:60,right:60},duration:1200}); }; return b; }); }};
  const show=k=>{ if(ATL.popup){ ATL.popup.remove(); ATL.popup=null; } atlasPlay(false); const F=$('#atlasFull').querySelector('.af-ficha'); if(F&&k!=='camino'){ F.hidden=true; } bar.querySelectorAll('button').forEach(b=>b.setAttribute('aria-selected',b.dataset.t===k)); cuerpo.replaceChildren(...pan[k]()); cuerpo.scrollTop=0; };
  tabs.forEach(([k,t])=>{ const b=el('button',{type:'button',role:'tab','data-t':k}); b.textContent=t; b.onclick=()=>show(k); bar.append(b); });
  w.append(bar,cuerpo); w.show=show; return w; }
function listaTramos(){ const T=ATL.data?ATL.data.tramos:[]; const ol=el('ol',{class:'tramos'});
  let tot=0; T.forEach(t=>{ const d=kmTramo(t); tot+=d; const li=el('li'), b=el('button',{type:'button','data-n':t.n});
    b.innerHTML=`<span class="tn-n">${t.n}</span><span class="tn-t"><b>${esc(t.de)} → ${esc(t.a)}</b><small>${esc(t.ref)} · ≈ ${fmtKm(d)} km</small></span>`; b.onclick=()=>{ atlasPlay(false); atlasTramo(t.n); }; li.append(b); ol.append(li); });
  const tot_=el('p',{class:'tramos-tot'}); tot_.innerHTML=`<b>≈ ${fmtKm(tot)} km</b> en ${T.length} tramos, a pie, en unos cien años de vida en camino.`;
  return [ol,tot_]; }
function atlasPlay(on){ clearInterval(ATL.play); ATL.play=0; document.querySelectorAll('.af-play,.vj-play').forEach(b=>{ b.innerHTML=on?`${ico('pausa')} Pausa`:`${ico('play')} Recorrer el camino`; b.setAttribute('aria-pressed',!!on); });
  document.querySelectorAll('.atl-play').forEach(b=>{ b.innerHTML=on?ICO.pausa:ICO.play; b.setAttribute('aria-pressed',!!on); });
  if(!on) return; let n=ATL.tramo&&ATL.tramo<ATL.data.tramos.length?ATL.tramo+1:1; atlasTramo(n);
  ATL.play=setInterval(()=>{ n++; if(n>ATL.data.tramos.length){ atlasPlay(false); return; } atlasTramo(n); },6500); }
