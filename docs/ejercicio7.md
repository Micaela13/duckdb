# Ejercicio 7: Construccion de indicadores y visualizacion

Herramienta de visualizacion: **Metabase** (`http://localhost:3000`, servicio
`metabase` en `docker-compose.yml`), conectado en modo solo lectura a
`data/processed/lab.duckdb` (tabla `trips_tbl`, materializada en el
Ejercicio 6). El tablero se construye con `scripts/ejercicio7_dashboard.py`,
que usa la API de Metabase para crear la conexion, las 8 preguntas y el
tablero; las consultas SQL de cada indicador tambien quedan documentadas de
forma independiente en `sql/ejercicio7_indicadores.sql` y se validan con
`scripts/ejercicio7.py` (salida completa en `docs/07_consola.txt`).

## Como reproducir el tablero

1. `docker compose up -d` (si no esta corriendo).
2. Tener materializada la tabla: `docker compose exec lab python scripts/ejercicio6.py`.
3. Abrir <http://localhost:3000> y completar el asistente de primer arranque de
   Metabase (crear el usuario administrador). Este paso es manual porque
   Metabase no permite crearlo sin conocer de antemano el correo/clave que el
   equipo quiere usar.
4. `docker compose exec lab python scripts/ejercicio7_dashboard.py --email <correo> --password '<clave>'`
5. Abrir la URL que imprime el script (`http://localhost:3000/dashboard/<id>`).

El script es idempotente: si la base de datos o el tablero ya existen (por
nombre), los reutiliza en vez de duplicarlos.

## 7.1 Diez preguntas de analisis

1. ¿Como evoluciona el volumen de viajes mes a mes, y difiere la tendencia
   entre yellow y green?
2. ¿En que horas del dia se concentra la demanda de viajes?
3. ¿Que dias de la semana concentran mas viajes y como se reparten entre
   yellow y green?
4. ¿Como se distribuye la distancia de los viajes? ¿predominan los viajes
   cortos o los largos?
5. ¿Que metodo de pago predomina y cual deja, en promedio, mejor propina?
6. ¿Cuales son los boroughs de recogida con mas viajes?
7. ¿Que tarifa promedio y cuantos USD por milla cobra cada tipo de taxi?
8. ¿Como varia el porcentaje promedio de propina segun la hora del viaje?
9. ¿Hay registros cuya fecha de recogida cae fuera de los anios realmente
   descargados (2024 y 2026)? (apoya la discusion de calidad de datos, 9.8)
10. ¿Que tan frecuentes son los viajes de mas de 50 millas que sobreviven a la
    limpieza del Ejercicio 4? (posibles atipicos remanentes)

## 7.2-7.3 Indicadores, consultas y tipo de visualizacion

| # | Indicador (pregunta) | Visualizacion en Metabase | Consulta |
|---|---|---|---|
| 1 | Viajes por mes y tipo de taxi (P1) | Linea (una serie por taxi) | `sql/ejercicio7_indicadores.sql` Indicador 1 |
| 2 | Viajes por hora del dia (P2) | Barras | Indicador 2 |
| 3 | Viajes por dia de la semana y taxi (P3) | Barras apiladas | Indicador 3 |
| 4 | Distribucion de la distancia (P4) | Barras (histograma) | Indicador 4 |
| 5 | Metodo de pago y propina promedio (P5) | Barras agrupadas | Indicador 5 |
| 6 | Viajes por borough de recogida (P6) | Barras horizontales (ranking) | Indicador 6 |
| 7 | Tarifa, total y USD/milla por taxi (P7) | Tabla (KPI comparativo) | Indicador 7 |
| 8 | % de propina promedio por hora (P8) | Linea | Indicador 8 |

Las preguntas 9 y 10 se responden con consultas puntuales (ver
`scripts/ejercicio7.py`, "Pregunta 9" y "Pregunta 10") y alimentan la
discusion de calidad de datos (9.8) en vez de tener una tarjeta propia en el
tablero, porque son hallazgos de una sola cifra, no series para graficar.

## 7.4-7.5 Visualizaciones y tablero

Las 8 tarjetas se organizan en un tablero de 2 columnas x 4 filas
("Lab 8 - Indicadores de viajes de taxi (Ejercicio 7)"), agrupando temporal
(1-3), caracteristicas del viaje (4), pago (5, 8), geografia (6) y
comparacion yellow/green (1, 3, 7) para poder leerlos de forma conjunta.

## 7.6 Justificacion de los indicadores

- **Indicador 1 (linea, mensual):** es la forma estandar de mostrar una
  tendencia en el tiempo y de comparar dos series (yellow vs green)
  directamente superpuestas.
- **Indicador 2 (barras, por hora):** una variable categorica ciclica (0-23)
  se lee mejor en barras que en linea, y permite ubicar visualmente las horas
  pico.
- **Indicador 3 (barras apiladas, por dia):** apilar yellow+green por dia
  muestra el total diario y, dentro de cada barra, cuanto aporta cada tipo.
