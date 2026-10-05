--Ejercicio 3

--3.1 Cantidad de archivos disponibles
SELECT 'green' AS tipo, COUNT(*) AS archivos
FROM glob('data/raw/green/2026/*.parquet')
UNION ALL
SELECT 'yellow' AS tipo, COUNT(*) AS archivos
FROM glob('data/raw/yellow/2026/*.parquet');

--3.2 Cantidad de registros disponibles
SELECT 'green' AS tipo, COUNT(*) AS registros
FROM read_parquet('data/raw/green/2026/*.parquet')
UNION ALL
SELECT 'yellow' AS tipo, COUNT(*) AS registros
FROM read_parquet('data/raw/yellow/2026/*.parquet');

--3.3 Y 3.4 Columnas y tipos de datos 
DESCRIBE SELECT *
FROM read_parquet('data/raw/green/2026/*.parquet')

DESCRIBE SELECT *
FROM read_parquet('data/raw/yellow/2026/*.parquet');

--3.5 Muestra de los registros
SELECT *
FROM read_parquet('data/raw/green/2026/*.parquet')
LIMIT 5;

SELECT *
FROM read_parquet('data/raw/yellow/2026/*.parquet')
LIMIT 5;

--3.6 Posibles problemas de calidad de datos
SELECT 
    'green' AS tipo, 
    COUNT(*) AS registros,
    SUM(CASE WHEN trip_distance <=0 then 1 ELSE 0 END) AS distancia_no_valida,
    SUM(CASE WHEN total_amount <=0 then 1 ELSE 0 END) AS monto_negativo
FROM read_parquet('data/raw/green/2026/*.parquet')
UNION ALL
SELECT 
    'yellow' AS tipo, 
    COUNT(*) AS registros,
    SUM(CASE WHEN trip_distance <=0 then 1 ELSE 0 END) AS distancia_no_valida,
    SUM(CASE WHEN total_amount <=0 then 1 ELSE 0 END) AS monto_negativo 
FROM read_parquet('data/raw/yellow/2026/*.parquet');

