"""Conexión y operaciones contra MySQL."""
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

import config


def conectar(con_bd: bool = True):
    p = config.parametros_bd()
    url = URL.create("mysql+pymysql", username=p["user"], password=p["password"], host=p["host"],
                     port=p["port"], database=p["database"] if con_bd else None, query={"charset": "utf8mb4"})
    return create_engine(url, pool_pre_ping=True)


def crear_esquema():
    """Crea la base y las tablas si no existen (schema.sql, con el nombre de BD del .env)."""
    bd = config.parametros_bd()["database"]
    sql = (config.BASE / "schema.sql").read_text(encoding="utf-8").replace("dw_ventas", bd)
    engine = conectar(con_bd=False)
    with engine.begin() as conn:
        for sentencia in filter(None, (s.strip() for s in sql.split(";"))):
            conn.execute(text(sentencia))
    engine.dispose()


def upsert(conn, tabla: str, pk: str, df, lote: int = 1000) -> None:
    """INSERT ... ON DUPLICATE KEY UPDATE: inserta lo nuevo y actualiza lo existente."""
    if df.empty:
        return
    cols = list(df.columns)
    sets = ", ".join(f"{c}=VALUES({c})" for c in cols if c != pk)
    sql = text(f"INSERT INTO {tabla} ({', '.join(cols)}) VALUES ({', '.join(':' + c for c in cols)}) "
               f"ON DUPLICATE KEY UPDATE {sets}")
    registros = df.astype(object).where(df.notna(), None).to_dict("records")
    for i in range(0, len(registros), lote):
        conn.execute(sql, registros[i:i + lote])


def contar(conn, tabla: str) -> int:
    return conn.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
