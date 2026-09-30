"""Funciones de lectura y limpieza compartidas por todas las tablas."""
import pandas as pd


def leer_csv(ruta) -> pd.DataFrame:
    """CSV con ';' como separador, coma decimal y BOM (Excel)."""
    df = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False)
    df.columns = df.columns.str.strip()
    return df.replace({"": pd.NA})


def normalizar(df, *, ids=(), texto=(), enteros=(), decimales=(), fechas=()) -> pd.DataFrame:
    """Quita espacios, unifica mayúsculas en IDs y convierte tipos."""
    df = df.copy()
    for c in texto:
        df[c] = df[c].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    for c in ids:
        df[c] = df[c].astype("string").str.strip().str.upper()
    for c in enteros:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    for c in decimales:
        df[c] = pd.to_numeric(df[c].astype("string").str.replace(",", ".", regex=False), errors="coerce")
    for c in fechas:
        df[c] = pd.to_datetime(df[c], errors="coerce").dt.date
    df["_motivo"] = pd.NA
    return df


def marcar(df, mascara, motivo) -> None:
    """Anota el motivo de rechazo en las filas que cumplen la máscara (si aún no tienen uno)."""
    df.loc[mascara & df["_motivo"].isna(), "_motivo"] = motivo


def validar_basico(df, pk) -> None:
    """Reglas comunes: sin campos vacíos/inválidos y sin llaves duplicadas (gana el último registro)."""
    marcar(df, df.drop(columns="_motivo").isna().any(axis=1), "campos vacíos o con formato inválido")
    marcar(df, df.duplicated(subset=pk, keep="last"), "llave duplicada en el archivo (se conserva el último)")


def separar(df):
    """Devuelve (válidos, rechazados)."""
    malos = df[df["_motivo"].notna()].copy()
    buenos = df[df["_motivo"].isna()].drop(columns="_motivo").reset_index(drop=True)
    return buenos, malos
