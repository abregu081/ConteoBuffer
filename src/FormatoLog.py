Plantilla_Inicio = [
    "",
    "#INIT",
    "MODEL : {MODEL}",
    "Tipo_Placa : {TIPO_PLACA}",
    "P/N : {SERIAL_NUMBER}",
    "DATE : {FECHA}",
    "TIME : {HORA}",
    "LOGVERSION : {VERSION}",
    "PC_CPU : {obtener_pc_cpu}",
    "PC_RAM(Available) : {obtener_pc_ram_available}",
    "PC_RAM_INIT(free) : {obtener_pc_ram_init_free}",
    "PC_DISK(C-Drive free/Total) : {obtener_pc_disk_free_total}",
    "PC_OS : {obtener_pc_os}",
    "JIG : {JIG}",
]

Plantilla_Test = [
    "",
    "#TEST",
    "/*================================================================================",
    "Test Conditions, Measured Value, Lower Limit, Upper Limit, P/F, Sec",
    "================================================================================*/",
]

Plantilla_Final = [
    "",
    "#END",
    "RESULT : {result}",
    "ERROR-CODE : ",
    "FAILITEM : {fail_item}",
    "PROCESS SKIP : ",
    "TEST-TIME : {test_time}",
    "//PC_RAM_END(free) : {obtener_pc_ram_end_free}",
    "",
    "{caracter_retorno}",
]
