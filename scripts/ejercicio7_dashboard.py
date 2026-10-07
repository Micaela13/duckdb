"""Ejercicio 7: crea, via la API de Metabase, la base de datos DuckDB y el
tablero con los 8 indicadores documentados en sql/ejercicio7_indicadores.sql.

Requisito previo: completar el asistente de primer arranque de Metabase en
http://localhost:3000 (crear el usuario administrador). Metabase no permite
automatizar ese primer paso sin conocer de antemano el correo/clave que el
equipo quiere usar, por eso es manual; todo lo demas (conectar la base de
datos, crear las 8 preguntas y armar el tablero) lo hace este script.

Es idempotente: si la base de datos o el tablero ya existen (por nombre), los
reutiliza en lugar de duplicarlos.

Uso (dentro del contenedor "lab", que comparte la red con "metabase"):
    docker compose exec lab python scripts/ejercicio7_dashboard.py \
        --email correo@dominio.com --password '...'

Variables de entorno equivalentes: METABASE_URL, METABASE_EMAIL, METABASE_PASSWORD.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DB_NAME = "NYC Taxi (Lab 8)"
DASHBOARD_NAME = "Lab 8 - Indicadores de viajes de taxi (Ejercicio 7)"
# Ruta vista por el contenedor de Metabase (ver docker-compose.yml: ./data -> /workspace/data)
DUCKDB_PATH = "/workspace/data/processed/lab.duckdb"
ZONE_CSV_PATH = "/workspace/data/raw/taxi_zone_lookup.csv"

CARDS = [
    dict(
        name="1. Viajes por mes y tipo de taxi",
        description="Pregunta 1: como evoluciona el volumen de viajes mes a mes y difiere la tendencia entre yellow y green?",
        sql="""SELECT date_trunc('month', pickup) AS mes, taxi, COUNT(*) AS viajes
FROM trips_tbl GROUP BY ALL ORDER BY mes, taxi""",
        display="line",
        viz_settings={"graph.dimensions": ["mes"], "graph.metrics": ["viajes"]},
    ),
    dict(
        name="2. Viajes por hora del dia",
        description="Pregunta 2: en que horas del dia se concentra la demanda de viajes?",
        sql="""SELECT hour(pickup) AS hora, COUNT(*) AS viajes
FROM trips_tbl GROUP BY hora ORDER BY hora""",
        display="bar",
        viz_settings={"graph.dimensions": ["hora"], "graph.metrics": ["viajes"]},
    ),
    dict(
        name="3. Viajes por dia de la semana y taxi",
        description="Pregunta 3: que dias de la semana concentran mas viajes y como se reparten entre yellow y green?",
        sql="""SELECT isodow(pickup) AS n, dayname(pickup) AS dia, taxi, COUNT(*) AS viajes
FROM trips_tbl GROUP BY ALL ORDER BY n""",
        display="bar",
        viz_settings={"graph.dimensions": ["dia"], "graph.metrics": ["viajes"], "stackable.stack_type": "stacked"},
    ),
    dict(
        name="4. Distribucion de la distancia de viaje",
        description="Pregunta 4: como se distribuye la distancia de los viajes? la mayoria son viajes cortos o largos?",
        sql="""SELECT CAST(FLOOR(trip_distance) AS INTEGER) AS millas, COUNT(*) AS viajes
FROM trips_tbl WHERE trip_distance < 20 GROUP BY millas ORDER BY millas""",
        display="bar",
        viz_settings={"graph.dimensions": ["millas"], "graph.metrics": ["viajes"]},
    ),
    dict(
        name="5. Metodo de pago y propina promedio",
        description="Pregunta 5: que metodo de pago predomina y cual deja, en promedio, mejor propina?",
        sql="""SELECT CASE payment_type WHEN 1 THEN 'Tarjeta' WHEN 2 THEN 'Efectivo' ELSE 'Otro' END AS metodo_pago,
       taxi, COUNT(*) AS viajes, ROUND(AVG(tip_amount), 2) AS propina_prom
FROM trips_tbl WHERE payment_type IN (1, 2) GROUP BY ALL ORDER BY viajes DESC""",
        display="bar",
        viz_settings={"graph.dimensions": ["metodo_pago"], "graph.metrics": ["propina_prom"]},
    ),
    dict(
        name="6. Viajes por borough de recogida",
        description="Pregunta 6: cuales son los boroughs de recogida con mas viajes?",
        sql=f"""SELECT COALESCE(z.borough, 'Desconocido') AS borough, COUNT(*) AS viajes
FROM trips_tbl t
LEFT JOIN read_csv('{ZONE_CSV_PATH}') z ON t.PULocationID = z.LocationID
GROUP BY borough ORDER BY viajes DESC""",
        display="row",
        viz_settings={"graph.dimensions": ["borough"], "graph.metrics": ["viajes"]},
    ),
    dict(
        name="7. Tarifa, total y USD por milla segun taxi",
        description="Pregunta 7: que tarifa promedio y cuantos USD por milla cobra cada tipo de taxi?",
        sql="""SELECT taxi, COUNT(*) AS viajes, ROUND(AVG(fare_amount), 2) AS tarifa_prom,
       ROUND(AVG(total_amount), 2) AS total_prom,
       ROUND(SUM(fare_amount) / SUM(trip_distance), 2) AS usd_por_milla
