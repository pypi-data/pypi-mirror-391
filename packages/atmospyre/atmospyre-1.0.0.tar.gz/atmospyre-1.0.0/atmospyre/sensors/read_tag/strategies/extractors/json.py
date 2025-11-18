import json
from typing import Dict, Any
from ..extractor import ExtractorStrategy
from ...metadata import ReadTagMetadata


class JSONExtractor(ExtractorStrategy):
    """Extract metadata as JSON format.

    This extractor serializes ReadTagMetadata objects to JSON strings
    for storage, transmission, or interoperability with other systems.

    Parameters
    ----------
    indent : int, optional
        Number of spaces for JSON indentation (default: 2)

    Examples
    --------
    Direct usage with metadata object:

    >>> from atmospyre.sensors.read_tag.strategies.extractors import JSONExtractor
    >>> from atmospyre.sensors.read_tag.metadata import ReadTagMetadata
    >>> extractor = JSONExtractor(indent=2)
    >>> metadata = ReadTagMetadata(unit="°C", description="Temperature")
    >>> json_str = extractor.extract(metadata)
    >>> print(json_str)
    {
      "unit": "°C",
      "description": "Temperature"
    }

    Using with sensor tags via public API:

    >>> from atmospyre.sensors.implementations.co2.gmp252 import GMP252, CO2
    >>> from atmospyre.sensors.read_tag.strategies.extractors import JSONExtractor
    >>>
    >>> # Set the extractor strategy on the tag's metadata
    >>> CO2.metadata.extractor = JSONExtractor(indent=2)
    >>>
    >>> # Extract metadata through the tag's public API
    >>> json_metadata = CO2.extract_metadata()
    >>> print(json_metadata)
    {
      "unit": "ppm",
      "description": "CO2 concentration (float)",
      "precision": 1,
      "valid_range": [0.0, 10000.0],
      "source": "Modbus Register 0-1 (float32)"
    }

    Extract metadata for multiple tags:

    >>> from atmospyre.sensors.implementations.co2.gmp252 import (
    ...     CO2, MEASURED_TEMPERATURE, MEASURED_HUMIDITY
    ... )
    >>>
    >>> # Configure all tags with JSON extractor
    >>> extractor = JSONExtractor(indent=2)
    >>> for tag in [CO2, MEASURED_TEMPERATURE, MEASURED_HUMIDITY]:
    ...     tag.metadata.extractor = extractor
    >>>
    >>> # Extract metadata from each tag
    >>> sensor = GMP252(port='/dev/ttyACM0', slave_address=121)
    >>> for tag in sensor.get_valid_tags():
    ...     if tag.metadata.extractor is not None:
    ...         print(f"{type(tag).__name__}:")
    ...         print(tag.extract_metadata())
    ...         print()

    Deserialize and use loaded metadata:

    >>> json_str = CO2.extract_metadata()
    >>> loaded_data = extractor.load(json_str)
    >>> print(f"Unit: {loaded_data['unit']}")
    Unit: ppm
    >>> print(f"Valid range: {loaded_data['valid_range']}")
    Valid range: [0.0, 10000.0]
    """

    def __init__(self, indent: int = 2):
        self.indent = indent

    def extract(self, metadata: ReadTagMetadata) -> str:
        """Serialize metadata to JSON string.

        Converts a ReadTagMetadata object to a JSON string representation.
        Strategy objects (extractor, printer) are excluded from serialization.
        Fields with None values are omitted for cleaner output.

        Parameters
        ----------
        metadata : ReadTagMetadata
            The metadata object to serialize

        Returns
        -------
        str
            JSON string with all non-None metadata fields

        Examples
        --------
        >>> metadata = ReadTagMetadata(
        ...     unit="ppm",
        ...     description="CO2 Sensor",
        ...     precision=2,
        ...     valid_range=(0, 5000)
        ... )
        >>> json_str = extractor.extract(metadata)
        >>> print(json_str)
        {
          "unit": "ppm",
          "description": "CO2 Sensor",
          "precision": 2,
          "valid_range": [0, 5000]
        }

        Notes
        -----
        This method automatically filters out None values to produce
        cleaner JSON output. Only fields with actual values are included.
        """
        # Convert dataclass to dict, excluding strategy objects
        data = {
            "unit": metadata.unit,
            "source": metadata.source,
            "min_interval": metadata.min_interval,
            "description": metadata.description,
            "precision": metadata.precision,
            "valid_range": metadata.valid_range,
        }

        # Remove None values for cleaner output
        data = {k: v for k, v in data.items() if v is not None}

        return json.dumps(data, indent=self.indent)

    def load(self, data: str) -> Dict[str, Any]:
        """Deserialize metadata from JSON string.

        Parses a JSON string and returns a dictionary of metadata fields
        that can be used to reconstruct a ReadTagMetadata object.

        Parameters
        ----------
        data : str
            JSON string containing metadata fields

        Returns
        -------
        Dict[str, Any]
            Dictionary of metadata fields with their values

        Raises
        ------
        json.JSONDecodeError
            If the input string is not valid JSON

        Examples
        --------
        >>> json_str = '{"unit": "°C", "description": "Temperature", "precision": 2}'
        >>> metadata_dict = extractor.load(json_str)
        >>> print(metadata_dict)
        {'unit': '°C', 'description': 'Temperature', 'precision': 2}

        >>> # Reconstruct metadata object
        >>> from atmospyre.sensors.metadata import ReadTagMetadata
        >>> metadata = ReadTagMetadata(**metadata_dict)

        Notes
        -----
        This method is the inverse of extract(). It does not create
        a ReadTagMetadata object directly, but returns a dictionary
        that can be unpacked to create one.
        """
        return json.loads(data)
