import datetime
import Configuraciones as cfg


class ConsultasSQL:
    def __init__(self, ConexionDB, Cursor, configuraciones=None):
        self.ConexionDB = ConexionDB
        self.Cursor = Cursor
        self.configuraciones = configuraciones or cfg.Configuraciones()

    def contar_buffer(self, medio_entrada_id, medio_salida_dcsd_id, medio_salida_main_id, modelo_like):
        """Cuenta serials únicos que entraron por Router (PASS) con modelo dado,
        y que aún NO aparecieron en ningún medio de salida (DCSD ni MAIN)."""
        dias_sin_conteo = self.configuraciones.obtener_dias_sin_conteo()
        consulta = """
            SELECT COUNT(DISTINCT r.serial) as buffer_count
            FROM Registros r
            WHERE r.medio_id = %s
              AND r.resultado = 'PASS'
              AND r.modelo LIKE %s
              AND r.fecha >= CURDATE() - INTERVAL %s DAY
              AND NOT EXISTS (
                  SELECT 1 FROM Registros r2
                  WHERE r2.medio_id = %s
                    AND r2.serial = r.serial
              )
              AND NOT EXISTS (
                  SELECT 1 FROM Registros r3
                  WHERE r3.medio_id = %s
                    AND r3.serial = r.serial
              )
        """
        self.Cursor.execute(consulta, (medio_entrada_id, modelo_like, dias_sin_conteo, medio_salida_dcsd_id, medio_salida_main_id))
        return self.Cursor.fetchone()["buffer_count"]

    def contar_entradas(self, medio_entrada_id):
        """Total de serials únicos PASS que entraron por Router (misma ventana temporal)."""
        dias_sin_conteo = self.configuraciones.obtener_dias_sin_conteo()
        consulta = """
            SELECT COUNT(DISTINCT serial) as total
            FROM Registros
            WHERE medio_id = %s AND resultado = 'PASS'
              AND fecha >= CURDATE() - INTERVAL %s DAY
        """
        self.Cursor.execute(consulta, (medio_entrada_id, dias_sin_conteo))
        return self.Cursor.fetchone()["total"]

    def contar_entradas_modelo(self, medio_entrada_id, modelo_like):
        """Total de serials únicos PASS por Router filtrado por modelo (misma ventana temporal)."""
        dias_sin_conteo = self.configuraciones.obtener_dias_sin_conteo()
        consulta = """
            SELECT COUNT(DISTINCT serial) as total
            FROM Registros
            WHERE medio_id = %s AND resultado = 'PASS'
              AND modelo LIKE %s
              AND fecha >= CURDATE() - INTERVAL %s DAY
        """
        self.Cursor.execute(consulta, (medio_entrada_id, modelo_like, dias_sin_conteo))
        return self.Cursor.fetchone()["total"]

    def contar_salidas(self, medio_salida_id):
        """Total de registros que pasaron por el medio de salida (misma ventana temporal)."""
        dias_sin_conteo = self.configuraciones.obtener_dias_sin_conteo()
        consulta = """
            SELECT COUNT(DISTINCT serial) as total
            FROM Registros
            WHERE medio_id = %s
              AND fecha >= CURDATE() - INTERVAL %s DAY
        """
        self.Cursor.execute(consulta, (medio_salida_id, dias_sin_conteo))
        return self.Cursor.fetchone()["total"]

    def obtener_serials_pendientes(self, medio_entrada_id, medio_salida_dcsd_id, medio_salida_main_id, modelo_like):
        """Devuelve lista de serials únicos que entraron por Router (PASS) con modelo dado,
        y que aún NO pasaron por ningún medio de salida (DCSD ni MAIN)."""
        dias_sin_conteo = self.configuraciones.obtener_dias_sin_conteo()
        consulta = """
            SELECT r.serial, r.modelo,
                   MAX(r.Fecha) AS fecha_entrada,
                   MAX(r.Hora) AS hora_entrada
            FROM Registros r
            WHERE r.medio_id = %s
              AND r.resultado = 'PASS'
              AND r.modelo LIKE %s
              AND r.fecha >= CURDATE() - INTERVAL %s DAY
              AND NOT EXISTS (
                  SELECT 1 FROM Registros r2
                  WHERE r2.medio_id = %s
                    AND r2.serial = r.serial
              )
              AND NOT EXISTS (
                  SELECT 1 FROM Registros r3
                  WHERE r3.medio_id = %s
                    AND r3.serial = r.serial
              )
            GROUP BY r.serial, r.modelo
            ORDER BY fecha_entrada DESC, hora_entrada DESC
        """
        self.Cursor.execute(consulta, (medio_entrada_id, modelo_like, dias_sin_conteo, medio_salida_dcsd_id, medio_salida_main_id))
        return self.Cursor.fetchall()

    def diagnostico(self, medio_entrada_id, medio_salida_dcsd_id, medio_salida_main_id):
        """Devuelve datos de diagnóstico para comparar entornos:
        timezone del servidor, CURDATE(), y modelos distintos que entran por Router."""
        dias_sin_conteo = self.configuraciones.obtener_dias_sin_conteo()

        self.Cursor.execute("SELECT @@global.time_zone as tz_global, @@session.time_zone as tz_session, CURDATE() as hoy, NOW() as ahora")
        servidor = self.Cursor.fetchone()

        self.Cursor.execute("""
            SELECT modelo, COUNT(DISTINCT serial) as cant
            FROM Registros
            WHERE medio_id = %s AND resultado = 'PASS'
              AND fecha >= CURDATE() - INTERVAL %s DAY
            GROUP BY modelo
            ORDER BY cant DESC
        """, (medio_entrada_id, dias_sin_conteo))
        modelos = self.Cursor.fetchall()

        self.Cursor.execute("""
            SELECT COUNT(DISTINCT serial) as cant
            FROM Registros
            WHERE medio_id = %s
              AND fecha >= CURDATE() - INTERVAL %s DAY
        """, (medio_salida_dcsd_id, dias_sin_conteo))
        salidas_dcsd = self.Cursor.fetchone()["cant"]

        self.Cursor.execute("""
            SELECT COUNT(DISTINCT serial) as cant
            FROM Registros
            WHERE medio_id = %s
              AND fecha >= CURDATE() - INTERVAL %s DAY
        """, (medio_salida_main_id, dias_sin_conteo))
        salidas_main = self.Cursor.fetchone()["cant"]

        return {
            "servidor": servidor,
            "modelos_router": modelos,
            "salidas_dcsd": salidas_dcsd,
            "salidas_main": salidas_main,
        }

    def obtener_ultimo_registro(self):
        consulta = """
            SELECT Fecha, Hora FROM Registros
            ORDER BY Fecha DESC, Hora DESC
            LIMIT 1
        """
        self.Cursor.execute(consulta)
        resultado = self.Cursor.fetchone()
        if not resultado:
            return None
        fecha_hora = f"{resultado['Fecha']} {resultado['Hora']}"
        return datetime.datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S")
