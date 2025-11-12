from typing import Optional, Any
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict


class ActualizacionRenta(ABC):
    """Clase base abstracta para las actualizaciones de renta."""

    @abstractmethod
    def calcular(
        self,
        cantidad: Decimal,
        dato: Optional[Decimal] = None,
        mes: Optional[int] = None,
        anyo_inicial: Optional[int] = None,
        anyo_final: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Calcula la actualización de la renta."""
        raise NotImplementedError

    def validar_datos(
        self,
        cantidad: Decimal,
        dato: Optional[Decimal] = None,
        mes: Optional[int] = None,
        anyo_inicial: Optional[int] = None,
        anyo_final: Optional[int] = None,
    ) -> None:
        """Valida los datos de entrada."""
        if not isinstance(cantidad, Decimal):
            raise ValueError("La cantidad debe ser Decimal.")
        if dato is not None and not isinstance(dato, Decimal):
            raise ValueError("El dato debe ser Decimal.")
        if mes is not None and (
            not isinstance(mes, int) or mes < 1 or mes > 12
        ):
            raise ValueError("Debes proporcionar un mes válido (1-12).")
        if anyo_inicial is not None and not isinstance(anyo_inicial, int):
            raise ValueError("El año inicial debe ser int.")
        if anyo_final is not None and not isinstance(anyo_final, int):
            raise ValueError("El año final debe ser int.")
        if anyo_inicial is not None and anyo_final is not None:
            if anyo_final < anyo_inicial:
                raise ValueError(
                    "El año final no puede ser anterior al año inicial."
                )
        return None
