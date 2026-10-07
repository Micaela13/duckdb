"""Ejercicio 7: valida las consultas de los indicadores contra trips_tbl.

Corre, en modo solo lectura, las mismas consultas documentadas en
sql/ejercicio7_indicadores.sql contra la tabla materializada en el
Ejercicio 6 (data/processed/lab.duckdb). Sirve para:
  - comprobar que cada consulta es correcta antes de darla de alta como
    "question" en Metabase;
  - dejar un registro reproducible de los resultados usados para redactar
    las interpretaciones en docs/ejercicio7.md.

Uso:
    docker compose exec lab python scripts/ejercicio7.py
"""

import duckdb

DB = "data/processed/lab.duckdb"
con = duckdb.connect(DB, read_only=True)

con.execute("""
CREATE OR REPLACE TEMP VIEW trips_con_zona AS
SELECT t.*, z.borough AS pickup_borough, z.zone AS pickup_zone
FROM trips_tbl t
LEFT JOIN read_csv('data/raw/taxi_zone_lookup.csv') z
       ON t.PULocationID = z.LocationID
""")

consultas = [
    (
        "Indicador 1 - Viajes por mes y tipo de taxi",
        """
        SELECT date_trunc('month', pickup) AS mes, taxi, COUNT(*) AS viajes
        FROM trips_tbl GROUP BY ALL ORDER BY mes, taxi
        """,
    ),
    (
        "Indicador 2 - Viajes por hora del dia",
        """
        SELECT hour(pickup) AS hora, COUNT(*) AS viajes
        FROM trips_tbl GROUP BY hora ORDER BY hora
        """,
    ),
    (
        "Indicador 3 - Viajes por dia de la semana y tipo",
        """
        SELECT isodow(pickup) AS n, dayname(pickup) AS dia, taxi, COUNT(*) AS viajes
        FROM trips_tbl GROUP BY ALL ORDER BY n
        """,
    ),
    (
        "Indicador 4 - Distribucion de la distancia (< 20 millas)",
        """
        SELECT CAST(FLOOR(trip_distance) AS INTEGER) AS millas, COUNT(*) AS viajes
        FROM trips_tbl WHERE trip_distance < 20 GROUP BY millas ORDER BY millas
        """,
    ),
    (
        "Indicador 5 - Metodo de pago y propina promedio",
        """
        SELECT CASE payment_type WHEN 1 THEN 'Tarjeta' WHEN 2 THEN 'Efectivo' ELSE 'Otro' END AS metodo_pago,
               taxi, COUNT(*) AS viajes, ROUND(AVG(tip_amount), 2) AS propina_prom
        FROM trips_tbl WHERE payment_type IN (1, 2) GROUP BY ALL ORDER BY viajes DESC
        """,
    ),
    (
        "Indicador 6 - Viajes por borough de recogida",
        """
        SELECT COALESCE(pickup_borough, 'Desconocido') AS borough, COUNT(*) AS viajes
        FROM trips_con_zona GROUP BY borough ORDER BY viajes DESC
        """,
    ),
    (
        "Indicador 7 - Tarifa y USD/milla por tipo de taxi",
        """
        SELECT taxi, COUNT(*) AS viajes, ROUND(AVG(fare_amount), 2) AS tarifa_prom,
               ROUND(AVG(total_amount), 2) AS total_prom,
               ROUND(SUM(fare_amount) / SUM(trip_distance), 2) AS usd_por_milla
        FROM trips_tbl GROUP BY taxi
        """,
    ),
    (
        "Indicador 8 - Pct de propina promedio por hora (pagos con tarjeta)",
        """
        SELECT hour(pickup) AS hora,
               ROUND(100.0 * AVG(tip_amount / NULLIF(fare_amount, 0)), 1) AS pct_propina_prom
        FROM trips_tbl WHERE payment_type = 1 GROUP BY hora ORDER BY hora
        """,
    ),
    (
        "Pregunta 9 - Registros por anio en trips_tbl",
        """
        SELECT year(pickup) AS anio, COUNT(*) AS registros_en_tbl
        FROM trips_tbl GROUP BY anio ORDER BY anio
        """,
    ),
    (
        "Pregunta 10 - Viajes de mas de 50 millas que sobreviven la limpieza",
        """
        SELECT taxi,
               COUNT(*) FILTER (WHERE trip_distance > 50) AS viajes_mas_50_millas,
               COUNT(*) AS total_viajes,
               ROUND(100.0 * COUNT(*) FILTER (WHERE trip_distance > 50) / COUNT(*), 4) AS pct
        FROM trips_tbl GROUP BY taxi
        """,
    ),
]

for titulo, sql in consultas:
    print("\n" + "=" * 80)
    print(titulo)
    print("=" * 80)
    duckdb.sql(sql, connection=con).show(max_rows=30)

con.close()
