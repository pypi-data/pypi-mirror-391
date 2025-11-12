"""AlphaTRACER radon sensor implementation with abstract interface."""

from multipledispatch import dispatch

from atmospyre.sensors import Sensor, ModbusBackendTag, Byteorder, Stopbits, Parity, ModbusMode, modbusbackend_namespace
from atmospyre.sensors.read_tag import ReadTag
from atmospyre.sensors.read_tag import ReadTagMetadata
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# AlphaTRACER-specific tags
# ============================================================================

class ModbusAddressTag(ReadTag):
    """Tag for Modbus slave address."""
    pass


class BaudrateTag(ReadTag):
    """Tag for Modbus baudrate."""
    pass


class RadonLiveTag(ReadTag):
    """Tag for live radon concentration measurement."""
    pass


class Radon24hTag(ReadTag):
    """Tag for 24-hour average radon concentration measurement."""
    pass


class RadonLongTermTag(ReadTag):
    """Tag for long-term average radon concentration measurement."""
    pass


# ============================================================================
# Tag instances
# ============================================================================

MODBUS_ADDRESS = ModbusAddressTag(ReadTagMetadata(
    unit="",
    description="Modbus slave address",
    precision=0,
    source="AlphaTRACER Register 0 (0x0000), 16-bit unsigned"
))
"""Modbus slave address (1-247) from register 0x0000."""

BAUDRATE = BaudrateTag(ReadTagMetadata(
    unit="bps",
    description="Serial baudrate",
    precision=0,
    source="AlphaTRACER Register 4 (0x0004), 16-bit unsigned"
))
"""Serial communication baudrate (2400, 4800, 9600, 19200, or 38400 bps) from register 0x0004."""

RADON_LIVE = RadonLiveTag(ReadTagMetadata(
    unit="Bq/m³",
    description="Live radon concentration",
    precision=0,
    source="AlphaTRACER Register 20 (0x0014), 32-bit long, ABCD"
))
"""Live radon concentration in Bq/m³ from register 0x0014. Updates approximately every 10 minutes."""

RADON_24H = Radon24hTag(ReadTagMetadata(
    unit="Bq/m³",
    description="24-hour average radon concentration",
    precision=0,
    source="AlphaTRACER Register 22 (0x0016), 32-bit long, ABCD"
))
"""24-hour rolling average radon concentration in Bq/m³ from register 0x0016. More stable than live reading, recommended for daily monitoring."""

RADON_LONG_TERM = RadonLongTermTag(ReadTagMetadata(
    unit="Bq/m³",
    description="Long-term average radon concentration",
    precision=0,
    source="AlphaTRACER Register 24 (0x0018), 32-bit long, ABCD"
))
"""Long-term rolling average radon concentration in Bq/m³ from register 0x0018. Most stable measurement, suitable for compliance reporting."""


# ============================================================================
# Tag collections for AlphaTRACER
# ============================================================================

# Serial communication configuration tags (require power cycle)
ALPHATRACER_SERIAL_CONFIG_TAGS = {
    MODBUS_ADDRESS,
    BAUDRATE
}

# Read-only measurement tags
ALPHATRACER_MEASUREMENT_TAGS = {
    RADON_LIVE,
    RADON_24H,
    RADON_LONG_TERM
}


# ============================================================================
# Dispatch namespace for AlphaTRACER
# ============================================================================

alphatracer_namespace = {}


# ============================================================================
# READ function implementations
# ============================================================================

@dispatch(object, ModbusAddressTag, ModbusBackendTag, namespace=alphatracer_namespace)
def _read(instrument, tag: ModbusAddressTag, backend_tag: ModbusBackendTag) -> int:
    _read_register = modbusbackend_namespace['_read_register']
    return _read_register(instrument, 0, 0, 3,False, backend_tag)


@dispatch(object, BaudrateTag, ModbusBackendTag, namespace=alphatracer_namespace)
def _read(instrument, tag: BaudrateTag, backend_tag: ModbusBackendTag) -> int:
    _read_register = modbusbackend_namespace['_read_register']
    return _read_register(instrument, 4, 0, 3,False, backend_tag)


