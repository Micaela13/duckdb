# Lab 8 - DuckDB

Repositorio base del laboratorio 8 del curso **CC3084 - Data Science**
(Universidad del Valle de Guatemala, Ciclo 2, 2026).

Este es el repositorio **proporcionado por el docente**. Contiene la estructura
del proyecto, el ambiente de ejecucion basado en Docker y un script que descarga
los datos de **2026**. Todo lo demas debe ser construido por cada equipo.

## Trabajo con fork

El laboratorio se desarrolla y se entrega sobre un **fork** de este repositorio.
No se trabaja directamente sobre el repositorio del docente.

1. Realice un fork de este repositorio:
   <https://github.com/menene/duckdb>

2. Clone **su propio fork** (no el del docente):

   ```bash
   git clone https://github.com/<su-usuario>/duckdb.git
   cd duckdb
   ```

3. Opcional, para recibir correcciones publicadas por el docente:

   ```bash
   git remote add upstream https://github.com/menene/duckdb.git
   git fetch upstream
   ```

Realice commits frecuentes y descriptivos: el historial del repositorio es parte
de la evaluacion. **La entrega del laboratorio es la URL de su fork.**

## Estructura

```text
duckdb/
|
+-- data/
|   +-- raw/
|   +-- processed/
|
+-- notebooks/
|
+-- scripts/
|
+-- sql/
|
+-- docs/
|
+-- Dockerfile
+-- metabase.Dockerfile
+-- docker-compose.yml
+-- README.md
```

## Requisitos

- Docker, con Docker Compose
- Git

La primera construccion del ambiente descarga varios cientos de MB y puede
tardar algunos minutos.

Considere el espacio en disco: las imagenes de Docker ocupan unos 3 GB y los
datos de los tres anios del laboratorio superan 1.5 GB, a los que se suma la
base materializada del Ejercicio 6. Se recomienda tener al menos 10 GB libres.

Si el puerto 8888 (Jupyter) o 3000 (Metabase) ya estan en uso por otro
proyecto en su maquina, cambie el mapeo en `docker-compose.yml` (por ejemplo
`"127.0.0.1:8891:8888"`) o libere el puerto antes de levantar el ambiente.

## Datos

El repositorio incluye `scripts/download_data.py`, que descarga los archivos de
2026 publicados por la TLC (`--help` muestra las opciones disponibles). Los
archivos se guardan en `data/raw/<tipo>/<anio>/`.

La TLC publica cada mes con varias semanas de atraso, por lo que los ultimos
meses de 2026 todavia no existen. El script consulta al servidor que meses estan
publicados, de modo que vuelve a ejecutarse sin problema conforme aparezcan
nuevos archivos.

Los datos descargados **no deben incluirse en el repositorio Git**. El archivo
`.gitignore` ya esta configurado para evitarlo.

Fuente de datos: NYC TLC Trip Record Data
<https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page>

Dentro de los contenedores, la carpeta `data/` del proyecto esta montada en
`/workspace/data`. Esa es la ruta que deben usar las herramientas que corren
dentro del ambiente, no la ruta de su computadora.

> **Nota sobre DuckDB:** un archivo `.duckdb` admite un solo proceso con permiso
> de escritura a la vez. Si conecta una herramienta externa a su base de datos,
> use el modo de solo lectura (`read_only`) en esa conexion; de lo contrario los
> demas procesos no podran abrir el archivo.

## Material a entregar

Al finalizar, su fork debe contener:

- el codigo fuente modificado y los scripts de descarga;
- las consultas SQL desarrolladas;
- el notebook o notebooks utilizados;
- la documentacion de las consultas;
- los scripts utilizados para los benchmarks;
- el codigo de los indicadores y visualizaciones;
- el tablero o la evidencia del tablero desarrollado;
- este `README.md`, completado segun la siguiente seccion.

Los archivos de datos descargados **no** deben incluirse.

---

# Documentacion del equipo

Las siguientes secciones deben ser completadas por cada equipo. El README final
debe permitir que una persona que no participo en el desarrollo pueda levantar el
ambiente, descargar los datos, ejecutar el analisis, reproducir los benchmarks y
generar los resultados principales.

## Como levantar el ambiente

Se clona el fork del repositorio, el proyecto utiliza Docker compose, por lo que se debe de tener abirto Docker desktop abierto. La primera ejecución Docker descarga y construye las imagenes necesarias. Se verifica en la terminal si los servicios funcionan, en el que se verifica que estaban activas.

Utilizar un abiente reproducible es de suma importancia, ya que permite a los integrantes ejecutar el proyecto con las mismas herramientas y configuraciones; reduciendo erorres y que el análisis pueda repetirse. 

## Como descargar los datos

Los datos se descargan con `scripts/download_data.py` (yellow y green de los
anios en `ANIOS`: 2024, 2025 y 2026).

Con el ambiente levantado (`docker compose up -d`), desde otra terminal y en
la raiz del proyecto:

```bash
docker compose exec lab python scripts/download_data.py
```

También permite descargar un solo tipo de taxi o anios especificos:

