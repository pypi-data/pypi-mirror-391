import unittest
from unittest.mock import patch
from decimal import Decimal
from arrendatools.actualiza_renta.factory import ActualizacionRentaFactory
from arrendatools.actualiza_renta.tipos.irav import IRAV


class TestIRAV(unittest.TestCase):
    def setUp(self):
        self.actualizacion_renta = ActualizacionRentaFactory.crear("IRAV")

    def test_calcular_raises_value_error_for_none_anyo_inicial(self):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                cantidad=Decimal("1000.00"), mes=11
            )
        self.assertEqual(
            str(context.exception),
            "Debes proporcionar un año inicial.",
        )

    def test_calcular_raises_value_error_for_none_mes(self):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                cantidad=Decimal("1000.00"), anyo_inicial=2025
            )
        self.assertEqual(str(context.exception), "Debes proporcionar un mes.")

    def test_calcular_raises_value_error_for_invalid_anyo_inicial(self):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                cantidad=Decimal("1000.00"), mes=10, anyo_inicial=2023
            )
        self.assertEqual(
            str(context.exception),
            "Sólo hay datos del IRAV a partir de noviembre de 2024.",
        )

    def test_calcular_irav(self):
        resultado = self.actualizacion_renta.calcular(
            cantidad=Decimal("1000.00"),
            mes=11,
            anyo_inicial=2024,
        )

        esperado = {
            "cantidad": Decimal("1000.00"),
            "cantidad_actualizada": Decimal("1022.00"),
            "anyo_inicial": 2024,
            "mes": "noviembre",
            "tasa_variacion": Decimal("0.022"),
        }
        self.assertEqual(resultado, esperado)

    @patch.object(IRAV, "_obtener_IRAV", return_value=Decimal("0.05"))
    def test_calcular_success(self, mock_obtener_IRAV):
        resultado = self.actualizacion_renta.calcular(
            cantidad=Decimal("1000.00"),
            mes=11,
            anyo_inicial=2025,
            anyo_final=2026,
        )
        esperado = {
            "cantidad": Decimal("1000.00"),
            "cantidad_actualizada": Decimal("1050.00"),
            "anyo_inicial": 2025,
            "mes": "noviembre",
            "tasa_variacion": Decimal("0.05"),
        }
        self.assertEqual(resultado, esperado)

    @patch.object(IRAV, "_obtener_IRAV", return_value=None)
    def test_calcular_raises_value_error_for_invalid_datos(
        self, mock_obtener_IRAV
    ):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.calcular(
                cantidad=Decimal("1000.00"),
                mes=11,
                anyo_inicial=2025,
                anyo_final=2026,
            )
        self.assertEqual(
            str(context.exception),
            "Renta no actualizada: No he podido recuperar los datos del IRAV para noviembre de 2025.",
        )


if __name__ == "__main__":
    unittest.main()
