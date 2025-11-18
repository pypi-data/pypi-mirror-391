from ..printer import PrinterStrategy
from ...metadata import ReadTagMetadata


class DefaultPrinterStrategy(PrinterStrategy):
    """Print metadata in human-readable format.

    This printer formats ReadTagMetadata objects into a multi-line,
    human-readable text format with labeled key-value pairs.

    Examples
    --------
    Direct usage with metadata object:

    >>> from atmospyre.sensors.read_tag.strategies.printers import DefaultPrinterStrategy
    >>> from atmospyre.sensors.read_tag.metadata import ReadTagMetadata
    >>> printer = DefaultPrinterStrategy()
    >>> metadata = ReadTagMetadata(
    ...     unit="°C",
    ...     description="Temperature Sensor",
    ...     precision=2,
    ...     valid_range=(-40.0, 85.0)
    ... )
    >>> print(printer.print(metadata))

    Using with sensor tags via public API:

    >>> from atmospyre.sensors.implementations.co2.gmp252 import GMP252, CO2
    >>> from atmospyre.sensors.read_tag.strategies.printers import DefaultPrinterStrategy
    >>>
    >>> # Set the printer strategy on the tag's metadata
    >>> CO2.metadata.printer = DefaultPrinterStrategy()
    >>>
    >>> # Print metadata through the tag's public API
    >>> print(CO2.print_metadata())
    """

    def print(self, metadata: ReadTagMetadata) -> str:
        """Format metadata for human reading.

        Creates a multi-line string with each metadata field on its own
        line. Fields with None values are omitted from the output. The
        output is formatted with clear labels for easy reading.

        Parameters
        ----------
        metadata : ReadTagMetadata
            The metadata object to format

        Returns
        -------
        str
            Multi-line formatted string with labeled metadata fields.
            Empty string if all fields are None.

        Examples
        --------
        Format complete metadata:

        >>> from atmospyre.sensors.implementations.co2.gmp252 import CO2
        >>> CO2.metadata.printer = DefaultPrinterStrategy()
        >>> formatted = CO2.metadata.print()
        >>> print(formatted)
        Description: CO2 concentration (float)
        Unit: ppm
        Precision: 1 decimal places
        Valid Range: 0.0 to 10000.0
        Source: Modbus Register 0-1 (float32)

        Format metadata with missing fields:

        >>> from atmospyre.sensors.implementations.co2.gmp252 import STATUS
        >>> STATUS.metadata.printer = DefaultPrinterStrategy()
        >>> formatted = STATUS.metadata.print()
        >>> print(formatted)
        Description: General device status
        Source: Modbus Register 2048 (uint16)

        Notes
        -----
        The output format is designed for human readability with clear
        labels. For machine-readable output, use JSONPrinterStrategy or
        a custom printer implementation.

        Fields are displayed in this order:
        1. Description
        2. Unit
        3. Precision
        4. Valid Range
        5. Min Interval
        6. Source

        Only fields with non-None values are included in the output.
        """
        lines = []

        if metadata.description:
            lines.append(f"Description: {metadata.description}")

        if metadata.unit:
            lines.append(f"Unit: {metadata.unit}")

        if metadata.precision is not None:
            lines.append(f"Precision: {metadata.precision} decimal places")

        if metadata.valid_range:
            lines.append(
                f"Valid Range: {metadata.valid_range[0]} to {metadata.valid_range[1]}"
            )

        if metadata.min_interval:
            lines.append(f"Min Interval: {metadata.min_interval} seconds")

        if metadata.source:
            lines.append(f"Source: {metadata.source}")

        return "\n".join(lines)
