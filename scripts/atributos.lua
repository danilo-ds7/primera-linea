-- Ajustes de la conversión LaTeX -> página web de la serie «Atributos de Dios».

local cajas = {
  cita = true, nota = true, filologia = true, verso = true, fuente = true,
  hebverso = true, refapa = true, resumen = true, rotulo = true,
}

-- Hebreo y griego con su tipografía del sitio
function Span(el)
  local lang = el.attributes.lang
  if lang then
    if lang:match("^he") then
      el.classes:insert("heb")
    elseif lang:match("^el") or lang:match("^grc") then
      el.classes:insert("grk")
      el.attributes.lang = "grc"
    end
  end
  -- los colores del PDF no se trasladan a la web
  if el.attributes.style and el.attributes.style:match("^color") then
    el.attributes.style = nil
    local sin_atributos = true
    for _ in pairs(el.attributes) do sin_atributos = false; break end
    if #el.classes == 0 and sin_atributos then
      return el.content
    end
  end
  return el
end

function Div(el)
  for i, c in ipairs(el.classes) do
    if cajas[c] then
      el.classes[i] = "tex-" .. c
    end
  end
  if el.classes:includes("center") then
    el.classes = pandoc.List({ "tex-centro" })
  end
  return el
end

-- Las figuras TikZ ocupan el ancho del texto
function Image(el)
  el.caption = {}
  if el.src:match("%.svg$") then
    el.classes:insert("tex-fig")
    el.attributes.width = nil
    el.attributes.height = nil
  end
  return el
end

-- Los encabezados del PDF numerados no llevan número en la web; los * quedan igual
function Header(el)
  el.classes = el.classes:filter(function(c) return c ~= "unnumbered" end)
  return el
end

-- Versalitas (SEÑOR) como en el PDF
function SmallCaps(el)
  return pandoc.Span(el.content, { class = "smallcaps" })
end

-- Tablas: si la primera fila está en negrita, es el encabezado
local function fila_en_negrita(row)
  for _, cell in ipairs(row.cells) do
    local blocks = cell.contents
    if #blocks ~= 1 or blocks[1].t ~= "Plain" and blocks[1].t ~= "Para" then return false end
    local inl = blocks[1].content
    if #inl ~= 1 or inl[1].t ~= "Strong" then return false end
  end
  return #row.cells > 0
end

function Table(el)
  if #el.head.rows == 0 and #el.bodies > 0 and #el.bodies[1].body > 0 then
    local primera = el.bodies[1].body[1]
    if fila_en_negrita(primera) then
      for _, cell in ipairs(primera.cells) do
        cell.contents = pandoc.Blocks({ pandoc.Plain(pandoc.utils.blocks_to_inlines(cell.contents)[1].content) })
      end
      el.head.rows = { primera }
      el.bodies[1].body:remove(1)
    end
  end
  return el
end

-- Sin pie automático: el pie viene escrito en el propio texto (Figura N. ...)
function Figure(el)
  local imgs = {}
  el.content:walk({ Image = function(i) table.insert(imgs, i) end })
  if #imgs == 1 then return pandoc.Para({ imgs[1] }) end
  return el
end

-- Referencias: se ordenan alfabéticamente (APA) y quedan en una pestaña desplegable
local titulos_ref = {
  ["referencias"] = true, ["referencias bibliograficas"] = true,
  ["bibliografia"] = true, ["obras citadas"] = true,
}

local acentos = {
  ["á"]="a", ["é"]="e", ["í"]="i", ["ó"]="o", ["ú"]="u", ["ü"]="u", ["ñ"]="n",
  ["Á"]="a", ["É"]="e", ["Í"]="i", ["Ó"]="o", ["Ú"]="u", ["Ü"]="u", ["Ñ"]="n",
  ["à"]="a", ["è"]="e", ["ì"]="i", ["ò"]="o", ["ù"]="u", ["ç"]="c", ["ö"]="o", ["ä"]="a",
}

local function normal(t)
  for k, v in pairs(acentos) do t = t:gsub(k, v) end
  t = t:lower():gsub("^[%s%p]+", "")
  -- APA: en obras sin autor se ignora el artículo inicial del título
  for _, art in ipairs({ "the ", "an ", "a ", "el ", "la ", "los ", "las ", "lo ", "un ", "una " }) do
    if t:sub(1, #art) == art then t = t:sub(#art + 1); break end
  end
  return t
end

-- Separa el bloque de referencias en entradas individuales
local function entradas(bloques)
  local lista = {}
  for _, b in ipairs(bloques) do
    if b.t == "BulletList" or b.t == "OrderedList" then
      for _, item in ipairs(b.content) do table.insert(lista, pandoc.Div(item, { class = "tex-refapa" })) end
    elseif b.t == "Div" and not b.classes:includes("tex-refapa") and #b.content > 1 then
      for _, x in ipairs(entradas(b.content)) do table.insert(lista, x) end
    elseif b.t == "Para" or b.t == "Plain" then
      table.insert(lista, pandoc.Div({ b }, { class = "tex-refapa" }))
    elseif b.t ~= "HorizontalRule" then
      table.insert(lista, b)
    end
  end
  return lista
end

local n_refs = 0
local function plegable(bloques)
  n_refs = n_refs + 1
  local lista = entradas(bloques)
  local claves = {}
  for i, e in ipairs(lista) do claves[e] = { normal(pandoc.utils.stringify(e)), i } end
  table.sort(lista, function(a, b)
    local x, y = claves[a], claves[b]
    if x[1] == y[1] then return x[2] < y[2] end
    return x[1] < y[1]
  end)
  local out = pandoc.List({ pandoc.RawBlock("html",
    '<details class="plegable plegable-refs" id="referencias' .. (n_refs > 1 and ('-' .. n_refs) or '') .. '"><summary>Referencias <span class="refs-n">' ..
    #lista .. '</span></summary><div class="plegable-body refs-lista">') })
  out:extend(lista)
  out:insert(pandoc.RawBlock("html", "</div></details>"))
  return out
end

function Pandoc(doc)
  local nuevos, i, b = pandoc.List(), 1, doc.blocks
  while i <= #b do
    local blk = b[i]
    if blk.t == "Header" and titulos_ref[normal(pandoc.utils.stringify(blk))] then
      local j, cuerpo = i + 1, pandoc.List()
      while j <= #b and not (b[j].t == "Header" and b[j].level <= blk.level) do
        cuerpo:insert(b[j]); j = j + 1
      end
      if #cuerpo > 0 then nuevos:extend(plegable(cuerpo)) end
      i = j
    else
      nuevos:insert(blk); i = i + 1
    end
  end
  doc.blocks = nuevos
  return doc
end
