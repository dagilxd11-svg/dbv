from comunes import normalizar, validar_basico, separar

NOMBRE = "DIM_CLIENTE"
PK = "ClienteID"


def transformar(df):
    df = normalizar(df, ids=[PK], texto=["NombreCliente", "Genero", "RangoEdad", "Ciudad", "SegmentoCliente"])
    validar_basico(df, PK)
    return separar(df)
