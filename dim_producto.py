from comunes import normalizar, validar_basico, separar, marcar

NOMBRE = "DIM_PRODUCTO"
PK = "ProductoID"


def transformar(df):
    df = normalizar(df, ids=[PK],
                    texto=["NombreProducto", "MarcaProducto", "NombreCategoria", "NombreProveedor", "PaisProveedor"],
                    decimales=["PrecioListado"])
    validar_basico(df, PK)
    marcar(df, df["PrecioListado"] < 0, "precio listado negativo")
    return separar(df)
