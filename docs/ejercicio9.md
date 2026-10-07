# Ejercicio 9: Discusion

## 9.1 ¿Que caracteristicas de DuckDB resultaron mas utiles?

- **Consultar Parquet directamente** (`read_parquet` con globs recursivos
  como `data/raw/yellow/**/*.parquet` y `union_by_name=true`) sin necesidad
  de un paso de carga/ETL previo. Esto permitio pasar de "archivos nuevos en
  disco" a "consulta SQL" sin escribir codigo de ingesta.
- **SQL completo dentro de un proceso Python embebido**: funciones de fecha
  (`date_trunc`, `hour`, `isodow`, `dayname`), `quantile_cont`,
  `FILTER (WHERE ...)` dentro de agregaciones, y `GROUP BY ALL`. Permitieron
  expresar el analisis exploratorio completo (Ejercicios 3-4) sin salir de
  SQL ni pasar por pandas.
- **Vistas encadenadas** (`yellow_raw`/`green_raw` -> `trips` -> `trips_clean`
  -> `trips_tbl`) para separar la union de fuentes, el renombrado de columnas
  y la limpieza, cada una como una capa independiente y reutilizable.
- **La opcion de materializar una tabla** (`CREATE TABLE AS SELECT`) cuando
  convenia, sin cambiar el motor ni el lenguaje de consulta.
- **Un driver JDBC oficial de la comunidad** que permitio conectar Metabase
  directamente al archivo `.duckdb` para el tablero del Ejercicio 7, sin
  exportar datos a otra base.

## 9.2 Ventajas y limitaciones de consultar Parquet directamente

**Ventajas:** no duplica los datos (se consulta el mismo archivo que se
descargo), es la opcion mas simple para explorar datos nuevos apenas llegan,
y escala razonablemente bien gracias al pushdown de filtros y columnas de
DuckDB (Ejercicio 3).

**Limitaciones (medidas en el Ejercicio 6):** cada consulta recalcula desde
cero cualquier filtro o limpieza (en nuestro caso, la vista `trips_clean`),
lo que impuso un costo base de ~1-2 segundos incluso para una consulta
trivial sobre el conjunto completo. Con consultas repetidas (como las de un
tablero), ese costo se paga una y otra vez.

## 9.3 Ventajas y limitaciones de las tablas materializadas

**Ventajas:** en el benchmark del Ejercicio 6/8, la tabla materializada fue
entre 1.8x y 366x mas rapida que Parquet segun la consulta, porque ya tiene
la limpieza aplicada y no necesita reabrir ni refiltrar los archivos origen.
Es la opcion correcta para un tablero que se consulta repetidamente.

**Limitaciones:** ocupa mas espacio en disco (+25-28% sobre el tamano de los
Parquet origen en nuestras corridas), hay que reconstruirla cada vez que
llegan datos nuevos (el costo de reconstruccion crecio de 7.51 s a 11.48 s al
pasar de 2 a 3 anios), materializarla requiere mas RAM de la que al principio
teniamos disponible (el contenedor fue terminado por el out-of-memory killer
con 2 GB asignados a Docker), y cualquier proceso externo con una conexion
abierta (en nuestro caso, Metabase) puede quedarse sirviendo datos viejos
tras una reconstruccion, si no se reinicia (ver `docs/ejercicio8.md`, 8.3).

## 9.4 Ventajas frente a cargar todo con Pandas

Pandas requeriria leer los ~2 GB de Parquet completos a memoria, mantener
todas las columnas (incluidas las que no se usan) y aplicar los filtros de
limpieza en cada ejecucion del script, sin pushdown de predicados ni de
columnas. DuckDB, en cambio, puede leer solo las columnas y los
grupos de filas que la consulta necesita, procesar los datos fuera de
memoria cuando no caben, y paralelizar automaticamente entre nucleos. En la
practica, esto significo poder consultar 113.6 millones de filas en segundos
con hardware modesto, algo que con Pandas habria exigido cargar el dataset
completo en RAM antes de poder hacer una sola agregacion.

## 9.5 Caracteristicas del diseno que permiten incorporar datos nuevos con cambios minimos

- Los globs recursivos (`data/raw/<tipo>/**/*.parquet`) no mencionan anios
  especificos: agregar 2025 o 2026 solo requiere que existan los archivos en
  esa carpeta.
