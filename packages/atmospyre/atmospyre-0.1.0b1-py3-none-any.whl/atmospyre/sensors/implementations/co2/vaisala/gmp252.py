"""GMP252 CO2 sensor implementation with complete register access."""

from typing import Any
from multipledispatch import dispatch

from atmospyre.sensors import Sensor, ModbusBackendTag, Byteorder, Stopbits, Parity, ModbusMode, modbusbackend_namespace
from atmospyre.sensors.read_tag import ReadTag
from atmospyre.sensors.read_tag import ReadTagMetadata
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# GMP252-specific tags
# ============================================================================

class CO2Tag(ReadTag):
    """Tag for CO2 concentration measurement as floating point."""
    pass

class CO2IntTag(ReadTag):
    """Tag for CO2 concentration measurement as integer."""
    pass

class CO2IntScaledTag(ReadTag):
    """Tag for CO2 concentration measurement as scaled integer (×10)."""
    pass

class CompensationTemperatureTag(ReadTag):
    """Tag for compensation temperature measurement."""
    pass

class MeasuredTemperatureTag(ReadTag):
    """Tag for measured temperature."""
    pass

class DeviceStatusTag(ReadTag):
    """Tag for general device status."""
    pass

class CO2StatusTag(ReadTag):
    """Tag for CO2 measurement status."""
    pass

class ErrorCodeTag(ReadTag):
    """Tag for error code."""
    pass

class PressureCompensationTag(ReadTag):
    """Tag for pressure compensation value (power-up)."""
    pass

class TemperatureCompensationTag(ReadTag):
    """Tag for temperature compensation value (power-up)."""
    pass

class HumidityCompensationTag(ReadTag):
    """Tag for humidity compensation value (power-up)."""
    pass

class OxygenCompensationTag(ReadTag):
    """Tag for oxygen compensation value (power-up)."""
    pass

class VolatilePressureCompensationTag(ReadTag):
    """Tag for volatile pressure compensation value."""
    pass

class VolatileTemperatureCompensationTag(ReadTag):
    """Tag for volatile temperature compensation value."""
    pass

class VolatileHumidityCompensationTag(ReadTag):
    """Tag for volatile humidity compensation value."""
    pass

class VolatileOxygenCompensationTag(ReadTag):
    """Tag for volatile oxygen compensation value."""
    pass

class ModbusAddressTag(ReadTag):
    """Tag for Modbus address."""
    pass

class SerialSpeedTag(ReadTag):
    """Tag for serial communication speed."""
    pass

class SerialParityTag(ReadTag):
    """Tag for serial parity."""
    pass

class SerialStopBitsTag(ReadTag):
    """Tag for serial stop bits."""
    pass

class PressureCompensationModeTag(ReadTag):
    """Tag for pressure compensation mode."""
    pass

class TemperatureCompensationModeTag(ReadTag):
    """Tag for temperature compensation mode."""
    pass

class HumidityCompensationModeTag(ReadTag):
    """Tag for humidity compensation mode."""
    pass

class OxygenCompensationModeTag(ReadTag):
    """Tag for oxygen compensation mode."""
    pass

class CO2FilteringFactorTag(ReadTag):
    """Tag for CO2 filtering factor."""
    pass


# ============================================================================
# Tag instances
# ============================================================================

CO2 = CO2Tag(ReadTagMetadata(
    unit="ppm",
    description="CO2 concentration (float)",
    precision=1,
    source="GMP252 Register 1 (0x0000), 32-bit float, CDAB"
))
"""CO2 concentration in ppm as a 32-bit float value from register 0x0000."""

CO2_INT = CO2IntTag(ReadTagMetadata(
    unit="ppm",
    description="CO2 concentration (integer)",
    precision=0,
    source="GMP252 Register 257 (0x0100), 16-bit signed integer"
))
"""CO2 concentration in ppm as a 16-bit signed integer from register 0x0100."""

