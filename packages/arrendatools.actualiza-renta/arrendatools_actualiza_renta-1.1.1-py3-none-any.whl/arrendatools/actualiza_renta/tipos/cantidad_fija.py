from typing import Optional
from decimal import Decimal, ROUND_HALF_UP
from arrendatools.actualiza_renta.actualizacion_renta import ActualizacionRenta


class CantidadFija(ActualizacionRenta):
    """Implementación de actualización por cantidad fija."""

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
        cantidad_actualizada = cantidad + Decimal(dato)  # type: ignore
        result = {
            "cantidad": cantidad,
            "dato": dato,
            "cantidad_actualizada": cantidad_actualizada,
        }
        return result

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
        return None
