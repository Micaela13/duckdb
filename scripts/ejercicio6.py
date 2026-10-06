import os
import statistics
import time
from pathlib import Path

import duckdb

DB = "data/processed/lab.duckdb"
REPETICIONES = 5        # la 1.a ejecucion se reporta aparte; la mediana usa las demas

Path(DB).parent.mkdir(parents=True, exist_ok=True)
if os.path.exists(DB):
    os.remove(DB)       # empezar de cero para medir bien tiempo y tamano de la tabla

con = duckdb.connect(DB)

# ---------------------------------------------------------------
# 6.1 Vistas sobre los Parquet (fuente "parquet")
# ---------------------------------------------------------------
con.execute("""
CREATE OR REPLACE VIEW yellow_raw AS
SELECT * FROM read_parquet('data/raw/yellow/**/*.parquet', union_by_name=true)
""")
con.execute("""
CREATE OR REPLACE VIEW green_raw AS
SELECT * FROM read_parquet('data/raw/green/**/*.parquet', union_by_name=true)
""")
con.execute("""
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
FROM green_raw
""")
con.execute("""
CREATE OR REPLACE VIEW trips_clean AS
SELECT *, date_diff('minute', pickup, dropoff) AS duracion_min
FROM trips
WHERE pickup >= '2024-01-01' AND pickup < '2027-01-01'
  AND dropoff > pickup
  AND date_diff('minute', pickup, dropoff) <= 360
  AND trip_distance > 0 AND trip_distance < 100
  AND fare_amount > 0 AND total_amount > 0
""")

# ---------------------------------------------------------------
# 6.2 Tabla materializada (se mide cuanto tarda en crearse)
# ---------------------------------------------------------------
print("Creando la tabla trips_tbl (puede tardar unos minutos)...")
inicio = time.perf_counter()
con.execute("CREATE TABLE trips_tbl AS SELECT * FROM trips_clean")
t_creacion = time.perf_counter() - inicio
filas_tabla = con.execute("SELECT COUNT(*) FROM trips_tbl").fetchone()[0]
print(f"trips_tbl: {filas_tabla:,} filas en {t_creacion:.2f} s")

# ---------------------------------------------------------------
# 6.3 Consultas representativas (identicas para ambas fuentes)
# ---------------------------------------------------------------
CONSULTAS = {
    "Q1_conteo":
        "SELECT COUNT(*) FROM {src}",
    "Q2_viajes_por_mes":
        "SELECT date_trunc('month', pickup) AS mes, taxi, COUNT(*) AS viajes FROM {src} GROUP BY ALL",
    "Q3_viajes_por_hora":
        "SELECT hour(pickup) AS hora, COUNT(*) AS viajes FROM {src} GROUP BY hora",
    "Q4_filtro_selectivo":
        "SELECT COUNT(*) FROM {src} WHERE trip_distance > 10 AND tip_amount > 5",
    "Q5_percentiles_tarifa":
        "SELECT taxi, quantile_cont(fare_amount, [0.5, 0.95]) AS p50_p95 FROM {src} GROUP BY taxi",
    "Q6_propina_por_pago":
        "SELECT payment_type, taxi, AVG(tip_amount) AS propina_prom FROM {src} GROUP BY ALL",
}

# ---------------------------------------------------------------
# 6.6 Distintos volumenes de datos
# ---------------------------------------------------------------
VOLUMENES = {
    "1_mes_2026":   "pickup >= '2026-01-01' AND pickup < '2026-02-01'",
    "3_meses_2026": "pickup >= '2026-01-01' AND pickup < '2026-04-01'",
    "anio_2024":    "pickup >= '2024-01-01' AND pickup < '2025-01-01'",
    "todo":         "TRUE",
}
FUENTES = {"parquet": "trips_clean", "tabla": "trips_tbl"}

filas_por_volumen = {
    v: con.execute(f"SELECT COUNT(*) FROM trips_tbl WHERE {f}").fetchone()[0]
    for v, f in VOLUMENES.items()
}