CO2_INT_SCALED = CO2IntScaledTag(ReadTagMetadata(
    unit="ppm",
    description="CO2 concentration (integer, scaled ×10 by sensor)",
    precision=1,
    source="GMP252 Register 258 (0x0101), 16-bit signed integer"
))
"""CO2 concentration in ppm (scaled ×10) from register 0x0101."""

COMPENSATION_TEMPERATURE = CompensationTemperatureTag(ReadTagMetadata(
    unit="°C",
    description="Compensation temperature",
    precision=2,
    source="GMP252 Register 3 (0x0002), 32-bit float, CDAB"
))
"""Temperature used for compensation (°C), register 0x0002."""

MEASURED_TEMPERATURE = MeasuredTemperatureTag(ReadTagMetadata(
    unit="°C",
    description="Measured temperature",
    precision=2,
    source="GMP252 Register 5 (0x0004), 32-bit float, CDAB"
))
"""Measured temperature in °C, from register 0x0004."""

DEVICE_STATUS = DeviceStatusTag(ReadTagMetadata(
    unit=None,
    description="General device status (0=OK, 1=Critical, 2=Error, 4=Warning)",
    precision=None,
    source="GMP252 Register 2049 (0x0800), 16-bit integer"
))
"""General device status (0=OK, 1=Critical, 2=Error, 4=Warning), register 0x0800."""

CO2_STATUS = CO2StatusTag(ReadTagMetadata(
    unit=None,
    description="CO2 measurement status (0=OK, 2=Not reliable, 256=Not ready)",
    precision=None,
    source="GMP252 Register 2050 (0x0801), 16-bit integer"
))
"""CO2 measurement status (0=OK, 2=Not reliable, 256=Not ready), register 0x0801."""

ERROR_CODE = ErrorCodeTag(ReadTagMetadata(
    unit=None,
    description="Error code bitmask",
    precision=None,
    source="GMP252 Register 2052 (0x0803), 32-bit integer"
))
"""Error code bitmask, 32-bit integer from register 0x0803."""

PRESSURE_COMPENSATION = PressureCompensationTag(ReadTagMetadata(
    unit="hPa",
    description="Power-up pressure compensation",
    precision=2,
    source="GMP252 Register 513 (0x0200), 32-bit float"
))
"""Power-up pressure compensation in hPa, register 0x0200."""

TEMPERATURE_COMPENSATION = TemperatureCompensationTag(ReadTagMetadata(
    unit="°C",
    description="Power-up temperature compensation",
    precision=2,
    source="GMP252 Register 515 (0x0202), 32-bit float"
))
"""Power-up temperature compensation (°C), register 0x0202."""

HUMIDITY_COMPENSATION = HumidityCompensationTag(ReadTagMetadata(
    unit="%RH",
    description="Power-up humidity compensation",
    precision=2,
    source="GMP252 Register 517 (0x0204), 32-bit float"
))
"""Power-up humidity compensation (%RH), register 0x0204."""

OXYGEN_COMPENSATION = OxygenCompensationTag(ReadTagMetadata(
    unit="%O2",
    description="Power-up oxygen compensation",
    precision=2,
    source="GMP252 Register 519 (0x0206), 32-bit float"
))
"""Power-up oxygen compensation (%O₂), register 0x0206."""

VOLATILE_PRESSURE_COMPENSATION = VolatilePressureCompensationTag(ReadTagMetadata(
    unit="hPa",
    description="Volatile pressure compensation (cleared at reset)",
    precision=2,
    source="GMP252 Register 521 (0x0208), 32-bit float"
))
"""Volatile pressure compensation (cleared at reset), register 0x0208."""

VOLATILE_TEMPERATURE_COMPENSATION = VolatileTemperatureCompensationTag(ReadTagMetadata(
    unit="°C",
    description="Volatile temperature compensation (cleared at reset)",
    precision=2,
    source="GMP252 Register 523 (0x020A), 32-bit float"
))
"""Volatile temperature compensation (cleared at reset), register 0x020A."""

