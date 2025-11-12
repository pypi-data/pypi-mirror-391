import importlib
import pkgutil
import inspect
from arrendatools.actualiza_renta.actualizacion_renta import (
    ActualizacionRenta,
)


class ActualizacionRentaFactory:
    """Factory para crear instancias de ActualizacionRenta dinámicamente."""

    _cache = {}

    @classmethod
    def _cargar_clases(cls):
        """Carga todas las clases que extienden de ActualizacionRenta en el módulo."""
        if cls._cache:
            return

        module_prefix = "arrendatools.actualiza_renta.tipos"
        package = importlib.import_module(module_prefix)

        for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            if not is_pkg:
                full_module_name = f"{module_prefix}.{module_name}"
                module = importlib.import_module(full_module_name)

                # Buscar todas las clases en el módulo que extiendan de ActualizacionRenta
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(obj, ActualizacionRenta)
                        and obj is not ActualizacionRenta
                    ):
                        cls._cache[obj.__name__.lower()] = obj

    @classmethod
    def crear(cls, tipo: str) -> ActualizacionRenta:
        """
        Crea una instancia de una clase que extiende ActualizacionRenta.

        :param tipo: Nombre de la clase de tipo ActualizacionRenta.
        :return: Instancia de la clase especificada.
        :raises ValueError: Si no existe una clase con el nombre especificado.
        """
        cls._cargar_clases()

        clase = cls._cache.get(tipo.lower())
        if not clase:
            raise ValueError(f"No existe una clase de tipo {tipo}")
        return clase()
