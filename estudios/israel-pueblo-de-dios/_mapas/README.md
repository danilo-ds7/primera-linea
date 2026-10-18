# Mapas de la serie Israel

`mapas.py` dibuja los mapas con cartografía real (costas, lagos y ríos GSHHS/WDB de Basemap y relieve sombreado; elevación y batimetría ETOPO1 a 10′: `earth-topography-10arcmin.nc` de fatiando-data, descargar junto al script), en estilo moderno: mar en azules, verdes en la Media Luna Fértil, arena en desiertos; trayectorias con degradado, flechas y paradas numeradas. `mapas_datos.py` define cada mapa.

    pip install basemap basemap-data-hires netCDF4 scipy pillow numpy matplotlib
    python3 mapas.py patriarcas --out ../01_Abraham_Exodo

Genera `crops/mapa_<id>.pdf` y `crops/mapa_<id>_leyenda.tex` (presentación) y `mapa_<id>.png` (capítulo y web). La carpeta empieza con `_`: el sitio no la publica como estudio.