VOLATILE_HUMIDITY_COMPENSATION = VolatileHumidityCompensationTag(ReadTagMetadata(
    unit="%RH",
    description="Volatile humidity compensation (cleared at reset)",
    precision=2,
    source="GMP252 Register 525 (0x020C), 32-bit float"
))
"""Volatile humidity compensation (cleared at reset), register 0x020C."""

VOLATILE_OXYGEN_COMPENSATION = VolatileOxygenCompensationTag(ReadTagMetadata(
    unit="%O2",
    description="Volatile oxygen compensation (cleared at reset)",
    precision=2,
    source="GMP252 Register 527 (0x020E), 32-bit float"
))
"""Volatile oxygen compensation (cleared at reset), register 0x020E."""

MODBUS_ADDRESS = ModbusAddressTag(ReadTagMetadata(
    unit=None,
    description="Modbus address (1-247)",
    precision=None,
    source="GMP252 Register 769 (0x0300), 16-bit integer"
))
"""Modbus slave address (1–247), register 0x0300."""

SERIAL_SPEED = SerialSpeedTag(ReadTagMetadata(
    unit="baud",
    description="Serial speed (0=4800, 1=9600, 2=19200, 3=38400, 4=57600, 5=115200)",
    precision=None,
    source="GMP252 Register 770 (0x0301), 16-bit integer"
))
"""Serial communication speed (code 0–5), register 0x0301."""

SERIAL_PARITY = SerialParityTag(ReadTagMetadata(
    unit=None,
    description="Serial parity (0=None, 1=Even, 2=Odd)",
    precision=None,
    source="GMP252 Register 771 (0x0302), 16-bit integer"
))
"""Serial parity mode (0=None, 1=Even, 2=Odd), register 0x0302."""

SERIAL_STOP_BITS = SerialStopBitsTag(ReadTagMetadata(
    unit=None,
    description="Serial stop bits (1–2)",
    precision=None,
    source="GMP252 Register 772 (0x0303), 16-bit integer"
))
"""Serial stop bits (1 or 2), register 0x0303."""

PRESSURE_COMPENSATION_MODE = PressureCompensationModeTag(ReadTagMetadata(
    unit=None,
    description="Pressure compensation mode (0=Off, 1=On)",
    precision=None,
    source="GMP252 Register 773 (0x0304), 16-bit integer"
))
"""Pressure compensation mode (0=Off, 1=On), register 0x0304."""

TEMPERATURE_COMPENSATION_MODE = TemperatureCompensationModeTag(ReadTagMetadata(
    unit=None,
    description="Temperature compensation mode (0=Off, 1=Given, 2=Measured)",
    precision=None,
    source="GMP252 Register 774 (0x0305), 16-bit integer"
))
"""Temperature compensation mode (0=Off, 1=Given, 2=Measured), register 0x0305."""

HUMIDITY_COMPENSATION_MODE = HumidityCompensationModeTag(ReadTagMetadata(
    unit=None,
    description="Humidity compensation mode (0=Off, 1=On)",
    precision=None,
    source="GMP252 Register 775 (0x0306), 16-bit integer"
))
"""Humidity compensation mode (0=Off, 1=On), register 0x0306."""

OXYGEN_COMPENSATION_MODE = OxygenCompensationModeTag(ReadTagMetadata(
    unit=None,
    description="Oxygen compensation mode (0=Off, 1=On)",
    precision=None,
    source="GMP252 Register 776 (0x0307), 16-bit integer"
))
"""Oxygen compensation mode (0=Off, 1=On), register 0x0307."""

CO2_FILTERING_FACTOR = CO2FilteringFactorTag(ReadTagMetadata(
    unit=None,
    description="CO2 filtering factor (0–100, 100=no filtering)",
    precision=None,
    source="GMP252 Register 777 (0x0308), 16-bit integer"
))
"""CO2 filtering factor (0–100, 100=no filtering), register 0x0308."""



# ============================================================================
# Tag collections for GMP252
# ============================================================================

# Serial communication configuration tags (require power cycle)
GMP252_SERIAL_CONFIG_TAGS = {
    MODBUS_ADDRESS,
    SERIAL_SPEED,
    SERIAL_PARITY,
    SERIAL_STOP_BITS
}

