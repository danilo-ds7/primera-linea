/* ---------- ATLAS VIVO: MapLibre GL + relieve Copernicus + capas Escritura · Arqueología · Hoy ---------- */
/* Un solo mapa WebGL compartido: cada diapositiva con mapa lo toma al activarse; el atlas completo lo
   abre a pantalla completa. Si WebGL no está disponible, queda el mapa TikZ con sus puntos tocables. */
const ATL={p:null,ok:null,map:null,host:null,data:null,base:null,rel:null,mk:[],ev:null,capas:{relato:true,arq:true,hoy:false,relieve:true},
  popup:null,full:false,tramo:0,play:0,lug:{}};
const ATL_BASE='abraham/';
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
  const tabs=[['esc','Escritura',B],['arq','Arqueología',A],['hoy','Hoy',H]];
  const t0=tab||(L.k==='arqueo'?'arq':L.k==='hoy'?'hoy':'esc');
  return `<div class="pp k-${L.k}"><div class="pp-h"><span class="pp-k">${KIND[L.k]||'Lugar'}</span><b>${esc(L.n)}</b>${L.he?`<span class="pp-he" lang="he" dir="rtl">${esc(L.he)}</span>`:''}${L.actual?`<small>${esc(L.actual)}</small>`:''}</div>
    <div class="pp-tabs" role="tablist">${tabs.map(([k,t])=>`<button type="button" role="tab" data-t="${k}" aria-selected="${k===t0}">${t}</button>`).join('')}</div>
    ${tabs.map(([k,,c])=>`<div class="pp-p" data-p="${k}" ${k===t0?'':'hidden'}>${c}</div>`).join('')}
    <div class="pp-f"><button type="button" data-ficha="${esc(L.site||L.id)}">Ficha completa</button>${usa.slice(0,4).map(u=>`<button type="button" data-goto="${u}">Hito ${u}</button>`).join('')}</div></div>`; }
function tramoHTML(t){ const T=ATL.data.tramos, d=kmTramo(t);
  return `<div class="pp k-tramo"><div class="pp-h"><span class="pp-k">Tramo ${t.n} de ${T.length} · ≈ ${fmtKm(d)} km</span><b>${esc(t.de)} → ${esc(t.a)}</b></div>
    <blockquote class="pp-q"><cite>${esc(t.ref)}</cite>${esc(t.txt)}</blockquote><div class="pp-sub">Camino y arqueología</div><p>${esc(t.arq)}</p>
    <div class="pp-f"><button type="button" data-tr="${t.n-1}" ${t.n>1?'':'disabled'}>← Tramo ${t.n-1||''}</button><button type="button" data-lug="${esc(t.site)}">${esc(t.a)}</button><button type="button" data-tr="${t.n+1}" ${t.n<T.length?'':'disabled'}>Tramo ${t.n<T.length?t.n+1:''} →</button></div></div>`; }
function cablear(root){ root.querySelectorAll('.pp-tabs button').forEach(b=>b.onclick=()=>{ const pp=b.closest('.pp'); pp.querySelectorAll('.pp-tabs button').forEach(x=>x.setAttribute('aria-selected',x===b)); pp.querySelectorAll('.pp-p').forEach(p=>p.hidden=p.dataset.p!==b.dataset.t); });
  root.querySelectorAll('[data-ficha]').forEach(b=>b.onclick=()=>abrirLugar(b.dataset.ficha,b));
  root.querySelectorAll('[data-goto]').forEach(b=>b.onclick=()=>{ atlasCerrar(); closeDrawer(); go(+b.dataset.goto); });
  root.querySelectorAll('[data-tr]').forEach(b=>b.onclick=()=>atlasTramo(+b.dataset.tr));
  root.querySelectorAll('[data-lug]').forEach(b=>b.onclick=()=>atlasLugar(b.dataset.lug)); }
