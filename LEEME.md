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

## Publicación

Cada cambio que llega a GitHub se publica solo (`.github/workflows/publicar.yml`) en
https://danilo-ds7.github.io/primera-linea/. Para usar un dominio propio (.cl o .com), se configura en
Settings → Pages → Custom domain y en los DNS del proveedor del dominio.