# Sensor behavior configuration tags
GMP252_SENSOR_CONFIG_TAGS = {
    PRESSURE_COMPENSATION,
    TEMPERATURE_COMPENSATION,
    HUMIDITY_COMPENSATION,
    OXYGEN_COMPENSATION,
    VOLATILE_PRESSURE_COMPENSATION,
    VOLATILE_TEMPERATURE_COMPENSATION,
    VOLATILE_HUMIDITY_COMPENSATION,
    VOLATILE_OXYGEN_COMPENSATION,
    PRESSURE_COMPENSATION_MODE,
    TEMPERATURE_COMPENSATION_MODE,
    HUMIDITY_COMPENSATION_MODE,
    OXYGEN_COMPENSATION_MODE,
    CO2_FILTERING_FACTOR
}

# Read-only measurement tags
GMP252_MEASUREMENT_TAGS = {
    CO2,
    CO2_INT,
    CO2_INT_SCALED,
    COMPENSATION_TEMPERATURE,
    MEASURED_TEMPERATURE,
    DEVICE_STATUS,
    CO2_STATUS,
    ERROR_CODE
}


# ============================================================================
# Dispatch namespace for GMP252
# ============================================================================

gmp252_namespace = {}


# ============================================================================
# READ function implementations
# ============================================================================

@dispatch(object, CO2Tag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: CO2Tag, backend_tag: ModbusBackendTag) -> float:
    _read_float = modbusbackend_namespace['_read_float']
    return _read_float(instrument, 0, 3, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, CO2IntTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: CO2IntTag, backend_tag: ModbusBackendTag) -> int:
    _read_register = modbusbackend_namespace['_read_register']
    return _read_register(instrument, 256, 0, 3, True, backend_tag)


@dispatch(object, CO2IntScaledTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: CO2IntScaledTag, backend_tag: ModbusBackendTag) -> float:
    _read_register = modbusbackend_namespace['_read_register']
    raw_value = _read_register(instrument, 257, 0, 3, True, backend_tag)
    return raw_value / 10.0


@dispatch(object, CompensationTemperatureTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: CompensationTemperatureTag, backend_tag: ModbusBackendTag) -> float:
    _read_float = modbusbackend_namespace['_read_float']
    return _read_float(instrument, 2, 3, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, MeasuredTemperatureTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: MeasuredTemperatureTag, backend_tag: ModbusBackendTag) -> float:
    _read_float = modbusbackend_namespace['_read_float']
    return _read_float(instrument, 4, 3, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, DeviceStatusTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: DeviceStatusTag, backend_tag: ModbusBackendTag) -> int:
    _read_register = modbusbackend_namespace['_read_register']
    return _read_register(instrument, 2048, 0, 3, False, backend_tag)


@dispatch(object, CO2StatusTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: CO2StatusTag, backend_tag: ModbusBackendTag) -> int:
    _read_register = modbusbackend_namespace['_read_register']
    return _read_register(instrument, 2049, 0, 3, False, backend_tag)


@dispatch(object, ErrorCodeTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: ErrorCodeTag, backend_tag: ModbusBackendTag) -> int:
    _read_long = modbusbackend_namespace['_read_long']
    return _read_long(instrument, 2051, 3, False, Byteorder.CDAB, 2, backend_tag)


