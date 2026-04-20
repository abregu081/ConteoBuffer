def _parsear_campos(dato_raw):
    """
    Parsea los campos separados por '|' en formato clave=valor.
    Maneja la clave duplicada 'testres' acumulandola en una lista.
    """
    campos = {}
    testres_list = []
    for campo in dato_raw.split('|'):
        if '=' in campo:
            clave, valor = campo.split('=', 1)
            clave = clave.strip()
            valor = valor.strip().rstrip('\r')
            if clave == 'testres':
                testres_list.append(valor)
            else:
                campos[clave] = valor
    campos['testres'] = testres_list
    return campos


def _nuevo_registro(id_placa, campos, hora):
    return {
        'id':                id_placa,
        'model':             campos.get('model', ''),
        'process':           campos.get('process', ''),
        'station':           campos.get('station', ''),
        'hora_inicio':       hora,
        'hora_bcnf':         '',
        'hora_bcmp':         '',
        'hora_back':         '',
        'status_bcnf':       '',
        'msg_bcnf':          '',
        'status':            '',
        'testres_timestamp': '',
        'testres_codigo':    '',
        'reintentos':        0,
    }


def recopilar_pasadas(ruta_archivo):
    """
    Lee un archivo [Operation] log y agrupa los registros por pasada.

    Una pasada está delimitada por:
        [S] Send Routing Command for Table_X  →  inicio
        [R] Start End                          →  fin

    Dentro de cada pasada, las placas se procesan en lote:
        MAIN / DCSD : siempre 2 placas por pasada
        SUB         : cantidad variable

    Los mensajes BREQ/BCNF/BCMP/BACK se intercalan pero siempre
    pertenecen a la pasada activa (BACK llega antes de Start End).
    Las placas con BCNF FAIL (sin BCMP/BACK) se incorporan a la
    pasada cuando esta cierra con Start End.

    Args:
        ruta_archivo (str): ruta al archivo [Operation] .log

    Returns:
        list[dict]: pasadas, cada una con:
            tabla        - Table_X1 o Table_X2
            hora_inicio  - hora del Send Routing Command
            hora_fin     - hora del Start End (vacia si pasada incompleta)
            model        - modelo de las placas de la pasada
            placas       - lista de registros individuales (ver _nuevo_registro)
    """
    pasadas    = []
    pasada_act = None    # pasada actualmente abierta
    en_proceso = {}      # { id_placa: registro_parcial }

    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue

            partes = linea.split('\t')
            if len(partes) < 3:
                continue

            hora    = partes[0]
            mensaje = partes[2]

            # ── Inicio de pasada ──────────────────────────────────────────────
            if '[S] Send Routing Command for Table_' in mensaje:
                tabla = mensaje.split('Table_')[-1].strip().rstrip('\r')
                pasada_act = {
                    'tabla':       tabla,
                    'hora_inicio': hora,
                    'hora_fin':    '',
                    'model':       '',
                    'placas':      [],
                    '_ids':        set(),   # ids de BREQs en esta pasada (interno)
                }

            # ── Fin de pasada ─────────────────────────────────────────────────
            elif '[R] Start End' in mensaje and pasada_act is not None:
                pasada_act['hora_fin'] = hora
                # Incorporar placas incompletas (ej. BCNF FAIL) de esta pasada
                for id_ in pasada_act['_ids']:
                    if id_ in en_proceso:
                        pasada_act['placas'].append(en_proceso.pop(id_))
                pasada_act.pop('_ids')
                pasadas.append(pasada_act)
                pasada_act = None

            # ── Mensajes TX / RX ──────────────────────────────────────────────
            elif (mensaje.startswith('[TX]') or mensaje.startswith('[RX]')) and ' : ' in mensaje:
                _, dato_raw = mensaje.split(' : ', 1)
                dato_raw  = dato_raw.strip().rstrip('\r')
                tipo      = dato_raw.split('|')[0]
                campos    = _parsear_campos(dato_raw)
                id_placa  = campos.get('id')

                if not id_placa:
                    continue

                if tipo == 'BREQ':
                    if id_placa in en_proceso:
                        # Reintento: conservar hora_inicio original
                        en_proceso[id_placa]['reintentos'] += 1
                        en_proceso[id_placa]['hora_bcnf']   = ''
                        en_proceso[id_placa]['status_bcnf'] = ''
                        en_proceso[id_placa]['msg_bcnf']    = ''
                    else:
                        en_proceso[id_placa] = _nuevo_registro(id_placa, campos, hora)
                    if pasada_act is not None:
                        pasada_act['_ids'].add(id_placa)
                        if not pasada_act['model']:
                            pasada_act['model'] = campos.get('model', '')

                elif tipo == 'BCNF' and id_placa in en_proceso:
                    en_proceso[id_placa]['hora_bcnf']   = hora
                    en_proceso[id_placa]['status_bcnf'] = campos.get('status', '')
                    en_proceso[id_placa]['msg_bcnf']    = campos.get('msg', '')

                elif tipo == 'BCMP' and id_placa in en_proceso:
                    testres = campos.get('testres', [])
                    en_proceso[id_placa].update({
                        'hora_bcmp':         hora,
                        'status':            campos.get('status', ''),
                        'testres_timestamp': testres[0] if testres else '',
                        'testres_codigo':    testres[1] if len(testres) > 1 else '',
                    })

                elif tipo == 'BACK' and id_placa in en_proceso:
                    en_proceso[id_placa]['hora_back'] = hora
                    registro = en_proceso.pop(id_placa)
                    if pasada_act is not None:
                        pasada_act['placas'].append(registro)

    # Pasada sin Start End al final del log (aún en curso)
    if pasada_act is not None and pasada_act['placas']:
        for id_ in pasada_act['_ids']:
            if id_ in en_proceso:
                pasada_act['placas'].append(en_proceso.pop(id_))
        pasada_act.pop('_ids')
        pasadas.append(pasada_act)

    return pasadas
