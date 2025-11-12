from typing import Optional
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from arrendatools.actualiza_renta.utils import FechaUtils
from arrendatools.actualiza_renta.actualizacion_renta import ActualizacionRenta
from arrendatools.actualiza_renta.ine import INE


class IRAV(ActualizacionRenta):
    """Actualización basada en el Índice de Rentas de Alquiler de Viviendas (IRAV)."""

    _SERIE_IRAV = "IRAV1"

    def _obtener_IRAV(self, anyo: int, mes: int) -> Decimal:
        """
        Obtiene el IRAV del INE para el año y mes indicado.

        :param anyo: Año para recuperar el IRAV.
        :type anyo: int
        :param mes: Mes para recuperar el IRAV. Los meses se empiezan a contar desde 1. 1 = Enero, 2 = Febrero, ... 12 = Diciembre.
        :type mes: int
        :return: Se conecta a la web del INE y consulta el IRAV para el mes y año indicados.
        :rtype: float
        """
        fecha = date(anyo, mes, 1)
        json = INE.obtener_datos_serie(fecha, fecha, self._SERIE_IRAV)
        valor = None
        if len(json["Data"]) > 0:
            valor = Decimal(json["Data"][0]["Valor"])
            return (valor / Decimal("100")).quantize(
                Decimal("0.001"), rounding=ROUND_HALF_UP
            )
        else:
            raise ValueError(
                f"Renta no actualizada: No he podido recuperar los datos del IRAV para {FechaUtils.mes_en_espanol(mes)} de {anyo}."
            )

    def calcular(
        self,
        cantidad: Decimal,
        dato: Optional[Decimal] = None,
        mes: Optional[int] = None,
        anyo_inicial: Optional[int] = None,
        anyo_final: Optional[int] = None,
    ) -> dict:
        self.validar_datos(cantidad, dato, mes, anyo_inicial, anyo_final)
        try:
            # Convertir explícitamente a Decimal y redondear a dos decimales
            cantidad = Decimal(cantidad).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            tasa_variacion = self._obtener_IRAV(anyo_inicial, mes)  # type: ignore
            if tasa_variacion is None or tasa_variacion.is_nan():
                raise ValueError(
                    f"Renta no actualizada: No he podido recuperar los datos del IRAV para {FechaUtils.mes_en_espanol(mes)} de {anyo_inicial}."  # type: ignore
                )
            cantidad_actualizada = (
                cantidad * (Decimal("1") + tasa_variacion)
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except ConnectionError as err:
            print(err)
            raise
        return {
            "cantidad": cantidad,
            "anyo_inicial": anyo_inicial,
            "mes": FechaUtils.mes_en_espanol(mes),  # type: ignore
            "cantidad_actualizada": cantidad_actualizada,
            "tasa_variacion": tasa_variacion,
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
        if anyo_inicial is None:
            raise ValueError("Debes proporcionar un año inicial.")
        if mes is None:
            raise ValueError("Debes proporcionar un mes.")
        if (anyo_inicial < 2024) or (
            anyo_inicial == 2024 and mes is not None and mes < 11
        ):
            raise ValueError(
                "Sólo hay datos del IRAV a partir de noviembre de 2024."
            )
        return None
