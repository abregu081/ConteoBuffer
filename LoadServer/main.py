import argparse
import logging
from ConectorDB import ConectorDB
from ConectorSQLite import ConectorSQLite
from Configuraciones import Configuraciones
from CalcularConteo import CalcularConteo
from ConsultasSQL import ConsultasSQL
from DebugBuffer import DebugBuffer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

#Segmento destina a ver los detalles de mi pantalla

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Genera los CSV de debug de serials pendientes",
    )
    parser.add_argument(
        "--diagnostico",
        action="store_true",
        help="Muestra informacion de diagnostico del servidor MySQL (timezone, modelos, salidas)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config = Configuraciones()
    sqlite_path = config.obtener_sqlite_path()
    dias_retencion = config.obtener_dias_retencion()
    objetivo_diario_dcsd = config.obtener_objetivo_diario_dcsd()
    objetivo_diario_main = config.obtener_objetivo_diario_main()

    logging.info(
        f"[CONFIG] cfg={config.ruta_programa}  "
        f"host={config.direccionario_valores.get('host')}  db={config.direccionario_valores.get('db')}  "
        f"medio_entrada={config.obtener_medio_entrada_id()}  "
        f"salida_dcsd={config.obtener_buffer_dcsd()['salida_id']}  salida_main={config.obtener_buffer_main()['salida_id']}  "
        f"dias_sin_conteo={config.obtener_dias_sin_conteo()}"
    )

    db = ConectorDB()
    db.conectar_db()
    logging.info("Conectado a MySQL")

    sqlite = ConectorSQLite(sqlite_path)
    logging.info(f"SQLite en {sqlite_path}")

    consultas = ConsultasSQL(db.conn, db.cursor, config)
    conteo = CalcularConteo(consultas, config)
    debug = DebugBuffer(consultas, config) if args.debug else None

    try:
        db.reconectar_si_necesario()
        logging.info("Calculando resumen de buffers...")
        resumen = conteo.resumen()
        logging.info("Resumen calculado OK")

        sqlite.insertar_conteo(resumen["buffer_dcsd"], resumen["buffer_main"], objetivo_diario_dcsd, objetivo_diario_main)

        logging.info(
            f"DCSD={resumen['buffer_dcsd']}  MAIN={resumen['buffer_main']}  "
            f"TOTAL={resumen['buffer_total']}  "
            f"ENTRADAS_DCSD={resumen['entradas_dcsd']}  ENTRADAS_MAIN={resumen['entradas_main']}  ENTRADAS_TOTAL={resumen['entradas']}  "
            f"SALIDAS_DCSD={resumen['salidas_dcsd']}  SALIDAS_MAIN={resumen['salidas_main']}  "
            f"OBJ_DAILY_DCSD={objetivo_diario_dcsd}  OBJ_DAILY_MAIN={objetivo_diario_main}"
        )

        if args.debug:
            logging.info("Generando debug de serials pendientes...")
            debug.reporte()
            logging.info("Debug generado OK")

        if args.diagnostico:
            cfg_dcsd = config.obtener_buffer_dcsd()
            cfg_main = config.obtener_buffer_main()
            diag = consultas.diagnostico(
                config.obtener_medio_entrada_id(),
                cfg_dcsd["salida_id"],
                cfg_main["salida_id"],
            )
            srv = diag["servidor"]
            logging.info(
                f"[DIAG] MySQL tz_global={srv['tz_global']}  tz_session={srv['tz_session']}  "
                f"CURDATE={srv['hoy']}  NOW={srv['ahora']}"
            )
            logging.info(f"[DIAG] SALIDAS_DCSD={diag['salidas_dcsd']}  SALIDAS_MAIN={diag['salidas_main']}")
            logging.info("[DIAG] Modelos en Router (ultimos dias_sin_conteo dias):")
            for row in diag["modelos_router"]:
                logging.info(f"  modelo={row['modelo']}  serials={row['cant']}")

        sqlite.limpiar_antiguos(dias_retencion)
        logging.info(f"Limpieza SQLite: eliminados registros > {dias_retencion} días")

    except Exception:
        logging.exception("Error al ejecutar conteo")
    finally:
        db.cerrar_conexion()
        sqlite.cerrar()
        logging.info("Conexiones cerradas. Fin.")

if __name__ == "__main__":
    main()


