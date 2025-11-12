"""Minimalmodbus backend implementation for Modbus communication.

This module provides the backend abstraction layer for the minimalmodbus library,
implementing dispatched read and write functions for different data types.
"""

from typing import List, Union
from multipledispatch import dispatch
import logging
logger = logging.getLogger(__name__)
from minimalmodbus import (
    BYTEORDER_BIG,
    BYTEORDER_BIG_SWAP,
    BYTEORDER_LITTLE_SWAP,
    BYTEORDER_LITTLE,
    MODE_RTU,
    MODE_ASCII,
    Instrument,
    serial
)


from atmospyre.sensors.sensor import ModbusBackendTag, modbusbackend_namespace, Byteorder, ModbusMode, Parity, Stopbits


class MinimalmodbusBackendTag(ModbusBackendTag):
    """Backend tag for minimalmodbus library.

    This tag is used to dispatch Modbus read operations to the
    minimalmodbus library implementation.

    Examples
    --------
    >>> from atmospyre.sensors.backends.minimalmodbus import MinimalmodbusBackendTag
    >>> backend = MinimalmodbusBackendTag()
    >>> # Used automatically by Sensor class
    """
    pass

# ============================================================================
# Mappings
# ============================================================================

@dispatch(Byteorder, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _get_byteorder(byteorder_enum: Byteorder, backend_tag: MinimalmodbusBackendTag) -> int:
    """Map generic Byteorder enum to minimalmodbus byte order constants.

    Parameters
    ----------
    byteorder_enum : Byteorder
        Generic byte order enumeration value
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Returns
    -------
    int
        Minimalmodbus byte order constant

    Examples
    --------
    >>> backend = MinimalmodbusBackendTag()
    >>> bo = _get_byteorder(Byteorder.CDAB, backend)
    >>> bo == BYTEORDER_LITTLE_SWAP
    True
    """
    mapping = {
        Byteorder.ABCD: BYTEORDER_BIG,
        Byteorder.BADC: BYTEORDER_BIG_SWAP,
        Byteorder.CDAB: BYTEORDER_LITTLE_SWAP,
        Byteorder.DCBA: BYTEORDER_LITTLE,
    }
    return mapping[byteorder_enum]

@dispatch(ModbusMode, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _get_modbus_mode(modbus_mode_enum: ModbusMode, backend_tag: MinimalmodbusBackendTag):
    mapping = {
        ModbusMode.RTU: MODE_RTU,
        ModbusMode.ASCII: MODE_ASCII
    }
    return mapping[modbus_mode_enum]

@dispatch(Parity, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _get_parity(parity_enum: Parity, backend_tag: MinimalmodbusBackendTag):
    mapping = {
        Parity.NONE: serial.PARITY_NONE,
        Parity.EVEN: serial.PARITY_EVEN,
        Parity.ODD: serial.PARITY_ODD,
        Parity.MARK: serial.PARITY_MARK,
        Parity.SPACE: serial.PARITY_SPACE,
    }
    return mapping[parity_enum]

@dispatch(Stopbits, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _get_stopbits(stopbits_enum: Stopbits, backend_tag: MinimalmodbusBackendTag):
    mapping = {
        Stopbits.ONE: serial.STOPBITS_ONE,
        Stopbits.ONE_POINT_FIVE: serial.STOPBITS_ONE_POINT_FIVE,
        Stopbits.TWO: serial.STOPBITS_TWO
    }
    return mapping[stopbits_enum]

# ============================================================================
# Instrument Creation
# ============================================================================

@dispatch(str, int, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _create_instrument(port: str, slave_address: int, backend_tag: MinimalmodbusBackendTag):
    """Create minimalmodbus Instrument instance."""
    from minimalmodbus import Instrument
    return Instrument(port, slave_address)

@dispatch(object, int, Stopbits, int, Parity,ModbusMode, float, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _setup_instrument(instrument, baudrate: int, stopbits: Stopbits, bytesize: int, parity: Parity, modbus_mode: ModbusMode, timeout: float, backend_tag: MinimalmodbusBackendTag) -> None:
    """Configure minimalmodbus instrument serial settings."""

    _get_stopbits = modbusbackend_namespace['_get_stopbits']
    _get_parity = modbusbackend_namespace['_get_parity']
    _get_modbus_mode = modbusbackend_namespace['_get_modbus_mode']

    instrument.serial.baudrate = baudrate
    instrument.serial.stopbits = _get_stopbits(stopbits,backend_tag)
    instrument.serial.bytesize = bytesize
    instrument.serial.parity = _get_parity(parity, backend_tag)
    instrument.serial.timeout = timeout
    instrument.mode = _get_modbus_mode(modbus_mode,backend_tag)
    instrument.close_port_after_each_call = True

@dispatch(object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _cleanup_instrument(
    instrument: Instrument,
    backend_tag: MinimalmodbusBackendTag
    ) -> None:
    """Clean up a minimalmodbus Instrument instance.

    Closes the serial port and releases resources. This is called after
    each read/write operation to ensure the port is available for other
    sensors.

    Parameters
    ----------
    instrument : Instrument
        The minimalmodbus Instrument instance to clean up.
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch.

    Notes
    -----
    This function is defensive - it checks if the serial port exists and
    is open before attempting to close it. This ensures cleanup works even
    if the instrument is in an unexpected state.

    The serial port object might be shared between multiple Instrument
    instances (if they use the same port string), so closing here affects
    all instruments using that port.

    Examples
    --------
    >>> instrument = Instrument('/dev/ttyACM0', 121)
    >>> # ... use instrument ...
    >>> _cleanup_instrument(instrument, MinimalmodbusBackendTag())
    >>> # Serial port is now closed
    """
    if instrument is not None:
        if hasattr(instrument, 'serial') and instrument.serial is not None:
            if hasattr(instrument.serial, 'is_open'):
                try:
                    if instrument.serial.is_open:
                        instrument.serial.close()
                except Exception:
                    # Silently ignore cleanup errors
                    # The port might already be closed or in an unexpected state
                    pass

@dispatch(object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _open_port(instrument, backend_tag):
    """Open port for minimalmodbus.

    Opens the serial port explicitly for clarity and documentation.

    Note: With close_port_after_each_call=True, minimalmodbus will
    automatically close and reopen the port for each transaction.
    This explicit open ensures the port is ready and documents the
    intent that the instrument should be in an "open" state.

    Parameters
    ----------
    instrument : Instrument
        The minimalmodbus Instrument instance
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch
    """
    if instrument and hasattr(instrument, 'serial') and instrument.serial:
        try:
            if not instrument.serial.is_open:
                instrument.serial.open()
                logger.debug(f"Opened port {instrument.serial.port}")
        except Exception as e:
            logger.warning(f"Failed to open port: {e}")
            raise


@dispatch(object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _close_port(instrument, backend_tag):
    """Close port for minimalmodbus.

    Closes the serial port explicitly to ensure cleanup.

    Note: With close_port_after_each_call=True, minimalmodbus
    automatically closes the port after each transaction, so this
    is primarily defensive cleanup to handle edge cases.

    Parameters
    ----------
    instrument : Instrument
        The minimalmodbus Instrument instance
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch
    """
    if instrument and hasattr(instrument, 'serial') and instrument.serial:
        try:
            if instrument.serial.is_open:
                instrument.serial.close()
                logger.debug(f"Closed port {instrument.serial.port}")
        except Exception as e:
            logger.warning(f"Failed to close port: {e}")

# ============================================================================
# Bit Operations
# ============================================================================

@dispatch(object, object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _read_bit(
    instrument: Instrument,
    address: int,
    functioncode: int,
    backend_tag: MinimalmodbusBackendTag
) -> int:
    """Read one bit from the slave.

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance for Modbus communication
    address : int
        Bit register address
    functioncode : int
        Modbus function code (1 or 2)
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Returns
    -------
    int
        Bit value (0 or 1)

    Raises
    ------
    IOError
        If communication with the Modbus device fails
    """
    return instrument.read_bit(registeraddress=address, functioncode=functioncode)


@dispatch(object, object, object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _write_bit(
    instrument: Instrument,
    address: int,
    value: int,
    functioncode: int,
    backend_tag: MinimalmodbusBackendTag
) -> None:
    """Write one bit to the slave.

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance for Modbus communication
    address : int
        Bit register address
    value : int
        Value to write (0 or 1)
    functioncode : int
        Modbus function code (5 or 15)
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Raises
    ------
    IOError
        If communication with the Modbus device fails
    """
    instrument.write_bit(registeraddress=address, value=value, functioncode=functioncode)


@dispatch(object, object, object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _read_bits(
    instrument: Instrument,
    address: int,
    number_of_bits: int,
    functioncode: int,
    backend_tag: MinimalmodbusBackendTag
) -> List[int]:
    """Read multiple bits from the slave.

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance for Modbus communication
    address : int
        Starting bit register address
    number_of_bits : int
        Number of bits to read
    functioncode : int
        Modbus function code (1 or 2)
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Returns
    -------
    List[int]
        List of bit values (0 or 1)

    Raises
    ------
    IOError
        If communication with the Modbus device fails
    """
    return instrument.read_bits(
        registeraddress=address,
        number_of_bits=number_of_bits,
        functioncode=functioncode
    )


@dispatch(object, object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _write_bits(
    instrument: Instrument,
    address: int,
    values: List[int],
    backend_tag: MinimalmodbusBackendTag
) -> None:
    """Write multiple bits to the slave.

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance for Modbus communication
    address : int
        Starting bit register address
    values : List[int]
        List of values to write (0 or 1)
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Raises
    ------
    IOError
        If communication with the Modbus device fails
    """
    instrument.write_bits(registeraddress=address, values=values)


# ============================================================================
# Register Operations (16-bit)
# ============================================================================

@dispatch(object, object, object, object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _read_register(
    instrument: Instrument,
    address: int,
    number_of_decimals: int,
    functioncode: int,
    signed: bool,
    backend_tag: MinimalmodbusBackendTag
) -> Union[int, float]:
    """Read a 16-bit integer from a single register.

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance for Modbus communication
    address : int
        Register address (0-based)
    number_of_decimals : int
        Number of decimal places for scaling (0 for no scaling)
    functioncode : int
        Modbus function code (3 or 4)
    signed : bool
        Whether to interpret as signed integer
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Returns
    -------
    int or float
        The register value (int if number_of_decimals=0, else float)

    Raises
    ------
    IOError
        If communication with the Modbus device fails

    Examples
    --------
    >>> # Read unsigned integer
    >>> value = _read_register(instrument, 256, 0, 3, False, backend)
    >>> print(f"CO2: {value} ppm")

    >>> # Read with decimal scaling
    >>> value = _read_register(instrument, 100, 1, 3, False, backend)
    >>> print(f"Temperature: {value} °C")  # Divides by 10
    """
    return instrument.read_register(
        registeraddress=address,
        number_of_decimals=number_of_decimals,
        functioncode=functioncode,
        signed=signed
    )


@dispatch(object, object, object, object, object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _write_register(
    instrument: Instrument,
    address: int,
    value: Union[int, float],
    number_of_decimals: int,
    functioncode: int,
    signed: bool,
    backend_tag: MinimalmodbusBackendTag
) -> None:
    """Write a 16-bit integer to a single register.

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance for Modbus communication
    address : int
        Register address (0-based)
    value : int or float
        Value to write
    number_of_decimals : int
        Number of decimal places for scaling (0 for no scaling)
    functioncode : int
        Modbus function code (6 or 16)
    signed : bool
        Whether to interpret as signed integer
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Raises
    ------
    IOError
        If communication with the Modbus device fails
    """
    instrument.write_register(
        registeraddress=address,
        value=value,
        number_of_decimals=number_of_decimals,
        functioncode=functioncode,
        signed=signed
    )


@dispatch(object, object, object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _read_registers(
    instrument: Instrument,
    address: int,
    number_of_registers: int,
    functioncode: int,
    backend_tag: MinimalmodbusBackendTag
) -> List[int]:
    """Read multiple 16-bit integers from consecutive registers.

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance for Modbus communication
    address : int
        Starting register address (0-based)
    number_of_registers : int
        Number of registers to read (max 125)
    functioncode : int
        Modbus function code (3 or 4)
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Returns
    -------
    List[int]
        List of register values

    Raises
    ------
    IOError
        If communication with the Modbus device fails
    """
    return instrument.read_registers(
        registeraddress=address,
        number_of_registers=number_of_registers,
        functioncode=functioncode
    )


@dispatch(object, object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _write_registers(
    instrument: Instrument,
    address: int,
    values: List[int],
    backend_tag: MinimalmodbusBackendTag
) -> None:
    """Write multiple 16-bit integers to consecutive registers.

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance for Modbus communication
    address : int
        Starting register address (0-based)
    values : List[int]
        List of values to write (max 123)
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Raises
    ------
    IOError
        If communication with the Modbus device fails
    """
    instrument.write_registers(registeraddress=address, values=values)


# ============================================================================
# Long Integer Operations (32/64-bit)
# ============================================================================

@dispatch(object, object, object, object, object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _read_long(
    instrument: Instrument,
    address: int,
    functioncode: int,
    signed: bool,
    byteorder: Byteorder,
    number_of_registers: int,
    backend_tag: MinimalmodbusBackendTag
) -> int:
    """Read a 32-bit or 64-bit integer from consecutive registers.

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance for Modbus communication
    address : int
        Starting register address (0-based)
    functioncode : int
        Modbus function code (3 or 4)
    signed : bool
        Whether to interpret as signed integer
    byteorder : Byteorder
        Byte order for reading the long value
    number_of_registers : int
        Number of registers (2 for 32-bit, 4 for 64-bit)
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Returns
    -------
    int
        The 32-bit or 64-bit integer value

    Raises
    ------
    IOError
        If communication with the Modbus device fails

    Examples
    --------
    >>> # Read 32-bit unsigned integer
    >>> value = _read_long(instrument, 100, 3, False, Byteorder.ABCD, 2, backend)
    >>> print(f"Counter: {value}")

    >>> # Read 64-bit signed integer
    >>> value = _read_long(instrument, 200, 3, True, Byteorder.CDAB, 4, backend)
    """
    mb_byteorder = _get_byteorder(byteorder, backend_tag)
    return instrument.read_long(
        registeraddress=address,
        functioncode=functioncode,
        signed=signed,
        byteorder=mb_byteorder,
        number_of_registers=number_of_registers
    )


@dispatch(object, object, object, object, object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _write_long(
    instrument: Instrument,
    address: int,
    value: int,
    signed: bool,
    byteorder: Byteorder,
    number_of_registers: int,
    backend_tag: MinimalmodbusBackendTag
) -> None:
    """Write a 32-bit or 64-bit integer to consecutive registers.

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance for Modbus communication
    address : int
        Starting register address (0-based)
    value : int
        Value to write
    signed : bool
        Whether to interpret as signed integer
    byteorder : Byteorder
        Byte order for writing the long value
    number_of_registers : int
        Number of registers (2 for 32-bit, 4 for 64-bit)
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Raises
    ------
    IOError
        If communication with the Modbus device fails
    """
    mb_byteorder = _get_byteorder(byteorder, backend_tag)
    instrument.write_long(
        registeraddress=address,
        value=value,
        signed=signed,
        byteorder=mb_byteorder,
        number_of_registers=number_of_registers
    )


# ============================================================================
# Float Operations (32/64-bit)
# ============================================================================

@dispatch(object, object, object, object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _read_float(
    instrument: Instrument,
    address: int,
    functioncode: int,
    number_of_registers: int,
    byteorder: Byteorder,
    backend_tag: MinimalmodbusBackendTag
) -> float:
    """Read a floating point number from consecutive registers.

    This function reads a floating point value from the Modbus device
    using the minimalmodbus library with the specified byte order.

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance for Modbus communication
    address : int
        Starting register address (0-based)
    functioncode : int
        Modbus function code (3 or 4)
    number_of_registers : int
        Number of registers (2 for 32-bit float, 4 for 64-bit double)
    byteorder : Byteorder
        Byte order for reading the float value
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Returns
    -------
    float
        The floating point value read from the registers

    Raises
    ------
    IOError
        If communication with the Modbus device fails

    Examples
    --------
    >>> # Read 32-bit float (single precision)
    >>> value = _read_float(instrument, 0, 3, 2, Byteorder.CDAB, backend)
    >>> print(f"CO2: {value} ppm")

    >>> # Read 64-bit double (double precision)
    >>> value = _read_float(instrument, 10, 3, 4, Byteorder.ABCD, backend)
    >>> print(f"Precise value: {value}")

    Notes
    -----
    The function automatically converts the generic Byteorder enum to
    the minimalmodbus-specific byte order constant before reading.

    For single precision (32-bit), use number_of_registers=2
    For double precision (64-bit), use number_of_registers=4
    """
    mb_byteorder = _get_byteorder(byteorder, backend_tag)
    return instrument.read_float(
        registeraddress=address,
        functioncode=functioncode,
        number_of_registers=number_of_registers,
        byteorder=mb_byteorder
    )


@dispatch(object, object, object, object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _write_float(
    instrument: Instrument,
    address: int,
    value: Union[int, float],
    number_of_registers: int,
    byteorder: Byteorder,
    backend_tag: MinimalmodbusBackendTag
) -> None:
    """Write a floating point number to consecutive registers.

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance for Modbus communication
    address : int
        Starting register address (0-based)
    value : float or int
        Value to write
    number_of_registers : int
        Number of registers (2 for 32-bit float, 4 for 64-bit double)
    byteorder : Byteorder
        Byte order for writing the float value
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Raises
    ------
    IOError
        If communication with the Modbus device fails
    """
    mb_byteorder = _get_byteorder(byteorder, backend_tag)
    instrument.write_float(
        registeraddress=address,
        value=value,
        number_of_registers=number_of_registers,
        byteorder=mb_byteorder
    )


# ============================================================================
# String Operations
# ============================================================================

@dispatch(object, object, object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _read_string(
    instrument: Instrument,
    address: int,
    number_of_registers: int,
    functioncode: int,
    backend_tag: MinimalmodbusBackendTag
) -> str:
    """Read an ASCII string from consecutive registers.

    Each 16-bit register holds 2 ASCII characters (2 bytes).

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance for Modbus communication
    address : int
        Starting register address (0-based)
    number_of_registers : int
        Number of registers to read
    functioncode : int
        Modbus function code (3 or 4)
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Returns
    -------
    str
        The ASCII string read from the registers

    Raises
    ------
    IOError
        If communication with the Modbus device fails

    Examples
    --------
    >>> # Read 16 registers = 32 characters
    >>> serial = _read_string(instrument, 500, 16, 3, backend)
    >>> print(f"Serial: {serial}")

    Notes
    -----
    Each register (16 bits) holds 2 ASCII characters.
    To read N characters, use number_of_registers = N/2 (rounded up).
    """
    return instrument.read_string(
        registeraddress=address,
        number_of_registers=number_of_registers,
        functioncode=functioncode
    )


@dispatch(object, object, object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _write_string(
    instrument: Instrument,
    address: int,
    textstring: str,
    number_of_registers: int,
    backend_tag: MinimalmodbusBackendTag
) -> None:
    """Write an ASCII string to consecutive registers.

    Each 16-bit register holds 2 ASCII characters (2 bytes).
    Shorter strings are padded with spaces.

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance for Modbus communication
    address : int
        Starting register address (0-based)
    textstring : str
        ASCII string to write (max 2*number_of_registers characters)
    number_of_registers : int
        Number of registers allocated for the string
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Raises
    ------
    IOError
        If communication with the Modbus device fails
    ValueError
        If textstring is too long for the allocated registers
    """
    instrument.write_string(
        registeraddress=address,
        textstring=textstring,
        number_of_registers=number_of_registers
    )


# ============================================================================
# Simplified Convenience Functions (commonly used signatures)
# ============================================================================

@dispatch(object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _read_register_simple(
    instrument: Instrument,
    address: int,
    backend_tag: MinimalmodbusBackendTag
) -> int:
    """Read a 16-bit unsigned integer with default parameters.

    Convenience function for common case: unsigned, no decimals, function code 3.

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance
    address : int
        Register address
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Returns
    -------
    int
        The register value
    """
    return instrument.read_register(
        registeraddress=address,
        number_of_decimals=0,
        functioncode=3,
        signed=False
    )


@dispatch(object, object, object, object, MinimalmodbusBackendTag, namespace=modbusbackend_namespace)
def _read_float_simple(
    instrument: Instrument,
    address: int,
    byteorder: Byteorder,
    backend_tag: MinimalmodbusBackendTag
) -> float:
    """Read a 32-bit float with default parameters.

    Convenience function for common case: 32-bit float, function code 3.

    Parameters
    ----------
    instrument : Instrument
        Minimalmodbus Instrument instance
    address : int
        Starting register address
    byteorder : Byteorder
        Byte order for reading
    backend_tag : MinimalmodbusBackendTag
        Backend tag for dispatch

    Returns
    -------
    float
        The float value
    """
    mb_byteorder = _get_byteorder(byteorder, backend_tag)
    return instrument.read_float(
        registeraddress=address,
        functioncode=3,
        number_of_registers=2,
        byteorder=mb_byteorder
    )

