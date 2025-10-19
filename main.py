from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

app = FastAPI(title="PNCP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=5432,
    )

@app.get("/")
def root():
    return {"status": "API Online 🚀"}

@app.get("/licitacoes")
def listar_licitacoes(
    cidade: str | None = Query(None),
    tipo_pregao: str | None = Query(None),
    data_inicio: str | None = Query(None),
    data_final: str | None = Query(None)
):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT id, cidade, tipo_pregao, data_inicio, data_final, status
        FROM licitacoes WHERE status = 'ativa'
    """
    params = []

    if cidade:
        query += " AND cidade ILIKE %s"
        params.append(f"%{cidade}%")
    if tipo_pregao:
        query += " AND tipo_pregao ILIKE %s"
        params.append(f"%{tipo_pregao}%")
    if data_inicio:
        query += " AND data_inicio >= %s"
        params.append(data_inicio)
    if data_final:
        query += " AND data_final <= %s"
        params.append(data_final)

    cur.execute(query, params)
    data = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "total": len(data),
        "results": [
            {
                "id": r[0],
                "cidade": r[1],
                "tipo_pregao": r[2],
                "data_inicio": r[3],
                "data_final": r[4],
                "status": r[5],
            } for r in data
        ]
    }
