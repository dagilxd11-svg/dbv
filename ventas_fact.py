import pandas as pd

from comunes import normalizar, validar_basico, separar, marcar

NOMBRE = "VENTAS_FACT"
PK = "VentaID"
# columna de la fact -> (tabla dimensión, llave en la dimensión)
FKS = {"FechaID": ("DIM_FECHA", "FechaID"), "TiendaID": ("DIM_TIENDA", "TiendaID"),
       "ProductoID": ("DIM_PRODUCTO", "ProductoID"), "ClienteID": ("DIM_CLIENTE", "ClienteID")}


def transformar(df):
    df = normalizar(df, ids=[PK, "TiendaID", "ProductoID", "ClienteID"],
                    enteros=["FechaID", "Unidades"],
                    decimales=["PrecioUnitario", "Descuento", "ValorVenta"])
    validar_basico(df, PK)
    marcar(df, (df["Unidades"] <= 0) | (df["PrecioUnitario"] < 0), "unidades/precio no válidos")
    marcar(df, ~df["Descuento"].between(0, 1), "descuento fuera de 0-1")
    # ValorVenta siempre se recalcula para garantizar consistencia
    df["ValorVenta"] = (df["Unidades"] * df["PrecioUnitario"] * (1 - df["Descuento"])).round(2)
    return separar(df)


def validar_integridad(fact, dims, conn=None):
    """Cada venta debe apuntar a dimensiones existentes (en los CSV o ya cargadas en MySQL).
    dims: {nombre_tabla: DataFrame ya validado}."""
    fact = fact.copy()
    fact["_motivo"] = pd.NA
    for fk, (dim, pk) in FKS.items():
        conocidos = set(dims[dim][pk].astype(str)) if dim in dims else set()
        if conn is not None:
            from sqlalchemy import text
            conocidos |= {str(r[0]) for r in conn.execute(text(f"SELECT {pk} FROM {dim}"))}
        marcar(fact, ~fact[fk].astype(str).isin(conocidos), f"{fk} no existe en {dim}")
    return separar(fact)
