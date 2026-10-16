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
