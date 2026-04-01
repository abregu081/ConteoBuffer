from Configuraciones import Configuraciones


class CalcularConteo:
    def __init__(self, consultas):
        self.consultas = consultas
        self.config = Configuraciones()
        self.medio_entrada_id = self.config.obtener_medio_entrada_id()
        self.cfg_dcsd = self.config.obtener_buffer_dcsd()
        self.cfg_main = self.config.obtener_buffer_main()

    def buffer_dcsd(self):
        return self.consultas.contar_buffer(
            self.medio_entrada_id,
            self.cfg_dcsd["box"],
            self.cfg_dcsd["salida_id"],
        )

    def buffer_main(self):
        return self.consultas.contar_buffer(
            self.medio_entrada_id,
            self.cfg_main["box"],
            self.cfg_main["salida_id"],
        )

    def resumen(self):
        dcsd = self.buffer_dcsd()
        main = self.buffer_main()

        entradas_dcsd = self.consultas.contar_entradas(self.medio_entrada_id, self.cfg_dcsd["box"])
        entradas_main = self.consultas.contar_entradas(self.medio_entrada_id, self.cfg_main["box"])
        salidas_dcsd = self.consultas.contar_salidas(self.cfg_dcsd["salida_id"])
        salidas_main = self.consultas.contar_salidas(self.cfg_main["salida_id"])

        return {
            "buffer_dcsd": dcsd,
            "buffer_main": main,
            "buffer_total": dcsd + main,
            "entradas_dcsd": entradas_dcsd,
            "entradas_main": entradas_main,
            "salidas_dcsd": salidas_dcsd,
            "salidas_main": salidas_main,
        }
