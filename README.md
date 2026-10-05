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

Para descargar los datos se utilizó "scripts/download_data.py", donde se obtienen los archivos públicados para taxis amarillos y taxis verdes del año 2026. 

Se debe de tener el ambiente levantado con Docker compose: bash docker compose up --build 

En la otra terminal, desde la carpeta de raíz del proyecto se hizo la descarga completa con: docker compose exec lab python scripts/download_data.py. 

También permitió descargar un solo tipo de taxi: 
docker compose exec lab python scripts/download_data.py --taxi yellow.
docker compose exec lab python scripts/download_data.py --taxi green. 

Los archivos descargados se almacenan en: dat/raw/<tipo>/2026/

En la ejecución, se descargó 16 archivos, 8 de taxis amarillos, 8 de taxis verdes correspondientes a cada mes del 2026 desde enero hasta agosto, ya que de septiembre a diciembre aun no se han publicado, obteniendo: 

descargados   : 16
ya existian   : 0
no publicados : 8
fallidos: 0

Para verificar si los archivos fueron descargados de forma correcta: docker compose exec lab bash -ln "find data/raw -type f -name '*.parquet'"

El resultado mostro que si descargó el conjunto de datos completamente.

Consultar de forma directa un archivo parquet implica que DuckDB lee los datos desde el archivo almacenado en el disco sin necesidad de importarlo previamente a una tabla de base de datos. Y resulta útil para gran volumen de datos evitando duplicar información, reduce el uso de almacenamiento y se puede ejecutar consultas exploratorias de forma rápida sobre los archivos originales. 
## Como ejecutar el analisis

El análisis exploratorio de los archivos Parquet se ejecuta con ejercicio3.py consultando directamente la cantidad de archivos disponibles, cantidad de registros, las columnas y tipos de datos y una muestra de registros y posibles problemas de calidad. 

Se notó  registros con distancia menor o igual a cero y hay montos negativos, por lo que estos datos deberan revisarse antes de usarse en el análisis finales. 

## Como reproducir los benchmarks

<!-- TODO (Ejercicio 6) -->

## Como generar los resultados principales

<!-- TODO -->
