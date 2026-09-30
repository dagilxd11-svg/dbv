"""
Orquestador del pipeline: CSV -> limpieza/validación (pandas) -> MySQL.

    python pipeline.py                 # lee data/entrada/*.csv y actualiza MySQL
    python pipeline.py --dry-run       # solo valida, no toca la base de datos
    python pipeline.py --entrada otra_carpeta

Es seguro repetirlo: lo nuevo se inserta, lo existente se actualiza, sin duplicados.
"""
import argparse
import logging
from pathlib import Path

import pandas as pd

import config
from comunes import leer_csv
from tablas import ORDEN_CARGA, ventas_fact

log = logging.getLogger("pipeline")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", default=str(config.ENTRADA))
    ap.add_argument("--dry-run", action="store_true", help="solo valida, sin escribir en MySQL")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # 1) Extraer + transformar cada tabla con su propio módulo
    limpios, rechazos = {}, []
    for t in ORDEN_CARGA:
        ruta = Path(args.entrada) / f"{t.NOMBRE}.csv"
        if not ruta.exists():
            log.warning("No se encontró %s, se omite", ruta.name)
            continue
        ok, mal = t.transformar(leer_csv(ruta))
        limpios[t.NOMBRE] = ok
        if len(mal):
            rechazos.append(mal.assign(_tabla=t.NOMBRE))
        log.info("%-12s leídos=%d válidos=%d rechazados=%d", t.NOMBRE, len(ok) + len(mal), len(ok), len(mal))

    # 2) Validar integridad y cargar
    def validar_hechos(conn=None):
        if ventas_fact.NOMBRE in limpios:
            limpios[ventas_fact.NOMBRE], huerf = ventas_fact.validar_integridad(limpios[ventas_fact.NOMBRE], limpios, conn)
            if len(huerf):
                rechazos.append(huerf.assign(_tabla=ventas_fact.NOMBRE))
                log.warning("VENTAS_FACT: %d ventas rechazadas por llaves inexistentes", len(huerf))

    if args.dry_run:
        validar_hechos()
    else:
        import db
        db.crear_esquema()
        engine = db.conectar()
        with engine.begin() as conn:               # una sola transacción: todo o nada
            validar_hechos(conn)
            for t in ORDEN_CARGA:                  # dimensiones primero, hechos al final
                if t.NOMBRE in limpios:
                    db.upsert(conn, t.NOMBRE, t.PK, limpios[t.NOMBRE])
                    log.info("%-12s upsert de %d registros", t.NOMBRE, len(limpios[t.NOMBRE]))
        with engine.connect() as conn:
            for t in ORDEN_CARGA:
                log.info("Total en MySQL %-12s = %d", t.NOMBRE, db.contar(conn, t.NOMBRE))

    # 3) Guardar rechazados para revisión
    if rechazos:
        config.RECHAZADOS.mkdir(parents=True, exist_ok=True)
        destino = config.RECHAZADOS / "rechazados.csv"
        pd.concat(rechazos).to_csv(destino, sep=";", index=False, encoding="utf-8-sig")
        log.warning("Registros rechazados guardados en %s", destino)
    log.info("Pipeline finalizado%s", " (dry-run)" if args.dry_run else "")


if __name__ == "__main__":
    main()