@dispatch(object, PressureCompensationTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: PressureCompensationTag, backend_tag: ModbusBackendTag) -> float:
    _read_float = modbusbackend_namespace['_read_float']
    return _read_float(instrument, 512, 3, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, TemperatureCompensationTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: TemperatureCompensationTag, backend_tag: ModbusBackendTag) -> float:
    _read_float = modbusbackend_namespace['_read_float']
    return _read_float(instrument, 514, 3, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, HumidityCompensationTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: HumidityCompensationTag, backend_tag: ModbusBackendTag) -> float:
    _read_float = modbusbackend_namespace['_read_float']
    return _read_float(instrument, 516, 3, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, OxygenCompensationTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: OxygenCompensationTag, backend_tag: ModbusBackendTag) -> float:
    _read_float = modbusbackend_namespace['_read_float']
    return _read_float(instrument, 518, 3, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, VolatilePressureCompensationTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: VolatilePressureCompensationTag, backend_tag: ModbusBackendTag) -> float:
    _read_float = modbusbackend_namespace['_read_float']
    return _read_float(instrument, 520, 3, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, VolatileTemperatureCompensationTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: VolatileTemperatureCompensationTag, backend_tag: ModbusBackendTag) -> float:
    _read_float = modbusbackend_namespace['_read_float']
    return _read_float(instrument, 522, 3, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, VolatileHumidityCompensationTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: VolatileHumidityCompensationTag, backend_tag: ModbusBackendTag) -> float:
    _read_float = modbusbackend_namespace['_read_float']
    return _read_float(instrument, 524, 3, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, VolatileOxygenCompensationTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: VolatileOxygenCompensationTag, backend_tag: ModbusBackendTag) -> float:
    _read_float = modbusbackend_namespace['_read_float']
    return _read_float(instrument, 526, 3, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, ModbusAddressTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: ModbusAddressTag, backend_tag: ModbusBackendTag) -> int:
    _read_register = modbusbackend_namespace['_read_register']
    return _read_register(instrument, 768, 0, 3, False, backend_tag)


@dispatch(object, SerialSpeedTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: SerialSpeedTag, backend_tag: ModbusBackendTag) -> int:
    _read_register = modbusbackend_namespace['_read_register']
    return _read_register(instrument, 769, 0, 3, False, backend_tag)


@dispatch(object, SerialParityTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: SerialParityTag, backend_tag: ModbusBackendTag) -> int:
    _read_register = modbusbackend_namespace['_read_register']
    return _read_register(instrument, 770, 0, 3, False, backend_tag)


@dispatch(object, SerialStopBitsTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: SerialStopBitsTag, backend_tag: ModbusBackendTag) -> int:
    _read_register = modbusbackend_namespace['_read_register']
    return _read_register(instrument, 771, 0, 3, False, backend_tag)


@dispatch(object, PressureCompensationModeTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: PressureCompensationModeTag, backend_tag: ModbusBackendTag) -> int:
    _read_register = modbusbackend_namespace['_read_register']
    return _read_register(instrument, 772, 0, 3, False, backend_tag)


@dispatch(object, TemperatureCompensationModeTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: TemperatureCompensationModeTag, backend_tag: ModbusBackendTag) -> int:
    _read_register = modbusbackend_namespace['_read_register']
    return _read_register(instrument, 773, 0, 3, False, backend_tag)


@dispatch(object, HumidityCompensationModeTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: HumidityCompensationModeTag, backend_tag: ModbusBackendTag) -> int:
    _read_register = modbusbackend_namespace['_read_register']
    return _read_register(instrument, 774, 0, 3, False, backend_tag)


@dispatch(object, OxygenCompensationModeTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: OxygenCompensationModeTag, backend_tag: ModbusBackendTag) -> int:
    _read_register = modbusbackend_namespace['_read_register']
    return _read_register(instrument, 775, 0, 3, False, backend_tag)


@dispatch(object, CO2FilteringFactorTag, ModbusBackendTag, namespace=gmp252_namespace)
def _read(instrument, tag: CO2FilteringFactorTag, backend_tag: ModbusBackendTag) -> int:
    _read_register = modbusbackend_namespace['_read_register']
    return _read_register(instrument, 776, 0, 3, False, backend_tag)


# ============================================================================
# WRITE function implementations
# ============================================================================

