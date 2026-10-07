-- Ejercicio 7: Construccion de indicadores y visualizacion
--
-- Estas consultas corren contra la tabla materializada en el Ejercicio 6
-- (data/processed/lab.duckdb, tabla trips_tbl) y contra taxi_zone_lookup.csv
-- (descargado por scripts/download_data.py). Son las mismas consultas que se
-- dan de alta como "preguntas" (questions) en Metabase para construir el
-- tablero. Cada bloque indica el indicador, la pregunta que responde y el
-- tipo de visualizacion recomendado en Metabase.

-- Vista de apoyo: nombre de zona y borough para el pickup.
-- (Metabase la necesita para el Indicador 6; se crea una sola vez.)
CREATE OR REPLACE VIEW trips_con_zona AS
SELECT t.*, z.borough AS pickup_borough, z.zone AS pickup_zone
FROM trips_tbl t
LEFT JOIN read_csv('data/raw/taxi_zone_lookup.csv') z
       ON t.PULocationID = z.LocationID;

-- -----------------------------------------------------------------------
-- Indicador 1 (línea) - Pregunta 1: ¿Cómo evoluciona el volumen de viajes
-- mes a mes, y difiere la tendencia entre yellow y green?
-- -----------------------------------------------------------------------
SELECT date_trunc('month', pickup) AS mes,
       taxi,
       COUNT(*) AS viajes
FROM trips_tbl
GROUP BY ALL
ORDER BY mes, taxi;

-- -----------------------------------------------------------------------
-- Indicador 2 (barras) - Pregunta 2: ¿En qué horas del día se concentra
-- la demanda de viajes?
-- -----------------------------------------------------------------------
SELECT hour(pickup) AS hora,
       COUNT(*) AS viajes
FROM trips_tbl
GROUP BY hora
ORDER BY hora;

-- -----------------------------------------------------------------------
-- Indicador 3 (barras apiladas) - Pregunta 3: ¿Qué días de la semana
-- concentran más viajes y cómo se reparten entre yellow y green?
-- -----------------------------------------------------------------------
SELECT isodow(pickup) AS n,
       dayname(pickup) AS dia,
       taxi,
       COUNT(*) AS viajes
FROM trips_tbl
GROUP BY ALL
ORDER BY n;

-- -----------------------------------------------------------------------
-- Indicador 4 (histograma) - Pregunta 4: ¿Cómo se distribuye la distancia
-- de los viajes? ¿La mayoría son viajes cortos o largos?
-- -----------------------------------------------------------------------
SELECT CAST(FLOOR(trip_distance) AS INTEGER) AS millas,
       COUNT(*) AS viajes
FROM trips_tbl
WHERE trip_distance < 20
GROUP BY millas
ORDER BY millas;

-- -----------------------------------------------------------------------
-- Indicador 5 (barras agrupadas) - Pregunta 5: ¿Qué método de pago
-- predomina y cuál deja, en promedio, mejor propina?
-- -----------------------------------------------------------------------
SELECT CASE payment_type
            WHEN 1 THEN 'Tarjeta'
            WHEN 2 THEN 'Efectivo'
            ELSE 'Otro'
       END AS metodo_pago,
       taxi,
       COUNT(*) AS viajes,
       ROUND(AVG(tip_amount), 2) AS propina_prom
FROM trips_tbl
WHERE payment_type IN (1, 2)
GROUP BY ALL
ORDER BY viajes DESC;

-- -----------------------------------------------------------------------
-- Indicador 6 (ranking / barras horizontales) - Pregunta 6: ¿Cuáles son
-- los 10 boroughs/zonas de recogida con más viajes?
-- -----------------------------------------------------------------------
SELECT COALESCE(pickup_borough, 'Desconocido') AS borough,
       COUNT(*) AS viajes
FROM trips_con_zona
GROUP BY borough
ORDER BY viajes DESC;

-- -----------------------------------------------------------------------
-- Indicador 7 (KPI numérico) - Pregunta 7: ¿Qué tarifa promedio y cuántos
-- USD por milla cobra cada tipo de taxi?
-- -----------------------------------------------------------------------
SELECT taxi,
       COUNT(*) AS viajes,
       ROUND(AVG(fare_amount), 2)  AS tarifa_prom,
       ROUND(AVG(total_amount), 2) AS total_prom,
       ROUND(SUM(fare_amount) / SUM(trip_distance), 2) AS usd_por_milla
FROM trips_tbl
GROUP BY taxi;

-- -----------------------------------------------------------------------
-- Indicador 8 (línea) - Pregunta 8: ¿Cómo varía el porcentaje promedio de
-- propina según la hora del viaje?
-- -----------------------------------------------------------------------
SELECT hour(pickup) AS hora,
       ROUND(100.0 * AVG(tip_amount / NULLIF(fare_amount, 0)), 1) AS pct_propina_prom
FROM trips_tbl
WHERE payment_type = 1
GROUP BY hora
ORDER BY hora;

-- -----------------------------------------------------------------------
-- Pregunta 9 (no es indicador del tablero, apoya el 9.6 de la discusión):
-- ¿Qué porcentaje de los registros originales fueron descartados por la
-- limpieza aplicada en trips_clean (Ej.4), por año?
-- -----------------------------------------------------------------------
SELECT year(pickup) AS anio,
       COUNT(*) AS registros_en_tbl
FROM trips_tbl
GROUP BY anio
ORDER BY anio;

-- -----------------------------------------------------------------------
-- Pregunta 10 (apoya el 9.8): ¿Qué tan dispersos son los viajes de más de
-- 50 millas? (cola larga / posibles atípicos que sobrevivieron la limpieza)
-- -----------------------------------------------------------------------
SELECT taxi,
       COUNT(*) FILTER (WHERE trip_distance > 50) AS viajes_mas_50_millas,
       COUNT(*) AS total_viajes,
       ROUND(100.0 * COUNT(*) FILTER (WHERE trip_distance > 50) / COUNT(*), 4) AS pct
FROM trips_tbl
GROUP BY taxi;
