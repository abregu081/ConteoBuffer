import os
import sys
from pathlib import Path

class Configuraciones:
    def __init__(self):
        self.directorio_salida = None
        self.directorio_entrada = None
        self.nombre_medio = None
        self.ruta_programa = None
        self.direccionario_valores = self.Capturar_Datos_txt()
        
    def _resolver_ruta_configuracion(self):
        candidatos = []

        if getattr(sys, "frozen", False):
            candidatos.append(Path(sys.executable).resolve().parent / "Configuraciones.cfg")

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

    def obtener_fecha_inicio(self):
        valores = self.direccionario_valores
        return valores.get("Fecha_Inicio", "")
                    
    def obtenerYcrear_directorio_salida(self):
        valores = self.direccionario_valores
        directorio_salida = valores.get("Directorio_Salida")

        if not os.path.exists(directorio_salida):
            os.makedirs(directorio_salida)

        return directorio_salida

    def obtener_directorio_Entrada(self):
        valores = self.direccionario_valores
        return valores.get("Directorio_Entrada")
    
    def obtener_nombre_medio(self):
        valores = self.direccionario_valores
        return valores.get("Medio")

    def obtener_codigo_operacional(self):
        valores = self.direccionario_valores
        return valores.get("Codigo_Operacional", "")

    def obtener_contador_modelo(self, model):
        """Devuelve el contador (01, 02, 03...) segun el sufijo del modelo."""
        sufijo = model.split('_')[-1]   # STLA_LATAM_AV_MAIN -> MAIN
        valores = self.direccionario_valores
        return valores.get(f"Contador_{sufijo}", "01")


