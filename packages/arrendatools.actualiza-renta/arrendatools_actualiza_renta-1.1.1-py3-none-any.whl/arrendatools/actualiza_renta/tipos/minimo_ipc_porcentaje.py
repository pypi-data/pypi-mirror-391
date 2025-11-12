from typing import Optional
from decimal import Decimal, ROUND_HALF_UP
from arrendatools.actualiza_renta.utils import FechaUtils
from arrendatools.actualiza_renta.actualizacion_renta import ActualizacionRenta
from arrendatools.actualiza_renta.tipos.ipc import IPC


class MinimoIPCPorcentaje(ActualizacionRenta):
    """Actualización basada en el mínimo entre IPC y porcentaje."""

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
        datos_ipc = IPC().calcular(
            cantidad=cantidad,
            mes=mes,
            anyo_inicial=anyo_inicial,
            anyo_final=anyo_final,
        )
        ipc_variacion = datos_ipc["tasa_variacion"]

        tasa_variacion = min(ipc_variacion, dato)  # type: ignore
        cantidad_actualizada = (
            cantidad + (cantidad * Decimal(tasa_variacion))
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "cantidad": cantidad,
            "mes": FechaUtils.mes_en_espanol(mes),  # type: ignore
            "dato": dato,
            "anyo_inicial": anyo_inicial,
            "anyo_final": anyo_final,
            "indice_inicial": datos_ipc["indice_inicial"],
            "indice_final": datos_ipc["indice_final"],
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
        # Validaciones para el IPC
        if anyo_inicial is None:
            raise ValueError("Debes proporcionar el año inicial.")
        if mes is None:
            raise ValueError("Debes proporcionar el mes.")
        if anyo_final is None:
            raise ValueError("Debes proporcionar el año final.")
        if (anyo_inicial < 1954) or (
            anyo_inicial == 1954 and mes is not None and mes < 3
        ):
            raise ValueError(
                "Sólo hay datos de IPC a partir de Marzo de 1954."
            )

        # Validaciones para el porcentaje
        if dato is None:
            raise ValueError("Debes proporcionar el campo 'dato'.")
        if not (Decimal("-1.0") <= dato <= Decimal("1.0")):
            raise ValueError(
                "El dato debe ser un porcentaje entre -1 (-100%) y 1 (100%)."
            )

        return None
