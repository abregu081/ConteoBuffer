import os

class Configuraciones:
    def __init__(self):
        self.directorio_salida = None
        self.directorio_entrada = None
        self.nombre_medio = None
        self.ruta_programa = None
        self.db_sql_lite = "Buffer_archivos_procesados.db"
        self.direccionario_valores = self.Capturar_Datos_txt
        self.ruta_db = None
        
    def Capturar_Datos_txt(self):
        self.ruta_programa = os.path.dirname(os.path.abspath(__file__))
        ruta_Archivo_configuraciones = os.path.join(self.ruta_programa,"Configuraciones.cfg")
        direccionario_valores = {}
        with open(ruta_Archivo_configuraciones, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                linea = linea.strip()
                if not linea:
                    continue
                if linea.startswith(';') or linea.startswith('//') or linea.startswith('#'):
                    continue
                if '=' in linea:
                    clave, valor = linea.split("=",1)
                    direccionario_valores[clave.strip()] = valor.strip()
            return direccionario_valores
                    
    def obtenerYcrear_directorio_salida(self):
        valores = self.direccionario_valores
        directorio_salida = valores.get("Directorio_Salida")
        if os.path.exists(directorio_salida):
            pass
        else:
            os.makedirs(directorio_salida)
            carpeta_db = "Registros_SQL"
            ruta_carpeta_db = os.path.join(directorio_salida, carpeta_db)
            if not os.path.exists(ruta_carpeta_db):
                os.makedirs(ruta_carpeta_db)
                ruta_archivo_db = os.path.join(ruta_carpeta_db, self.db_sql_lite)
                if not os.path.exists(ruta_archivo_db):
                    with open(ruta_archivo_db, 'w', encoding='utf-8'):
                        pass
                else:
                    pass
            else:
                pass
        self.ruta_db = ruta_archivo_db
        return directorio_salida

    def obtener_directorio_Entrada(self):
        valores = self.direccionario_valores
        return valores.get("Directorio_Entrada")
    
    def obtener_nombre_medio(self):
        valores = self.direccionario_valores
        return valores.get("Medio")

    
    
    

        
    



