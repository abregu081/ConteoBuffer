import datetime
import Configuraciones as cfg


class ConsultasSQL:
    def __init__(self, ConexionDB, Cursor):
        self.ConexionDB = ConexionDB
        self.Cursor = Cursor
        self.configuraciones = cfg.Configuraciones()

    def contar_buffer(self, medio_entrada_id, box, medio_salida_id):
        """Cuenta placas que entraron por Router con un box específico (PASS)
        y cuyo serial aún no apareció en el medio de salida correspondiente.
        Descuenta si la placa pasó por salida con cualquier resultado (PASS o FAIL).
        Excluye registros con más de dias_sin_conteo días de antigüedad."""
        dias_sin_conteo = self.configuraciones.obtener_dias_sin_conteo()
        consulta = """
            SELECT COUNT(DISTINCT r.serial) as buffer_count
            FROM Registros r
            WHERE r.medio_id = %s
              AND r.box = %s
              AND r.resultado = 'PASS'
              AND r.fecha >= CURDATE() - INTERVAL %s DAY
              AND NOT EXISTS (
                  SELECT 1 FROM Registros r2
                  WHERE r2.medio_id = %s
                    AND r2.serial = r.serial
              )
        """
        self.Cursor.execute(consulta, (medio_entrada_id, box, dias_sin_conteo, medio_salida_id))
        return self.Cursor.fetchone()["buffer_count"]

    def contar_entradas(self, medio_entrada_id, box):
        """Total de registros PASS que entraron por Router para un box."""
        consulta = """
            SELECT COUNT(DISTINCT serial) as total
            FROM Registros
            WHERE medio_id = %s AND box = %s AND resultado = 'PASS'
        """
        self.Cursor.execute(consulta, (medio_entrada_id, box))
        return self.Cursor.fetchone()["total"]

    def contar_salidas(self, medio_salida_id):
        """Total de registros que pasaron por el medio de salida."""
        consulta = """
            SELECT COUNT(DISTINCT serial) as total
            FROM Registros
            WHERE medio_id = %s
        """
        self.Cursor.execute(consulta, (medio_salida_id,))
        return self.Cursor.fetchone()["total"]

    def obtener_serials_pendientes(self, medio_entrada_id, box, medio_salida_id):
        """Devuelve lista de serials que entraron por Router (PASS) con un box
        pero que aún no pasaron por el medio de salida correspondiente (ni PASS ni FAIL).
        Incluye serial, modelo, fecha y hora de entrada."""
        dias_sin_conteo = self.configuraciones.obtener_dias_sin_conteo()
        consulta = """
            SELECT r.serial, r.modelo, r.Fecha AS fecha_entrada, r.Hora AS hora_entrada
            FROM Registros r
            WHERE r.medio_id = %s
              AND r.box = %s
              AND r.resultado = 'PASS'
              AND r.fecha >= CURDATE() - INTERVAL %s DAY
              AND NOT EXISTS (
                  SELECT 1 FROM Registros r2
                  WHERE r2.medio_id = %s
                    AND r2.serial = r.serial
              )
            GROUP BY r.serial, r.modelo, r.Fecha, r.Hora
            ORDER BY r.Fecha DESC, r.Hora DESC
        """
        self.Cursor.execute(consulta, (medio_entrada_id, box, dias_sin_conteo, medio_salida_id))
        return self.Cursor.fetchall()

    
    
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
