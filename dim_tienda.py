from comunes import normalizar, validar_basico, separar

NOMBRE = "DIM_TIENDA"
PK = "TiendaID"


def transformar(df):
    df = normalizar(df, ids=[PK], texto=["NombreTienda", "Ciudad", "Region"], fechas=["FechaApertura"])
    validar_basico(df, PK)
    return separar(df)
