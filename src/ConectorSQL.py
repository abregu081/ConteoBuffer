import sqlite3

class ConectorSQL():
    def __init__(self,ruta_db):
        self.conexion = None
        self.cursor = None
        self.ruta_db = ruta_db

    def Conectar(self):
        self.conexion = sqlite3.connect(self.ruta_db)
        self.cursor = self.conexion.cursor()
    
    def CrearTabla(self):
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='archivos_procesados'"
        )
        if not self.cursor.fetchone():
            self.cursor.execute('''
                CREATE TABLE archivos_procesados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Fecha TEXT UNIQUE,
                    Direccion_Archivo TEXT,
                    Nombre_Archivo TEXT,
                    Hora_Procesamiento TEXT
                )
            ''')
            self.conexion.commit()
    
    def InsertarRegistro(self, fecha, direccion_archivo, nombre_archivo, hora_procesamiento):
        try:
            self.cursor.execute('''
                INSERT INTO archivos_procesados (Fecha, Direccion_Archivo, Nombre_Archivo, Hora_Procesamiento)
                VALUES (?, ?, ?, ?)
            ''', (fecha, direccion_archivo, nombre_archivo, hora_procesamiento))
            self.conexion.commit()
        except sqlite3.IntegrityError:
            print(f"El archivo con fecha {fecha} ya ha sido registrado.")

    def ultimo_archivo_procesado(self):
        self.cursor.execute('''
            SELECT Direccion_Archivo
            FROM archivos_procesados
            ORDER BY id DESC
            LIMIT 1
        ''')
        return self.cursor.fetchone()
