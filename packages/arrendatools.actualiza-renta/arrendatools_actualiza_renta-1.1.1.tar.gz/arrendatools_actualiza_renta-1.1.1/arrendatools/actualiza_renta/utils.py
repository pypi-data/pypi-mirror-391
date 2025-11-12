class FechaUtils:
    """Utilidades para manejo de fechas."""

    @staticmethod
    def mes_en_espanol(mes: int) -> str:
        """
        Convierte un número de mes en su nombre en español.

        Args:
            mes (int): Número del mes (1-12).

        Returns:
            str: Nombre del mes en español.

        Raises:
            ValueError: Si el número de mes no está entre 1 y 12.
        """
        meses_espanol = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ]
        if 1 <= mes <= 12:
            return meses_espanol[mes - 1]
        raise ValueError(
            f"El número de mes {mes} no es válido. Debe estar entre 1 y 12."
        )
