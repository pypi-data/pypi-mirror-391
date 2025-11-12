import time
from typing import List, Union, Any, Set
from enum import Enum
from contextlib import contextmanager
import logging
logger = logging.getLogger(__name__)

from .read_tag.read_tag import ReadTag

class SensorReadError(Exception):
    """Exception raised when sensor read operation fails.

    Attributes
    ----------
    tag : ReadTag
        The tag that failed to read.
    original_exception : Exception
        The underlying exception that caused the failure.
    """
    def __init__(self, tag: ReadTag, original_exception: Exception):
        self.tag = tag
        self.original_exception = original_exception
        super().__init__(
            f"Failed to read {type(tag).__name__}: {original_exception}"
        )


class Instrument:
    pass


class ModbusBackendTag:
    pass


modbusbackend_namespace = {}


class ModbusMode(Enum):
    RTU = 1
    ASCII = 2


class Byteorder(Enum):
    ABCD = 1
    BADC = 2
    CDAB = 3
    DCBA = 4


class Parity(Enum):
    NONE = 1
    EVEN = 2
    ODD = 3
    MARK = 4
    SPACE = 5


class Stopbits(Enum):
    ONE = 1
    ONE_POINT_FIVE = 1.5
    TWO = 2


class Sensor:
    """Generic sensor instrument configured with valid tags and namespace.

    The Sensor class provides a base for all sensor implementations,
    handling Modbus RTU communication, tag validation, and dispatch to
    sensor-specific read functions.

    **Key Feature**: Instruments are created on-demand during read/write operations
    and immediately cleaned up afterward. This prevents serial port conflicts when
    multiple sensors share the same physical port.

    Parameters
    ----------
    port : str
        Serial port name (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux).
    valid_tags : List[ReadTag]
        List of ReadTag instances that are valid for this sensor.
    namespace : dict
        Dispatch namespace dictionary containing the multipledispatch Dispatcher
        for this sensor's tag-specific read functions.
    serial_config_tags : Set[ReadTag], optional
        Set of tags that configure serial communication (require power cycle).
    sensor_config_tags : Set[ReadTag], optional
        Set of tags that configure sensor behavior (may require power cycle).
    backend_tag : ModbusBackendTag, optional
        Backend tag for dispatch (default: MinimalmodbusBackendTag).
    slave_address : int, optional
        Modbus slave address (default: 1).
    baudrate : int, optional
        Serial baudrate (default: 19200).
    stopbits : Stopbits, optional
        Number of stop bits (default: Stopbits.ONE).
    bytesize : int, optional
        Number of data bits (default: 8).
    parity : Parity, optional
        Parity setting (default: Parity.NONE).
    modbus_mode : ModbusMode, optional
        Modbus mode (default: ModbusMode.RTU).
    timeout : float, optional
        Serial timeout in seconds (default: 0.5).

    Attributes
    ----------
    serial_config_tags : Set[ReadTag]
        Tags that configure serial communication settings.
    sensor_config_tags : Set[ReadTag]
        Tags that configure sensor behavior settings.

    Notes
    -----
    **Instrument Lifecycle**:

    Unlike traditional implementations where the instrument is created once
    in __init__ and persists, this implementation creates the instrument
    on-demand for each read/write operation:

    1. User calls read() or write()
    2. Instrument is created and configured with correct serial settings
    3. Operation is performed
    4. Instrument is cleaned up and serial port is closed
    5. Port is now available for other sensors

    This design allows multiple sensors to share the same serial port
    without conflicts, even if they have different baudrate/stopbit settings.

    **Performance Impact**:

    Creating/destroying the instrument adds ~50-100ms overhead per operation.
    For typical sensor logging intervals (>1s), this is negligible.

    Examples
    --------
    Multiple sensors on the same port (no conflicts!):

    >>> sensor1 = GMP252(port='/dev/ttyACM0', slave_address=121)
    >>> sensor2 = AlphaTRACER(port='/dev/ttyACM0', slave_address=122, baudrate=9600)
    >>>
    >>> # Both work perfectly - no serial port conflicts
    >>> result1 = sensor1.read([CO2])  # Creates instrument, reads, cleans up
    >>> result2 = sensor2.read([RADON])  # Creates instrument, reads, cleans up

    Use with scheduler (original API unchanged):

    >>> logger1 = SensorLogger(sensor=sensor1, tags=[CO2], interval_seconds=10, ...)
    >>> logger2 = SensorLogger(sensor=sensor2, tags=[RADON], interval_seconds=600, ...)
    >>>
    >>> scheduler = LoggerScheduler()
    >>> scheduler.add_logger(logger1)
    >>> scheduler.add_logger(logger2)
    >>> scheduler.run()  # Just works!
    """

    def __init__(
        self,
        port: str,
        valid_tags: List[ReadTag],
        namespace: dict,
        slave_address: int,
        baudrate: int,
        stopbits: Stopbits,
        bytesize: int,
        parity: Parity,
        modbus_mode: ModbusMode,
        timeout: float,
        serial_config_tags: Set[ReadTag] = None,
        sensor_config_tags: Set[ReadTag] = None,
        backend_tag: ModbusBackendTag | None = None,
    ):
        """Initialize sensor configuration without creating instrument.

        The instrument will be created on-demand during read/write operations.
        """
        # Store configuration for later instrument creation
        self._port = port
        self._slave_address = slave_address
        self._baudrate = baudrate
        self._stopbits = stopbits
        self._bytesize = bytesize
        self._parity = parity
        self._modbus_mode = modbus_mode
        self._timeout = timeout

        # Store sensor metadata
        self._valid_tags = valid_tags
        self._namespace = namespace
        self.serial_config_tags = serial_config_tags if serial_config_tags else set()
        self.sensor_config_tags = sensor_config_tags if sensor_config_tags else set()

        if backend_tag is None:
            backend_tag = self._default_backend_tag()
        self._backend_tag = backend_tag

        with self._get_instrument() as instrument:
            print("created instrument")


    def _create_instrument(self) -> Instrument:
        """Create and configure a new instrument instance.

        This method is called internally before each read/write operation.
        The instrument is configured with the serial settings provided during
        initialization.

        Returns
        -------
        Instrument
            Configured minimalmodbus Instrument instance.

        Notes
        -----
        The instrument's serial port will have close_port_after_each_call=True
        set by _setup_instrument, ensuring the port is released after each
        Modbus transaction.
        """
        _create_instrument = modbusbackend_namespace["_create_instrument"]
        instrument = _create_instrument(self._port, self._slave_address, self._backend_tag)

        _setup_instrument = modbusbackend_namespace["_setup_instrument"]
        _setup_instrument(
            instrument,
            self._baudrate,
            self._stopbits,
            self._bytesize,
            self._parity,
            self._modbus_mode,
            self._timeout,
            self._backend_tag
        )

        return instrument

    @contextmanager
    def _get_instrument(self):
        """Context manager for instrument lifecycle.

        Handles port management via backend-specific open/close functions.
        For backends with automatic port management (like minimalmodbus with
        close_port_after_each_call=True), these are no-ops. For backends
        requiring manual management, they're essential.
        """
        instrument = self._create_instrument()

        # Backend-specific port opening
        _open_port = modbusbackend_namespace.get('_open_port')
        if _open_port is not None:
            _open_port(instrument, self._backend_tag)

        try:
            yield instrument
        finally:
            # Backend-specific port closing (always runs)
            _close_port = modbusbackend_namespace.get('_close_port')
            if _close_port is not None:
                try:
                    _close_port(instrument, self._backend_tag)
                except Exception as e:
                    logger.warning(f"Failed to close port: {e}")

    def _cleanup_instrument(self, instrument: Instrument) -> None:
        """Clean up and close the instrument's serial port.

        This method is called internally after each read/write operation
        to ensure the serial port is properly closed and resources are freed.
        Uses backend dispatch to maintain abstraction.

        Parameters
        ----------
        instrument : Instrument
            The instrument instance to clean up.

        Notes
        -----
        Dispatches to the backend's cleanup function to maintain proper
        abstraction and avoid coupling to specific backend implementations.
        """
        if instrument is not None:
            _cleanup_instrument = modbusbackend_namespace.get('_cleanup_instrument')
            if _cleanup_instrument is not None:
                try:
                    _cleanup_instrument(instrument, self._backend_tag)
                except Exception as e:
                    logger.warning(f"Failed to cleanup instrument: {e}")
        del instrument


    def _open_port(self, instrument: Instrument) -> None:
        """Clean up and close the instrument's serial port.

        This method is called internally after each read/write operation
        to ensure the serial port is properly closed and resources are freed.
        Uses backend dispatch to maintain abstraction.

        Parameters
        ----------
        instrument : Instrument
            The instrument instance to clean up.

        Notes
        -----
        Dispatches to the backend's cleanup function to maintain proper
        abstraction and avoid coupling to specific backend implementations.
        """
        if instrument is not None:
            _open_port = modbusbackend_namespace.get('_open_port')
            if _open_port is not None:
                try:
                    _open_port(instrument, self._backend_tag)
                except Exception as e:
                    logger.warning(f"Failed to cleanup instrument: {e}")

    def _close_port(self, instrument: Instrument) -> None:
        """Clean up and close the instrument's serial port.

        This method is called internally after each read/write operation
        to ensure the serial port is properly closed and resources are freed.
        Uses backend dispatch to maintain abstraction.

        Parameters
        ----------
        instrument : Instrument
            The instrument instance to clean up.

        Notes
        -----
        Dispatches to the backend's cleanup function to maintain proper
        abstraction and avoid coupling to specific backend implementations.
        """
        if instrument is not None:
            _close_port = modbusbackend_namespace.get('_close_port')
            if _close_port is not None:
                try:
                    _close_port(instrument, self._backend_tag)
                except Exception as e:
                    logger.warning(f"Failed to close port: {e}")


    def write(self, settings: dict[ReadTag, Any]) -> None:
        """Write one or more settings using tag dispatch.

        Creates an instrument, performs the write operations, then cleans up.
        The serial port is only held during the actual write operation.

        Parameters
        ----------
        settings : dict[ReadTag, Any]
            Dictionary mapping tag instances to values to write.

        Raises
        ------
        ValueError
            If any tag is not valid for writing.

        Warnings
        --------
        If writing serial configuration tags, a power cycle is required.
        Use get_serial_config_tags() to see which tags require power cycle.

        Examples
        --------
        >>> from atmospyre.sensors.implementations.gmp252 import (
        ...     PRESSURE_COMPENSATION_MODE, CO2_FILTERING_FACTOR
        ... )
        >>> sensor.write({
        ...     PRESSURE_COMPENSATION_MODE: True,
        ...     CO2_FILTERING_FACTOR: 90
        ... })
        >>> # If any serial_config_tags were written, power cycle the sensor

        Multiple sensors on same port (no conflicts):

        >>> sensor1.write({TAG1: value1})  # Creates instrument, writes, cleans up
        >>> sensor2.write({TAG2: value2})  # Creates instrument, writes, cleans up
        """
        # Create instrument for this operation
        with self._get_instrument() as instrument:

            try:
                _write = self._namespace['_write']

                # Check if any serial config tags are being written
                serial_tags_written = [tag for tag in settings.keys() if tag in self.serial_config_tags]

                for tag, value in settings.items():
                    try:
                        _write(instrument, tag, value, self._backend_tag)
                        time.sleep(1)
                    except Exception as e:
                        logger.error(f"Failed to write {type(tag).__name__}: {e}", exc_info=True)
                        raise

                # Warn user if serial config was changed
                if serial_tags_written:
                    logger.warning(
                        f"Serial configuration tags written: {[type(t).__name__ for t in serial_tags_written]}. "
                        "Power cycle required for changes to take effect."
                    )
                    print("\n⚠️  WARNING: Serial configuration changed!")
                    print("Power cycle the sensor to apply changes.")
                    print(f"Tags written: {', '.join([type(t).__name__ for t in serial_tags_written])}\n")

            finally:
                # Always cleanup, even if an error occurred
                self._cleanup_instrument(instrument)

    def read(self, tags: Union[ReadTag, List[ReadTag]]) -> dict[ReadTag, Any]:
        """Read one or more measurements using tag dispatch.

        Creates an instrument, performs the read operations, then cleans up.
        The serial port is only held during the actual read operation.

        Parameters
        ----------
        tags : ReadTag or List[ReadTag]
            Single ReadTag instance or list of ReadTag instances to read.
            All tags must be in the sensor's valid tag list.

        Returns
        -------
        dict[ReadTag, Any]
            Dictionary mapping each input tag to its measured value.

        Raises
        ------
        ValueError
            If any tag is not in the sensor's valid tag list.
        SensorReadError
            If reading any tag fails due to communication errors.
            The exception contains the failed tag and original error.

        Examples
        --------
        Single tag read:

        >>> result = sensor.read(CO2)
        >>> print(result[CO2])
        415.2

        Multiple tags:

        >>> result = sensor.read([CO2, MEASURED_TEMPERATURE])
        >>> print(f"CO2: {result[CO2]}, Temp: {result[MEASURED_TEMPERATURE]}")
        CO2: 415.2, Temp: 23.5

        Error handling:

        >>> try:
        ...     result = sensor.read([CO2, MEASURED_TEMPERATURE])
        ... except SensorReadError as e:
        ...     print(f"Failed to read {type(e.tag).__name__}")
        ...     print(f"Reason: {e.original_exception}")

        Multiple sensors on same port:

        >>> sensor1 = GMP252(port='/dev/ttyACM0', slave_address=121)
        >>> sensor2 = AlphaTRACER(port='/dev/ttyACM0', slave_address=122)
        >>> result1 = sensor1.read([CO2])    # No conflict!
        >>> result2 = sensor2.read([RADON])  # No conflict!
        """
        # Normalize input to list
        if isinstance(tags, ReadTag):
            tags = [tags]

        # Validate all tags upfront (before creating instrument)
        for tag in tags:
            if tag not in self._valid_tags:
                raise ValueError(
                    f"Tag {type(tag).__name__} not valid for this sensor. "
                    f"Valid tags: {[type(t).__name__ for t in self._valid_tags]}"
                )

        # Create instrument for this operation
        with self._get_instrument() as instrument:

            try:
                # Get the dispatchers registered at the sensor's namespace
                _read = self._namespace['_read']

                results = {}
                for tag in tags:
                    try:
                        value = _read(instrument, tag, self._backend_tag)
                        results[tag] = value

                    except Exception as e:
                        logger.error(
                            f"Failed to read {type(tag).__name__}: {e}",
                            exc_info=True
                        )
                        raise SensorReadError(tag, e) from e

                return results

            finally:
                # Always cleanup, even if an error occurred
                self._cleanup_instrument(instrument)

    def get_valid_tags(self) -> List[ReadTag]:
        """Get list of all valid tags for this sensor.

        Returns a copy of the valid tags list to prevent external modification.

        Returns
        -------
        List[ReadTag]
            Copy of the list of valid ReadTag instances for this sensor.

        Examples
        --------
        >>> tags = sensor.get_valid_tags()
        >>> print(f"This sensor supports {len(tags)} measurements")
        This sensor supports 5 measurements
        >>>
        >>> for tag in tags:
        ...     meta = tag.metadata
        ...     print(f"- {type(tag).__name__}: {meta.description} ({meta.unit})")
        - CO2Tag: CO2 concentration (float) (ppm)
        - TemperatureTag: Measurement temperature (°C)
        - StatusTag: General device status (None)
        """
        return self._valid_tags.copy()

    def get_serial_config_tags(self) -> Set[ReadTag]:
        """Get set of tags that configure serial communication.

        Writing to these tags requires a power cycle for changes to take effect.

        Returns
        -------
        Set[ReadTag]
            Set of tags that configure serial communication (Modbus address,
            baudrate, parity, stop bits, etc.)

        Examples
        --------
        >>> serial_tags = sensor.get_serial_config_tags()
        >>> for tag in serial_tags:
        ...     print(f"- {type(tag).__name__}: {tag.metadata.description}")
        - ModbusAddressTag: Modbus address (1-247)
        - SerialSpeedTag: Serial speed (0=4800, 1=9600, ...)
        - SerialParityTag: Serial parity (0=None, 1=Even, 2=Odd)
        - SerialStopBitsTag: Serial stop bits (1-2)
        """
        return self.serial_config_tags.copy()

    def get_sensor_config_tags(self) -> Set[ReadTag]:
        """Get set of tags that configure sensor behavior.

        These tags configure sensor-specific settings like compensation modes,
        filtering factors, etc. Some may require power cycle - check documentation.

        Returns
        -------
        Set[ReadTag]
            Set of tags that configure sensor behavior

        Examples
        --------
        >>> config_tags = sensor.get_sensor_config_tags()
        >>> for tag in config_tags:
        ...     print(f"- {type(tag).__name__}: {tag.metadata.description}")
        - PressureCompensationModeTag: Pressure compensation mode
        - CO2FilteringFactorTag: CO2 filtering factor (0-100)
        """
        return self.sensor_config_tags.copy()

    def _default_backend_tag(self):
        """Get the default Modbus backend tag."""
        from atmospyre.sensors.backends.minimalmodbus import MinimalmodbusBackendTag
        return MinimalmodbusBackendTag()

    def __repr__(self) -> str:
        """Return string representation of the sensor.

        Returns
        -------
        str
            Human-readable representation showing sensor type and configuration.

        Examples
        --------
        >>> sensor = GMP252(port='/dev/ttyACM0', slave_address=121)
        >>> print(sensor)
        GMP252(port='/dev/ttyACM0', address=121, baudrate=19200)
        """
        return (
            f"{self.__class__.__name__}("
            f"port='{self._port}', "
            f"address={self._slave_address}, "
            f"baudrate={self._baudrate})"
        )