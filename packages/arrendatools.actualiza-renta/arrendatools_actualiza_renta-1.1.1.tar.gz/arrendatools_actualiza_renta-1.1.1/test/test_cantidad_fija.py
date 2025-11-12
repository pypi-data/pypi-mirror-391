import unittest
from decimal import Decimal
from arrendatools.actualiza_renta.factory import ActualizacionRentaFactory


class TestActualizacionRentaCantidadFija(unittest.TestCase):

    def setUp(self):
        self.actualizacion_renta = ActualizacionRentaFactory.crear(
            "CantidadFija"
        )

    def test_calcular_valid_inputs(self):
        resultado = self.actualizacion_renta.calcular(
            cantidad=Decimal("100.00"),
            dato=Decimal("50.00"),
        )
        esperado = {
            "cantidad": Decimal("100.00"),
            "dato": Decimal("50.00"),
            "cantidad_actualizada": Decimal("150.00"),
        }
        self.assertEqual(resultado, esperado)

    def test_calcular_missing_dato(self):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                cantidad=Decimal("100.00"),
                mes=1,
                anyo_inicial=2020,
                anyo_final=2021,
            )
        self.assertEqual(
            str(context.exception),
            "Debes proporcionar el campo 'dato'.",
        )

    def test_calcular_edge_case_mes(self):
        resultado = self.actualizacion_renta.calcular(
            cantidad=Decimal("100.00"),
            dato=Decimal("50.00"),
            mes=12,
            anyo_inicial=2020,
            anyo_final=2021,
        )
        esperado = {
            "cantidad": Decimal("100.00"),
            "dato": Decimal("50.00"),
            "cantidad_actualizada": Decimal("150.00"),
        }
        self.assertEqual(resultado, esperado)

    def test_calcular_edge_case_anyo_inicial_final(self):
        resultado = self.actualizacion_renta.calcular(
            cantidad=Decimal("100.00"),
            dato=Decimal("50.00"),
            mes=1,
            anyo_inicial=1900,
            anyo_final=2100,
        )
        esperado = {
            "cantidad": Decimal("100.00"),
            "dato": Decimal("50.00"),
            "cantidad_actualizada": Decimal("150.00"),
        }
        self.assertEqual(resultado, esperado)


if __name__ == "__main__":
    unittest.main()