@dispatch(object, PressureCompensationTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: PressureCompensationTag, value: float, backend_tag: ModbusBackendTag) -> None:
    if not 500 <= value <= 1100:
        raise ValueError("Pressure must be between 500 and 1100 hPa")
    _write_float = modbusbackend_namespace['_write_float']
    _write_float(instrument, 512, value, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, VolatilePressureCompensationTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: VolatilePressureCompensationTag, value: float, backend_tag: ModbusBackendTag) -> None:
    if not 500 <= value <= 1100:
        raise ValueError("Pressure must be between 500 and 1100 hPa")
    _write_float = modbusbackend_namespace['_write_float']
    _write_float(instrument, 520, value, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, TemperatureCompensationTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: TemperatureCompensationTag, value: float, backend_tag: ModbusBackendTag) -> None:
    if not -40 <= value <= 80:
        raise ValueError("Temperature must be between -40 and +80 °C")
    _write_float = modbusbackend_namespace['_write_float']
    _write_float(instrument, 514, value, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, VolatileTemperatureCompensationTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: VolatileTemperatureCompensationTag, value: float, backend_tag: ModbusBackendTag) -> None:
    if not -40 <= value <= 80:
        raise ValueError("Temperature must be between -40 and +80 °C")
    _write_float = modbusbackend_namespace['_write_float']
    _write_float(instrument, 522, value, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, HumidityCompensationTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: HumidityCompensationTag, value: float, backend_tag: ModbusBackendTag) -> None:
    if not 0 <= value <= 100:
        raise ValueError("Humidity must be between 0 and 100 %RH")
    _write_float = modbusbackend_namespace['_write_float']
    _write_float(instrument, 516, value, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, VolatileHumidityCompensationTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: VolatileHumidityCompensationTag, value: float, backend_tag: ModbusBackendTag) -> None:
    if not 0 <= value <= 100:
        raise ValueError("Humidity must be between 0 and 100 %RH")
    _write_float = modbusbackend_namespace['_write_float']
    _write_float(instrument, 524, value, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, OxygenCompensationTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: OxygenCompensationTag, value: float, backend_tag: ModbusBackendTag) -> None:
    if not 0 <= value <= 100:
        raise ValueError("Oxygen must be between 0 and 100 %O2")
    _write_float = modbusbackend_namespace['_write_float']
    _write_float(instrument, 518, value, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, VolatileOxygenCompensationTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: VolatileOxygenCompensationTag, value: float, backend_tag: ModbusBackendTag) -> None:
    if not 0 <= value <= 100:
        raise ValueError("Oxygen must be between 0 and 100 %O2")
    _write_float = modbusbackend_namespace['_write_float']
    _write_float(instrument, 526, value, 2, Byteorder.CDAB, backend_tag)


@dispatch(object, ModbusAddressTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: ModbusAddressTag, value: int, backend_tag: ModbusBackendTag) -> None:
    if not 1 <= value <= 247:
        raise ValueError("Modbus address must be between 1 and 247")
    _write_register = modbusbackend_namespace['_write_register']
    _write_register(instrument, 768, value, 0, 16, False, backend_tag)


@dispatch(object, SerialSpeedTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: SerialSpeedTag, value: int, backend_tag: ModbusBackendTag) -> None:
    if not 0 <= value <= 5:
        raise ValueError("Serial speed must be 0-5")
    _write_register = modbusbackend_namespace['_write_register']
    _write_register(instrument, 769, value, 0, 16, False, backend_tag)


@dispatch(object, SerialParityTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: SerialParityTag, parity: Parity, backend_tag: ModbusBackendTag) -> None:
    if parity==Parity.NONE:
        value=0
    if parity==Parity.EVEN:
        value=1
    if parity==Parity.ODD:
        value=2
    _write_register = modbusbackend_namespace['_write_register']
    _write_register(instrument, 770, value, 0, 16, False, backend_tag)


@dispatch(object, SerialStopBitsTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: SerialStopBitsTag, stop_bit: Stopbits, backend_tag: ModbusBackendTag) -> None:
    if stop_bit==Stopbits.ONE:
        value=1
    if stop_bit==Stopbits.TWO:
        value=2
    _write_register = modbusbackend_namespace['_write_register']
    _write_register(instrument, 771, value, 0, 16, False, backend_tag)


