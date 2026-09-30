"""Un módulo por tabla. Orden de carga: dimensiones primero, hechos al final."""
from . import dim_cliente, dim_fecha, dim_producto, dim_tienda, ventas_fact

ORDEN_CARGA = [dim_cliente, dim_fecha, dim_producto, dim_tienda, ventas_fact]
