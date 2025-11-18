"""Sensors package for Modbus sensor communication.

Recommended usage pattern (module as namespace):

    >>> from sensors.co2.vaisala import gmp252
    >>> from sensors.radon.radontech import alphatracer
    >>>
    >>> co2_sensor = gmp252.GMP252('COM3')
    >>> result = co2_sensor.read([gmp252.CO2, gmp252.TEMPERATURE])
    >>>
    >>> radon_sensor = alphatracer.AlphaTRACER('COM4')
    >>> result = radon_sensor.read([alphatracer.RADON_LIVE])

This pattern avoids tag name collisions when using multiple sensor types.
"""

from .sensor import Sensor as Sensor
from .sensor import ModbusBackendTag as ModbusBackendTag
from .sensor import Byteorder as Byteorder
from .sensor import modbusbackend_namespace as modbusbackend_namespace
from .sensor import Instrument as Instrument
from .sensor import ModbusMode as ModbusMode
from .sensor import Parity as Parity
from .sensor import Stopbits as Stopbits
