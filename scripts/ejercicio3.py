import duckdb

consultas = [
    (
        "3.1 Cantidad de archivos disponibles",
        """
        SELECT 'green' AS tipo, COUNT(*) AS archivos
        FROM glob('data/raw/green/2026/*.parquet')
        UNION ALL
        SELECT 'yellow' AS tipo, COUNT(*) AS archivos
        FROM glob('data/raw/yellow/2026/*.parquet');
        """
    ),
    (
        "3.2 Cantidad de registros disponibles",
        """
        SELECT 'green' AS tipo, COUNT(*) AS registros
        FROM read_parquet('data/raw/green/2026/*.parquet')
        UNION ALL
        SELECT 'yellow' AS tipo, COUNT(*) AS registros
        FROM read_parquet('data/raw/yellow/2026/*.parquet');
        """
    ),
    (
        "3.3 y 3.4 Columnas y tipos - green",
        """
        DESCRIBE SELECT *
        FROM read_parquet('data/raw/green/2026/*.parquet');
        """
    ),
    (
        "3.3 y 3.4 Columnas y tipos - yellow",
        """
        DESCRIBE SELECT *
        FROM read_parquet('data/raw/yellow/2026/*.parquet');
        """
    ),
    (
        "3.5 Muestra de registros - green",
        """
        SELECT *
        FROM read_parquet('data/raw/green/2026/*.parquet')
        LIMIT 5;
        """
    ),
    (
        "3.5 Muestra de registros - yellow",
        """
        SELECT *
        FROM read_parquet('data/raw/yellow/2026/*.parquet')
        LIMIT 5;
        """
    ),
    (
        "3.6 Problemas de calidad de datos",
        """
        SELECT
            'green' AS tipo,
            COUNT(*) AS total_registros,
            SUM(CASE WHEN trip_distance <= 0 THEN 1 ELSE 0 END) AS distancia_no_valida,
            SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END) AS monto_negativo
        FROM read_parquet('data/raw/green/2026/*.parquet')
        UNION ALL
        SELECT
            'yellow' AS tipo,
            COUNT(*) AS total_registros,
            SUM(CASE WHEN trip_distance <= 0 THEN 1 ELSE 0 END) AS distancia_no_valida,
            SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END) AS monto_negativo
        FROM read_parquet('data/raw/yellow/2026/*.parquet');
        """
    ),
]

for titulo, sql in consultas:
    print("\n" + "=" * 80)
    print(titulo)
    print("=" * 80)
    resultado = duckdb.sql(sql)
    resultado.show()