FROM trips_tbl GROUP BY taxi""",
        display="table",
        viz_settings={},
    ),
    dict(
        name="8. Porcentaje de propina promedio por hora (tarjeta)",
        description="Pregunta 8: como varia el porcentaje promedio de propina segun la hora del viaje?",
        sql="""SELECT hour(pickup) AS hora,
       ROUND(100.0 * AVG(tip_amount / NULLIF(fare_amount, 0)), 1) AS pct_propina_prom
FROM trips_tbl WHERE payment_type = 1 GROUP BY hora ORDER BY hora""",
        display="line",
        viz_settings={"graph.dimensions": ["hora"], "graph.metrics": ["pct_propina_prom"]},
    ),
]

# 2 columnas x 4 filas (grid de Metabase: 24 unidades de ancho)
POSITIONS = [
    (0, 0, 12, 8), (12, 0, 12, 8),
    (0, 8, 12, 8), (12, 8, 12, 8),
    (0, 16, 12, 8), (12, 16, 12, 8),
    (0, 24, 12, 8), (12, 24, 12, 8),
]


class Metabase:
    def __init__(self, base_url, email, password):
        self.base_url = base_url.rstrip("/")
        body = {"username": email, "password": password}
        resp = self._call("POST", "/api/session", body, session=None)
        self.session = resp["id"]

    def _call(self, method, path, body=None, session="__use_self__"):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base_url + path, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        token = self.session if session == "__use_self__" else session
        if token:
            req.add_header("X-Metabase-Session", token)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{method} {path} -> {e.code}: {e.read().decode()}")

    def get(self, path):
        return self._call("GET", path)

    def post(self, path, body=None):
        return self._call("POST", path, body)

    def put(self, path, body=None):
        return self._call("PUT", path, body)

    def delete(self, path):
        return self._call("DELETE", path)


def find_database(mb, name):
    data = mb.get("/api/database")
    for d in data.get("data", data):
        if d["name"] == name:
            return d["id"]
    return None


def find_dashboard(mb, name):
    for d in mb.get("/api/dashboard"):
        if d["name"] == name:
            return d["id"]
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.environ.get("METABASE_URL", "http://metabase:3000"))
    parser.add_argument("--email", default=os.environ.get("METABASE_EMAIL"))
    parser.add_argument("--password", default=os.environ.get("METABASE_PASSWORD"))
    args = parser.parse_args()

    if not args.email or not args.password:
        sys.exit(
            "Falta --email/--password (o METABASE_EMAIL/METABASE_PASSWORD).\n"
            "Use las credenciales del usuario administrador creado en el "
            "asistente de primer arranque de http://localhost:3000."
        )

    mb = Metabase(args.url, args.email, args.password)

    db_id = find_database(mb, DB_NAME)
    if db_id is None:
        print(f"Creando base de datos '{DB_NAME}'...")
        db = mb.post("/api/database", {
            "engine": "duckdb",
            "name": DB_NAME,
            "details": {"database_file": DUCKDB_PATH, "read_only": True},
        })
        db_id = db["id"]
    else:
        print(f"Base de datos '{DB_NAME}' ya existe (id={db_id}), se reutiliza.")

    existing_dash_id = find_dashboard(mb, DASHBOARD_NAME)
    if existing_dash_id is not None:
        print(f"El tablero '{DASHBOARD_NAME}' ya existe (id={existing_dash_id}). "
              f"No se crea de nuevo. URL: {args.url}/dashboard/{existing_dash_id}")
        return

    print("Creando preguntas (cards)...")
    created = []
    for c in CARDS:
        card = mb.post("/api/card", {
            "name": c["name"],
            "description": c["description"],
            "dataset_query": {
                "type": "native",
                "native": {"query": c["sql"], "template-tags": {}},
                "database": db_id,
            },
            "display": c["display"],
            "visualization_settings": c["viz_settings"],
        })
        print(f"  card {card['id']:>3}  {c['name']}")
        created.append(card)

    print("Creando tablero...")
    dash = mb.post("/api/dashboard", {"name": DASHBOARD_NAME})
    dash_id = dash["id"]

    dash_cards = [
        {
            "id": -(card["id"]),
            "card_id": card["id"],
            "col": col, "row": row, "size_x": size_x, "size_y": size_y,
            "parameter_mappings": [],
        }
        for card, (col, row, size_x, size_y) in zip(created, POSITIONS)
    ]
    mb.put(f"/api/dashboard/{dash_id}/cards", {"cards": dash_cards})

    print(f"\nListo. Tablero disponible en: {args.url}/dashboard/{dash_id}")


if __name__ == "__main__":
    main()
