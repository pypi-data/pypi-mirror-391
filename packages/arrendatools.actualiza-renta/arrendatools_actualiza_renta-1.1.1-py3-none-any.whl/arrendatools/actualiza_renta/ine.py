import logging
import json
import requests
from datetime import date


class INE:
    """Clase para conexión con la API del INE."""

    _BASE_URL = "https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE"

    @staticmethod
    def obtener_datos_serie(
        fecha_inicio: date, fecha_fin: date, serie: str
    ) -> dict:
        """
        Obtiene datos de una serie del INE.

        Args:
            fecha_inicio (date): Fecha de inicio para la serie.
            fecha_fin (date): Fecha de fin para la serie.
            serie (str): Código de la serie temporal.

        Returns:
            dict: Datos de la serie temporal proporcionados por la API.

        Raises:
            ValueError: Si las fechas no son válidas.
            ConnectionError: Si hay un problema con la conexión a la API.
            json.JSONDecodeError: Si la respuesta de la API no es JSON válido.
        """
        if fecha_inicio > fecha_fin:
            raise ValueError(
                "La fecha de inicio no puede ser posterior a la fecha de fin."
            )

        fecha_inicio_str = fecha_inicio.strftime("%Y%m%d")
        fecha_fin_str = fecha_fin.strftime("%Y%m%d")
        url = (
            f"{INE._BASE_URL}/{serie}?date={fecha_inicio_str}:{fecha_fin_str}"
        )

        try:
            logging.info("Realizando petición a la API del INE: %s", url)
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            logging.error(
                "La solicitud a la API del INE ha excedido el tiempo límite."
            )
            raise ConnectionError(
                "El tiempo límite de la solicitud ha sido excedido."
            )
        except requests.exceptions.HTTPError as err:
            logging.error("Error HTTP al conectar con la API del INE: %s", err)
            raise ConnectionError(
                f"Error HTTP al conectar con la API del INE: {err}"
            )
        except requests.exceptions.RequestException as err:
            logging.error(
                "Error de conexión al realizar la solicitud a la API del INE: %s",
                err,
            )
            raise ConnectionError(
                f"Error de conexión al realizar la solicitud: {err}"
            )

        try:
            datos = response.json()
            logging.info("Datos obtenidos correctamente de la API del INE.")
            return datos
        except json.JSONDecodeError as err:
            logging.error(
                "Error al decodificar la respuesta JSON de la API del INE: %s",
                err,
            )
            raise json.JSONDecodeError(
                f"Error al decodificar la respuesta JSON: {err}",
                response.text,
                0,
            )
