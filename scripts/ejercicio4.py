import duckdb

duckdb.sql("""
CREATE OR REPLACE VIEW yellow_raw AS
SELECT * FROM read_parquet('data/raw/yellow/**/*.parquet', union_by_name=true);
""")

duckdb.sql("""
CREATE OR REPLACE VIEW green_raw AS
SELECT * FROM read_parquet('data/raw/green/**/*.parquet', union_by_name=true);
""")

duckdb.sql("""
CREATE OR REPLACE VIEW trips AS
SELECT 'yellow' AS taxi,
       tpep_pickup_datetime  AS pickup,
       tpep_dropoff_datetime AS dropoff,
       passenger_count, trip_distance, PULocationID, DOLocationID,
       payment_type, fare_amount, tip_amount, total_amount
FROM yellow_raw
UNION ALL BY NAME
SELECT 'green' AS taxi,
       lpep_pickup_datetime  AS pickup,
       lpep_dropoff_datetime AS dropoff,
       passenger_count, trip_distance, PULocationID, DOLocationID,
       payment_type, fare_amount, tip_amount, total_amount
FROM green_raw;
""")

duckdb.sql("""
CREATE OR REPLACE VIEW trips_clean AS
SELECT *, date_diff('minute', pickup, dropoff) AS duracion_min
FROM trips
WHERE pickup >= '2024-01-01' AND pickup < '2027-01-01'
  AND dropoff > pickup
  AND date_diff('minute', pickup, dropoff) <= 360
  AND trip_distance > 0 AND trip_distance < 100
  AND fare_amount > 0 AND total_amount > 0;
""")

