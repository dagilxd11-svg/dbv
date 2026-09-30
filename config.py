"""Rutas y parámetros de conexión (leídos del archivo .env)."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE = Path(__file__).parent
ENTRADA = BASE / "data" / "entrada"
RECHAZADOS = BASE / "data" / "rechazados"

load_dotenv(BASE / ".env")


def parametros_bd() -> dict:
    faltan = [v for v in ("DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME") if not os.getenv(v)]
    if faltan:
        raise SystemExit(f"Faltan variables en .env: {', '.join(faltan)}")
    return dict(host=os.getenv("DB_HOST"), port=int(os.getenv("DB_PORT")), user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"))
