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
        "5.5 Archivos por tipo y anio (2024 debe tener 12 por tipo)",
        """
        SELECT regexp_extract(file, '(yellow|green)_tripdata_([0-9]{4})', 1) AS tipo,
               regexp_extract(file, '(yellow|green)_tripdata_([0-9]{4})', 2) AS anio,
               COUNT(*) AS archivos
        FROM glob('data/raw/*/*/*.parquet')
        GROUP BY ALL
        ORDER BY ALL;
        """
    ),
    (
        "5.5 Registros por archivo (ninguno debe estar vacio)",
        """
        SELECT regexp_extract(filename, '(yellow|green)_tripdata_([0-9]{4}-[0-9]{2})', 1) AS tipo,
               regexp_extract(filename, '(yellow|green)_tripdata_([0-9]{4}-[0-9]{2})', 2) AS mes_archivo,
               COUNT(*) AS registros
        FROM read_parquet('data/raw/*/*/*.parquet', filename=true, union_by_name=true)
        GROUP BY ALL
        ORDER BY ALL;
        """
    ),
    (
        "5.6 Consulta conjunta 2024 y 2026: viajes por anio y tipo de taxi",
        """
        SELECT year(pickup) AS anio,
               COUNT(*) FILTER (WHERE taxi = 'yellow') AS yellow,
               COUNT(*) FILTER (WHERE taxi = 'green')  AS green
        FROM trips_clean
        GROUP BY anio
        ORDER BY anio;
        """
    ),
    (
        "5.7 Consulta 4.1 SIN MODIFICAR sobre el conjunto ampliado",
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
        "5.7 Consulta 4.7 SIN MODIFICAR sobre el conjunto ampliado",
        """
        SELECT taxi, COUNT(*) AS viajes,
               ROUND(AVG(fare_amount), 2)  AS tarifa_prom,
               ROUND(AVG(total_amount), 2) AS total_prom,
               ROUND(SUM(fare_amount) / SUM(trip_distance), 2) AS usd_por_milla
        FROM trips_clean
        GROUP BY taxi;
        """
    ),
    (
        "5.8 Registros cuya fecha de viaje no coincide con el anio de su archivo (yellow)",
        """
        SELECT regexp_extract(filename, '_tripdata_([0-9]{4})', 1) AS anio_archivo,
               year(tpep_pickup_datetime) AS anio_pickup,
               COUNT(*) AS registros
        FROM read_parquet('data/raw/yellow/*/*.parquet', filename=true, union_by_name=true)
        GROUP BY ALL
        ORDER BY ALL;
        """
    ),
]

for titulo, sql in consultas:
    print("\n" + "=" * 80)
    print(titulo)
    print("=" * 80)
    duckdb.sql(sql).show(max_rows=60)