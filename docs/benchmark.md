# Resultados del benchmark (Ejercicio 6)

- Creacion de la tabla `trips_tbl`: **15.13 s** (68,842,371 filas)
- Tamano de los Parquet (data/raw): **1,172 MB**
- Tamano de lab.duckdb: **1,499 MB**
- Repeticiones por consulta: 5 (mediana sin la 1.a)

| volumen | filas | consulta | parquet (mediana s) | tabla (mediana s) | tabla/parquet |
|---|---|---|---|---|---|
| 1_mes_2026 | 3,553,853 | Q1_conteo | 1.0 | 0.003 | 0.00x |
| 1_mes_2026 | 3,553,853 | Q2_viajes_por_mes | 1.014 | 0.059 | 0.06x |
| 1_mes_2026 | 3,553,853 | Q3_viajes_por_hora | 1.174 | 0.012 | 0.01x |
| 1_mes_2026 | 3,553,853 | Q4_filtro_selectivo | 1.242 | 0.012 | 0.01x |
| 1_mes_2026 | 3,553,853 | Q5_percentiles_tarifa | 1.221 | 0.164 | 0.13x |
| 1_mes_2026 | 3,553,853 | Q6_propina_por_pago | 1.095 | 0.029 | 0.03x |
| 3_meses_2026 | 10,601,451 | Q1_conteo | 1.336 | 0.009 | 0.01x |
| 3_meses_2026 | 10,601,451 | Q2_viajes_por_mes | 1.358 | 0.141 | 0.10x |
| 3_meses_2026 | 10,601,451 | Q3_viajes_por_hora | 1.348 | 0.029 | 0.02x |
| 3_meses_2026 | 10,601,451 | Q4_filtro_selectivo | 1.429 | 0.03 | 0.02x |
| 3_meses_2026 | 10,601,451 | Q5_percentiles_tarifa | 1.835 | 0.399 | 0.22x |
| 3_meses_2026 | 10,601,451 | Q6_propina_por_pago | 1.373 | 0.07 | 0.05x |
| anio_2024 | 40,302,302 | Q1_conteo | 1.972 | 0.016 | 0.01x |
| anio_2024 | 40,302,302 | Q2_viajes_por_mes | 2.328 | 0.509 | 0.22x |
| anio_2024 | 40,302,302 | Q3_viajes_por_hora | 2.1 | 0.118 | 0.06x |
| anio_2024 | 40,302,302 | Q4_filtro_selectivo | 2.077 | 0.114 | 0.05x |
| anio_2024 | 40,302,302 | Q5_percentiles_tarifa | 4.219 | 1.915 | 0.45x |
| anio_2024 | 40,302,302 | Q6_propina_por_pago | 2.51 | 0.235 | 0.09x |
| todo | 68,842,371 | Q1_conteo | 3.088 | 0.007 | 0.00x |
| todo | 68,842,371 | Q2_viajes_por_mes | 3.542 | 0.742 | 0.21x |
| todo | 68,842,371 | Q3_viajes_por_hora | 3.235 | 0.179 | 0.06x |
| todo | 68,842,371 | Q4_filtro_selectivo | 3.073 | 0.166 | 0.05x |
| todo | 68,842,371 | Q5_percentiles_tarifa | 6.974 | 3.222 | 0.46x |
| todo | 68,842,371 | Q6_propina_por_pago | 3.849 | 0.305 | 0.08x |
