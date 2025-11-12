# ArrendaTools Actualiza Renta
![License](https://img.shields.io/github/license/hokus15/ArrendaToolsActualizaRenta)
[![Build Status](https://github.com/hokus15/ArrendaToolsActualizaRenta/actions/workflows/main.yml/badge.svg)](https://github.com/hokus15/ArrendaToolsActualizaRenta/actions)
![GitHub last commit](https://img.shields.io/github/last-commit/hokus15/ArrendaToolsActualizaRenta?logo=github)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/hokus15/ArrendaToolsActualizaRenta?logo=github)

Módulo de python para calcular la actualización de rentas de alquiler en España por anualidades completas. Compatible con múltiples métodos, incluyendo:
- Porcentaje
- Cantidad fija
- Actualización basada en IPC (Índice de Precios al Consumo)
- IRAV (Índice de Rentas de Alquiler de Viviendas)
- Combinación mínima entre IPC y porcentaje

El cálculo usando el IPC (LAU), se basa según lo descrito en la página web del [Instituto Nacional de Estadística (INE)](https://www.ine.es/ss/Satellite?c=Page&cid=1254735905720&pagename=ProductosYServicios%2FPYSLayout&L=0&p=1254735893337). Es equivalente a utilizar la calculadora publicada por el INE en el siguiente enlace [Actualización de rentas con el IPC general (sistema IPC base 2021) para periodos anuales completos](https://www.ine.es/calcula).

## Limitaciones
Este módulo es válido solamente:
- En España
- Actualización usando el IPC: Para los periodos comprendidos entre marzo de 1954 y el último mes con datos de IPC publicados por el INE.
- Actualización usando el IRAV: Para los periodos comprendidos entre noviembre de 2024 y el último mes con datos de IRAV publicados por el INE.

## Estructura
El módulo utiliza una arquitectura basada en clases con un patrón Factory para la creación dinámica de diferentes métodos de actualización:

1. **`ActualizacionRenta`**: Clase base abstracta que define la interfaz para las actualizaciones.
2. **Factory**: Proporciona una forma dinámica de instanciar clases de actualización según el tipo requerido.
3. **Implementaciones**:

    - `Porcentaje`
    - `CantidadFija`
    - `IPC`
    - `MinimoIPCPorcentaje`
    - `IRAV`

4. **INE**: Clase que se conecta al INE para obtener los datos del IPC e IRAV.

## Requisitos

Este módulo requiere Python 3.8 o superior.

## Uso


### Parámetros de entrada
`cantidad (Decimal)`: **Obligatorio**. La cantidad de la renta a actualizar.

`mes (int)`: Obligatorio para los tipos de actualización **IPC**, **IRAV** y **MinimoIPCPorcentaje**. El mes en que se quiere calcular la actualización de la renta (1 a 12).

`anyo_inicial (int)`: Obligatorio para los tipos de actualización **IPC**, **IRAV** y **MinimoIPCPorcentaje**. El año inicial de referencia para el cálculo.

`anyo_final (int)`: Obligatorio para los tipos de actualización **IPC** y **MinimoIPCPorcentaje**. El año final de referencia para el cálculo.

`dato (Decimal)`: Obligatorio para los tipos de actualización **Porcentaje**, **CantidadFija** y **MinimoIPCPorcentaje**. Dato adicional para hacer los cálculos, por ejemplo en la actualización por porcentaje es el porcentaje de actualización (-1 -> -100% y 1 -> 100%). En la actualización por cantidad fija es la cantidad a actualizar.

### Retorno
La función devuelve un diccionario con los siguientes campos:

`cantidad (Decimal)`: **Obligatorio**. La cantidad pasada inicialmente por el usuario.

`cantidad_actualizada (Decimal)`: **Obligatorio**. La cantidad de la renta actualizada con el método escogido.

`indice_inicial (int)`: **Opcional**, sólo se devuelve para la actualización por IPC o MinimoIPCPorcentaje. El índice del IPC del mes inicial.

`indice_final (int)`: **Opcional**, sólo se devuelve para la actualización por IPC o MinimoIPCPorcentaje. El índice del IPC del mes final.

`mes (str)`: **Opcional**, sólo se devuelve para la actualización por IPC, MinimoIPCPorcentaje o IRAV. El nombre del mes en que se calculó la actualización de la renta.

`anyo_inicial (int)`: **Opcional**, sólo se devuelve para la actualización por IPC, MinimoIPCPorcentaje o IRAV. El año inicial de referencia para el cálculo. 

`anyo_final (int)`: **Opcional**, sólo se devuelve para la actualización por IPC o MinimoIPCPorcentaje. El año final de referencia para el cálculo.

`tasa_variacion (Decimal)`: **Opcional**, sólo se devuelve para la actualización por IPC, MinimoIPCPorcentaje, IRAV, Porcentaje. La tasa de variación utilizada en el cálculo. Multiplicado por 100 es el porcentaje.

## Ejemplo de uso

```python
from decimal import Decimal
from arrendatools.actualiza_renta.factory import ActualizacionRentaFactory

# Crear una instancia usando el Factory
actualizacion_renta = ActualizacionRentaFactory.crear("Porcentaje")

# Calcular pasando los datos al método calcular
resultado = actualizacion_renta.calcular(
    cantidad=Decimal("1000.00"),
    dato=Decimal("0.05")
)

print(resultado)
```

Resultado:
```
{'cantidad': Decimal('1000.00'), 'dato': Decimal('0.05'), 'cantidad_actualizada': Decimal('1050.00'), 'tasa_variacion': Decimal('0.05')}
```

## Descargo de responsabilidad
Este módulo proporciona una opción para actualizar una renta de alquiler en España por anualidades completas usando varios métodos como el IPC (LAU) o IRAV y realiza los cálculos necesarios conectándose a la página web del INE. Sin embargo, es importante tener en cuenta que este módulo no garantiza el cálculo correcto ni sirve como certificación oficial ante el arrendatario. **El usuario es responsable de verificar la exactitud de los datos generados y de obtener el certificado correspondiente en la página web del INE si es necesario.**

Es importante destacar que **el autor de este módulo está exento de cualquier tipo de responsabilidad derivada del uso de la información generada por este módulo**. La veracidad y exactitud de los datos generados son responsabilidad exclusiva del usuario. Cualquier sanción que pudiera derivarse del uso correcto, incorrecto o fraudulento de los datos generados por este módulo será responsabilidad exclusiva del usuario.

Por tanto, se recomienda al usuario **revisar cuidadosamente la información generada antes de notificar al inquilino la actualización de la renta y asegurarse de que cumple con los requisitos y está libre de errores**.
