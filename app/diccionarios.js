/* Primera Línea · Diccionarios enlazados por número Strong.
   Lo usan el Lector (app/index.html) y las páginas del sitio (_includes/citas.html).
   Solo diccionarios de dominio público, abiertos para todos (nada privado):
     Strong (1890)        datos/strong-{h,g}-fichas.json  (inglés)  y  datos/strong-{h,g}-es.json  (español)
     BDB (1906)           app/lexicos/bdb/     (inglés)  y  app/lexicos/bdb-es/     (español)   números H
     Abbott-Smith (1922)  app/lexicos/abbott/  (inglés)  y  app/lexicos/abbott-es/  (español)   números G
     Thayer (1889)        app/lexicos/thayer/  (inglés)  y  app/lexicos/thayer-es/  (español)   números G
     AHLB (Benner, 2005)  app/lexicos/ahlb/    (inglés)  y  app/lexicos/ahlb-es/    (español)   números H (uso educativo sin fines de lucro)
   De cada diccionario se muestran solo las definiciones. Las traducciones al español son de Primera Línea.
   Se elige un diccionario por pestaña y, en cada uno, el idioma (Español / Inglés). */
(function(){
  if(window.PLDic) return;
  var BLOQUE=250;
  var BASE=(function(){ var s=document.currentScript&&document.currentScript.src; return s ? s.slice(0, s.lastIndexOf("/")+1) : ""; })();
  var DICS=[
    {id:"strong", n:"Strong", pref:"HG",
      fuente:"Strong, J. (1890). A concise dictionary of the words in the Hebrew Bible; A concise dictionary of the words in the Greek Testament. Dominio público."},
    {id:"bdb", n:"BDB", pref:"H", carpeta:"bdb",
      fuente:"Brown, F., Driver, S. R. y Briggs, C. A. (1906). A Hebrew and English lexicon of the Old Testament. Clarendon Press. Dominio público; edición digital: Open Scriptures Hebrew Bible Project (CC BY 4.0)."},
    {id:"abbott", n:"Abbott-Smith", pref:"G", carpeta:"abbott",
      fuente:"Abbott-Smith, G. (1922). A manual Greek lexicon of the New Testament. Charles Scribner's Sons. Dominio público; edición digital: translatable-exegetical-tools/Abbott-Smith."},
    {id:"thayer", n:"Thayer", pref:"G", carpeta:"thayer",
      fuente:"Thayer, J. H. (1889). A Greek-English lexicon of the New Testament. American Book Company. Dominio público; edición abreviada «Thayer's Greek Definitions» de e-Sword."},
    {id:"ahlb", n:"Hebreo antiguo (AHLB)", pref:"H", carpeta:"ahlb",
      fuente:"Benner, J. A. (2005). Ancient Hebrew lexicon of the Bible. Virtualbookworm. © Jeff A. Benner; se permite copiar con fines educativos sin fines de lucro. Edición de e-Sword."}
  ];
  var mem={};
  function json(url){
    if(!mem[url]) mem[url]=fetch(url).then(function(r){ if(!r.ok) throw new Error(r.status); return r.json(); }).catch(function(e){ delete mem[url]; throw e; });
    return mem[url];
  }
  function bloque(cod){ return ("00"+Math.floor(parseInt(cod.slice(1),10)/BLOQUE)).slice(-3)+".json"; }
  // Devuelve {en, es} para un diccionario y un número; en/es son texto o lista de artículos [lema, texto].
  function cargar(d, cod){
    var nada=function(){ return {}; };
    if(d.id==="strong"){
      var t=cod[0].toLowerCase(), raiz=BASE+"../datos/strong-"+t+"-";
      return Promise.all([json(raiz+"fichas.json").catch(nada), json(raiz+"es.json").catch(nada)])
        .then(function(r){ var f=r[0][cod]; return {en:(f&&f[3])||"", es:r[1][cod]||""}; });
    }
    return Promise.all([json(BASE+"lexicos/"+d.carpeta+"/"+bloque(cod)).catch(nada), json(BASE+"lexicos/"+d.carpeta+"-es/"+bloque(cod)).catch(nada)])
      .then(function(r){ return {en:r[0][cod]||null, es:r[1][cod]||null}; });
  }

  // ---------- Estilos (usan las variables del sitio y de la app) ----------
  var css=".pd{display:grid;gap:10px;margin-top:10px;font-size:.92rem;line-height:1.55;text-align:left}"+
  ".pd-t{font:700 .72rem/1.2 var(--sans,system-ui,sans-serif);letter-spacing:.12em;text-transform:uppercase;color:var(--muted,#5b6376);margin:4px 0 0}"+
  ".pd-chips{display:flex;flex-wrap:nowrap;gap:6px;overflow-x:auto;scrollbar-width:thin;padding-bottom:6px;border-bottom:1px solid var(--line,#e2e6ee);-webkit-overflow-scrolling:touch}"+
  ".pd-chips .pd-chip{flex:0 0 auto;white-space:nowrap}"+
  ".pd-lang{display:flex;gap:4px;justify-content:flex-end}.pd-lang .pd-chip{padding:3px 10px;font-size:.76rem}"+
  ".pd-chip{all:unset;box-sizing:border-box;cursor:pointer;border:1px solid var(--line,#e2e6ee);background:var(--surface,#fff);color:var(--ink,#131a2c);border-radius:999px;padding:5px 12px;font:600 .82rem/1.2 var(--sans,system-ui,sans-serif)}"+
  ".pd-chip:hover,.pd-chip:focus-visible{border-color:var(--accent,#2350b8)}"+
  ".pd-chip[aria-pressed=true]{background:var(--accent,#2350b8);border-color:var(--accent,#2350b8);color:var(--accent-ink,#fff)}"+
  ".pd-box{border:1px solid var(--line,#e2e6ee);border-radius:14px;padding:12px 14px;background:var(--surface,#fff);max-height:min(60vh,520px);overflow:auto;overscroll-behavior:contain}"+
  ".pd-box p{margin:0 0 .45em;text-align:left;overflow-wrap:anywhere}.pd-box p:last-child{margin-bottom:0}"+
  ".pd-box h4{font:700 .95rem/1.3 var(--sans,system-ui,sans-serif);color:var(--accent,#2350b8);margin:0 0 6px}"+
  ".pd-art+.pd-art{border-top:1px solid var(--line,#e2e6ee);margin-top:10px;padding-top:10px}"+
  ".pd-s{all:unset;cursor:pointer;color:var(--accent,#2350b8);font-weight:700;border-bottom:1px dotted currentColor}"+
  ".pd-fuente{font-size:.76rem;color:var(--muted,#5b6376);margin:0}"+
  "[lang=he].pd-he,.pd-box [lang=he]{font-family:var(--heb,'Noto Serif Hebrew','SBL Hebrew',serif)}";
  function estilos(){ if(document.getElementById("pd-css")) return; var s=document.createElement("style"); s.id="pd-css"; s.textContent=css; document.head.appendChild(s); }

  function el(t,c,x){ var e=document.createElement(t); if(c) e.className=c; if(x!=null) e.textContent=x; return e; }
  // Texto línea por línea; los números Strong del texto se pueden tocar y el hebreo lleva su tipografía.
  var HE=/[֐-׿][֐-׿\s־]*/g;
  function linea(p, t, onStrong){
    t.split(/(\b[HG]\d{1,5}\b)/).forEach(function(seg,i){
      if(i%2 && onStrong){ var b=el("button","pd-s",seg); b.type="button"; b.onclick=function(ev){ ev.stopPropagation(); onStrong(seg); }; p.append(b); return; }
      var k=0; seg.replace(HE,function(m,pos){ if(pos>k) p.append(document.createTextNode(seg.slice(k,pos))); var s=el("span","pd-he",m); s.lang="he"; p.append(s); k=pos+m.length; return m; });
      if(k<seg.length) p.append(document.createTextNode(seg.slice(k)));
    });
  }
  function texto(box, t, onStrong, lang){
    String(t||"").split(/\n+/).forEach(function(l){ if(!l.trim()) return; var p=el("p"); p.lang=lang; linea(p,l,onStrong); box.append(p); });
  }

  /* Pinta la sección «Diccionarios» para un número Strong (H2617, G26) dentro de «cont».
     opts.onStrong(cod): qué hacer al tocar otro número dentro de un diccionario.
     opts.sinStrong: no repetir la pestaña Strong (cuando la página ya muestra esa definición). */
  // Diccionarios temáticos (Easton, Smith, Fausset, Hastings, Hawker, Nave, Torrey): artículos traducidos enlazados a un número Strong.
  function temaArt(d, tp){
    return Promise.all([json(BASE+"temas/"+d+".json"), json(BASE+"temas/"+d+"-es.json"), json(BASE+"temas/indice.json")]).then(function(r){
      var en=r[0][tp], es=r[1][tp], I=r[2]; if(!en||!es) return null;
      return {d:{id:"tema-"+d+"-"+tp, n:I.nombres[d]+": "+es.t, fuente:I.fuentes[d], tema:true}, en:[[tp, en.join("\n")]], es:[[es.t, es.p.join("\n")]]};
    });
  }
  function temas(cod){
    return json(BASE+"temas/strong.json").then(function(m){ var l=m[cod]||[]; return Promise.all(l.map(function(x){ return temaArt(x[0],x[1]).catch(function(){ return null; }); })); })
      .then(function(l){ return l.filter(Boolean); });
  }
  function render(cont, cod, opts){
    opts=opts||{}; estilos(); cont.textContent="";
    var raiz=el("div","pd"); cont.append(raiz);
    raiz.append(el("p","pd-t","Diccionarios · "+cod));
    var chips=el("div","pd-chips"), idioma=el("div","pd-lang"), box=el("div","pd-box"), fuente=el("p","pd-fuente");
    chips.setAttribute("role","tablist"); chips.setAttribute("aria-label","Diccionarios");
    raiz.append(chips, idioma, box, fuente);
    box.textContent="Cargando…";
    var lista=DICS.filter(function(d){ return d.pref.indexOf(cod[0])>=0 && !(opts.sinStrong && d.id==="strong"); });
    Promise.all([Promise.all(lista.map(function(d){ return cargar(d,cod).catch(function(){ return {}; }); })), temas(cod).catch(function(){ return []; })]).then(function(rr){
      var res=rr[0], items=[], botones=[];
      lista.forEach(function(d,k){ var r=res[k]; if((r.en&&r.en.length)||(r.es&&r.es.length)) items.push({d:d, en:r.en, es:r.es}); });
      rr[1].forEach(function(t){ items.push(t); });
      if(!items.length){ raiz.remove(); return; }
      function elegir(it, b){
        botones.forEach(function(x){ var si=x===b?"true":"false"; x.setAttribute("aria-pressed",si); x.setAttribute("aria-selected",si); });
        var L=PLDic.idioma(); if(L==="es" && !(it.es&&it.es.length)) L="en"; if(L==="en" && !(it.en&&it.en.length)) L="es";
        idioma.textContent="";
        [["es","Español"],["en","Inglés"]].forEach(function(x){
          var hay=it[x[0]]&&it[x[0]].length; if(!hay) return;
          var lb=el("button","pd-chip",x[1]); lb.type="button"; lb.setAttribute("aria-pressed", x[0]===L?"true":"false");
          lb.onclick=function(){ PLDic.idioma(x[0]); elegir(it,b); }; idioma.append(lb);
        });
        box.textContent=""; box.scrollTop=0;
        var v=it[L];
        if(Array.isArray(v)) v.forEach(function(a){ var art=el("div","pd-art"); if(v.length>1||it.d.id!=="strong") art.append(el("h4",null,a[0])); texto(art,a[1],opts.onStrong,L); box.append(art); });
        else texto(box, v, opts.onStrong, L);
        fuente.textContent=it.d.fuente+(L==="es"?" Traducción al español: Primera Línea.":"");
      }
      items.forEach(function(it){
        var b=el("button","pd-chip",it.d.n); b.type="button"; b.setAttribute("role","tab"); b.setAttribute("aria-pressed","false");
        b.onclick=function(){ elegir(it,b); }; botones.push(b); chips.append(b);
      });
      elegir(items[0], botones[0]);
    });
  }
  function idioma(v){ try{ if(v) localStorage.setItem("pl-dic-lang",v); return localStorage.getItem("pl-dic-lang")||"es"; }catch(e){ return v||"es"; } }

  window.PLDic={render:render, idioma:idioma, lista:DICS, temaArt:temaArt, texto:texto};
})();