function abrirLugar(key,from){ const L=datosLugar(key); if(!L) return;
  const usa=L.site?SITEUSE[L.site]||[]:[], A=L.site?(DATA.altars||{})[L.site]:null;
  openDrawer(`<div class="era">${KIND[L.k]||'Lugar'}${A?` · altar ${A.n}`:''}</div><h3 class="ref" id="dref">${esc(L.n)}</h3>${L.he?`<div class="he" lang="he" dir="rtl">${esc(L.he)}</div>`:''}
    ${L.actual?`<div class="src">${esc(L.actual)} · ${L.ll[0].toFixed(3).replace('.',',')}° N, ${L.ll[1].toFixed(3).replace('.',',')}° E</div>`:''}
    <div class="lab">Escritura</div>${(L.biblia||[]).map(([r,t])=>`<blockquote><b>${esc(r)}</b> ${esc(t)}</blockquote>`).join('')||'<p>—</p>'}
    ${A?`<div class="lab">Altar ${A.n} · ${esc(A.ref)}</div><p><b>${esc(A.tr)}</b> — ${esc(A.mean)}</p><p><b>Atributo de Dios:</b> ${esc(A.attr)}</p>`:''}
    <div class="lab">Arqueología</div>${(L.arq||[]).map(t=>`<p>${esc(t)}</p>`).join('')}
    <div class="lab">Hoy</div><p>${esc(L.hoy||'—')}</p>${(L.fuentes||[]).length?`<div class="lab">Fuentes</div>${L.fuentes.map(f=>`<p class="src">${esc(f)}</p>`).join('')}`:''}
    <p><button type="button" class="vermapa" data-lug="${esc(L.site||L.id)}">Ver en el atlas</button></p>
    ${usa.length?`<div class="lab">Aparece en</div><div class="see" style="border:0;padding:0">${usa.map(u=>`<button type="button" data-goto="${u}"><span>${u}</span>${esc(events[u-1].title)}</button>`).join('')}</div>`:''}`,
    'c'+(events[cur-1]?events[cur-1].era:7),from);
  $('#dbody').querySelectorAll('[data-goto]').forEach(bt=>bt.onclick=()=>{ closeDrawer(); atlasCerrar(); go(+bt.dataset.goto); });
  $('#dbody').querySelectorAll('.vermapa').forEach(bt=>bt.onclick=()=>{ closeDrawer(); atlasLugar(bt.dataset.lug); }); }

