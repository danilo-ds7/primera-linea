# Lector · Primera Línea (app para celular)

App web instalable (PWA) dentro del sitio. Se abre en `app/index.html`; desde el celular, "Agregar a pantalla de inicio".

- **Estudio:** cuatro lecturas (histórica, filológica, teológica, literaria) y pasajes paralelos, desde `estudios/`.
- **Raíces (método BDB):** al tocar una palabra hebrea o griega, la app muestra su raíz (en hebreo, la raíz de tres consonantes, p. ej. ש־ל־ם) y debajo toda la familia de palabras que derivan de ella, con su número Strong y cómo la traduce Reina-Valera. La lectura filológica del estudio muestra lo mismo en cada palabra.
- **Comparación filológica:** versiones en paralelo (`app/index.html#comparar`), con los textos de `biblias/` y las notas de `comparaciones/notas.json`.
- **Modo de lectura:** claro, medio u oscuro.

## Agregar un estudio
1. Crea `estudios/<id>.json` con la misma estructura de `estudios/isaias-57-15.json`.
2. Agrégalo a la lista de `estudios/index.json`.
3. En `sw.js`, sube la versión (por ejemplo `lector-v4` → `lector-v5`).

## Archivos
| Archivo | Para qué sirve |
|---|---|
| `index.html` | La app. |
| `manifest.webmanifest` | Nombre, colores e íconos de la app instalada. |
| `sw.js` | Guarda la app y los estudios para usarlos sin conexión. |
| `estudios/` | Estudios preparados (uno por archivo) y su lista. |
| `biblias/` | Textos de dominio público por versión, en ocho grupos de libros (`g1` a `g8`). |
| `paralelos/` | Treasury of Scripture Knowledge (pasajes paralelos), por grupo. |
| `morfo/` | Morfología y números Strong (hebreo y griego) y léxicos. |
| `comparaciones/notas.json` | Notas filológicas de la comparación. |
| `iconos/` | Íconos de la app. |

## Raíces y familias
Se calculan con `scripts/raices.py` desde la derivación de Strong ("from H7999") y quedan guardadas en `morfo/lex-h.json` y `morfo/lex-g.json` (campos `rz`, la raíz, y `fz`, la familia). Si se reemplazan los léxicos, vuelve a correr `python3 scripts/raices.py`.
