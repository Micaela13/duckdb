# Resultados del benchmark (Ejercicio 6)

- Creacion de la tabla `trips_tbl`: **11.48 s** (113,556,358 filas)
- Tamano de los Parquet (data/raw): **1,977 MB**
- Tamano de lab.duckdb: **2,482 MB**
- Repeticiones por consulta: 5 (mediana sin la 1.a)

| volumen | filas | consulta | parquet (mediana s) | tabla (mediana s) | tabla/parquet |
|---|---|---|---|---|---|
| 1_mes_2026 | 3,553,867 | Q1_conteo | 0.253 | 0.002 | 0.01x |
| 1_mes_2026 | 3,553,867 | Q2_viajes_por_mes | 0.281 | 0.026 | 0.09x |
| 1_mes_2026 | 3,553,867 | Q3_viajes_por_hora | 0.263 | 0.006 | 0.02x |
| 1_mes_2026 | 3,553,867 | Q4_filtro_selectivo | 0.286 | 0.006 | 0.02x |
| 1_mes_2026 | 3,553,867 | Q5_percentiles_tarifa | 0.33 | 0.086 | 0.26x |
| 1_mes_2026 | 3,553,867 | Q6_propina_por_pago | 0.266 | 0.014 | 0.05x |
| 3_meses_2026 | 10,601,465 | Q1_conteo | 0.33 | 0.003 | 0.01x |
| 3_meses_2026 | 10,601,465 | Q2_viajes_por_mes | 0.383 | 0.066 | 0.17x |
| 3_meses_2026 | 10,601,465 | Q3_viajes_por_hora | 0.353 | 0.017 | 0.05x |
| 3_meses_2026 | 10,601,465 | Q4_filtro_selectivo | 0.358 | 0.015 | 0.04x |
| 3_meses_2026 | 10,601,465 | Q5_percentiles_tarifa | 0.541 | 0.216 | 0.40x |
| 3_meses_2026 | 10,601,465 | Q6_propina_por_pago | 0.381 | 0.032 | 0.08x |
| anio_2024 | 40,302,328 | Q1_conteo | 0.639 | 0.008 | 0.01x |
| anio_2024 | 40,302,328 | Q2_viajes_por_mes | 0.829 | 0.223 | 0.27x |
| anio_2024 | 40,302,328 | Q3_viajes_por_hora | 0.723 | 0.063 | 0.09x |
| anio_2024 | 40,302,328 | Q4_filtro_selectivo | 0.592 | 0.053 | 0.09x |
| anio_2024 | 40,302,328 | Q5_percentiles_tarifa | 1.701 | 0.982 | 0.58x |
| anio_2024 | 40,302,328 | Q6_propina_por_pago | 0.771 | 0.099 | 0.13x |
| todo | 113,556,358 | Q1_conteo | 1.832 | 0.005 | 0.00x |
| todo | 113,556,358 | Q2_viajes_por_mes | 2.18 | 0.651 | 0.30x |
| todo | 113,556,358 | Q3_viajes_por_hora | 1.846 | 0.176 | 0.10x |
| todo | 113,556,358 | Q4_filtro_selectivo | 1.456 | 0.137 | 0.09x |
| todo | 113,556,358 | Q5_percentiles_tarifa | 5.248 | 2.889 | 0.55x |
| todo | 113,556,358 | Q6_propina_por_pago | 2.512 | 0.254 | 0.10x |