```bash
docker compose exec lab python scripts/download_data.py --taxi yellow
docker compose exec lab python scripts/download_data.py --anios 2024
```

Los archivos se guardan en `data/raw/<tipo>/<anio>/`, y la tabla de zonas en
`data/raw/taxi_zone_lookup.csv`. Un archivo que ya existe localmente no se
vuelve a descargar (el resumen final distingue `descargados` de
`ya existian`).

En la ejecucion de este equipo se obtuvieron 64 archivos (12 meses x 2 tipos
de 2024, 12 meses x 2 tipos de 2025, mas los meses de 2026 publicados hasta
agosto x 2 tipos) y la tabla de zonas, sin fallos. Para verificar:

```bash
docker compose exec lab bash -lc "find data/raw -type f -name '*.parquet' | wc -l"
```

Consultar de forma directa un archivo Parquet implica que DuckDB lee los
datos desde el archivo almacenado en disco sin necesidad de importarlo antes
a una tabla. Es util cuando el volumen de datos es grande porque evita
duplicar informacion, reduce el uso de almacenamiento y permite ejecutar
consultas exploratorias de forma rapida sobre los archivos originales.

## Como ejecutar el analisis

Cada ejercicio tiene su propio script en `scripts/`, pensado para correr
dentro del contenedor `lab`:

```bash
docker compose exec lab python scripts/ejercicio3.py   # exploracion inicial de los Parquet
docker compose exec lab python scripts/ejercicio4.py   # analisis exploratorio (temporal, pago, atipicos)
docker compose exec lab python scripts/ejercicio5.py   # validacion de la incorporacion de anios nuevos
docker compose exec lab python scripts/ejercicio6.py   # benchmark Parquet vs tabla materializada
docker compose exec lab python scripts/ejercicio7.py   # valida las consultas de los indicadores (Ejercicio 7)
```

El Ejercicio 3 mostro registros con `trip_distance <= 0` y montos negativos;
esos casos se excluyen en la vista `trips_clean` definida en los Ejercicios
4-6 (ver `docs/ejercicio7.md` y `docs/ejercicio8.md` para la lista completa de
hallazgos de calidad de datos sobre el conjunto ampliado a tres anios).

> **Importante:** si reconstruye `trips_tbl` (`ejercicio6.py` borra y recrea
> `lab.duckdb`) despues de haber conectado Metabase, reinicie ese servicio
> para que tome el archivo nuevo: `docker compose restart metabase`. Metabase
> mantiene una conexion abierta al archivo anterior y, sin el restart, sigue
> mostrando los datos previos aunque las consultas se vuelvan a ejecutar (ver
> `docs/ejercicio8.md`, seccion 8.3).

## Como reproducir los benchmarks

El benchmark del Ejercicio 6 compara consultar los Parquet directamente contra
una tabla materializada (`trips_tbl`) en `data/processed/lab.duckdb`. Se
ejecuta con:

```bash
docker compose exec lab python scripts/ejercicio6.py
```

El script crea la tabla, corre 6 consultas representativas sobre 4 volúmenes
de datos (1 mes, 3 meses, un año completo y todo el dataset), cada una 5 veces
(se reporta la mediana sin contar la primera ejecución), y guarda los
resultados en `docs/benchmark.csv` y `docs/benchmark.md`. El análisis se
documenta en `docs/06_consola.txt`.

> **Nota de memoria:** materializar ~69 millones de filas requiere varios GB
> de RAM disponibles para Docker. En este laboratorio el contenedor fue
> terminado por el out-of-memory killer con 2 GB asignados a la VM de Docker;
> se resolvió asignándole 8 GB (en Colima: `colima start --memory 8 --cpu 4`,
> lo que reinicia todos los contenedores Docker de la máquina). Si usa Docker
> Desktop, el equivalente es aumentar la memoria en Settings > Resources.

## Como generar los resultados principales

Con el ambiente levantado y los datos descargados:

1. Materializar la tabla (si no se ha hecho ya): `docker compose exec lab python scripts/ejercicio6.py`.
2. Abrir <http://localhost:3000> (Metabase, ya corre como parte de
   `docker compose up`) y completar el asistente de primer arranque (crear el
   usuario administrador). Es el unico paso manual: Metabase no permite
   crear ese usuario sin que el equipo elija su propio correo/clave.
3. `docker compose exec lab python scripts/ejercicio7_dashboard.py --email <correo> --password '<clave>'`
   crea, via la API de Metabase, la conexion de solo lectura a
   `data/processed/lab.duckdb`, las 8 preguntas documentadas en
   `sql/ejercicio7_indicadores.sql` y el tablero del Ejercicio 7. Es
   idempotente: si ya existen, los reutiliza.
4. Abrir la URL que imprime el script para ver el tablero. Los indicadores,
   su justificacion y la interpretacion de resultados estan en
   `docs/ejercicio7.md`; la evolucion 2024-2025-2026 y los hallazgos del
   conjunto completo estan en `docs/ejercicio8.md`.
5. Respuestas de la discusion final del laboratorio: `docs/ejercicio9.md`.
