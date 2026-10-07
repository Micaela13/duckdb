# Ejercicio 8: Incorporacion de datos de 2025 y analisis completo

## 8.1-8.2 Descarga de 2025 sin perder 2024/2026

`scripts/download_data.py` ya traia `ANIOS` preparado para este paso (ver su
docstring, "Historial de cambios"); el unico cambio real fue:

```python
ANIOS = [2024, 2025, 2026]   # antes: [2024, 2026]
```

Ejecucion:

```bash
docker compose exec lab python scripts/download_data.py
```

Resultado: **24 archivos descargados** (yellow y green, 12 meses de 2025),
**40 ya existian** (los de 2024 y 2026 del Ejercicio 5/2, intactos) y 8 meses
de 2026 (sept-dic) siguen `no publicados` por la TLC. Cero fallidos. El
detalle completo del resumen queda en la salida del script (reproducible
corriendo el mismo comando).

## 8.3 Las consultas siguen funcionando sin cambios

Se corrieron de nuevo, sin modificar una sola linea, los scripts de los
ejercicios anteriores sobre el conjunto ampliado:

```bash
docker compose exec lab python scripts/ejercicio6.py   # rematerializa trips_tbl
docker compose exec lab python scripts/ejercicio5.py   # 5.6/5.7/5.8 con 3 anios
docker compose exec lab python scripts/ejercicio7.py   # 8 indicadores con 3 anios
```

Las consultas 4.1 y 4.7 (re-ejecutadas sin modificar en `ejercicio5.py`, ver
"5.7 SIN MODIFICAR") y los 8 indicadores del Ejercicio 7 produjeron resultados
correctos de inmediato: ninguna referencia a un anio o archivo especifico
existe en su SQL, porque todas leen `trips_tbl` (que a su vez se arma con
`read_parquet('data/raw/<tipo>/**/*.parquet', union_by_name=true)`, un glob
recursivo). `trips_tbl` paso de 68,842,371 a **113,556,358 filas** al
incorporar 2025.

> **Nota operativa importante:** el dashboard de Metabase (Ejercicio 7) usa
> una conexion persistente al archivo `lab.duckdb`. Como `ejercicio6.py` borra
> y recrea ese archivo (`os.remove` + `duckdb.connect`), Metabase se queda con
> un *file handle* abierto al archivo viejo hasta que se reinicia:
>
> ```bash
> docker compose restart metabase
> ```
>
> Sin este paso, el tablero sigue mostrando los datos de antes de incorporar
> el anio nuevo aunque la consulta se re-ejecute (se verifico: antes del
> restart, una tarjeta reportaba 45 filas —el conteo correcto para 2 anios—
> en vez de las 64 esperadas con 3 anios). Se documenta aqui porque no es
> evidente y de lo contrario se podria confundir con un error en las
> consultas.

## 8.4 Indicadores y visualizaciones actualizados

Como ninguna consulta cambio, **el mismo tablero del Ejercicio 7**
(`http://localhost:3000/dashboard/2`, construido con
`scripts/ejercicio7_dashboard.py`) ya refleja los tres anios tras el restart
de Metabase. No se crearon tarjetas nuevas porque las 8 existentes ya agregan
por mes/hora/dia sin fijar un anio. Los numeros actualizados de cada
indicador se documentaron en `docs/ejercicio7.md` (seccion 7.8, nota al
inicio) para no duplicar contenido.

## 8.5-8.6 Evolucion de los indicadores y patrones 2024-2025-2026

Consulta usada (agrega por anio, taxi y mide volumen, tarifa, distancia,
duracion y % de pago con tarjeta):

```sql
SELECT year(pickup) AS anio, taxi,
       COUNT(*) AS viajes,
       ROUND(AVG(fare_amount), 2) AS tarifa_prom,
       ROUND(AVG(trip_distance), 2) AS distancia_prom,
       ROUND(AVG(duracion_min), 1) AS duracion_prom,
       ROUND(100.0 * COUNT(*) FILTER (WHERE payment_type = 1)
                    / COUNT(*) FILTER (WHERE payment_type IN (1,2)), 1) AS pct_tarjeta
FROM trips_tbl
GROUP BY ALL ORDER BY taxi, anio;
```

