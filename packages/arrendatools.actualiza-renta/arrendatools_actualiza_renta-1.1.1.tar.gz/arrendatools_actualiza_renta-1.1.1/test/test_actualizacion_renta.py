import unittest
from decimal import Decimal
from arrendatools.actualiza_renta.actualizacion_renta import ActualizacionRenta


class TestActualizacionRenta(unittest.TestCase):
    class ActualizacionRentaImpl(ActualizacionRenta):
        def calcular(
            self,
            cantidad,
            dato=None,
            mes=None,
            anyo_inicial=None,
            anyo_final=None,
        ):
            return {}

    def setUp(self):
        self.actualizacion_renta = self.ActualizacionRentaImpl()

    def test_validar_datos_valid(self):
        try:
            self.actualizacion_renta.validar_datos(
                cantidad=Decimal("100.0"),
                dato=Decimal("10.0"),
                mes=5,
                anyo_inicial=2020,
                anyo_final=2021,
            )
        except ValueError:
            self.fail("validar_datos() raised ValueError unexpectedly!")

    def test_validar_datos_invalid_cantidad(self):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.validar_datos(cantidad="100.0")
        self.assertEqual(
            str(context.exception),
            "La cantidad debe ser Decimal.",
        )

    def test_validar_datos_invalid_dato(self):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.validar_datos(
                cantidad=Decimal("100.0"), dato="10.0"
            )
        self.assertEqual(
            str(context.exception),
            "El dato debe ser Decimal.",
        )

    def test_validar_datos_invalid_mes_upper(self):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.validar_datos(
                cantidad=Decimal("100.0"), mes=13
            )
        self.assertEqual(
            str(context.exception),
            "Debes proporcionar un mes válido (1-12).",
        )

    def test_validar_datos_invalid_mes_lower(self):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.validar_datos(
                cantidad=Decimal("100.0"), mes=0
            )
        self.assertEqual(
            str(context.exception),
            "Debes proporcionar un mes válido (1-12).",
        )

    def test_validar_datos_invalid_anyo_inicial(self):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.validar_datos(
                cantidad=Decimal("100.0"), anyo_inicial="2020"
            )
        self.assertEqual(
            str(context.exception),
            "El año inicial debe ser int.",
        )

    def test_validar_datos_invalid_anyo_final(self):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.validar_datos(
                cantidad=Decimal("100.0"), anyo_final="2021"
            )
        self.assertEqual(
            str(context.exception),
            "El año final debe ser int.",
        )

    def test_validar_datos_anyo_final_menor_anyo_inicial(self):
        with self.assertRaises(ValueError) as context:
            self.actualizacion_renta.validar_datos(
                cantidad=Decimal("100.0"), anyo_inicial=2021, anyo_final=2020
            )
        self.assertEqual(
            str(context.exception),
            "El año final no puede ser anterior al año inicial.",
        )


if __name__ == "__main__":
    unittest.main()
