import os
import sys
from pathlib import Path


class Configuraciones:
    def __init__(self):
        self.host = None
        self.user = None
        self.password = None
        self.db = None
        self.medio_entrada = None
        self.medios_salida = None
        self.linea_id = None
        self.ruta_programa = None
        self.direccionario_valores = self.Capturar_Datos_txt()

    def _resolver_ruta_configuracion(self):
        candidatos = []

        if getattr(sys, "frozen", False):
            candidatos.append(
                Path(sys.executable).resolve().parent / "Configuraciones.cfg"
            )

        candidatos.append(Path(__file__).resolve().parent / "Configuraciones.cfg")
        candidatos.append(Path.cwd() / "Configuraciones.cfg")

        for ruta in candidatos:
            if ruta.exists():
                self.ruta_programa = str(ruta.parent)
                return ruta

        self.ruta_programa = str(candidatos[0].parent)
        return candidatos[0]

    def Capturar_Datos_txt(self):
        ruta_Archivo_configuraciones = self._resolver_ruta_configuracion()
        direccionario_valores = {}
        with open(ruta_Archivo_configuraciones, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if not linea:
                    continue
                if (
                    linea.startswith(";")
                    or linea.startswith("//")
                    or linea.startswith("#")
                ):
                    continue
                if "=" in linea:
                    clave, valor = linea.split("=", 1)
                    direccionario_valores[clave.strip()] = valor.strip()
            return direccionario_valores

    def obtener_datos_parametros_db(self):
        valores = self.direccionario_valores
        self.host = valores.get("host", "")
        self.user = valores.get("user", "")
        self.password = valores.get("password", "")
        self.db = valores.get("db", "")
        return self.host, self.user, self.password, self.db

    def obtener_medio_entrada_id(self):
        return int(self.direccionario_valores.get("Medio_Entrada_ID", "10"))

    def obtener_buffer_dcsd(self):
        return {
            "salida_id": int(self.direccionario_valores.get("Buffer_DCSD_Salida_ID", "4")),
            "max": int(self.direccionario_valores.get("Buffer_DCSD_Max", "384")),
        }

    def obtener_buffer_main(self):
        return {
            "salida_id": int(self.direccionario_valores.get("Buffer_MAIN_Salida_ID", "6")),
            "max": int(self.direccionario_valores.get("Buffer_MAIN_Max", "512")),
        }

    def obtener_linea_id(self):
        return self.direccionario_valores.get("Linea_ID", "1")

    def obtener_intervalo_polling(self):
        return int(self.direccionario_valores.get("intervalo_polling", "10"))

    def obtener_sqlite_path(self):
        raw = self.direccionario_valores.get("sqlite_path", "./buffer_counts.db")
        path = Path(raw)
        if not path.is_absolute():
            path = Path(self.ruta_programa) / raw
        return str(path)

    def obtener_dias_retencion(self):
        return int(self.direccionario_valores.get("dias_retencion_sqlite", "30"))
    
    def obtener_objetivo_diario_dcsd(self):
        return int(self.direccionario_valores.get("objetivo_diario_dcsd", "100"))
    
    def obtener_objetivo_diario_main(self):
        return int(self.direccionario_valores.get("objetivo_diario_main", "100"))

    def obtener_dias_sin_conteo(self):
        return int(self.direccionario_valores.get("dias_sin_conteo", "14"))