| anio | taxi | viajes/mes prom | tarifa prom | distancia prom | duracion prom | % tarjeta |
|---|---|---|---|---|---|---|
| 2024 | green | 51,763 | $18.09 | 2.94 mi | 14.8 min | 71.8% |
| 2025 | green | 46,569 | $17.99 | 3.18 mi | 15.9 min | 75.7% |
| 2026* | green | 39,759 | $17.07 | 3.30 mi | 17.0 min | 77.2% |
| 2024 | yellow | 3,306,764 | $19.81 | 3.42 mi | 16.9 min | 85.1% |
| 2025 | yellow | 3,679,595 | $20.06 | 3.49 mi | 17.2 min | 87.6% |
| 2026* | yellow | 3,527,749 | $21.30 | 3.52 mi | 17.7 min | 87.8% |

\* 2026 es parcial (8 meses); se usa el promedio mensual para comparar
anios de forma justa contra 2024 y 2025 (12 meses completos).

Patrones que solo se hacen visibles al tener los tres anios juntos:

1. **El taxi green sigue perdiendo volumen cada anio, de forma sostenida.**
   El promedio mensual cayo de 51,763 (2024) a 46,569 (2025, -10.0%) y a
   39,759 (2026, -14.6% adicional; -23.2% acumulado desde 2024). Con solo dos
   anios (2024 y 2026) se veia la caida total, pero no que fuera un declive
   year-over-year consistente y no un salto puntual.
2. **El taxi yellow crecio en 2025 y luego se estabilizo.** El promedio
   mensual subio 11.3% de 2024 a 2025, y en 2026 (parcial) esta 4.1% por
   debajo del pico de 2025 pero todavia 6.7% arriba de 2024. Es decir, el
   crecimiento no fue lineal: hubo un salto en 2025 que no se sostuvo en
   2026, algo que una comparacion de solo dos anios no distingue de una
   tendencia continua.
3. **El pago con tarjeta sigue desplazando al efectivo en ambos taxis, todos
   los anios.** Yellow paso de 85.1% a 87.6% a 87.8% con tarjeta; green de
   71.8% a 75.7% a 77.2%. Es una tendencia monotona (sube cada anio sin
   retrocesos), consistente con la adopcion gradual de pago electronico.
4. **El viaje promedio se alarga cada anio** (yellow: 16.9 -> 17.2 -> 17.7
   min; green: 14.8 -> 15.9 -> 17.0 min), con distancia promedio casi
   constante. La duracion crece mas rapido que la distancia en ambos casos,
   lo que sugiere mas tiempo detenido en trafico por viaje, no viajes mas
   largos.
5. **Las tarifas promedio divergen entre taxis:** yellow sube 7.5% en total
   (2024->2026, $19.81 -> $21.30) mientras que green baja 5.6% ($18.09 ->
   $17.07). Yellow encarece year-over-year; green, aun con viajes de
   distancia creciente, cobra un poco menos en promedio cada anio.

## 8.7 Consultas documentadas

- Descarga: `scripts/download_data.py` (sin cambios de codigo salvo el
  valor de `ANIOS`).
- Materializacion: `scripts/ejercicio6.py` (sin cambios).
- Validacion de la incorporacion: `scripts/ejercicio5.py` (sin cambios,
  salida con 3 anios en `docs/05_consola_2025.txt` si se desea regenerar).
- Indicadores: `scripts/ejercicio7.py` y `sql/ejercicio7_indicadores.sql`
  (sin cambios; salida actualizada en `docs/07_consola.txt`).
- Evolucion anual (tabla de la seccion 8.5-8.6): consulta ad-hoc incluida
  arriba, no forma parte de un script porque es un analisis de una sola vez
  para esta discusion (no un indicador del tablero).
