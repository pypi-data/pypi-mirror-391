import unittest
from datetime import date
from decimal import Decimal
from arrendatools.actualiza_renta.factory import ActualizacionRentaFactory


class TestActualizaRentaIPC(unittest.TestCase):
    def setUp(self):
        self.actualizacion_renta = ActualizacionRentaFactory.crear("IPC")

    def test_calcular_meses_posteriores_enero_2002(self):
        # Caso Actualización de rentas de alquiler con el IPC entre dos meses posteriores a enero de 2002
        # Se quiere actualizar una renta de 400€ con el IPC entre agosto de 2002 y agosto de 2003.
        resultado = self.actualizacion_renta.calcular(
            cantidad=Decimal("400.00"),
            anyo_inicial=2002,
            anyo_final=2003,
            mes=8,
        )
        esperado = {
            "cantidad": Decimal("400.00"),
            "cantidad_actualizada": Decimal("412.00"),
            "indice_inicial": Decimal("71.085"),
            "indice_final": Decimal("73.213"),
            "mes": "agosto",
            "anyo_inicial": 2002,
            "anyo_final": 2003,
            "tasa_variacion": Decimal("0.03"),
        }
        self.assertEqual(resultado, esperado)

    def test_calcular_entre_mes_anterior_2002_y_mes_posterior_enero_2002(
        self,
    ):
        # Caso: Actualización de rentas de alquiler con el IPC entre un mes anterior a enero de 2002 y otro posterior
        # Se quiere actualizar una renta con el IPC entre enero de 2001 y enero de 2002.
        resultado = self.actualizacion_renta.calcular(
            mes=1,
            anyo_inicial=2001,
            anyo_final=2002,
            cantidad=Decimal("400.00"),
        )
        esperado = {
            "cantidad": Decimal("400.00"),
            "cantidad_actualizada": Decimal("412.40"),
            "indice_inicial": Decimal("133.413"),
            "indice_final": Decimal("137.484"),
            "mes": "enero",
            "anyo_inicial": 2001,
            "anyo_final": 2002,
            "tasa_variacion": Decimal("0.031"),
        }
        self.assertEqual(resultado, esperado)

    def test_calcular_entre_meses_anteriores_enero_2002(self):
        # Caso: Actualización de rentas de alquiler con el IPC entre dos meses anteriores a enero de 2002
        # Se quiere actualizar una renta con el IPC entre agosto de 1999 y agosto de 2001
        resultado = self.actualizacion_renta.calcular(
            mes=8,
            anyo_inicial=1999,
            anyo_final=2001,
            cantidad=Decimal("400.00"),
        )
        esperado = {
            "cantidad": Decimal("400.00"),
            "cantidad_actualizada": Decimal("429.6"),
            "indice_inicial": Decimal("127.312"),
            "indice_final": Decimal("136.745"),
            "mes": "agosto",
            "anyo_inicial": 1999,
            "anyo_final": 2001,
            "tasa_variacion": Decimal("0.074"),
        }
        self.assertEqual(resultado, esperado)

    def test_calcular_anterior_1954(self):
        # Caso: Actualización de rentas de alquiler año inicial anterior a 1954
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                mes=8,
                anyo_inicial=1953,
                anyo_final=2001,
                cantidad=Decimal("400.00"),
            )
        self.assertEqual(
            str(context.exception),
            "Sólo hay datos de IPC a partir de Marzo de 1954.",
        )

    def test_calcular_anterior_marzo_1954(self):
        # Caso: Actualización de rentas de alquiler año inicial anterior a 1954
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                mes=2,
                anyo_inicial=1954,
                anyo_final=2001,
                cantidad=Decimal("400.00"),
            )
        self.assertEqual(
            str(context.exception),
            "Sólo hay datos de IPC a partir de Marzo de 1954.",
        )

    def test_calcular_futuro(self):
        hoy = date.today()  # Obtiene la fecha actual
        anyo_siguiente = hoy.year + 1  # Año que viene
        # Caso: Actualización de rentas de alquiler de un periodo en el que todavía no se ha publacado los datos del IPC
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                mes=2,
                anyo_inicial=2022,
                anyo_final=anyo_siguiente,
                cantidad=Decimal("400.00"),
            )
        self.assertEqual(
            str(context.exception),
            f"Renta no actualizada: No he podido recuperar los datos del IPC para febrero de {anyo_siguiente}.",
        )

    def test_calcular_no_mes(self):
        # Caso: Actualización de rentas de alquiler sin proporcionar el mes
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                anyo_inicial=2022,
                anyo_final=2023,
                cantidad=Decimal("400.00"),
            )
        self.assertEqual(str(context.exception), "Debes proporcionar el mes.")

    def test_calcular_no_anyo_inicial(self):
        # Caso: Actualización de rentas de alquiler sin proporcionar el año inicial
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                mes=2,
                anyo_final=2023,
                cantidad=Decimal("400.00"),
            )
        self.assertEqual(
            str(context.exception), "Debes proporcionar el año inicial."
        )

    def test_calcular_no_anyo_final(self):
        # Caso: Actualización de rentas de alquiler sin proporcionar el año final
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                mes=2,
                anyo_inicial=2022,
                cantidad=Decimal("400.00"),
            )
        self.assertEqual(
            str(context.exception), "Debes proporcionar el año final."
        )

    def test_calcular_anyo_inicial_no_valido(self):
        # Caso: Actualización de rentas de alquiler con año inicial no válido
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                mes=2,
                anyo_inicial=1953,
                anyo_final=2023,
                cantidad=Decimal("400.00"),
            )
        self.assertEqual(
            str(context.exception),
            "Sólo hay datos de IPC a partir de Marzo de 1954.",
        )


if __name__ == "__main__":
    unittest.main()