@dispatch(object, RadonLiveTag, ModbusBackendTag, namespace=alphatracer_namespace)
def _read(instrument, tag: RadonLiveTag, backend_tag: ModbusBackendTag) -> int:
    _read_long = modbusbackend_namespace['_read_long']
    return _read_long(instrument, 20, 3, False, Byteorder.ABCD, 2, backend_tag)


@dispatch(object, Radon24hTag, ModbusBackendTag, namespace=alphatracer_namespace)
def _read(instrument, tag: Radon24hTag, backend_tag: ModbusBackendTag) -> int:
    _read_long = modbusbackend_namespace['_read_long']
    return _read_long(instrument, 22, 3, False, Byteorder.ABCD, 2, backend_tag)


@dispatch(object, RadonLongTermTag, ModbusBackendTag, namespace=alphatracer_namespace)
def _read(instrument, tag: RadonLongTermTag, backend_tag: ModbusBackendTag) -> int:
    _read_long = modbusbackend_namespace['_read_long']
    return _read_long(instrument, 24, 3, False, Byteorder.ABCD, 2, backend_tag)


# ============================================================================
# WRITE function implementations
# ============================================================================

@dispatch(object, ModbusAddressTag, object, ModbusBackendTag, namespace=alphatracer_namespace)
def _write(instrument, tag: ModbusAddressTag, value: int, backend_tag: ModbusBackendTag) -> None:
    if not 1 <= value <= 247:
        raise ValueError("Modbus address must be between 1 and 247")
    _write_register = modbusbackend_namespace['_write_register']
    _write_register(instrument, 0, value, 0, 6, False, backend_tag)


@dispatch(object, BaudrateTag, object, ModbusBackendTag, namespace=alphatracer_namespace)
def _write(instrument, tag: BaudrateTag, value: int, backend_tag: ModbusBackendTag) -> None:
    valid_baudrates = {2400, 4800, 9600, 19200, 38400}
    if value not in valid_baudrates:
        raise ValueError(f"Baudrate must be one of {sorted(valid_baudrates)}")
    if value==2400:
        value=0
    if value==4800:
        value=1
    if value==9600:
        value=2
    if value==19200:
        value=3
    if value==38400:
        value=4
    _write_register = modbusbackend_namespace['_write_register']
    _write_register(instrument, 4, value, 0, 6, False, backend_tag)


# ============================================================================
# AlphaTRACER Sensor Class
# ============================================================================

class AlphaTRACER(Sensor):
    """RadonTech AlphaTRACER radon sensor with Modbus RTU communication.

    Examples
    --------
    Read measurements:
    >>> sensor = AlphaTRACER(port='COM4', slave_address=1)
    >>> result = sensor.read([RADON_LIVE, RADON_24H])
    >>> print(f"Live: {result[RADON_LIVE]} Bq/m³")

    Read all available measurements:
    >>> result = sensor.read([RADON_LIVE, RADON_24H, RADON_LONG_TERM])
    >>> print(f"24h avg: {result[RADON_24H]} Bq/m³")

    Write serial configuration (requires power cycle):
    >>> sensor.write({MODBUS_ADDRESS: 5, BAUDRATE: 9600})
    ⚠️  WARNING: Serial configuration changed!
    Power cycle the sensor to apply changes.
    Tags written: ModbusAddressTag, BaudrateTag

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
        modbus_mode: ModbusMode = ModbusMode.RTU,
        timeout: float = 0.5,
        backend_tag: ModbusBackendTag | None = None,
    ):
        # All valid tags for AlphaTRACER
        valid_tags = list(ALPHATRACER_MEASUREMENT_TAGS | ALPHATRACER_SERIAL_CONFIG_TAGS)

        super().__init__(
            port=port,
            valid_tags=valid_tags,
            namespace=alphatracer_namespace,
            serial_config_tags=ALPHATRACER_SERIAL_CONFIG_TAGS,
            sensor_config_tags=set(),  # No sensor config tags for this device
            slave_address=slave_address,
            baudrate=baudrate,
            stopbits=stopbits,
            bytesize=bytesize,
            parity=parity,
            modbus_mode=modbus_mode,
            timeout=timeout,
            backend_tag=backend_tag
        )