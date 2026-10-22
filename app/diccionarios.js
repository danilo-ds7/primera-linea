/* Primera Línea · Diccionarios enlazados por número Strong.
   Lo usan el Lector (app/index.html) y las páginas del sitio (_includes/citas.html).
   BDB (1906) y Abbott-Smith (1922) son de dominio público: se leen para todos desde app/lexicos/.
   Los demás tienen derechos de autor: se leen en modo privado, con la clave personal de GitHub
   guardada en este dispositivo (la misma de los comentarios privados del Lector), desde la rama
   app-privado del repositorio privado danilo-ds7/primera-linea-biblioteca. */
(function(){
  if(window.PLDic) return;
  var REPO="danilo-ds7/primera-linea-biblioteca", RAMA="app-privado", CLAVE="lector-gh", BLOQUE=250, CACHE="pl-dic-privado";
  var PUBLICOS=[
    {id:"bdb", n:"BDB (inglés)", carpeta:"bdb", pref:"H", lang:"en", fuente:"Brown, F., Driver, S. R. y Briggs, C. A. (1906). A Hebrew and English lexicon of the Old Testament. Clarendon Press. Dominio público; edición digital: Open Scriptures Hebrew Bible Project (CC BY 4.0)."},
    {id:"abbott", n:"Abbott-Smith (inglés)", carpeta:"abbott", pref:"G", lang:"en", fuente:"Abbott-Smith, G. (1922). A manual Greek lexicon of the New Testament. Charles Scribner's Sons. Dominio público; edición digital: translatable-exegetical-tools/Abbott-Smith."}
  ];
  var BASE=(function(){ var s=document.currentScript&&document.currentScript.src; return s ? s.slice(0, s.lastIndexOf("/")+1) : ""; })(), pubMem={};
  function publico(d, cod){
    var url=BASE+"lexicos/"+d.carpeta+"/"+("00"+Math.floor(parseInt(cod.slice(1),10)/BLOQUE)).slice(-3)+".json";
    if(!pubMem[url]) pubMem[url]=fetch(url).then(function(r){ if(!r.ok) throw new Error(r.status); return r.json(); }).catch(function(e){ delete pubMem[url]; throw e; });
    return pubMem[url].then(function(j){ return j[cod]||null; });
  }
  var DICS=[
    {id:"sesp", n:"Strong en español", fuente:"Strong, J. (2002). Nueva concordancia Strong exhaustiva: Diccionario de palabras hebreas, arameas y griegas. Editorial Caribe."},
    {id:"vine", n:"Vine", fuente:"Vine, W. E. (1999). Diccionario expositivo de palabras del Antiguo y del Nuevo Testamento exhaustivo. Editorial Caribe."},
    {id:"chavez", n:"Chávez", fuente:"Chávez, M. (1997). Diccionario de hebreo bíblico (3.ª ed.). Editorial Mundo Hispano."},
    {id:"cge", n:"Ortiz (CGE)", fuente:"Ortiz, P. (2006). Concordancia manual y diccionario greco-español del Nuevo Testamento. Sociedad Bíblica."},
    {id:"barclay", n:"Barclay", fuente:"Barclay, W. (1977). Palabras griegas del Nuevo Testamento: Su uso y su significado. Casa Bautista de Publicaciones."},
    {id:"pt", n:"BDB · Thayer (port.)", fuente:"Strong, J., Brown, F., Driver, S. R., Briggs, C. A. y Thayer, J. H. (2002). Dicionário bíblico Strong: Léxico hebraico, aramaico e grego (trad. portuguesa). Sociedade Bíblica do Brasil.", lang:"pt"},
    {id:"ncse", n:"Concordancia NCSE", fuente:"Strong, J. (2002). Nueva concordancia Strong exhaustiva. Editorial Caribe. Pasajes de la Reina-Valera 1960 (© 1960 Sociedades Bíblicas en América Latina).", conc:true}
  ];
  var mem={};

  function idiomaPref(v){ try{ if(v) localStorage.setItem("pl-dic-lang",v); return localStorage.getItem("pl-dic-lang")||"es"; }catch(e){ return v||"es"; } }
  function token(){ try{ return localStorage.getItem(CLAVE)||""; }catch(e){ return ""; } }
  function guardarToken(t){ try{ if(t) localStorage.setItem(CLAVE,t); else localStorage.removeItem(CLAVE); }catch(e){} mem={}; }
  function ruta(cod, carpeta){ var p=cod[0], n=parseInt(cod.slice(1),10); return "app-privado/"+carpeta+"/"+p+"/"+("00"+Math.floor(n/BLOQUE)).slice(-3)+".json"; }
  function leer(path){
    if(mem[path]) return mem[path];
    var url="https://api.github.com/repos/"+REPO+"/contents/"+path+"?ref="+RAMA, tk=token();
    var guardado=function(){ return ("caches" in window) ? caches.open(CACHE).then(function(c){ return c.match(url); }).then(function(r){ if(!r) throw new Error("sin copia"); return r.json(); }) : Promise.reject(new Error("sin copia")); };
    mem[path]=fetch(url,{headers:{"Authorization":"Bearer "+tk,"Accept":"application/vnd.github.raw+json"}})
      .then(function(r){
        if(r.status===401||r.status===403||r.status===404){ var e=new Error("clave"); e.clave=true; throw e; }
        if(!r.ok) throw new Error(r.status);
        if("caches" in window){ var c=r.clone(); caches.open(CACHE).then(function(k){ k.put(url,c); }).catch(function(){}); }
        return r.json();
      })
      .catch(function(e){ if(e.clave) { delete mem[path]; throw e; } return guardado().catch(function(){ delete mem[path]; throw e; }); });
    return mem[path];
  }
  function entrada(cod){ return leer(ruta(cod,"lexicos")).then(function(j){ return j[cod]||{}; }); }
  function concordancia(cod){ return leer(ruta(cod,"concordancia")).then(function(j){ return j[cod]||{}; }); }

  // ---------- Estilos (usan las variables del sitio y de la app) ----------
  var css=".pd{display:grid;gap:10px;margin-top:10px;font-size:.92rem;line-height:1.55;text-align:left}"+
  ".pd-t{font:700 .72rem/1.2 var(--sans,system-ui,sans-serif);letter-spacing:.12em;text-transform:uppercase;color:var(--muted,#5b6376);margin:4px 0 0}"+
  ".pd-chips{display:flex;flex-wrap:nowrap;gap:6px;overflow-x:auto;scrollbar-width:thin;padding-bottom:4px;border-bottom:1px solid var(--line,#e2e6ee);-webkit-overflow-scrolling:touch}"+
  ".pd-chips .pd-chip{flex:0 0 auto;white-space:nowrap}"+
  ".pd-chip .pd-lock{font-weight:500;opacity:.7;margin-left:4px}"+
  ".pd-lang{display:flex;gap:4px;justify-content:flex-end}.pd-lang .pd-chip{padding:3px 10px;font-size:.76rem}"+
  ".pd-chip{all:unset;box-sizing:border-box;cursor:pointer;border:1px solid var(--line,#e2e6ee);background:var(--surface,#fff);color:var(--ink,#131a2c);border-radius:999px;padding:5px 12px;font:600 .82rem/1.2 var(--sans,system-ui,sans-serif)}"+
  ".pd-chip:hover,.pd-chip:focus-visible{border-color:var(--accent,#2350b8)}"+
  ".pd-chip[aria-pressed=true]{background:var(--accent,#2350b8);border-color:var(--accent,#2350b8);color:var(--accent-ink,#fff)}"+
  ".pd-chip[disabled]{opacity:.45;cursor:default}"+
  ".pd-box{border:1px solid var(--line,#e2e6ee);border-radius:14px;padding:12px 14px;background:var(--surface,#fff);max-height:min(60vh,520px);overflow:auto;overscroll-behavior:contain}"+
  ".pd-box p{margin:0 0 .7em;text-align:left;overflow-wrap:anywhere}.pd-box p:last-child{margin-bottom:0}"+
  ".pd-box h4{font:700 .85rem/1.3 var(--sans,system-ui,sans-serif);letter-spacing:.03em;color:var(--accent,#2350b8);margin:0 0 6px}"+
  ".pd-art+.pd-art{border-top:1px solid var(--line,#e2e6ee);margin-top:12px;padding-top:12px}"+
  ".pd-s{all:unset;cursor:pointer;color:var(--accent,#2350b8);font-weight:700;border-bottom:1px dotted currentColor}"+
  ".pd-mas{all:unset;cursor:pointer;color:var(--accent,#2350b8);font-weight:700;font-size:.85rem}"+
  ".pd-fuente{font-size:.76rem;color:var(--muted,#5b6376);margin:0}"+
  ".pd-priv{border:1px dashed var(--line,#e2e6ee);border-radius:14px;padding:12px 14px;display:grid;gap:8px;font-size:.88rem;color:var(--muted,#5b6376)}"+
  ".pd-priv b{color:var(--ink,#131a2c)}.pd-priv .row{display:flex;gap:8px;flex-wrap:wrap}"+
  ".pd-priv input{flex:1;min-width:160px;border:1px solid var(--line,#e2e6ee);border-radius:10px;padding:9px 10px;background:var(--surface,#fff);color:var(--ink,#131a2c);font:inherit}"+
  ".pd-btn{all:unset;cursor:pointer;border-radius:10px;padding:9px 14px;background:var(--accent,#2350b8);color:var(--accent-ink,#fff);font:700 .85rem var(--sans,system-ui,sans-serif)}"+
  ".pd-btn.sec{background:none;color:var(--accent,#2350b8);padding:4px 0}"+
  ".pd-con details{border-bottom:1px solid var(--line,#e2e6ee);padding:6px 0}.pd-con summary{cursor:pointer;font-weight:700;color:var(--ink,#131a2c)}"+
  ".pd-con summary small{color:var(--muted,#5b6376);font-weight:600;margin-left:6px}"+
  ".pd-con ul{list-style:none;margin:6px 0 0;padding:0;display:grid;gap:4px}.pd-con li b{color:var(--accent,#2350b8);margin-right:6px;white-space:nowrap}"+
  "[lang=he].pd-he,.pd-box [lang=he]{font-family:var(--heb,'Noto Serif Hebrew','SBL Hebrew',serif)}";
  function estilos(){ if(document.getElementById("pd-css")) return; var s=document.createElement("style"); s.id="pd-css"; s.textContent=css; document.head.appendChild(s); }

  function el(t,c,x){ var e=document.createElement(t); if(c) e.className=c; if(x!=null) e.textContent=x; return e; }
  // Texto con párrafos; los números Strong del texto se pueden tocar.
  var HE=/[֐-׿][֐-׿\s־־]*/g;
  function linea(p, t, onStrong){
    t.split(/(\b[HG]\d{1,5}\b)/).forEach(function(seg,i){
      if(i%2 && onStrong){ var b=el("button","pd-s",seg); b.type="button"; b.onclick=function(ev){ ev.stopPropagation(); onStrong(seg); }; p.append(b); return; }
      var k=0; seg.replace(HE,function(m,pos){ if(pos>k) p.append(document.createTextNode(seg.slice(k,pos))); var s=el("span","pd-he",m); s.lang="he"; p.append(s); k=pos+m.length; return m; });
      if(k<seg.length) p.append(document.createTextNode(seg.slice(k)));
    });
  }
  function texto(box, t, onStrong, lang, corto){
    var pars=String(t||"").split(/\n\s*\n/), lim=corto ? 2 : pars.length, cont=el("div");
    function pintar(n){ cont.textContent=""; pars.slice(0,n).forEach(function(par){ var p=el("p"); if(lang) p.lang=lang; par.split("\n").forEach(function(l,i){ if(i) p.append(el("br")); linea(p,l,onStrong); }); cont.append(p); }); }
    pintar(lim); box.append(cont);
    if(pars.length>lim){ var m=el("button","pd-mas","Leer completo ("+pars.length+" párrafos)"); m.type="button"; m.onclick=function(){ pintar(pars.length); m.remove(); }; box.append(m); }
  }
  function concordar(box, c){
    var pal=Object.keys(c).sort(function(a,b){ return c[b].length-c[a].length; }), tot=0;
    pal.forEach(function(p){ tot+=c[p].length; });
    var wrap=el("div","pd-con"); box.append(el("p",null,"La Reina-Valera 1960 traduce este número con "+pal.length+(pal.length===1?" palabra":" palabras")+" en "+tot+" pasajes. En cada cita la palabra se abrevia con su inicial, como en la NCSE."), wrap);
    pal.forEach(function(p,i){
      var d=el("details"), s=el("summary",null,p); s.append(el("small",null,String(c[p].length))); d.append(s);
      if(i===0) d.open=true;
      var ul=el("ul"); d.append(ul);
      function pintar(n){ ul.textContent=""; c[p].slice(0,n).forEach(function(x){ var li=el("li"); li.append(el("b",null,x[0]), document.createTextNode(x[1])); ul.append(li); }); }
      pintar(40);
      if(c[p].length>40){ var m=el("button","pd-mas","Ver los "+c[p].length+" pasajes"); m.type="button"; m.onclick=function(){ pintar(c[p].length); m.remove(); }; d.append(m); }
      wrap.append(d);
    });
  }

  function cajaClave(alGuardar){
    var box=el("div","pd-priv");
    box.append(el("b",null,"Diccionarios en modo privado"));
    box.append(el("span",null,"Strong en español, Vine, Chávez, Ortiz, Barclay, BDB y Thayer (portugués) y la concordancia NCSE tienen derechos de autor. Para verlos, guarda tu clave personal de GitHub (solo lectura del repositorio privado). Queda guardada solo en este dispositivo."));
    var row=el("div","row"), inp=el("input"); inp.type="password"; inp.placeholder="Clave de GitHub (github_pat_…)"; inp.autocomplete="off";
    var g=el("button","pd-btn","Guardar"); g.type="button";
    g.onclick=function(){ var v=inp.value.trim(); if(!v) return; guardarToken(v); alGuardar(); };
    row.append(inp,g); box.append(row); return box;
  }

  /* Pinta la sección «Diccionarios» para un número Strong (H2617, G26) dentro de «cont».
     opts.onStrong(cod): qué hacer al tocar otro número dentro de un diccionario. */
  function render(cont, cod, opts){
    opts=opts||{}; estilos(); cont.textContent="";
    var raiz=el("div","pd"); cont.append(raiz);
    raiz.append(el("p","pd-t","Diccionarios · "+cod+" · elige uno"));
    var chips=el("div","pd-chips"), idioma=el("div","pd-lang"), box=el("div","pd-box"), fuente=el("p","pd-fuente"), pie=el("div");
    raiz.append(chips, idioma, box, fuente, pie);
    box.textContent="Cargando…";
    var tk=token(), pubs=PUBLICOS.filter(function(d){ return d.pref===cod[0]; });
    var pB=Promise.resolve(opts.base||[]).catch(function(){ return []; });
    var pP=Promise.all(pubs.map(function(d){ return publico(d,cod).catch(function(){ return null; }); }));
    var pV=tk ? entrada(cod).then(function(E){ return {E:E}; }, function(e){ return {err:e}; }) : Promise.resolve({E:null});
    chips.setAttribute("role","tablist"); chips.setAttribute("aria-label","Diccionarios disponibles");
    Promise.all([pP, pV, pB]).then(function(res){
      var P=res[0], V=res[1], B=res[2]||[], E=V.E||{}, items=[], botones=[];
      B.forEach(function(x){ if(x && x.v) items.push({d:{id:x.id||"base", n:x.n, lang:x.lang, fuente:x.fuente, fuente_es:x.fuente_es, carpeta:"base"}, v:x.v, v_es:x.v_es}); });
      if(tk && V.E) DICS.forEach(function(d){ if(d.conc || E[d.id]) items.push({d:d, v:E[d.id]}); });
      pubs.forEach(function(d,k){ if(P[k]) items.push({d:d, v:P[k]}); });
      // Sin clave: los diccionarios privados aparecen como pestañas con candado; al tocarlas se pide la clave.
      if(!tk || (V.err && V.err.clave)) DICS.forEach(function(d){ items.push({d:d, bloqueado:true}); });
      function elegir(it, b){
        var d=it.d, v=it.v;
        botones.forEach(function(x){ x.setAttribute("aria-pressed", x===b?"true":"false"); x.setAttribute("aria-selected", x===b?"true":"false"); });
        box.textContent=""; box.scrollTop=0; fuente.textContent=d.fuente+(d.carpeta?"":" Uso privado."); idioma.textContent="";
        if(it.v_es){
          var es=idiomaPref()!=="en";
          [["es","Español"],["en","Inglés"]].forEach(function(L){ var lb=el("button","pd-chip",L[1]); lb.type="button"; lb.setAttribute("aria-pressed", (L[0]==="es")===es?"true":"false"); lb.onclick=function(){ idiomaPref(L[0]); elegir(it,b); }; idioma.append(lb); });
          if(es){ texto(box, it.v_es, opts.onStrong, "es", false); if(d.fuente_es) fuente.textContent=d.fuente_es; return; }
        }
        if(it.bloqueado){
          box.append(el("p",null,d.n+" tiene derechos de autor: se consulta en modo privado, con tu clave personal de GitHub guardada en este dispositivo."));
          box.append(cajaClave(function(){ render(cont, cod, opts); }));
          return;
        }
        if(d.conc){
          box.textContent="Cargando…";
          concordancia(cod).then(function(c){ box.textContent=""; if(!Object.keys(c).length){ box.append(el("p",null,"La concordancia no registra este número.")); return; } concordar(box,c); })
            .catch(function(){ box.textContent="No se pudo leer la concordancia. Revisa la conexión."; });
          return;
        }
        if(Array.isArray(v)){ v.forEach(function(a){ var art=el("div","pd-art"); art.append(el("h4",null,a[0])); texto(art,a[1],opts.onStrong,d.lang,v.length>1||a[1].length>1400); box.append(art); }); }
        else texto(box, v, opts.onStrong, d.lang, false);
      }
      items.forEach(function(it){ var n=Array.isArray(it.v)&&it.v.length>1&&!it.d.carpeta?" ("+it.v.length+")":""; var b=el("button","pd-chip",it.d.n+n); if(it.bloqueado) b.append(el("span","pd-lock","· privado")); b.type="button"; b.setAttribute("role","tab"); b.setAttribute("aria-pressed","false"); b.onclick=function(){ elegir(it,b); }; botones.push(b); chips.append(b); });
      var primero=items.findIndex(function(it){ return !it.bloqueado; });
      if(primero>=0) elegir(items[primero], botones[primero]); else if(items.length) elegir(items[0], botones[0]); else { box.remove(); fuente.remove(); }
      if(!tk){
        pie.append(el("p","pd-fuente","Toca una pestaña para ver ese diccionario. Las marcadas «privado» tienen derechos de autor y se abren en modo privado."));
      } else if(V.err && V.err.clave){
        pie.append(el("p","pd-fuente","La clave guardada no tiene acceso al repositorio privado. Toca una pestaña «privado» para guardar una nueva."));
      } else if(V.err){
        pie.append(el("p","pd-fuente","No se pudieron leer los diccionarios privados. Revisa la conexión."));
      } else {
        var q=el("button","pd-btn sec","Quitar la clave de este dispositivo"); q.type="button"; q.onclick=function(){ guardarToken(""); render(cont, cod, opts); }; pie.append(q);
      }
    });
  }

  window.PLDic={render:render, token:token, guardarToken:guardarToken, lista:DICS};
})();
