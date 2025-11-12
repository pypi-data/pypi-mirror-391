from typing import Optional
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from arrendatools.actualiza_renta.utils import FechaUtils
from arrendatools.actualiza_renta.actualizacion_renta import ActualizacionRenta
from arrendatools.actualiza_renta.ine import INE


class IPC(ActualizacionRenta):
    """Actualización de renta basada en IPC."""

    # Serie IPC206446 -> IPC Base 2016. Tiene que usar el coeficiente LAU base 2016. Este inidice se usó hasta 2021.
    # Serie IPC251852 -> IPC Base 2021. Tiene que usar el coeficiente LAU base 2021
    _SERIE_IPC = "IPC251852"

    # Cada número representa el coeficiente del mes del indice 0 = enero, 1=febrero,... 11=diciembre
    # https://www.ine.es/ss/Satellite?c=Page&cid=1254735905720&pagename=ProductosYServicios%2FPYSLayout&L=0&p=1254735893337
    # Estos coeficientes se usaron hasta 2021
    # _COEFICIENTES_LAU_BASE_2016 = [1.843315, 1.849032, 1.84201, 1.835371, 1.835434, 1.83756, 1.855259, 1.858562, 1.849043, 1.837433, 1.832176, 1.834031]

    _COEFICIENTES_LAU_BASE_2021 = [
        1.977332,
        1.983464,
        1.975933,
        1.96881,
        1.968878,
        1.971159,
        1.990145,
        1.993687,
        1.983476,
        1.971022,
        1.965383,
        1.967373,
    ]

    # Nota: Los datos anteriores a 1961 corresponden al Índice Nacional Urbano.
    # Estos datos tienen carácter oficial a los efectos regulados por la Ley 29/94, de 24 de noviembre, de Arrendamientos Urbanos.
    # PDF: https://www.ine.es/ss/Satellite?blobcol=urldata&blobheader=application%2Fpdf&blobheadername1=Content-Disposition&blobheadervalue1=attachment%3B+filename%3DindicesLAU_enlazado.pdf&blobkey=urldata&blobtable=MungoBlobs&blobwhere=730%2F953%2FindicesLAU_enlazado.pdf&ssbinary=true
    # Excel: http://www.ine.es/ss/Satellite?blobcol=urldata&blobheader=application%2Fvnd.ms-excel&blobheadername1=Content-Disposition&blobheadervalue1=attachment%3B+filename%3DindicesLAU_enlazado.xls&blobkey=urldata&blobtable=MungoBlobs&blobwhere=487%2F961%2FindicesLAU_enlazado.xls&ssbinary=true
    _TABLA_IPC_BASE_1992 = {
        1954: [
            0,
            0,
            3.282,
            3.289,
            3.289,
            3.277,
            3.28,
            3.267,
            3.269,
            3.286,
            3.314,
            3.344,
        ],
        1955: [
            3.365,
            3.376,
            3.389,
            3.408,
            3.41,
            3.401,
            3.401,
            3.408,
            3.431,
            3.459,
            3.474,
            3.485,
        ],
        1956: [
            3.489,
            3.532,
            3.566,
            3.604,
            3.621,
            3.609,
            3.598,
            3.604,
            3.63,
            3.662,
            3.713,
            3.779,
        ],
        1957: [
            3.848,
            3.869,
            3.889,
            3.906,
            3.916,
            3.906,
            3.967,
            4.023,
            4.08,
            4.166,
            4.234,
            4.279,
        ],
        1958: [
            4.309,
            4.313,
            4.397,
            4.491,
            4.52,
            4.514,
            4.544,
            4.574,
            4.646,
            4.689,
            4.732,
            4.787,
        ],
        1959: [
            4.794,
            4.817,
            4.843,
            4.873,
            4.888,
            4.86,
            4.86,
            4.868,
            4.894,
            4.909,
            4.926,
            4.969,
        ],
        1960: [
            4.93,
            4.926,
            4.92,
            4.924,
            4.909,
            4.905,
            4.903,
            4.913,
            4.943,
            4.956,
            4.962,
            4.999,
        ],
        1961: [
            5.02,
            4.979,
            4.957,
            4.97,
            4.957,
            4.93,
            4.93,
            4.938,
            4.942,
            4.961,
            5.038,
            5.047,
        ],
        1962: [
            5.038,
            5.061,
            5.105,
            5.177,
            5.243,
            5.27,
            5.27,
            5.257,
            5.289,
            5.34,
            5.477,
            5.547,
        ],
        1963: [
            5.56,
            5.604,
            5.713,
            5.709,
            5.741,
            5.635,
            5.695,
            5.754,
            5.741,
            5.757,
            5.829,
            5.851,
        ],
        1964: [
            5.842,
            5.846,
            5.864,
            5.886,
            5.901,
            5.98,
            6.109,
            6.205,
            6.266,
            6.369,
            6.516,
            6.592,
        ],
        1965: [
            6.657,
            6.771,
            6.824,
            6.874,
            6.902,
            6.871,
            6.88,
            6.915,
            6.981,
            7.018,
            7.169,
            7.21,
        ],
        1966: [
            7.197,
            7.191,
            7.191,
            7.26,
            7.366,
            7.38,
            7.376,
            7.389,
            7.366,
            7.411,
            7.54,
            7.589,
        ],
        1967: [
            7.593,
            7.652,
            7.684,
            7.791,
            7.818,
            7.75,
            7.755,
            7.868,
            7.89,
            7.922,
            8.087,
            8.087,
        ],
        1968: [
            8.11,
            8.11,
            8.193,
            8.265,
            8.238,
            8.261,
            8.193,
            8.198,
            8.185,
            8.211,
            8.265,
            8.32,
        ],
        1969: [
            8.301,
            8.251,
            8.301,
            8.399,
            8.399,
            8.301,
            8.366,
            8.392,
            8.408,
            8.44,
            8.515,
            8.605,
        ],
        1970: [
            8.646,
            8.613,
            8.679,
            8.727,
            8.67,
            8.703,
            8.867,
            9.007,
            9.048,
            9.138,
            9.162,
            9.188,
        ],
        1971: [
            9.285,
            9.278,
            9.376,
            9.475,
            9.533,
            9.573,
            9.573,
            9.59,
            9.704,
            9.811,
            9.944,
            10.074,
        ],
        1972: [
            10.082,
            10.074,
            10.172,
            10.172,
            10.222,
            10.246,
            10.386,
            10.493,
            10.641,
            10.714,
            10.731,
            10.814,
        ],
        1973: [
            10.895,
            10.912,
            11.002,
            11.158,
            11.322,
            11.494,
            11.617,
            11.808,
            12.012,
            12.202,
            12.217,
            12.35,
        ],
        1974: [
            12.423,
            12.465,
            12.736,
            13.015,
            13.179,
            13.236,
            13.393,
            13.614,
            13.828,
            13.975,
            14.361,
            14.558,
        ],
        1975: [
            14.762,
            14.903,
            15,
            15.264,
            15.452,
            15.494,
            15.74,
            15.987,
            16.241,
            16.241,
            16.347,
            16.61,
        ],
        1976: [
            16.807,
            16.997,
            17.391,
            17.743,
            18.556,
            18.442,
            18.556,
            18.713,
            19.065,
            19.329,
            19.69,
            19.894,
        ],
        1977: [
            20.542,
            20.849,
            21.348,
            21.736,
            21.926,
            22.539,
            23.278,
            24.033,
            24.368,
            24.747,
            24.947,
            25.144,
        ],
        1978: [
            25.545,
            25.796,
            26.127,
            26.677,
            26.944,
            27.216,
            27.806,
            28.291,
            28.524,
            28.785,
            28.911,
            29.303,
        ],
        1979: [
            29.806,
            30.037,
            30.349,
            30.807,
            31.167,
            31.442,
            32.121,
            32.437,
            32.864,
            33.305,
            33.385,
            33.872,
        ],
        1980: [
            34.804,
            35.115,
            35.304,
            35.645,
            35.892,
            36.449,
            36.964,
            37.397,
            37.795,
            38.098,
            38.487,
            39.025,
        ],
        1981: [
            39.818,
            40.02,
            40.817,
            41.223,
            41.415,
            41.451,
            42.263,
            42.778,
            43.118,
            43.603,
            43.981,
            44.647,
        ],
        1982: [
            45.572,
            45.927,
            46.378,
            46.988,
            47.668,
            48.126,
            48.744,
            49.082,
            49.139,
            49.631,
            49.793,
            50.901,
        ],
        1983: [
            51.761,
            52.021,
            52.337,
            53.056,
            53.276,
            53.588,
            53.779,
            54.501,
            54.937,
            55.682,
            56.249,
            57.122,
        ],
        1984: [
            58.007,
            58.227,
            58.696,
            58.973,
            59.292,
            59.712,
            60.629,
            61.05,
            61.174,
            61.543,
            61.859,
            62.278,
        ],
        1985: [
            63.438,
            63.898,
            64.296,
            64.959,
            65.163,
            65.052,
            65.422,
            65.52,
            66.239,
            66.58,
            67.093,
            67.371,
        ],
        1986: [
            69.308,
            69.617,
            69.852,
            70.022,
            70.217,
            70.862,
            71.57,
            71.773,
            72.516,
            72.787,
            72.62,
            72.93,
        ],
        1987: [
            73.489,
            73.802,
            74.231,
            74.399,
            74.307,
            74.325,
            75.078,
            75.045,
            75.737,
            76.187,
            76.012,
            76.284,
        ],
        1988: [
            76.768,
            76.978,
            77.536,
            77.266,
            77.262,
            77.562,
            78.586,
            79.363,
            80.06,
            80.15,
            80.105,
            80.742,
        ],
        1989: [
            81.68,
            81.738,
            82.26,
            82.481,
            82.598,
            83.048,
            84.396,
            84.59,
            85.485,
            85.83,
            85.969,
            86.304,
        ],
        1990: [
            87.144,
            87.697,
            88.018,
            88.218,
            88.211,
            88.483,
            89.672,
            90.065,
            91.013,
            91.821,
            91.729,
            91.955,
        ],
        1991: [
            93.025,
            92.895,
            93.197,
            93.399,
            93.664,
            93.934,
            95.1,
            95.453,
            96.233,
            96.838,
            96.985,
            97.038,
        ],
        1992: [
            98.576,
            99.233,
            99.592,
            99.485,
            99.745,
            99.726,
            100.05,
            100.962,
            101.795,
            101.856,
            101.921,
            102.227,
        ],
        1993: [
            103.185,
            103.218,
            103.581,
            104.035,
            104.322,
            104.581,
            104.955,
            105.583,
            106.18,
            106.576,
            106.755,
            107.262,
        ],
        1994: [
            108.346,
            108.385,
            108.743,
            109.171,
            109.394,
            109.512,
            109.941,
            110.651,
            110.988,
            111.229,
            111.422,
            111.914,
        ],
        1995: [
            113.074,
            113.628,
            114.29,
            114.896,
            114.942,
            115.051,
            115.069,
            115.394,
            115.848,
            116.064,
            116.372,
            116.748,
        ],
        1996: [
            117.462,
            117.782,
            118.2,
            118.871,
            119.281,
            119.181,
            119.34,
            119.678,
            119.97,
            120.134,
            120.141,
            120.497,
        ],
        1997: [
            120.847,
            120.765,
            120.825,
            120.869,
            121.045,
            121.041,
            121.263,
            121.798,
            122.401,
            122.356,
            122.599,
            122.925,
        ],
        1998: [
            123.215,
            122.927,
            122.984,
            123.289,
            123.45,
            123.53,
            123.986,
            124.318,
            124.41,
            124.421,
            124.309,
            124.653,
        ],
        1999: [
            125.111,
            125.185,
            125.737,
            126.202,
            126.198,
            126.225,
            126.772,
            127.312,
            127.557,
            127.509,
            127.714,
            128.29,
        ],
        2000: [
            128.712,
            128.894,
            129.405,
            129.943,
            130.159,
            130.553,
            131.346,
            131.897,
            132.238,
            132.576,
            132.906,
            133.366,
        ],
        2001: [
            133.413,
            133.851,
            134.415,
            135.113,
            135.624,
            136.081,
            136.415,
            136.745,
            136.726,
            136.585,
            136.483,
            136.978,
        ],
    }

    def _obtener_IPC(self, anyo: int, mes: int) -> Decimal:
        """
        Obtiene el IPC del INE para el año y mes indicado.

        :param año: Año para recuperar el IPC.
        :type año: int
        :param mes: Mes para recuperar el IPC. Los meses se empiezan a contar desde 1. 1 = Enero, 2 = Febrero, ... 12 = Diciembre.
        :type mes: int
        :return: Se conecta a la web del INE y consulta el IPC Base 2021 para el mes y año indicados.
        :rtype: Decimal
        """
        fecha = date(anyo, mes, 1)
        json = INE.obtener_datos_serie(fecha, fecha, self._SERIE_IPC)
        valor = None
        if len(json["Data"]) > 0:
            valor = Decimal(json["Data"][0]["Valor"])
            return valor
        else:
            raise ValueError(
                f"Renta no actualizada: No he podido recuperar los datos del IPC para {FechaUtils.mes_en_espanol(mes)} de {anyo}."
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
        # Convertir explícitamente a Decimal y redondear a dos decimales
        cantidad = Decimal(cantidad).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        dividendo = Decimal(0)
        divisor = Decimal(0)
        try:
            if anyo_inicial < 2002 and anyo_final >= 2002:  # type: ignore
                indice_ipc = self._obtener_IPC(anyo_final, mes)  # type: ignore
                if indice_ipc is None or indice_ipc.is_nan():
                    raise ValueError(
                        f"Renta no actualizada: No he podido recuperar los datos del IPC para {FechaUtils.mes_en_espanol(mes)} de {anyo_final}."  # type: ignore
                    )
                # Actualización de rentas de alquiler con el IPC entre un mes anterior a enero de 2002 y otro posterior
                # Indice LAU mes final
                # El índice LAU se obtiene multiplicando el índice general del mes, en base 2021 (llamando al método _obtener_IPC)
                # por el coeficiente LAU (constante COEFICIENTES_LAU_BASE_2021) de ese mismo mes.
                # NOTA: El cociente de índices se deberá redondear a 3 decimales antes de multiplicarlo por la renta inicial
                dividendo = (
                    indice_ipc
                    * Decimal(self._COEFICIENTES_LAU_BASE_2021[mes - 1])  # type: ignore
                ).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

                divisor = Decimal(
                    self._TABLA_IPC_BASE_1992[anyo_inicial][mes - 1]  # type: ignore
                ).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

            elif anyo_inicial < 2002 and anyo_final < 2002:  # type: ignore
                # Actualización de rentas de alquiler con el IPC entre dos meses anteriores a enero de 2002
                # Se obtiene de la tabla TABLA_IPC_BASE_1992
                dividendo = Decimal(
                    self._TABLA_IPC_BASE_1992[anyo_final][mes - 1]  # type: ignore
                ).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

                divisor = Decimal(
                    self._TABLA_IPC_BASE_1992[anyo_inicial][mes - 1]  # type: ignore
                ).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

            else:
                indice_ipc = self._obtener_IPC(anyo_final, mes)  # type: ignore
                if indice_ipc is None or indice_ipc.is_nan():
                    raise ValueError(
                        f"Renta no actualizada: No he podido recuperar los datos del IPC para {FechaUtils.mes_en_espanol(mes)} de {anyo_final}."  # type: ignore
                    )
                # Actualización de rentas de alquiler con el IPC entre dos meses posteriores a enero de 2002
                # IPC mes final
                dividendo = indice_ipc.quantize(
                    Decimal("0.001"), rounding=ROUND_HALF_UP
                )
                indice_ipc = self._obtener_IPC(anyo_inicial, mes)  # type: ignore
                if indice_ipc is None or indice_ipc.is_nan():
                    raise ValueError(
                        f"Renta no actualizada: No he podido recuperar los datos del IPC para {FechaUtils.mes_en_espanol(mes)} de {anyo_inicial}."  # type: ignore
                    )
                # IPC mes inicial
                divisor = indice_ipc.quantize(
                    Decimal("0.001"), rounding=ROUND_HALF_UP
                )
        except ConnectionError as err:
            print(err)
            raise
        # Para calcular la tasa de variación se hace:((IPC mes final / IPC mes inicial) - 1) * 100
        # Lo multiplico por 100 redondeo a 1 decimal y luego vuelvo a dividir entre 100 y luego rendondeo el resultado a 3 decimales.
        # Así se consigue que de exactamente la misma tasa de variación que en la web del INE.
        tasa_variacion = (((dividendo / divisor) - Decimal(1))).quantize(
            Decimal("0.001"), rounding=ROUND_HALF_UP
        )

        # Aplicar la tasa de variación a la cantidad inicial
        cantidad_actualizada = (
            cantidad + (cantidad * tasa_variacion)
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "cantidad": cantidad,
            "mes": FechaUtils.mes_en_espanol(mes),  # type: ignore
            "anyo_inicial": anyo_inicial,
            "anyo_final": anyo_final,
            "indice_inicial": divisor,
            "indice_final": dividendo,
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

        return None
