from typing import Optional
from decimal import Decimal, ROUND_HALF_UP
from arrendatools.actualiza_renta.actualizacion_renta import ActualizacionRenta


class Porcentaje(ActualizacionRenta):
    """Implementación de actualización por porcentaje."""

    def calcular(
        self,
        cantidad: Decimal,
        dato: Optional[Decimal] = None,
        mes: Optional[int] = None,
        anyo_inicial: Optional[int] = None,
        anyo_final: Optional[int] = None,
    ) -> dict:
        self.validar_datos(cantidad, dato, mes, anyo_inicial, anyo_final)
        # Convertir explícitamente a Decimal y redondear a dos decimales
        cantidad = Decimal(cantidad).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        cantidad_actualizada = cantidad + (cantidad * Decimal(dato)).quantize(  # type: ignore
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return {
            "cantidad": cantidad,
            "dato": dato,
            "cantidad_actualizada": cantidad_actualizada,
            "tasa_variacion": dato,
        }

    def validar_datos(
        self,
        cantidad: Decimal,
        dato: Optional[Decimal] = None,
        mes: Optional[int] = None,
        anyo_inicial: Optional[int] = None,
        anyo_final: Optional[int] = None,
    ) -> None:
        """Valida los datos de entrada."""
        super().validar_datos(cantidad, dato, mes, anyo_inicial, anyo_final)
        if dato is None:
            raise ValueError("Debes proporcionar el campo 'dato'.")
        if not (Decimal("-1.0") <= dato <= Decimal("1.0")):
            raise ValueError(
                "El dato debe ser un porcentaje entre -1 (-100%) y 1 (100%)."
            )
        return None
