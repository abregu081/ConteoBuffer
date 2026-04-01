import os
import csv
import re
from datetime import datetime

from Configuraciones import Configuraciones
from LectorLog import recopilar_pasadas
from FormatoLog import Plantilla_Inicio, Plantilla_Test, Plantilla_Final


def calcular_test_time(hora_inicio, hora_fin):
    """Diferencia en segundos entre dos tiempos HH:MM:SS.mmm."""
    if not hora_inicio or not hora_fin:
        return ""
    try:
        fmt = "%H:%M:%S.%f"
        t1 = datetime.strptime(hora_inicio, fmt)
        t2 = datetime.strptime(hora_fin, fmt)
        return round((t2 - t1).total_seconds(), 3)
    except ValueError:
        return ""


def construir_seccion_test(pasada):
    for linea in pasada.get("test_lines", []):
        yield linea
    test_conditions = pasada.get("test_conditions")
    if test_conditions:
        yield "/*================================================================================"
        yield "Test Conditions, Measured Value, Lower Limit, Upper Limit, P/F, Sec"
        yield "================================================================================*/"
        for cond in test_conditions:
            yield f"{cond['condition']} | {cond['measured']} | {cond['lower']} | {cond['upper']} | {cond['pf']} | {cond['sec']}"


def formatear_placa(placa, pasada, fecha_log):
    """
    Genera un bloque #INIT ... BREQ/BCNF/BCMP/BACK ... #END para una sola placa.
    """
    model = pasada["model"]
    tipo_placa = model.split("_")[-1]
    fecha_fmt = f"{fecha_log[:4]}/{fecha_log[4:6]}/{fecha_log[6:8]}"

    result = placa["status"] or placa["status_bcnf"] or "FAIL"
    fail_item = placa["msg_bcnf"] if placa["msg_bcnf"] else ""
    test_time = calcular_test_time(
        placa["hora_inicio"], placa["hora_back"] or placa["hora_bcmp"]
    )

    _jig_map = {"DCSD": "01", "MAIN": "02", "SUB": "03"}
    jig = _jig_map.get(tipo_placa, "")

    valores_inicio = {
        "MODEL": model,
        "TIPO_PLACA": tipo_placa,
        "SERIAL_NUMBER": placa["id"],
        "FECHA": fecha_fmt,
        "HORA": placa["hora_inicio"].split(".")[0],
        "VERSION": "1.0.0",
        "obtener_pc_cpu": "",
        "obtener_pc_ram_available": "",
        "obtener_pc_ram_init_free": "",
        "obtener_pc_disk_free_total": "",
        "obtener_pc_os": "",
        "JIG": jig,
    }
    lineas = [linea.format(**valores_inicio) for linea in Plantilla_Inicio]

    # ── Sección #TEST ─────────────────────────────────────────────────────────
    lineas += list(Plantilla_Test)

    pf = "P" if result == "PASS" else "F"
    lineas.append(f"BREQ [], 0.00, 0.00, 0.00, {pf}, 0.00")
    if placa["hora_bcnf"]:
        lineas.append(f"BCNF [], 0.00, 0.00, 0.00, {pf}, 0.00")
    if placa["hora_bcmp"]:
        lineas.append(f"BCMP [], 0.00, 0.00, 0.00, {pf}, 0.00")
    if placa["hora_back"]:
        lineas.append(f"BACK [], 0.00, 0.00, 0.00, {pf}, 0.00")

    # ── Sección #END ──────────────────────────────────────────────────────────
    valores_final = {
        "result": result,
        "fail_item": fail_item,
        "test_time": test_time,
        "obtener_pc_ram_end_free": "",
        "caracter_retorno": "",
    }
    lineas += [linea.format(**valores_final) for linea in Plantilla_Final]

    return "\n".join(lineas)


def exportar_append(pasadas, ruta_salida, fecha_log):
    """Agrega un bloque #INIT...#END por cada placa individual al archivo de salida."""
    with open(ruta_salida, "a", encoding="utf-8") as f:
        for pasada in pasadas:
            for placa in pasada["placas"]:
                f.write(formatear_placa(placa, pasada, fecha_log) + "\n")


