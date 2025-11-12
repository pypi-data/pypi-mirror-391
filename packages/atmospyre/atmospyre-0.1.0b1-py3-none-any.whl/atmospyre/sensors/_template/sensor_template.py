from multipledispatch import dispatch
from minimalmodbus import Instrument

from atmospyre.sensors import Sensor
from atmospyre.sensors.read_tag import ReadTag
from atmospyre.sensors.read_tag import ReadTagMetadata


# ============================================================================
# `[YourSensor]`-specific tags (empty structs)
# ============================================================================


class YourMeasurementTag(ReadTag):
    """Tag for `[measurement name]` measurement.

    This tag class represents `[measurement description]` from the
    `[YourSensor]` sensor. It is used with the dispatch mechanism to
    route read operations to the appropriate register reading function.
    """
    pass


YOUR_MEASUREMENT = YourMeasurementTag(ReadTagMetadata(
    unit="[unit]",  # e.g., "ppm", "°C", "Pa"
    description="[Measurement description]",
    precision=2,  # Number of decimal places
    data_type="float",  # or "int"
    min_interval=1,  # Minimum seconds between readings
    source="[YourSensor] User Manual, Register [X]"
))
"""` [Measurement name]` measurement tag.

This tag instance provides access to `[measurement description]` from
the `[YourSensor]` sensor.

Attributes
----------
unit : str
    `[unit]` (e.g., parts per million, degrees Celsius)
description : str
    `[Measurement description]`
precision : int
    `[X]` (decimal places)
data_type : str
    `[float/int]`
min_interval : int
    `[X]` seconds minimum between readings
source : str
    Modbus register `[X]`

Examples
--------
Read measurement:

>>> from atmospyre.sensors.implementations.yourtype import yoursensor
>>> sensor = yoursensor.YourSensor(port='/dev/ttyUSB0', slave_address=1)
>>> result = sensor.read([yoursensor.YOUR_MEASUREMENT])
>>> print(result[yoursensor.YOUR_MEASUREMENT])
[example value]

Read multiple measurements:

>>> from atmospyre.sensors.implementations.yourtype.yoursensor import (
...     YourSensor, YOUR_MEASUREMENT, ANOTHER_MEASUREMENT
... )
>>> sensor = YourSensor(port='/dev/ttyUSB0')
>>> result = sensor.read([YOUR_MEASUREMENT, ANOTHER_MEASUREMENT])
>>> print(f"{result[YOUR_MEASUREMENT]} [unit]")
[example output]
"""

# ============================================================================
# Dispatch namespace for `[YourSensor]` read functions
# ============================================================================

yoursensor_namespace = {}


# ============================================================================
# `[YourSensor]` Read function implementations using dispatch decorator
# ============================================================================

@dispatch(object, YourMeasurementTag, namespace=yoursensor_namespace)
def _read(instrument: Instrument, tag: YourMeasurementTag) -> float:
    """Read `[measurement name]` from register `[X]`.

    This function reads `[measurement description]` from Modbus register `[X]`
    using `[format description, e.g., 32-bit floating point]`.

    Parameters
    ----------
    instrument : Instrument
        minimalmodbus Instrument instance for Modbus communication
    tag : YourMeasurementTag
        Tag instance identifying this measurement type

    Returns
    -------
    float
        `[Measurement description]` in `[unit]`
    """
    pass


# ============================================================================
# `[YourSensor]` Sensor Class
# ============================================================================


class YourSensor(Sensor):
    """`[Manufacturer]` `[Model]` `[sensor type]` with Modbus RTU communication.

    The `[YourSensor]` is a `[description of sensor capabilities and use cases]`.
    It communicates via Modbus RTU protocol and measures `[list of measurements]`.

    Parameters
    ----------
    port : str
        Serial port name (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
    slave_address : int, optional
        Modbus slave address, by default 1
    baudrate : int, optional
        Serial communication speed in baud, by default 19200
    stopbits : int, optional
        Number of stop bits, by default 1
    bytesize : int, optional
        Number of data bits per byte, by default 8
    parity : str, optional
        Parity checking method ('N' for None, 'E' for Even, 'O' for Odd),
        by default 'N'
    timeout : float, optional
        Read timeout in seconds, by default 0.5

    Attributes
    ----------
    port : str
        Serial port name
    slave_address : int
        Modbus slave address
    valid_tags : list of ReadTag
        List of valid measurement tags for this sensor

    Raises
    ------
    SerialException
        If the serial port cannot be opened or configured
    ModbusException
        If Modbus communication fails

    Examples
    --------
    Basic initialization and single tag reading:

    >>> from atmospyre.sensors.implementations.yourtype import yoursensor
    >>> sensor = yoursensor.YourSensor(port='/dev/ttyUSB0', slave_address=1)
    >>> result = sensor.read([yoursensor.YOUR_MEASUREMENT])
    >>> print(result[yoursensor.YOUR_MEASUREMENT])
    [example value]

    Read multiple measurements:

    >>> from atmospyre.sensors.implementations.yourtype.yoursensor import (
    ...     YourSensor, YOUR_MEASUREMENT, ANOTHER_MEASUREMENT
    ... )
    >>> sensor = YourSensor(port='/dev/ttyUSB0')
    >>> result = sensor.read([YOUR_MEASUREMENT, ANOTHER_MEASUREMENT])
    >>> print(f"Measurement: {result[YOUR_MEASUREMENT]} [unit]")
    Measurement: [example] [unit]

    Custom serial configuration:

    >>> sensor = YourSensor(
    ...     port='COM3',
    ...     slave_address=2,
    ...     baudrate=9600,
    ...     timeout=1.0
    ... )
    """

    def __init__(
        self,
        port: str,
        slave_address: int = 1,
        baudrate: int = 19200,
        stopbits: int = 1,
        bytesize: int = 8,
        parity: str = 'N',
        timeout: float = 0.5
    ):
        """Initialize `[YourSensor]` sensor with serial communication parameters.

        Parameters
        ----------
        port : str
            Serial port name (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
        slave_address : int, optional
            Modbus slave address, by default 1
        baudrate : int, optional
            Serial communication speed in baud, by default 19200
        stopbits : int, optional
            Number of stop bits, by default 1
        bytesize : int, optional
            Number of data bits per byte, by default 8
        parity : str, optional
            Parity checking method ('N', 'E', 'O'), by default 'N'
        timeout : float, optional
            Read timeout in seconds, by default 0.5
        """
        # TODO: Update valid_tags list with your tag instances
        super().__init__(
            port=port,
            valid_tags=[YOUR_MEASUREMENT],  # Add all your tag instances here
            namespace=yoursensor_namespace,
            slave_address=slave_address,
            baudrate=baudrate,
            stopbits=stopbits,
            bytesize=bytesize,
            parity=parity,
            timeout=timeout
        )