consultas = [
    (
        "4.1 Volumen de viajes por mes y tipo de taxi",
        """
        SELECT date_trunc('month', pickup) AS mes,
               COUNT(*) FILTER (WHERE taxi = 'yellow') AS yellow,
               COUNT(*) FILTER (WHERE taxi = 'green')  AS green
        FROM trips_clean
        GROUP BY mes
        ORDER BY mes;
        """
    ),
    (
        "4.2 Viajes por hora del día",
        """
        SELECT hour(pickup) AS hora,
               COUNT(*) FILTER (WHERE taxi = 'yellow') AS yellow,
               COUNT(*) FILTER (WHERE taxi = 'green')  AS green
        FROM trips_clean
        GROUP BY hora
        ORDER BY hora;
        """
    ),
    (
        "4.3 Viajes por día de la semana",
        """
        SELECT isodow(pickup) AS n,
               dayname(pickup) AS dia,
               COUNT(*) FILTER (WHERE taxi = 'yellow') AS yellow,
               COUNT(*) FILTER (WHERE taxi = 'green')  AS green
        FROM trips_clean
        GROUP BY n, dia
        ORDER BY n;
        """
    ),
    (
        "4.4 Distancia, duración y pasajeros por tipo de taxi",
        """
        SELECT taxi,
               COUNT(*) AS viajes,
               ROUND(AVG(trip_distance), 2) AS distancia_prom_millas,
               ROUND(AVG(duracion_min), 1)  AS duracion_prom_min,
               ROUND(AVG(passenger_count), 2) AS pasajeros_prom
        FROM trips_clean
        GROUP BY taxi;
        """
    ),
    (
        "4.5 Distribución de la distancia (viajes por rango de millas)",
        """
        SELECT CAST(FLOOR(trip_distance) AS INTEGER) AS millas,
               COUNT(*) AS viajes
        FROM trips_clean
        WHERE trip_distance < 30
        GROUP BY millas
        ORDER BY millas;
        """
    ),
    (
        "4.6 Percentiles de distancia, duración y tarifa por taxi",
        """
        SELECT taxi,
               ROUND(quantile_cont(trip_distance, 0.50), 2) AS dist_p50,
               ROUND(quantile_cont(trip_distance, 0.90), 2) AS dist_p90,
               ROUND(quantile_cont(trip_distance, 0.99), 2) AS dist_p99,
               ROUND(quantile_cont(duracion_min, 0.50), 1)  AS dur_p50,
               ROUND(quantile_cont(duracion_min, 0.99), 1)  AS dur_p99,
               ROUND(quantile_cont(fare_amount, 0.50), 2)   AS tarifa_p50,
               ROUND(quantile_cont(fare_amount, 0.99), 2)   AS tarifa_p99
        FROM trips_clean
        GROUP BY taxi;
        """
    ),
    (
        "4.7 Comparación yellow vs green (tarifas, totales y propina)",
        """
        SELECT taxi,
               COUNT(*) AS viajes,
               ROUND(AVG(fare_amount), 2)  AS tarifa_prom,
               ROUND(AVG(total_amount), 2) AS total_prom,
               ROUND(AVG(tip_amount), 2)   AS propina_prom,
               ROUND(SUM(fare_amount) / SUM(trip_distance), 2) AS usd_por_milla
        FROM trips_clean
        GROUP BY taxi;
        """
    ),
    (
        "4.8 Métodos de pago y propina",
        """
        SELECT CASE payment_type
                    WHEN 0 THEN 'Flexible'
                    WHEN 1 THEN 'Tarjeta'
                    WHEN 2 THEN 'Efectivo'
                    WHEN 3 THEN 'Sin cargo'
                    WHEN 4 THEN 'Disputa'
                    ELSE 'Otro'
               END AS metodo_pago,
               taxi,
               COUNT(*) AS viajes,
               ROUND(AVG(tip_amount), 2) AS propina_prom,
               ROUND(AVG(tip_amount / fare_amount) * 100, 1) AS pct_propina
        FROM trips_clean
        GROUP BY metodo_pago, taxi
        ORDER BY viajes DESC;
        """
    ),
    (
        "4.9 Proporción de viajes con propina según método de pago",
        """
        SELECT CASE payment_type WHEN 1 THEN 'Tarjeta' WHEN 2 THEN 'Efectivo' ELSE 'Otro' END AS metodo_pago,
               COUNT(*) AS viajes,
               ROUND(100.0 * COUNT(*) FILTER (WHERE tip_amount > 0) / COUNT(*), 1) AS pct_con_propina
        FROM trips_clean
        GROUP BY metodo_pago
        ORDER BY viajes DESC;
        """
    ),
    (
        "4.10 Atípicos e inconsistencias en los datos SIN limpiar",
        """
        SELECT taxi,
               COUNT(*) AS total,
               COUNT(*) FILTER (WHERE trip_distance <= 0)                  AS dist_no_positiva,
               COUNT(*) FILTER (WHERE trip_distance > 100)                 AS dist_mayor_100,
               COUNT(*) FILTER (WHERE fare_amount < 0)                     AS tarifa_negativa,
               COUNT(*) FILTER (WHERE total_amount < 0)                    AS total_negativo,
               COUNT(*) FILTER (WHERE dropoff <= pickup)                   AS dropoff_no_posterior,
               COUNT(*) FILTER (WHERE date_diff('hour', pickup, dropoff) > 24) AS mas_de_24h,
               COUNT(*) FILTER (WHERE passenger_count IS NULL OR passenger_count = 0) AS sin_pasajeros,
               COUNT(*) FILTER (WHERE pickup < '2024-01-01' OR pickup >= '2027-01-01') AS fecha_fuera_rango
        FROM trips
        GROUP BY taxi;
        """
    ),
    (
        "4.11 Cuántos registros elimina la limpieza",
        """
        SELECT t.taxi,
               t.total AS registros_originales,
               c.total AS registros_limpios,
               t.total - c.total AS eliminados,
               ROUND(100.0 * (t.total - c.total) / t.total, 2) AS pct_eliminado
        FROM (SELECT taxi, COUNT(*) AS total FROM trips GROUP BY taxi) t
        JOIN (SELECT taxi, COUNT(*) AS total FROM trips_clean GROUP BY taxi) c USING (taxi);
        """
    ),
    (
        "4.12 Viajes con duración o velocidad poco realista (muestra)",
        """
        SELECT taxi, pickup, dropoff, trip_distance,
               date_diff('minute', pickup, dropoff) AS duracion_min,
               ROUND(trip_distance / (date_diff('minute', pickup, dropoff) / 60.0), 1) AS mph
        FROM trips
        WHERE dropoff > pickup
          AND trip_distance > 0
          AND trip_distance / (date_diff('minute', pickup, dropoff) / 60.0) > 100
        ORDER BY mph DESC
        LIMIT 10;
        """
    ),
]

for titulo, sql in consultas:
    print("\n" + "=" * 80)
    print(titulo)
    print("=" * 80)
    resultado = duckdb.sql(sql)
    resultado.show()