# ---------------------------------------------------------------
# 6.4 y 6.5 Ejecutar y registrar tiempos
# ---------------------------------------------------------------
resultados = []
total = len(VOLUMENES) * len(CONSULTAS) * len(FUENTES)
n = 0
for volumen, filtro in VOLUMENES.items():
    for consulta, sql in CONSULTAS.items():
        for fuente, origen in FUENTES.items():
            n += 1
            src = f"(SELECT * FROM {origen} WHERE {filtro})"
            tiempos = []
            for _ in range(REPETICIONES):
                inicio = time.perf_counter()
                con.execute(sql.format(src=src)).fetchall()
                tiempos.append(time.perf_counter() - inicio)
            fila = {
                "volumen": volumen,
                "filas": filas_por_volumen[volumen],
                "consulta": consulta,
                "fuente": fuente,
                "primera_s": round(tiempos[0], 3),
                "mediana_s": round(statistics.median(tiempos[1:]), 3),
            }
            resultados.append(fila)
            print(f"[{n}/{total}] {volumen:13} {consulta:22} {fuente:8} "
                  f"1.a={fila['primera_s']:8.3f}s  mediana={fila['mediana_s']:8.3f}s")

con.close()   # libera el archivo (Metabase lo necesitara en el ejercicio 7)

# ---------------------------------------------------------------
# Tamanos en disco
# ---------------------------------------------------------------
def tamanio_mb(ruta):
    p = Path(ruta)
    if p.is_file():
        return p.stat().st_size / 1024**2
    return sum(f.stat().st_size for f in p.rglob("*.parquet")) / 1024**2

mb_parquet = tamanio_mb("data/raw")
mb_duckdb = tamanio_mb(DB)

# ---------------------------------------------------------------
# 6.7 Guardar resultados (CSV y Markdown)
# ---------------------------------------------------------------
columnas = ["volumen", "filas", "consulta", "fuente", "primera_s", "mediana_s"]

with open("docs/benchmark.csv", "w", encoding="utf-8") as f:
    f.write(",".join(columnas) + "\n")
    for r in resultados:
        f.write(",".join(str(r[c]) for c in columnas) + "\n")

with open("docs/benchmark.md", "w", encoding="utf-8") as f:
    f.write("# Resultados del benchmark (Ejercicio 6)\n\n")
    f.write(f"- Creacion de la tabla `trips_tbl`: **{t_creacion:.2f} s** ({filas_tabla:,} filas)\n")
    f.write(f"- Tamano de los Parquet (data/raw): **{mb_parquet:,.0f} MB**\n")
    f.write(f"- Tamano de lab.duckdb: **{mb_duckdb:,.0f} MB**\n")
    f.write(f"- Repeticiones por consulta: {REPETICIONES} (mediana sin la 1.a)\n\n")

    # Tabla comparativa: una fila por (volumen, consulta), parquet vs tabla
    f.write("| volumen | filas | consulta | parquet (mediana s) | tabla (mediana s) | tabla/parquet |\n")
    f.write("|---|---|---|---|---|---|\n")
    indice = {(r["volumen"], r["consulta"], r["fuente"]): r for r in resultados}
    for volumen in VOLUMENES:
        for consulta in CONSULTAS:
            p = indice[(volumen, consulta, "parquet")]["mediana_s"]
            t = indice[(volumen, consulta, "tabla")]["mediana_s"]
            razon = f"{t / p:.2f}x" if p > 0 else "n/a"
            f.write(f"| {volumen} | {filas_por_volumen[volumen]:,} | {consulta} | {p} | {t} | {razon} |\n")

print("\n" + "=" * 70)
print(f"Tabla creada en {t_creacion:.2f} s")
print(f"Parquet: {mb_parquet:,.0f} MB | lab.duckdb: {mb_duckdb:,.0f} MB")
print("Resultados en docs/benchmark.csv y docs/benchmark.md")