- **Indicador 4 (barras, histograma de distancia):** un histograma es la
  visualizacion canonica para ver la forma de una distribucion (sesgada a la
  derecha, con una posible moda secundaria).
- **Indicador 5 (barras agrupadas, pago):** compara dos dimensiones a la vez
  (metodo de pago x tipo de taxi) sobre una metrica continua (propina).
- **Indicador 6 (barras horizontales, boroughs):** un ranking de pocas
  categorias con nombres largos se lee mejor horizontal que vertical.
- **Indicador 7 (tabla, tarifas):** son solo 2 filas x 3 metricas; una tabla
  compacta comunica las cifras exactas mejor que un grafico.
- **Indicador 8 (linea, % propina por hora):** es una tasa (no un conteo) a
  lo largo de una variable ordenada (hora), por lo que una linea muestra
  mejor su tendencia que barras.

## 7.7 Documentacion de las consultas

Todas las consultas SQL usadas (las 8 del tablero mas las preguntas 9 y 10)
estan en `sql/ejercicio7_indicadores.sql`, con comentarios que indican el
indicador, la pregunta que responden y la visualizacion recomendada. La
version ejecutable y validada (contra `trips_tbl` en modo solo lectura) esta
en `scripts/ejercicio7.py`; su salida completa, usada para redactar la
interpretacion de abajo, quedo guardada en `docs/07_consola.txt`.

## 7.8 Interpretacion y hallazgos principales

> Nota: estos numeros corresponden al conjunto final de tres anios (2024,
> 2025 y 2026 hasta agosto) incorporado en el Ejercicio 8; las consultas y el
> tablero no cambiaron entre el Ejercicio 7 y el 8 (ver `docs/ejercicio8.md`
> 8.9/5.9 sobre por que no hizo falta modificarlas).

- **Yellow domina casi 75 a 1 sobre green.** En el periodo analizado (2024,
  2025 y 2026 hasta agosto) hubo 112.1 millones de viajes yellow contra 1.5
  millones green (Indicador 7). El servicio green, pensado para boroughs
  fuera de Manhattan, representa una fraccion marginal del volumen total.
- **La demanda tiene un patron horario claro con pico a las 18:00** (7.74
  millones de viajes acumulados en esa hora a lo largo de todo el periodo) y
  un minimo entre las 3:00 y las 5:00 (bajo 1 millon). Jueves y sabado son los
  dias con mas viajes para yellow, y domingo el mas bajo para ambos tipos
  (Indicadores 2 y 3).
- **Las propinas en efectivo aparecen siempre en 0.00 (Indicador 5).** Esto
  no significa que nadie pague propina en efectivo: la TLC solo registra la
  propina cuando se paga con tarjeta, porque el conductor la reporta en el
  sistema de pago electronico. Es una limitacion conocida del dataset, no un
  patron de comportamiento real, y se documenta aqui para no interpretarla
  como un hallazgo de negocio.
- **Manhattan concentra el 87.6% de las recogidas** (98.7 de 113.6 millones,
  Indicador 6); Queens es el segundo borough (9.4%), consistente con los
  aeropuertos JFK y LaGuardia. Alrededor de 244 mil viajes (0.21%) no se
  pudieron asociar a un borough conocido (`Unknown`/`N/A` en la tabla de
  zonas), un problema de calidad de datos menor pero no despreciable.
- **La distribucion de distancia tiene una moda secundaria alrededor de las
  16-17 millas** (Indicador 4: 819,509 y 1,227,892 viajes, muy por encima de
  los rangos vecinos de 13-15 millas). Esto coincide con la distancia
  aproximada entre Manhattan y el aeropuerto JFK, que tiene tarifa plana en
  NYC: es consistente con un volumen alto de viajes al aeropuerto, no con un
  error de datos.
- **Se encontraron registros con fecha de recogida muy fuera de rango**
  (Pregunta 9/5.8): ademas de los 44.7 millones de 2025 esperados, aparecen
  decenas de registros sueltos con anios como 2001, 2002, 2007-2009 o 2023
  dentro de archivos nominalmente de 2024/2025/2026. Son del orden de 0.0001%
  del total y no se filtran aparte, pero confirman un problema de calidad de
  datos preexistente en la fuente de la TLC (timestamps mal capturados), no
  un error introducido por el pipeline del laboratorio.
- **Persisten algunos viajes extremos tras la limpieza del Ejercicio 4**
  (Pregunta 10): 15,065 viajes yellow (0.0134%) y 141 green (0.0094%) superan
  las 50 millas. La limpieza actual solo descarta `trip_distance >= 100`, por
  lo que este rango (50-100 millas) sigue siendo parte del analisis; son
  pocos y no distorsionan los promedios, pero conviene tenerlos presentes si
  se calculan percentiles altos.
- **Yellow cobra, en promedio, mas que green** (tarifa promedio $20.28 vs
  $17.83, Indicador 7), pero el costo por milla es casi identico ($5.84 vs
  $5.74): la diferencia en el promedio se explica porque los viajes yellow
  (concentrados en Manhattan) tienden a combinar mayor congestion y recargos,
  no porque la tarifa por milla sea distinta.
