# Primera Línea — regla para trabajar en este repo

- La única versión vigente del sitio y de la app es `main` de este repo. Siempre partir de `main` actualizado; nunca de un ZIP (`primera-linea.zip`, `lector-app.zip`), de la vista previa (artifact) ni de una copia de otra conversación.
- Nada queda solo en la vista previa o en un ZIP: lo que no está en `main` no existe para el público ni para el celular. La entrega es el push.
- Antes del push: `git fetch` + `rebase` sobre `origin/main`, conservando los cambios de otras conversaciones.
- En cada cambio de la app, subir la versión de caché en `app/sw.js` (`lector-vN` → `lector-vN+1`). No quitar `cache: "no-cache"` ni `updateViaCache: "none"`.
- La entrega termina cuando la Action "Publicar sitio" está en verde y el cambio se ve en https://danilo-ds7.github.io/primera-linea/ y en la app (`/app/`), también a 390 px.
- Si los léxicos de la app cambian, volver a correr `python3 scripts/raices.py` (raíces BDB).

Detalle completo: documento "REGLA - Publicacion automatica" del proyecto de Claude.
