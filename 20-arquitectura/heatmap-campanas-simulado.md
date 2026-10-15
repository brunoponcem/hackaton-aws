---
tipo: implementacion
fecha: 2026-10-15
responsable: codex
---
# Heatmap y despliegue simulado de campañas

Extensión de [[backend-embudo-contacto]], según [[contacto-y-campanas]] y [[0008-heatmap-campanas-sinteticas]]. Disponible en **http://localhost:8502** y en Detectar e invitar del portal. No necesita AWS, claves de mapas ni geocodificación.

## Recorrido de demostración

1. Nueva simulación → Sin respuestas → Inicializar embudo → Avanzar 19 días.
2. Ir a «Campañas territoriales · vista de ejecutivos». Las 92 personas detectadas quedan repartidas entre seis provincias sintéticas.
3. Arrastrar o ampliar el mapa; pasar sobre un círculo muestra provincia, personas y puntaje demo. Calor y tamaño representan volumen absoluto, no tasas ni densidad poblacional. La posición es una ciudad de referencia aproximada, no un centroide provincial ni un domicilio.
4. Filtrar por región y revisar el ranking. «Todo el seguimiento activo» es diagnóstico; no habilita propuestas de despliegue.
5. Elegir provincia, personal y capacidad diaria para estimar jornadas. Descargar ranking CSV o propuesta JSON. No se guarda una campaña, se agenda ni se despachan funcionarios. El responsable decide lugar y fechas.
6. Iniciar o declinar en el inspector y observar el mapa/ranking. Una provincia con menos de cinco casos desaparece de mapa, ranking, selectores y exportaciones agregadas. Es un umbral de demo, no una garantía de anonimato ante consultas repetidas.

La base inicial puede conservar respuestas simuladas anteriores. Para ver cobertura completa usar el escenario nuevo sin respuestas; no se inflan los datos para llenar el mapa.

## Datos RSH: qué existe y qué no

El RSH contempla domicilio e información del hogar según sus [preguntas frecuentes oficiales](https://www.registrosocial.gob.cl/preguntas-frecuentes-web). **El `rsh.csv` del hackatón no contiene comuna, provincia ni coordenadas**; tampoco `residencia.csv` permite geolocalizar domicilios. No hay conexión con un RSH real.

Esta demo une perfiles por RUN con `contacto.py`, exclusivamente sintético: seis combinaciones región/provincia/comuna, asignadas reproduciblemente, sin representar distribución real. No se infiere ubicación del tramo CSE o percentil PFP. Una integración real requeriría fuente territorial autorizada, fecha de actualización, catálogo comuna → provincia y revisión institucional de su uso. No se presupone una API pública de domicilios.

## Agregación y prioridad

`src/app/ruta/campanas.py` consume el snapshot sin modificar estados ni autorizaciones. Por defecto selecciona `status=active` y `stage=4`: quienes no iniciaron trámite, aunque hayan abierto o contestado. Excluye inicios y rechazos; omite territorios desconocidos y contactos no sintéticos.

Agrupa por región/provincia y suprime grupos menores de 5 **antes de devolverlos al frontend**. No devuelve RUN, nombres, direcciones ni integrantes. La vista convive con el inspector individual de la demo; no implementa autenticación institucional ni reemplaza controles de acceso de producción.

Puntaje **ilustrativo, no institucional** por persona: 1 base + 2 si el motor indica que podría solicitar PGU + 1 si falta antecedente PGU + 1 si hay hito de edad legal, apertura o acceso PGU entre hoy y 90 días. Evaluación del motor a la fecha inicial y reloj simulado para cercanía del hito. Sin perfil disponible solo suma base. Ranking por suma descendente, luego volumen y territorio para desempate determinista. No declara PGU adjudicada o impaga. Jornadas = `ceil(personas / (funcionarios × capacidad diaria))`.

## Cartografía y límites

`ui_campanas.py` usa pydeck (incluido con Streamlit): HeatmapLayer, círculos y etiquetas sobre contornos locales. `assets/campaign-basemap.geojson` extrae Chile, Argentina, Bolivia y Perú de [Natural Earth 1:110m](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson), descargado el 15-10-2026, reducido a nombre y geometría. [Dominio público](https://www.naturalearthdata.com/about/terms-of-use/). No son límites provinciales ni cartografía oficial. Las seis posiciones en `PROVINCE_POINTS` son aproximaciones de ciudades; no se dispersan puntos para aparentar residencias.

No usa proveedores de teselas durante la ejecución. El mapa necesita WebGL; ranking y descargas permiten revisar los mismos agregados. Quedan pendientes cobertura de 56 provincias, localización validada, asignación de equipos, agenda, rutas, despacho, alertas y CESFAM.

## Verificación

`uv run --group app pytest` → **90 tests pasan**. Incluye supresión a 4/5, terminales, territorios desconocidos, ausencia de identificadores, prioridad trazable, capacidad y recorrido UI con reloj y filtros. `uv run --group app python src/app/verificar.py` → TODO OK sobre 500 perfiles. Ruff check/format en módulos nuevos. Ver [[board-clemente]].
