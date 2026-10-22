# Primera Línea (Quarto)

1. Instala Quarto: https://quarto.org/docs/get-started/
2. Abre esta carpeta en VS Code o en la Terminal.
3. Vista previa en vivo: `quarto preview`
4. Generar el sitio: `quarto render` (queda en `_site/`)
5. Publicar: basta con subir los cambios a GitHub (se publica solo)

Dónde editar:
- `index.qmd`: página de inicio (textos en Markdown).
- `estudios/`: un archivo `.qmd` por estudio. Copia `plantilla-estudio.qmd` para crear uno nuevo; aparece solo en la página Estudios.
- `referencias.bib`: tus fuentes. Se citan con `[@clave]` y salen en formato APA.
- `styles.scss`: colores y tipografías.
- `images/`: fotos.

## Serie «Atributos de Dios»

Los estudios se escriben en LaTeX en `estudios/atributos-de-dios/` (desde el proyecto de estudio).
Antes de cada `quarto render` o `quarto preview`, `scripts/atributos.py` compila los PDF con XeLaTeX
y genera las páginas en `atributos/` (carpeta generada: no editarla a mano).
Para verlo en tu computador necesitas Quarto y XeLaTeX (MacTeX).

## Serie «Festividades santas»

Igual que Atributos: los estudios en LaTeX van en `estudios/fiestas-santas/` (desde el proyecto
de estudio «Fiestas Santas») y el mismo `scripts/atributos.py` genera las páginas en `festividades/`
(carpeta generada) y las muestra en la página **Festividades santas** (`festividades.qmd`).

## Serie «Israel y su restauración»

Igual que Atributos: los estudios en LaTeX van en `estudios/israel-pueblo-de-dios/` (desde el proyecto
de estudio «Israel») y el mismo `scripts/atributos.py` genera las páginas en `israel/`
(carpeta generada) y las muestra en la página **Israel y su restauración** (`israel.qmd`).

## Predicaciones

Las predicaciones van listas, en PDF y audio, en `estudios/predicaciones/`, separadas por tipo
(`biograficas/`, `tematicas/`, `autoayuda/`, `otras/`) y las series en `series/`. Antes de cada render,
`scripts/predicaciones.py` genera sus páginas en `predicaciones/` (carpeta generada: no editarla a mano)
y las muestra en la página **Predicaciones** (`predicaciones.qmd`). Detalle en `estudios/predicaciones/README.md`.

## Líneas de tiempo

Cada línea de tiempo es un HTML interactivo (skill «linea-de-tiempo») guardado como fuente en
`estudios/lineas/<slug>.html`, con sus figuras TikZ en `estudios/lineas/<slug>/img/` y sus fuentes
(Latin Modern, GFS Porson) en `estudios/lineas/<slug>/fonts/`. Antes de cada render, `scripts/lineas.py`
integra cada línea en su página `lineas/<slug>.qmd` (acota el CSS, pasa la pantalla completa al
contenedor) y la muestra en **Líneas de tiempo** (`lineas.qmd`). Los mapas de atlas, la portada y las
cronologías se dibujan en TikZ con `python3 scripts/lineas_tikz.py <slug>` (XeLaTeX + pdftocairo),
que anota en el HTML las rutas y los puntos tocables; hay que correrlo cada vez que cambian los
mapas o los datos de la línea, y subir los SVG resultantes.

## Publicación

Cada cambio que llega a GitHub se publica solo (`.github/workflows/publicar.yml`) en
https://primera-linea.cl (dominio propio, inscrito en NIC Chile; DNS en Cloudflare con registros A a
GitHub Pages y `www` → danilo-ds7.github.io, sin proxy; Settings → Pages → Custom domain = primera-linea.cl).
La dirección antigua https://danilo-ds7.github.io/primera-linea/ redirige al dominio.