/* ---------- construcción del mapa ---------- */
function atlasCrear(){ if(ATL.map) return ATL.map;
  const host=el('div',{class:'atl'}), cont=el('div',{class:'atl-map'});
  const bar=el('div',{class:'atl-capas',role:'group','aria-label':'Capas del mapa'});
  [['relato','Relato'],['arq','Arqueología'],['hoy','Hoy'],['relieve','Relieve']].forEach(([k,t])=>{ const b=el('button',{type:'button','data-capa':k,'aria-pressed':ATL.capas[k]}); b.textContent=t; b.onclick=()=>{ ATL.capas[k]=!ATL.capas[k]; b.setAttribute('aria-pressed',ATL.capas[k]); atlasCapas(); }; bar.append(b); });
  const tools=el('div',{class:'atl-tools'});
  const mkb=(t,l,f)=>{ const b=el('button',{type:'button','aria-label':l,title:l}); b.innerHTML=t; b.onclick=f; tools.append(b); return b; };
  mkb('+','Acercar',()=>ATL.map.zoomIn()); mkb('−','Alejar',()=>ATL.map.zoomOut()); mkb('⟲','Volver a la vista del hito',()=>atlasVista(ATL.ev,true));
  ATL.btnFull=mkb('⤢','Abrir el atlas completo',()=>ATL.full?atlasCerrar():atlasAbrir());
  const leyenda=el('div',{class:'atl-ley'}); leyenda.innerHTML='<span><i class="lg-b"></i>Lugar bíblico</span><span><i class="lg-a"></i>Arqueología</span><span><i class="lg-h"></i>Hoy</span><span><i class="lg-r"></i>Camino</span>';
  const cred=el('div',{class:'atl-cred'}); cred.textContent='Relieve: Copernicus DEM GLO-90 © ESA · Cartografía: Natural Earth';
  host.append(cont,bar,tools,leyenda,cred); ATL.host=host;
  const st={version:8,sources:{},layers:[{id:'mar',type:'background',paint:{'background-color':'#c4d0ca'}}]};
  ATL.rel.forEach((r,k)=>{ st.sources['rel'+k]={type:'image',url:ATL_BASE+r.src.replace(/^abraham\//,''),coordinates:r.coords};
    st.layers.push({id:'rel'+k,type:'raster',source:'rel'+k,...(r.nivel==='levante'?{minzoom:5.6}:{}),paint:{'raster-fade-duration':180,'raster-contrast':.04}}); });
  const B=ATL.base, fc=f=>({type:'geojson',data:f});
  st.sources.lagos=fc(B.lagos); st.sources.rios=fc(B.rios); st.sources.costa=fc(B.costa); st.sources.fronteras=fc(B.fronteras);
  st.sources.ruta=fc({type:'FeatureCollection',features:ATL.data.tramos.map(t=>({type:'Feature',id:t.n,properties:{n:t.n,v:t.vuelta?1:0},geometry:{type:'LineString',coordinates:curva(t.pts)}}))});
  st.sources.trazo=fc({type:'FeatureCollection',features:[]});
  const cfx=[...B.ciudades.map(c=>({n:c.n,c:c.c})),...(ATL.data.ciudades_extra||[]).map(([n,la,lo])=>({n,c:[lo,la]}))];
  st.sources.ciudades=fc({type:'FeatureCollection',features:cfx.map(c=>({type:'Feature',properties:{n:c.n},geometry:{type:'Point',coordinates:c.c}}))});
  st.layers.push(
    {id:'lagos',type:'fill',source:'lagos',filter:['==',['get','hoy'],0],paint:{'fill-color':'#b6c9c4','fill-outline-color':'#5f8a8c'}},
    {id:'lagos-hoy',type:'fill',source:'lagos',filter:['==',['get','hoy'],1],layout:{visibility:'none'},paint:{'fill-color':'#a9c3c8','fill-opacity':.85}},
    {id:'costa',type:'line',source:'costa',paint:{'line-color':'#5d6f69','line-width':['interpolate',['linear'],['zoom'],4,.5,9,1.2],'line-opacity':.8}},
    {id:'rios',type:'line',source:'rios',filter:['==',['get','hoy'],0],layout:{'line-cap':'round','line-join':'round'},
      paint:{'line-color':'#4f7f84','line-width':['interpolate',['linear'],['zoom'],4,['case',['<=',['get','r'],4],1.4,.7],9,['case',['<=',['get','r'],4],3,1.6]],'line-opacity':['case',['==',['get','esq'],1],.75,.95]}},
    {id:'rios-hoy',type:'line',source:'rios',filter:['==',['get','hoy'],1],layout:{visibility:'none'},paint:{'line-color':'#2f6f8a','line-width':1.2,'line-dasharray':[2,1.5]}},
    {id:'fronteras',type:'line',source:'fronteras',layout:{visibility:'none','line-join':'round'},paint:{'line-color':'#7a2f3b','line-width':['interpolate',['linear'],['zoom'],4,.8,9,1.6],'line-dasharray':[4,2],'line-opacity':.8}},
    {id:'ciudades',type:'circle',source:'ciudades',layout:{visibility:'none'},paint:{'circle-radius':3.2,'circle-color':'#2f4f6f','circle-stroke-color':'#fff','circle-stroke-width':1.2}},
    {id:'ruta-casco',type:'line',source:'ruta',layout:{'line-cap':'round','line-join':'round'},paint:{'line-color':'#fff8e8','line-width':['interpolate',['linear'],['zoom'],4,4.5,9,8],'line-opacity':.75}},
    {id:'ruta',type:'line',source:'ruta',layout:{'line-cap':'round','line-join':'round'},
      paint:{'line-color':['case',['boolean',['feature-state','sel'],false],'#d6aa40',['boolean',['feature-state','hov'],false],'#c4612f','#9a4a2a'],
        'line-width':['interpolate',['linear'],['zoom'],4,['case',['boolean',['feature-state','sel'],false],4.5,2.4],9,['case',['boolean',['feature-state','sel'],false],8,4.2]]},filter:['==',['get','v'],0]},
    {id:'ruta-v',type:'line',source:'ruta',filter:['==',['get','v'],1],layout:{'line-join':'round'},
      paint:{'line-color':['case',['boolean',['feature-state','sel'],false],'#d6aa40',['boolean',['feature-state','hov'],false],'#c4612f','#9a4a2a'],
        'line-width':['interpolate',['linear'],['zoom'],4,['case',['boolean',['feature-state','sel'],false],4,2],9,['case',['boolean',['feature-state','sel'],false],7,3.6]],'line-dasharray':[1.4,1.2]}},
    {id:'ruta-toque',type:'line',source:'ruta',paint:{'line-color':'#000','line-opacity':0,'line-width':18}},
    {id:'trazo-casco',type:'line',source:'trazo',layout:{'line-cap':'round','line-join':'round'},paint:{'line-color':'#fff8e8','line-width':6,'line-opacity':.7}},
    {id:'trazo',type:'line',source:'trazo',layout:{'line-cap':'round','line-join':'round'},paint:{'line-color':['coalesce',['get','col'],'#9a4a2a'],'line-width':3.4}});
  const map=new maplibregl.Map({container:cont,style:st,center:[38,33],zoom:5,minZoom:4.2,maxZoom:12.5,maxBounds:[[28.05,27.05],[50.95,39.95]],attributionControl:false,
    cooperativeGestures:false,dragRotate:false,pitchWithRotate:false,touchPitch:false,renderWorldCopies:false,fadeDuration:150,locale:{
      'CooperativeGesturesHandler.WindowsHelpText':'Usa Ctrl + rueda para acercar o alejar el mapa','CooperativeGesturesHandler.MacHelpText':'Usa ⌘ + rueda para acercar o alejar el mapa','CooperativeGesturesHandler.MobileHelpText':'Usa dos dedos para mover el mapa'}});
  map.touchZoomRotate.disableRotation();
  ATL.map=map;
  let hov=null;
  map.on('mousemove','ruta-toque',e=>{ const f=e.features[0]; if(hov!==f.id){ if(hov!==null) map.setFeatureState({source:'ruta',id:hov},{hov:false}); hov=f.id; map.setFeatureState({source:'ruta',id:hov},{hov:true}); } map.getCanvas().style.cursor='pointer';
    const t=ATL.data.tramos[f.id-1]; ATL.tip.innerHTML=`<b>Tramo ${t.n}</b> ${esc(t.de)} → ${esc(t.a)} · <i>${esc(t.ref)}</i>`; ATL.tip.style.left=e.point.x+'px'; ATL.tip.style.top=e.point.y+'px'; ATL.tip.hidden=false; });
  map.on('mouseleave','ruta-toque',()=>{ if(hov!==null) map.setFeatureState({source:'ruta',id:hov},{hov:false}); hov=null; map.getCanvas().style.cursor=''; ATL.tip.hidden=true; });
  map.on('click','ruta-toque',e=>{ ATL.tip.hidden=true; atlasTramo(e.features[0].id,e.lngLat); });
  map.on('click','ciudades',e=>{ const f=e.features[0]; new maplibregl.Popup({closeButton:true,className:'atl-pop',maxWidth:'260px'}).setLngLat(f.geometry.coordinates).setHTML(`<div class="pp k-hoy"><div class="pp-h"><span class="pp-k">Ciudad actual</span><b>${esc(f.properties.n)}</b></div></div>`).addTo(map); });
  map.on('zoom',()=>atlasEtiquetas()); map.on('moveend',()=>atlasEtiquetas());
  ATL.tip=el('div',{class:'atl-tip',hidden:''}); host.append(ATL.tip);
  map.on('load',()=>{ ATL.listo=true; map.resize(); atlasCapas(); if(ATL.ev) atlasVista(ATL.ev,false); });
  let rw=0; new ResizeObserver(()=>{ const w=host.clientWidth; if(!w) return; map.resize(); if(Math.abs(w-rw)>40&&ATL.ev&&ATL.listo) atlasVista(ATL.ev,false); rw=w; }).observe(host);
  return map; }

function atlasCapas(){ const m=ATL.map; if(!m||!ATL.listo) return; const C=ATL.capas, vis=v=>v?'visible':'none';
  ATL.rel.forEach((r,k)=>m.setLayoutProperty('rel'+k,'visibility',vis(C.relieve)));
  m.setPaintProperty('mar','background-color',C.relieve?'#c4d0ca':'#efe6cf');
  ['fronteras','ciudades','lagos-hoy','rios-hoy'].forEach(id=>m.setLayoutProperty(id,'visibility',vis(C.hoy)));
  const verRuta=ATL.ev&&ATL.ev.viaje||ATL.full; ['ruta-casco','ruta','ruta-v','ruta-toque'].forEach(id=>m.setLayoutProperty(id,'visibility',vis(C.relato&&verRuta)));
  ['trazo','trazo-casco'].forEach(id=>m.setLayoutProperty(id,'visibility',vis(C.relato&&!verRuta)));
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
  if(C.arq) ATL.data.lugares.filter(l=>l.k==='arqueo').forEach(L=>{ const n=el('button',{type:'button',class:'atl-pin k-arqueo','aria-label':`${L.n}: hallazgo arqueológico`}); n.innerHTML=`<span class="atl-dot"></span><span class="atl-lab">${esc(L.n)}</span>`; n.onclick=e=>{ e.stopPropagation(); atlasPopLugar(L.id,'arq'); }; add(L.ll,n,verTodo?4.6:0); });
  if(C.hoy){ ATL.data.lugares.filter(l=>l.k==='hoy').forEach(L=>{ const n=el('button',{type:'button',class:'atl-pin k-hoy'}); n.innerHTML=`<span class="atl-dot"></span><span class="atl-lab">${esc(L.n)}</span>`; n.onclick=e=>{ e.stopPropagation(); atlasPopLugar(L.id,'hoy'); }; add(L.ll,n,0); });
    ATL.base.paises.forEach(p=>{ const n=el('div',{class:'atl-pais'}); n.textContent=p.n; const k=new maplibregl.Marker({element:n,anchor:'center'}).setLngLat(p.c).addTo(m); n.dataset.minz=0; n.dataset.maxz=8.5; ATL.mk.push(k); });
    [...ATL.base.ciudades.map(c=>[c.n,c.c]),...(ATL.data.ciudades_extra||[]).map(([n,la,lo])=>[n,[lo,la]])].forEach(([nm,c])=>{ const n=el('div',{class:'atl-ciu'}); n.textContent=nm; const k=new maplibregl.Marker({element:n,anchor:'left',offset:[6,0]}).setLngLat(c).addTo(m); n.dataset.minz=5.4; ATL.mk.push(k); }); }
  atlasEtiquetas(); }
function atlasEtiquetas(){ const z=ATL.map.getZoom(); ATL.mk.forEach(k=>{ const n=k.getElement(); n.classList.toggle('zoculto',z<+(n.dataset.minz||0)||(!!n.dataset.maxz&&z>+n.dataset.maxz)); });
  cancelAnimationFrame(ATL.dcl); ATL.dcl=requestAnimationFrame(desamontonar); }
/* rótulos sin choques: prioridad altar > bíblico > arqueología > hoy > ciudades; los que chocan quedan solo con su punto */
function desamontonar(){ const pri=n=>n.classList.contains('altar')?5:n.classList.contains('atl-est')?6:n.classList.contains('k-biblico')?4:n.classList.contains('k-arqueo')?3:n.classList.contains('k-hoy')?2:n.classList.contains('atl-pais')?1:0;
  const L=ATL.mk.map(k=>k.getElement()).filter(n=>!n.classList.contains('zoculto')); L.forEach(n=>n.classList.remove('sinlab'));
  L.sort((a,b)=>pri(b)-pri(a)); const ok=[], hit=(r,q)=>r.left<q.right+2&&r.right>q.left-2&&r.top<q.bottom+1&&r.bottom>q.top-1;
  L.forEach(n=>{ const lab=n.querySelector('.atl-lab'), dot=n.querySelector('.atl-dot,.atl-alt')||n;
    const rd=dot.getBoundingClientRect(); const rl=lab?lab.getBoundingClientRect():n.getBoundingClientRect();
    if(ok.some(q=>hit(rl,q))){ n.classList.add('sinlab'); if(!lab) return; ok.push(rd); } else { ok.push(rl); if(lab) ok.push(rd); } }); }

function atlasPopLugar(key,tab){ const L=datosLugar(key); if(!L) return; if(ATL.popup) ATL.popup.remove();
  const m_=ATL.map, ll_=lonlat(L.ll); if(!m_.getBounds().contains(ll_)) m_.easeTo({center:ll_,duration:600});
  if(ATL.host.clientWidth<560){ openDrawer(fichaHTML(L,tab),'c'+(events[cur-1]?events[cur-1].era:7)); cablear($('#dbody')); return; }
  ATL.popup=new maplibregl.Popup({className:'atl-pop',maxWidth:'360px',offset:[0,-14],focusAfterOpen:true}).setLngLat(lonlat(L.ll)).setHTML(fichaHTML(L,tab)).addTo(ATL.map);
  cablear(ATL.popup.getElement()); }
function atlasTramo(n,at){ const T=ATL.data.tramos, t=T[n-1]; if(!t) return; const m=ATL.map;
  if(ATL.tramo) m.setFeatureState({source:'ruta',id:ATL.tramo},{sel:false}); ATL.tramo=n; m.setFeatureState({source:'ruta',id:n},{sel:true});
  const b=new maplibregl.LngLatBounds(); t.pts.forEach(p=>b.extend(lonlat(p)));
  const pad=ATL.host.clientWidth<560?{top:60,bottom:30,left:30,right:30}:{top:70,bottom:60,left:60,right:ATL.full?420:60};
  m.fitBounds(b,{padding:pad,maxZoom:t.pts.length<5?9.6:8.4,duration:matchMedia('(prefers-reduced-motion: reduce)').matches?0:1400});
  if(ATL.popup) ATL.popup.remove(); const mid=t.pts[Math.floor(t.pts.length/2)];
  if(ATL.host.clientWidth<560){ openDrawer(tramoHTML(t),'c7'); cablear($('#dbody')); document.querySelectorAll('.tramos button').forEach(x=>x.setAttribute('aria-current',+x.dataset.n===n)); return; }
  ATL.popup=new maplibregl.Popup({className:'atl-pop',maxWidth:'380px',focusAfterOpen:false}).setLngLat(at||lonlat(mid)).setHTML(tramoHTML(t)).addTo(m); cablear(ATL.popup.getElement());
  document.querySelectorAll('.tramos button').forEach(x=>x.setAttribute('aria-current',+x.dataset.n===n)); }
function atlasLugar(key){ atlasAbrir(); const L=datosLugar(key); if(!L) return; const go_=()=>{ ATL.map.flyTo({center:lonlat(L.ll),zoom:Math.max(ATL.map.getZoom(),8.6),duration:1300}); atlasPopLugar(key); };
  ATL.listo?go_():ATL.map.once('load',go_); }

/* vista de cada hito */
function atlasVista(ev,anim){ ATL.ev=ev; const m=ATL.map; if(!m||!ATL.listo) return; m.resize();
  const B=ev.bbox; m.fitBounds([[B[2],B[0]],[B[3],B[1]]],{padding:ATL.full?{top:40,bottom:40,left:40,right:400}:14,duration:anim?900:0});
  const cs=getComputedStyle(document.querySelector('.slide.on')||document.body), col=c=>{ if(!c) return null; const v=/var\((--[\w-]+)\)/.exec(c); return v?(cs.getPropertyValue(v[1]).trim()||null):c; };
  const feats=(ev.paths||[]).map(p=>({type:'Feature',properties:{col:col(p.col)},geometry:{type:'LineString',coordinates:curva(p.pts)}}));
  (ev.route||[]).forEach(([a,b])=>feats.push({type:'Feature',properties:{},geometry:{type:'LineString',coordinates:[lonlat(sites[a]),lonlat(sites[b])]}}));
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
function atlasAbrir(){ if(ATL.full){ return; } atlasCargar().then(()=>{ const map=atlasCrear(); ATL.full=true;
    const ov=$('#atlasFull'); ov.hidden=false; ov.querySelector('.af-map').append(ATL.host); ATL.btnFull.textContent='✕'; ATL.btnFull.setAttribute('aria-label','Cerrar el atlas'); ATL.btnFull.title='Cerrar el atlas';
    const prev=ATL.ev; ATL.ev={bbox:[29.4,37.6,30.8,47.2],viaje:1}; ATL.evPrev=prev; requestAnimationFrame(()=>{ map.resize(); atlasVista(ATL.ev,false); }); ov.querySelector('.af-cerrar').focus(); })
  .catch(()=>{}); }
function atlasCerrar(){ if(!ATL.full) return; ATL.full=false; atlasPlay(false); $('#atlasFull').hidden=true; ATL.btnFull.textContent='⤢'; ATL.btnFull.setAttribute('aria-label','Abrir el atlas completo'); ATL.btnFull.title='Abrir el atlas completo';
  if(ATL.popup){ ATL.popup.remove(); ATL.popup=null; } ATL.ev=ATL.evPrev||null; renderMedia(cur); }
function listaTramos(){ const T=ATL.data?ATL.data.tramos:[]; const ol=el('ol',{class:'tramos'});
  let tot=0; T.forEach(t=>{ const d=kmTramo(t); tot+=d; const li=el('li'), b=el('button',{type:'button','data-n':t.n});
    b.innerHTML=`<span class="tn-n">${t.n}</span><span class="tn-t"><b>${esc(t.de)} → ${esc(t.a)}</b><small>${esc(t.ref)} · ≈ ${fmtKm(d)} km</small></span>`; b.onclick=()=>{ atlasPlay(false); atlasTramo(t.n); }; li.append(b); ol.append(li); });
  const tot_=el('p',{class:'tramos-tot'}); tot_.innerHTML=`<b>≈ ${fmtKm(tot)} km</b> en ${T.length} tramos, a pie, en unos cien años de vida en camino.`;
  return [ol,tot_]; }
function atlasPlay(on){ clearInterval(ATL.play); ATL.play=0; document.querySelectorAll('.af-play,.vj-play').forEach(b=>{ b.textContent=on?'❚❚ Pausa':'▶ Recorrer el camino'; b.setAttribute('aria-pressed',!!on); });
  if(!on) return; let n=ATL.tramo&&ATL.tramo<ATL.data.tramos.length?ATL.tramo+1:1; atlasTramo(n);
  ATL.play=setInterval(()=>{ n++; if(n>ATL.data.tramos.length){ atlasPlay(false); return; } atlasTramo(n); },6500); }