@dispatch(object, PressureCompensationModeTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: PressureCompensationModeTag, value: bool, backend_tag: ModbusBackendTag) -> None:
    _write_register = modbusbackend_namespace['_write_register']
    _write_register(instrument, 772, 1 if value else 0, 0, 16, False, backend_tag)


@dispatch(object, TemperatureCompensationModeTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: TemperatureCompensationModeTag, value: int, backend_tag: ModbusBackendTag) -> None:
    if not 0 <= value <= 2:
        raise ValueError("Temperature compensation mode must be 0-2")
    _write_register = modbusbackend_namespace['_write_register']
    _write_register(instrument, 773, value, 0, 16, False, backend_tag)


@dispatch(object, HumidityCompensationModeTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: HumidityCompensationModeTag, value: bool, backend_tag: ModbusBackendTag) -> None:
    _write_register = modbusbackend_namespace['_write_register']
    _write_register(instrument, 774, 1 if value else 0, 0, 16, False, backend_tag)


@dispatch(object, OxygenCompensationModeTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: OxygenCompensationModeTag, value: bool, backend_tag: ModbusBackendTag) -> None:
    _write_register = modbusbackend_namespace['_write_register']
    _write_register(instrument, 775, 1 if value else 0, 0, 16, False, backend_tag)


@dispatch(object, CO2FilteringFactorTag, object, ModbusBackendTag, namespace=gmp252_namespace)
def _write(instrument, tag: CO2FilteringFactorTag, value: int, backend_tag: ModbusBackendTag) -> None:
    if not 0 <= value <= 100:
        raise ValueError("Filtering factor must be between 0 and 100")
    _write_register = modbusbackend_namespace['_write_register']
    _write_register(instrument, 776, value, 0, 16, False, backend_tag)


# ============================================================================
# GMP252 Sensor Class
# ============================================================================

class GMP252(Sensor):
    """Vaisala GMP252 CO2 probe with complete register access.

    Examples
    --------
    Read measurements:
    >>> sensor = GMP252(port='/dev/ttyUSB0', slave_address=1)
    >>> result = sensor.read([CO2, MEASURED_TEMPERATURE])
    >>> print(f"CO2: {result[CO2]} ppm")

    Write sensor configuration:
    >>> sensor.write({
    ...     PRESSURE_COMPENSATION_MODE: True,
    ...     PRESSURE_COMPENSATION: 1013.25
    ... })

    Write serial configuration (requires power cycle):
    >>> sensor.write({MODBUS_ADDRESS: 5, SERIAL_SPEED: 2})
    ⚠️  WARNING: Serial configuration changed!
    Power cycle the sensor to apply changes.
    Tags written: ModbusAddressTag, SerialSpeedTag

    Check which tags require power cycle:
    >>> serial_tags = sensor.get_serial_config_tags()
    >>> for tag in serial_tags:
    ...     print(f"- {type(tag).__name__}")
    """

    def __init__(
        self,
        port: str,
        slave_address: int = 1,
        baudrate: int = 19200,
        stopbits: Stopbits = Stopbits.TWO,
        bytesize: int = 8,
        parity: Parity = Parity.NONE,
        modbus_mode: ModbusMode=ModbusMode.RTU,
        timeout: float = 0.5,
        backend_tag: ModbusBackendTag | None = None,
    ):
        # All valid tags for GMP252
        valid_tags = list(GMP252_MEASUREMENT_TAGS | GMP252_SERIAL_CONFIG_TAGS | GMP252_SENSOR_CONFIG_TAGS)

        super().__init__(
            port=port,
            valid_tags=valid_tags,
            namespace=gmp252_namespace,
            serial_config_tags=GMP252_SERIAL_CONFIG_TAGS,
            sensor_config_tags=GMP252_SENSOR_CONFIG_TAGS,
            slave_address=slave_address,
            baudrate=baudrate,
            stopbits=stopbits,
            bytesize=bytesize,
            parity=parity,
            modbus_mode=modbus_mode,
            timeout=timeout,
            backend_tag=backend_tag
        )