- Las vistas y la tabla separan "union de fuentes" de "limpieza" de
  "analisis", asi que una consulta de indicador nunca referencia un anio.
- `scripts/download_data.py` es idempotente (omite archivos ya descargados),
  asi que incorporar un anio nuevo es cambiar una lista (`ANIOS`) y
  reejecutar el mismo comando.
- El tablero de Metabase se construyo apuntando a `trips_tbl` por nombre,
  no por consulta a archivos especificos, asi que las 8 tarjetas no
  necesitaron edicion alguna al pasar de 2 a 3 anios (solo un restart del
  servicio, ver 9.3).

## 9.6 Que deberia automatizarse en un sistema de produccion

- La deteccion y descarga de archivos nuevos (cron/scheduler en vez de
  ejecucion manual), ya que la TLC publica con semanas de atraso y de forma
  irregular.
- La materializacion **incremental** de la tabla (agregar solo los meses
  nuevos con `INSERT` o reconstruyendo por particion) en vez de borrar y
  recrear `trips_tbl` completa cada vez, porque el costo de reconstruccion
  crece con el volumen total, no con lo que realmente cambio.
- El refresco de conexiones de herramientas externas (Metabase) despues de
  actualizar los datos, para evitar el problema de archivo desactualizado
  detectado en el Ejercicio 8.
- Validaciones automaticas de calidad de datos (las que aqui se hicieron a
  mano en los Ejercicios 3-5: distancias no validas, montos negativos,
  fechas fuera de rango) como pruebas que corran en cada carga.

## 9.7 Decisiones de diseno importantes para la reproducibilidad

- Separar el codigo (versionado en Git) de los datos (excluidos via
  `.gitignore`, descargados siempre desde la fuente original).
- Hacer que el script de descarga sea idempotente y verificable (resumen de
  descargados/omitidos/no publicados/fallidos), en vez de asumir que "ya se
  corrio una vez" es suficiente evidencia.
- Documentar cada consulta SQL junto con su objetivo, su fuente de datos y
  la decision que motivo (este archivo, `docs/ejercicio7.md` y
  `docs/ejercicio8.md`), en vez de dejar las consultas sueltas en notebooks.
- Versionar el script que construye el tablero de Metabase
  (`scripts/ejercicio7_dashboard.py`) en vez de depender unicamente de clics
  manuales en la interfaz, que no quedan registrados en el repositorio.
- Fijar el ambiente con Docker Compose, incluyendo que la version de
  `duckdb` en `requirements.txt` coincida con la version del driver JDBC de
  Metabase (ver comentario en `metabase.Dockerfile`), para evitar
  incompatibilidades silenciosas entre el archivo `.duckdb` y quien lo lee.

## 9.8 Que aprendimos sobre datos grandes que no seria evidente con datasets pequenos

- **Los limites de memoria son reales y no triviales de diagnosticar**: con
  2 GB de RAM asignados a Docker, materializar ~69 millones de filas termino
  el proceso por out-of-memory sin un mensaje de error claro en la salida del
  script (hubo que inspeccionar `docker inspect` y el estado del contenedor
  para confirmarlo). Con un dataset de miles de filas esto nunca habria
  ocurrido.
- **Las conexiones persistentes a un archivo que cambia de contenido son una
  fuente de bugs silenciosos**: Metabase siguio sirviendo datos de la version
  anterior de `trips_tbl` tras incorporar 2025, sin ningun error, hasta
  reiniciar el servicio. Con un archivo pequeno que se abre y cierra rapido
  este problema pasa desapercibido.
- **Los problemas de calidad de datos solo se revelan agregando a escala**:
  encontramos 21-44 registros (de mas de 100 millones) con fechas de
  recogida en anios como 2001, 2002, 2007-2009, 2023 o 2025 "adelantado",
  mezclados dentro de archivos de otro anio. En un dataset chico se detectan
  revisando filas a simple vista; aqui solo aparecieron al agrupar por
  `year(pickup)` y comparar contra el anio del archivo.
- **El costo de reconstruir una tabla crece con el volumen total, no con lo
  que cambio**: pasar de 2 a 3 anios (+65% de filas) hizo que el tiempo de
  materializacion subiera de 7.51 s a 11.48 s, pese a que "solo" se agrego un
  anio. En produccion, esto empuja a disenar actualizaciones incrementales
  en vez de recrear todo cada vez, algo que no se justifica con datasets
  pequenos.
