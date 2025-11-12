import unittest
from datetime import date
from decimal import Decimal
from arrendatools.actualiza_renta.factory import ActualizacionRentaFactory


class TestMinimoIPCPorcentaje(unittest.TestCase):
    def setUp(self):
        self.actualizacion_renta = ActualizacionRentaFactory.crear(
            "MinimoIPCPorcentaje"
        )

    def test_calcular_same(self):
        resultado = self.actualizacion_renta.calcular(
            cantidad=Decimal("400.00"),
            dato=Decimal("0.03"),
            anyo_inicial=2002,
            anyo_final=2003,
            mes=8,
        )
        esperado = {
            "cantidad": Decimal("400.00"),
            "cantidad_actualizada": Decimal("412.00"),
            "indice_inicial": Decimal("71.085"),
            "indice_final": Decimal("73.213"),
            "dato": Decimal("0.03"),
            "mes": "agosto",
            "anyo_inicial": 2002,
            "anyo_final": 2003,
            "tasa_variacion": Decimal("0.03"),
        }
        self.assertEqual(resultado, esperado)

    def test_calcular_dato(self):
        resultado = self.actualizacion_renta.calcular(
            cantidad=Decimal("400.00"),
            dato=Decimal("0.022"),
            anyo_inicial=2002,
            anyo_final=2003,
            mes=8,
        )
        esperado = {
            "cantidad": Decimal("400.00"),
            "cantidad_actualizada": Decimal("408.80"),
            "indice_inicial": Decimal("71.085"),
            "indice_final": Decimal("73.213"),
            "mes": "agosto",
            "anyo_inicial": 2002,
            "anyo_final": 2003,
            "dato": Decimal("0.022"),
            "tasa_variacion": Decimal("0.022"),
        }
        self.assertEqual(resultado, esperado)

    def test_calcular_ipc(self):
        resultado = self.actualizacion_renta.calcular(
            cantidad=Decimal("400.00"),
            dato=Decimal("0.055"),
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
            "dato": Decimal("0.055"),
            "tasa_variacion": Decimal("0.030"),
        }
        self.assertEqual(resultado, esperado)

    def test_calcular_anterior_1954(self):
        # Caso: Actualización de rentas de alquiler año inicial anterior a 1954
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                mes=8,
                dato=Decimal("0.05"),
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
                dato=Decimal("0.05"),
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
                dato=Decimal("0.05"),
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
                dato=Decimal("0.05"),
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
                dato=Decimal("0.05"),
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
                dato=Decimal("0.05"),
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
                dato=Decimal("0.05"),
                anyo_inicial=1953,
                anyo_final=2023,
                cantidad=Decimal("400.00"),
            )
        self.assertEqual(
            str(context.exception),
            "Sólo hay datos de IPC a partir de Marzo de 1954.",
        )

    def test_calcular_dato_invalido(self):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                cantidad=Decimal("100.00"),
                dato=Decimal("1.10"),
                anyo_inicial=1954,
                anyo_final=2001,
                mes=8,
            )
        self.assertEqual(
            str(context.exception),
            "El dato debe ser un porcentaje entre -1 (-100%) y 1 (100%).",
        )

    def test_calcular_missing_dato(self):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                cantidad=Decimal("100.00"),
                anyo_inicial=1954,
                anyo_final=2001,
                mes=8,
            )
        self.assertEqual(
            str(context.exception),
            "Debes proporcionar el campo 'dato'.",
        )


if __name__ == "__main__":
    unittest.main()