# ── Gestión de archivos_procesados.csv y pasadas_procesadas.csv ──────────────


def cargar_archivos_procesados(ruta_csv):
    """Retorna un set de fechas (YYYYMMDD) ya procesadas completamente."""
    fechas = set()
    if not os.path.exists(ruta_csv):
        return fechas
    with open(ruta_csv, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fechas.add(row["fecha"])
    return fechas


def registrar_archivo_procesado(ruta_csv, fecha, nombre_archivo, hora):
    """Agrega una fecha al CSV de archivos procesados."""
    existe = os.path.exists(ruta_csv)
    with open(ruta_csv, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["fecha", "nombre_archivo", "hora_procesamiento"])
        writer.writerow([fecha, nombre_archivo, hora])


def obtener_ultima_fecha_procesada(ruta_csv):
    """Retorna la fecha YYYYMMDD más reciente en archivos_procesados.csv, o None."""
    if not os.path.exists(ruta_csv):
        return None
    ultima = None
    with open(ruta_csv, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if ultima is None or row["fecha"] > ultima:
                ultima = row["fecha"]
    return ultima


def encontrar_fecha_mas_antigua(directorio):
    """Busca la fecha más antigua entre los logs disponibles en el directorio."""
    patron = re.compile(r"^\[Operation\] (\d{4}-\d{2}-\d{2})\.log$")
    fechas = []
    try:
        for nombre in os.listdir(directorio):
            m = patron.match(nombre)
            if m:
                fechas.append(datetime.strptime(m.group(1), "%Y-%m-%d"))
    except OSError:
        pass
    return min(fechas) if fechas else None


def obtener_fechas_con_log(directorio, fecha_desde, fecha_hasta):
    """
    Retorna lista ordenada de fechas YYYYMMDD que tienen un archivo log
    en el directorio, dentro del rango [fecha_desde, fecha_hasta].
    """
    patron = re.compile(r"^\[Operation\] (\d{4}-\d{2}-\d{2})\.log$")
    fechas = []
    try:
        for nombre in os.listdir(directorio):
            m = patron.match(nombre)
            if m:
                fecha = datetime.strptime(m.group(1), "%Y-%m-%d").strftime("%Y%m%d")
                if fecha_desde <= fecha <= fecha_hasta:
                    fechas.append(fecha)
    except OSError:
        pass
    return sorted(fechas)


def obtener_fecha_inicio_configurada(configuracion):
    """Retorna la Fecha_Inicio configurada como datetime, o None si no aplica."""
    fecha_inicio = configuracion.obtener_fecha_inicio().strip()
    if not fecha_inicio:
        return None

    try:
        return datetime.strptime(fecha_inicio, "%Y-%m-%d")
    except ValueError:
        print(
            f"Fecha_Inicio invalida en configuracion: {fecha_inicio}. Formato esperado: YYYY-MM-DD"
        )
        return None


def procesar_archivo(
    ruta_archivo,
    fecha_log,
    configuracion,
    directorio_salida,
    nombre_medio,
    codigo_operacional,
):
    """Parsea el log, exporta pasadas nuevas. Retorna cantidad de pasadas exportadas."""
    pasadas = recopilar_pasadas(ruta_archivo)

    nuevas = [p for p in pasadas if p["hora_fin"]]
    pendientes = [p for p in pasadas if not p["hora_fin"]]

    archivo = os.path.basename(ruta_archivo)
    print(f"[{archivo}]")
    print(f"  Total pasadas   : {len(pasadas)}")
    print(f"  Nuevas completas: {len(nuevas)}")
    print(f"  Pendientes      : {len(pendientes)}")

    if nuevas:
        por_modelo = {}
        for pasada in nuevas:
            por_modelo.setdefault(pasada["model"], []).append(pasada)

        for model, pasadas_modelo in por_modelo.items():
            contador = configuracion.obtener_contador_modelo(model)
            nombre_csv = f"{model}_{nombre_medio}_{codigo_operacional}_{fecha_log}_{contador}.csv"
            ruta_csv = os.path.join(directorio_salida, nombre_csv)
            exportar_append(pasadas_modelo, ruta_csv, fecha_log)
            total_placas = sum(len(p["placas"]) for p in pasadas_modelo)
            print(
                f"  +{len(pasadas_modelo):>3} pasadas / {total_placas:>4} placas -> {nombre_csv}"
            )

    return len(nuevas)


# ── Inicialización ────────────────────────────────────────────────────────────

configuracion = Configuraciones()
directorio_salida = configuracion.obtenerYcrear_directorio_salida()
directorio_entrada = configuracion.obtener_directorio_Entrada()
nombre_medio = configuracion.obtener_nombre_medio()
codigo_operacional = configuracion.obtener_codigo_operacional()

ruta_archivos_procesados = os.path.join(directorio_salida, "archivos_procesados.csv")

archivos_procesados_set = cargar_archivos_procesados(ruta_archivos_procesados)

# ── Procesamiento ─────────────────────────────────────────────────────────────

hoy = datetime.now()
fecha_hoy = hoy.strftime("%Y%m%d")

fecha_inicio_cfg = obtener_fecha_inicio_configurada(configuracion)
ultima_fecha = obtener_ultima_fecha_procesada(ruta_archivos_procesados)

if ultima_fecha is None:
    dt_base = encontrar_fecha_mas_antigua(directorio_entrada)
    if dt_base is None:
        dt_base = datetime.strptime(fecha_hoy, "%Y%m%d")
else:
    dt_base = datetime.strptime(ultima_fecha, "%Y%m%d")

if fecha_inicio_cfg is not None:
    dt_inicio = max(dt_base, fecha_inicio_cfg)
else:
    dt_inicio = dt_base

dt_hoy = datetime.strptime(fecha_hoy, "%Y%m%d")

if ultima_fecha:
    fecha_fmt_ultima = datetime.strptime(ultima_fecha, "%Y%m%d").strftime("%Y-%m-%d")
    print(f"Ultimo archivo procesado: [Operation] {fecha_fmt_ultima}.log")
else:
    print("Primera ejecucion: sin historial previo")

if fecha_inicio_cfg:
    print(f"Fecha_Inicio configurada: {fecha_inicio_cfg.strftime('%Y-%m-%d')}")

print(f"Procesando desde: {dt_inicio.strftime('%Y-%m-%d')}")

fecha_inicio_str = dt_inicio.strftime("%Y%m%d")

# Solo iterar sobre fechas que tienen log disponible en el directorio
fechas_a_procesar = obtener_fechas_con_log(
    directorio_entrada, fecha_inicio_str, fecha_hoy
)

# Siempre incluir hoy para capturar el log del día actual si aparece
if fecha_hoy not in fechas_a_procesar:
    fechas_a_procesar.append(fecha_hoy)

archivos_encontrados = 0
for fecha_log in fechas_a_procesar:
    fecha_fmt = f"{fecha_log[:4]}-{fecha_log[4:6]}-{fecha_log[6:8]}"
    archivo = f"[Operation] {fecha_fmt}.log"
    ruta_archivo = os.path.join(directorio_entrada, archivo)
    es_hoy = fecha_log == fecha_hoy

    # Días anteriores ya procesados completamente: saltar
    if not es_hoy and fecha_log in archivos_procesados_set:
        continue

    if not os.path.exists(ruta_archivo):
        # Solo puede ocurrir para hoy (no tiene log aún)
        print(f"Sin log: {archivo}")
        continue

    archivos_encontrados += 1
    procesar_archivo(
        ruta_archivo,
        fecha_log,
        configuracion,
        directorio_salida,
        nombre_medio,
        codigo_operacional,
    )

    # Días anteriores quedan cerrados: registrar como completamente procesados
    if not es_hoy and fecha_log not in archivos_procesados_set:
        registrar_archivo_procesado(
            ruta_archivos_procesados, fecha_log, archivo, hoy.strftime("%H:%M:%S")
        )
        archivos_procesados_set.add(fecha_log)

if archivos_encontrados == 0:
    print("Sin archivos para procesar")
