import unittest
from decimal import Decimal
from arrendatools.actualiza_renta.factory import ActualizacionRentaFactory


class TestPorcentaje(unittest.TestCase):

    def setUp(self):
        self.actualizacion_renta = ActualizacionRentaFactory.crear(
            "Porcentaje"
        )

    def test_calcular_incremento(self):
        resultado = self.actualizacion_renta.calcular(
            Decimal("100.00"), Decimal("0.10")
        )
        esperado = {
            "cantidad": Decimal("100.00"),
            "cantidad_actualizada": Decimal("110.00"),
            "dato": Decimal("0.10"),
            "tasa_variacion": Decimal("0.10"),
        }
        self.assertEqual(resultado, esperado)

    def test_calcular_decremento(self):
        resultado = self.actualizacion_renta.calcular(
            Decimal("100.00"), Decimal("-0.10")
        )
        esperado = {
            "cantidad": Decimal("100.00"),
            "cantidad_actualizada": Decimal("90.00"),
            "dato": Decimal("-0.10"),
            "tasa_variacion": Decimal("-0.10"),
        }
        self.assertEqual(resultado, esperado)

    def test_calcular_sin_cambio(self):
        resultado = self.actualizacion_renta.calcular(
            Decimal("100.00"), Decimal("0.00")
        )
        esperado = {
            "cantidad": Decimal("100.00"),
            "cantidad_actualizada": Decimal("100.00"),
            "dato": Decimal("0.00"),
            "tasa_variacion": Decimal("0.00"),
        }
        self.assertEqual(resultado, esperado)

    def test_calcular_dato_invalido(self):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                Decimal("100.00"), Decimal("1.10")
            )
        self.assertEqual(
            str(context.exception),
            "El dato debe ser un porcentaje entre -1 (-100%) y 1 (100%).",
        )

    def test_calcular_missing_dato(self):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                cantidad=Decimal("100.00"),
            )
        self.assertEqual(
            str(context.exception),
            "Debes proporcionar el campo 'dato'.",
        )


if __name__ == "__main__":
    unittest.main()
