import sqlite3
import datetime

class ConectorSQLite:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self._inicializar()

    def _inicializar(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS buffer_counts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                buffer_dcsd INTEGER NOT NULL,
                buffer_main INTEGER NOT NULL,
                buffer_total INTEGER NOT NULL,
                objetivo_diario_dcsd INTEGER NOT NULL,
                objetivo_diario_main INTEGER NOT NULL
            )
        """)
        # Migración: agregar columnas nuevas si la tabla ya existía con esquema anterior
        for column, definition in [
            ("objetivo_diario_dcsd", "INTEGER NOT NULL DEFAULT 0"),
            ("objetivo_diario_main", "INTEGER NOT NULL DEFAULT 0"),
        ]:
            try:
                self.conn.execute(f"ALTER TABLE buffer_counts ADD COLUMN {column} {definition}")
            except sqlite3.OperationalError:
                pass  # La columna ya existe
        self.conn.commit()

    def insertar_conteo(self, buffer_dcsd, buffer_main, objetivo_diario_dcsd, objetivo_diario_main):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            "INSERT INTO buffer_counts (timestamp, buffer_dcsd, buffer_main, buffer_total, objetivo_diario_dcsd, objetivo_diario_main) VALUES (?, ?, ?, ?, ?, ?)",
            (timestamp, buffer_dcsd, buffer_main, buffer_dcsd + buffer_main, objetivo_diario_dcsd, objetivo_diario_main),
        )
        self.conn.commit()

    def limpiar_antiguos(self, dias):
        fecha_limite = (datetime.datetime.now() - datetime.timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute("DELETE FROM buffer_counts WHERE timestamp < ?", (fecha_limite,))
        self.conn.commit()

    def cerrar(self):
        if self.conn:
            self.conn.close()
            self.conn = None
