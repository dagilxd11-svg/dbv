from comunes import normalizar, validar_basico, separar, marcar

NOMBRE = "DIM_FECHA"
PK = "FechaID"


def transformar(df):
    df = normalizar(df,
                    texto=["Trimestre", "NombreMes", "NombreDiaSemana", "EsFinDeSemana"],
                    enteros=["FechaID", "Anio", "Mes", "Dia", "DiaSemana"],
                    fechas=["Fecha"])
    validar_basico(df, PK)
    # FechaID debe coincidir con la fecha (formato AAAAMMDD)
    marcar(df, df["Fecha"].notna() & (df["FechaID"].astype("string") != df["Fecha"].astype("string").str.replace("-", "")),
           "FechaID no coincide con Fecha")
    marcar(df, df["Fecha"].duplicated(keep="last"), "fecha duplicada")
    return separar(df)
