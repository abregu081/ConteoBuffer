import logging
from Configuraciones import Configuraciones
logger = logging.getLogger(__name__)


class CalcularConteo:
    def __init__(self, consultas, config=None):
        self.consultas = consultas
        self.config = config or Configuraciones()
        self.medio_entrada_id = self.config.obtener_medio_entrada_id()
        self.cfg_dcsd = self.config.obtener_buffer_dcsd()
        self.cfg_main = self.config.obtener_buffer_main()

    def buffer_dcsd(self):
        conteo = self.consultas.contar_buffer(
            self.medio_entrada_id,
            self.cfg_dcsd["salida_id"],
            self.cfg_main["salida_id"],
            "%DCSD%",
        )
        if conteo > self.cfg_dcsd["max"]:
            logger.warning(
                f"Buffer DCSD: conteo ({conteo}) excede capacidad fisica ({self.cfg_dcsd['max']})"
            )
        return conteo

    def buffer_main(self):
        conteo = self.consultas.contar_buffer(
            self.medio_entrada_id,
            self.cfg_dcsd["salida_id"],
            self.cfg_main["salida_id"],
            "%MAIN%",
        )
        if conteo > self.cfg_main["max"]:
            logger.warning(
                f"Buffer MAIN: conteo ({conteo}) excede capacidad fisica ({self.cfg_main['max']})"
            )
        return conteo

    def resumen(self):
        dcsd = self.buffer_dcsd()
        main = self.buffer_main()

        entradas = self.consultas.contar_entradas(self.medio_entrada_id)
        entradas_dcsd = self.consultas.contar_entradas_modelo(self.medio_entrada_id, "%DCSD%")
        entradas_main = self.consultas.contar_entradas_modelo(self.medio_entrada_id, "%MAIN%")
        salidas_dcsd = self.consultas.contar_salidas(self.cfg_dcsd["salida_id"])
        salidas_main = self.consultas.contar_salidas(self.cfg_main["salida_id"])

        return {
            "buffer_dcsd": dcsd,
            "buffer_main": main,
            "buffer_total": dcsd + main,
            "entradas": entradas,
            "entradas_dcsd": entradas_dcsd,
            "entradas_main": entradas_main,
            "salidas_dcsd": salidas_dcsd,
            "salidas_main": salidas_main,
        }
