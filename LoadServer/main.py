import logging
from ConectorDB import ConectorDB
from ConectorSQLite import ConectorSQLite
from Configuraciones import Configuraciones
from CalcularConteo import CalcularConteo
from ConsultasSQL import ConsultasSQL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def main():
    config = Configuraciones()
    sqlite_path = config.obtener_sqlite_path()
    dias_retencion = config.obtener_dias_retencion()
    objetivo_diario_dcsd = config.obtener_objetivo_diario_dcsd()
    objetivo_diario_main = config.obtener_objetivo_diario_main()

    db = ConectorDB()
    db.conectar_db()
    logging.info("Conectado a MySQL")

    sqlite = ConectorSQLite(sqlite_path)
    logging.info(f"SQLite en {sqlite_path}")

    consultas = ConsultasSQL(db.conn, db.cursor)
    conteo = CalcularConteo(consultas)

    try:
        resumen = conteo.resumen()

        sqlite.insertar_conteo(resumen["buffer_dcsd"], resumen["buffer_main"], objetivo_diario_dcsd, objetivo_diario_main)

        logging.info(
            f"DCSD={resumen['buffer_dcsd']}  MAIN={resumen['buffer_main']}  "
            f"TOTAL={resumen['buffer_total']}  OBJ_DAILY_DCSD={objetivo_diario_dcsd}  OBJ_DAILY_MAIN={objetivo_diario_main}"
        )

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


