from .metadata import ReadTagMetadata


class ReadTag:
    """Tag with metadata for sensor measurements.

    ReadTag serves as a type-safe identifier for sensor measurements, carrying
    metadata about the measurement including units, valid ranges, precision,
    and custom extraction/printing strategies.

    Each sensor defines its own tag instances (e.g., CO2, TEMPERATURE) which
    are used both for type-based dispatch in the read system and for carrying
    measurement metadata.

    Parameters
    ----------
    metadata : ReadTagMetadata
        Metadata describing this measurement, including unit, description,
        valid range, precision, and extraction/printing strategies.

    Attributes
    ----------
    metadata : ReadTagMetadata
        The metadata associated with this tag.

    Examples
    --------
    Create a simple tag with basic metadata:

    >>> from atmospyre.sensors.read_tag import ReadTag
    >>> from atmospyre.sensors.read_tag import ReadTagMetadata
    >>> co2_meta = ReadTagMetadata(
    ...     unit="ppm",
    ...     description="CO2 concentration (float)",
    ...     valid_range=(0.0, 10000.0),
    ...     precision=1
    ... )
    >>> CO2 = ReadTag(co2_meta)
    >>> print(CO2.metadata.unit)
    ppm

    Extract and print metadata:

    >>> # Assuming extractor and printer strategies are set
    >>> data = CO2.extract_metadata()
    >>> display = CO2.print_metadata()

    Notes
    -----
    ReadTag instances are typically defined as module-level constants in
    sensor implementation files. They serve dual purposes:

    1. **Type-based dispatch**: The multipledispatch system uses the tag's
       type to route to the correct read function.
    2. **Metadata carrier**: Tags carry information about units, ranges,
       and how to format the data.

    Tags should be treated as immutable identifiers. Do not modify tag
    instances after creation.

    See Also
    --------
    ReadTagMetadata : Metadata container for tags
    Sensor.read : Read measurements using tags
    """

    def __init__(self, metadata: ReadTagMetadata):
        """Initialize tag with metadata.

        Parameters
        ----------
        metadata : ReadTagMetadata
            Metadata describing this measurement, including unit, description,
            valid range, precision, and strategies for extraction/printing.
        """
        self.metadata = metadata

    def extract_metadata(self) -> str:
        """Extract/serialize metadata to string using the configured strategy.

        Uses the extractor strategy defined in the tag's metadata to serialize
        the metadata into a string format. The exact format depends on the
        extractor implementation.

        Returns
        -------
        str
            Serialized metadata string. Format depends on the configured
            ExtractorStrategy.

        Raises
        ------
        ValueError
            If no extraction strategy is defined in the metadata.

        Examples
        --------
        >>> co2_tag.extract_metadata()
        'unit=ppm,range=0.0-10000.0,precision=1'

        Notes
        -----
        This method delegates to the metadata's extract() method, which in
        turn uses the configured ExtractorStrategy. This allows different
        serialization formats (JSON, CSV, custom) to be plugged in.

        See Also
        --------
        ReadTagMetadata.extract : The underlying extraction method
        ExtractorStrategy : Strategy interface for metadata extraction
        """
        return self.metadata.extract()

    def print_metadata(self) -> str:
        """Format metadata for human-readable display.

        Uses the printer strategy defined in the tag's metadata to format
        the metadata for display purposes. The exact format depends on the
        printer implementation.

        Returns
        -------
        str
            Formatted metadata string suitable for display. Format depends
            on the configured PrinterStrategy.

        Raises
        ------
        ValueError
            If no printing strategy is defined in the metadata.

        Examples
        --------
        >>> print(co2_tag.print_metadata())
        CO2 Concentration
        Unit: ppm
        Range: 0.0 - 10000.0 ppm
        Precision: ±1 ppm

        Notes
        -----
        This method delegates to the metadata's print() method, which in
        turn uses the configured PrinterStrategy. This allows different
        display formats (verbose, compact, terminal colors) to be plugged in.

        See Also
        --------
        ReadTagMetadata.print : The underlying printing method
        PrinterStrategy : Strategy interface for metadata formatting
        """
        return self.metadata.print()