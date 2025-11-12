from dataclasses import dataclass
from typing import Optional, Any


class ExtractorStrategy:
    pass


class PrinterStrategy:
    pass


@dataclass
class ReadTagMetadata:
    """Metadata container for sensor measurement tags.

    ReadTagMetadata stores all metadata associated with a sensor measurement,
    including physical properties (unit, valid range), documentation (description),
    and behavioral properties (minimum read interval, precision). It uses the
    Strategy pattern to allow pluggable extraction and printing behavior.

    Parameters
    ----------
    unit : str, optional
        Measurement unit (e.g., "ppm", "°C", "Bq/m³"). Used for display
        and validation. Default is None.
    source : str, optional
        Data source identifier or register address information
        (e.g., "Modbus Register 0-1 (float32)"). Default is None.
    min_interval : float, optional
        Minimum time interval in seconds between consecutive reads of this
        measurement. Used to prevent over-polling sensors. Default is None.
    description : str, optional
        Human-readable description of the measurement
        (e.g., "CO2 concentration (float)"). Default is None.
    precision : int, optional
        Number of decimal places for the measurement. Used for formatting
        output. Default is None.
    valid_range : tuple[float, float], optional
        Valid measurement range as (min, max) tuple. Values outside this
        range may indicate sensor errors. Default is None.
    extractor : ExtractorStrategy, optional
        Strategy object for serializing this metadata to a string or other
        format. Default is None.
    printer : PrinterStrategy, optional
        Strategy object for formatting this metadata for human-readable display.
        Default is None.

    Attributes
    ----------
    unit : str or None
        Measurement unit string.
    source : str or None
        Data source identifier.
    min_interval : float or None
        Minimum read interval in seconds.
    description : str or None
        Measurement description.
    precision : int or None
        Measurement precision (decimal places).
    valid_range : tuple[float, float] or None
        Valid measurement range.
    extractor : ExtractorStrategy or None
        Serialization strategy instance.
    printer : PrinterStrategy or None
        Display formatting strategy instance.

    Raises
    ------
    ValueError
        If extract() or print() is called without a corresponding strategy set.

    Examples
    --------
    Create metadata for CO2 measurement:

    >>> from atmospyre.sensors.read_tag import ReadTagMetadata
    >>> co2_metadata = ReadTagMetadata(
    ...     unit="ppm",
    ...     description="CO2 concentration (float)",
    ...     precision=1,
    ...     source="Modbus Register 0-1 (float32)",
    ...     valid_range=(0.0, 10000.0)
    ... )
    >>> print(co2_metadata.unit)
    ppm
    >>> print(co2_metadata.precision)
    1

    Create metadata for temperature measurement:

    >>> temp_metadata = ReadTagMetadata(
    ...     unit="°C",
    ...     description="Measurement temperature",
    ...     precision=2,
    ...     source="Modbus Register 4-5 (float32)",
    ...     valid_range=(-40.0, 60.0)
    ... )

    Convert metadata to dictionary:

    >>> co2_dict = co2_metadata.to_dict()
    >>> print(co2_dict["unit"])
    ppm
    >>> print(co2_dict["precision"])
    1

    Use with extraction strategy:

    >>> from atmospyre.sensors.read_tag.strategies.extractors import JSONExtractor
    >>> co2_metadata.extractor = JSONExtractor()
    >>> json_str = co2_metadata.extract()
    >>> print(json_str)
    {
      "unit": "ppm",
      "description": "CO2 concentration (float)",
      "precision": 1,
      ...
    }

    Use with printer strategy:

    >>> from atmospyre.sensors.read_tag.strategies.printes import DefaultPrinterStrategy
    >>> co2_metadata.printer = DefaultPrinterStrategy()
    >>> print(co2_metadata.print())
    Description: CO2 concentration (float)
    Unit: ppm
    Precision: 1
    ...

    Use in tag definition (real GMP252 example):

    >>> from atmospyre.sensors.read_tag import ReadTag
    >>>
    >>> class CO2Tag(ReadTag):
    ...     pass
    >>>
    >>> CO2 = CO2Tag(ReadTagMetadata(
    ...     unit="ppm",
    ...     description="CO2 concentration (float)",
    ...     precision=1,
    ...     source="Modbus Register 0-1 (float32)",
    ...     valid_range=(0.0, 10000.0)
    ... ))

    Notes
    -----
    The Strategy pattern allows different serialization and display formats
    to be plugged in without modifying the core metadata class. This is
    particularly useful when different output formats are needed for different
    contexts (e.g., JSON for APIs, formatted text for documentation).

    All fields are optional to allow flexibility in metadata specification.
    However, at minimum, ``unit`` and ``description`` are recommended for
    clarity and usability.
    """

    # Basic metadata
    unit: Optional[str] = None
    source: Optional[str] = None
    min_interval: Optional[float] = None
    description: Optional[str] = None
    precision: Optional[int] = None
    valid_range: Optional[tuple[float, float]] = None

    # Strategy pattern components
    extractor: Optional[ExtractorStrategy] = None
    printer: Optional[PrinterStrategy] = None

    def to_dict(self, include_none: bool = False) -> dict[str, Any]:
        """Convert metadata to dictionary for serialization.

        Returns a dictionary containing all metadata fields, excluding
        strategy objects (extractor, printer). By default, fields with
        None values are excluded from the output.

        Parameters
        ----------
        include_none : bool, optional
            If True, include fields with None values in the output.
            Default is False.

        Returns
        -------
        dict[str, Any]
            Dictionary containing metadata fields. Tuples (like valid_range)
            are automatically converted to lists for JSON compatibility.

        Examples
        --------
        Basic usage with CO2 metadata:

        >>> from atmospyre.sensors.implementations.co2.vaisala.gmp252 import CO2
        >>> metadata_dict = CO2.metadata.to_dict()
        >>> print(metadata_dict["unit"])
        ppm
        >>> print(metadata_dict["precision"])
        1

        Exclude None values (default):

        >>> from atmospyre.sensors.implementations.co2.vaisala.gmp252 import STATUS
        >>> status_dict = STATUS.metadata.to_dict()
        >>> print("unit" in status_dict)
        False

        Include None values:

        >>> status_dict_full = STATUS.metadata.to_dict(include_none=True)
        >>> print("unit" in status_dict_full)
        True
        >>> print(status_dict_full["unit"])
        None
        """
        # Define data fields to include (exclude strategy objects)
        data_fields = ['unit', 'source', 'min_interval', 'description', 'precision', 'valid_range']

        result = {}
        for field in data_fields:
            value = getattr(self, field)

            # Skip None values unless explicitly requested
            if value is None and not include_none:
                continue

            # Convert tuples to lists for JSON compatibility
            if isinstance(value, tuple):
                value = list(value)

            result[field] = value

        return result

    def extract(self) -> Any:
        """Extract/serialize metadata using the configured strategy.

        Delegates to the extractor strategy to serialize this metadata
        object into a desired format (e.g., JSON string, CSV row, XML).

        Returns
        -------
        Any
            Serialized metadata. The exact type and format depend on the
            configured ExtractorStrategy. Common return types include str,
            dict, or bytes.

        Raises
        ------
        ValueError
            If no extraction strategy is defined (extractor is None).

        Examples
        --------
        Extract CO2 metadata as JSON:

        >>> from atmospyre.sensors.implementations.co2.vaisala.gmp252 import CO2
        >>> from atmospyre.sensors.read_tag.strategies.extractors import JSONExtractor
        >>> CO2.metadata.extractor = JSONExtractor()
        >>> json_string = CO2.metadata.extract()
        >>> print(json_string)
        {
          "unit": "ppm",
          "description": "CO2 concentration (float)",
          "precision": 1,
          ...
        }

        Parse the extracted JSON:

        >>> import json
        >>> data = json.loads(json_string)
        >>> print(data["unit"])
        ppm

        Extract multiple tags:

        >>> from atmospyre.sensors.implementations.co2.vaisala.gmp252 import TEMPERATURE
        >>> TEMPERATURE.metadata.extractor = JSONExtractor()
        >>> temp_json = TEMPERATURE.metadata.extract()

        Error if no extractor set:

        >>> from atmospyre.sensors.read_tag.metadata import ReadTagMetadata
        >>> metadata = ReadTagMetadata(unit="ppm")
        >>> try:
        ...     metadata.extract()
        ... except ValueError as e:
        ...     print(e)
        No extraction strategy defined
        """
        if self.extractor is None:
            raise ValueError("No extraction strategy defined")
        return self.extractor.extract(self)

    def print(self) -> str:
        """Format metadata for human-readable display using the configured strategy.

        Delegates to the printer strategy to format this metadata object
        into a human-readable string suitable for display, logging, or
        documentation.

        Returns
        -------
        str
            Formatted metadata string. The exact format depends on the
            configured PrinterStrategy (e.g., compact one-liner, verbose
            multi-line, terminal with colors).

        Raises
        ------
        ValueError
            If no printing strategy is defined (printer is None).

        Examples
        --------
        Print CO2 metadata:

        >>> from atmospyre.sensors.implementations.co2.vaisala.gmp252 import CO2
        >>> from atmospyre.sensors.read_tag.strategies.printers import DefaultPrinterStrategy
        >>> CO2.metadata.printer = DefaultPrinterStrategy()
        >>> print(CO2.metadata.print())
        Description: CO2 concentration (float)
        Unit: ppm
        Precision: 1
        Source: Modbus Register 0-1 (float32)

        Print temperature metadata:

        >>> from atmospyre.sensors.implementations.co2.vaisala.gmp252 import TEMPERATURE
        >>> TEMPERATURE.metadata.printer = DefaultPrinterStrategy()
        >>> print(TEMPERATURE.metadata.print())
        Description: Measurement temperature
        Unit: °C
        Precision: 2
        Valid Range: -40.0 - 60.0
        Source: Modbus Register 4-5 (float32)

        Print status metadata (no unit):

        >>> from atmospyre.sensors.implementations.co2.vaisala.gmp252 import STATUS
        >>> STATUS.metadata.printer = DefaultPrinterStrategy()
        >>> print(STATUS.metadata.print())
        Description: General device status
        Source: Modbus Register 2048 (uint16)

        Error if no printer set:

        >>> from atmospyre.sensors.read_tag.metadata import ReadTagMetadata
        >>> metadata = ReadTagMetadata(unit="ppm")
        >>> try:
        ...     metadata.print()
        ... except ValueError as e:
        ...     print(e)
        No printing strategy defined
        """
        if self.printer is None:
            raise ValueError("No printing strategy defined")
        return self.printer.print(self)