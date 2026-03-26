import os
import sys
from datetime import datetime
import ConectorSQL
from Configuraciones import Configuraciones
from FormatoLog import Plantilla_Inicio, Plantilla_Final
import csv

conector = ConectorSQL.ConectorSQL("Buffer_archivos_procesados.db")
configuracion = Configuraciones()
directorio_salida = configuracion.obtenerYcrear_directorio_salida()
directorio_entrada = configuracion.obtener_directorio_Entrada()
nombre_medio = configuracion.obtener_nombre_medio()

configuracion.obtenerYcrear_directorio_salida()
conector.Conectar()
conector.CrearTabla()

registros = []



def Procesar_registros(linea):
    mensaje_procesar = linea.split(" ")
    hora_inicio = mensaje_procesar[1]
    dato_relevante = mensaje_procesar[3]

    if "BREQ" in dato_relevante:
        serial = dato_relevante[1].split("/")
        status = dato_relevante[-1]

    


for archivo in os.listdir(directorio_entrada):
    ultimo_registro = conector.ultimo_archivo_procesado()
    if ultimo_registro is None:
        if archivo.startswith("[Operation]") and archivo.endswith(".log"):
            fecha = archivo.split(" ")[1].split(".")[0]
            ruta_archivo = os.path.join(directorio_entrada, archivo)
            hora_procesamiento = datetime.now().strftime("%H:%M:%S")
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                for linea in f:
                    if "[S]" in linea or "[O]" in linea or "[R]" in linea:
                        continue
                    Procesar_registros()




                


            