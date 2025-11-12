import json
from typing import Dict,Any
from pathlib import Path

from ..saver import SaverStrategy

class JSONMetadataSaver(SaverStrategy):
    """Save logger metadata in JSON format.

    The JSONMetadataSaver class implements the MetadataSaver interface for
    JavaScript Object Notation (JSON) output. It creates human-readable text
    files with configurable indentation that can be easily parsed by many
    programming languages and tools.

    JSON is the default metadata format for SensorLogger and is suitable for:

    - Configuration files and logging metadata
    - Interchange with web services and APIs
    - Parsing in any programming language
    - Version control and diff-friendly output (with indentation)

    Parameters
    ----------
    indent : int, optional
        Number of spaces for JSON indentation (default: 2). Use 0 or None
        for compact output without whitespace.

    Attributes
    ----------
    indent : int
        The configured indentation level.

    Methods
    -------
    save(filepath: Path, metadata: Dict[str, Any]) -> None
        Save metadata dictionary to JSON file with configured indentation.
    get_extension() -> str
        Return 'json' as the file extension.

    Notes
    -----
    Output Format
    ~~~~~~~~~~~~~
    The JSON output:

    - Uses UTF-8 encoding
    - Includes pretty-printing with indentation (by default)
    - Sorts keys alphabetically (Python's json.dump default)
    - Escapes special characters as needed

    Example output with indent=2::

        {
          "date": "2025-10-24",
          "interval_seconds": 60,
          "sensor_type": "GMP252",
          "tags": {
            "CO2": {
              "description": "CO2 concentration",
              "unit": "ppm",
              "precision": 1
            }
          }
        }

    Data Type Handling
    ~~~~~~~~~~~~~~~~~~
    JSON supports these Python types natively:

    - dict → object
    - list, tuple → array
    - str → string
    - int, float → number
    - True, False → true, false
    - None → null

    Custom objects must be converted to these types before saving.

    Examples
    --------
    Default usage with SensorLogger:

    >>> from atmospyre.loggers import SensorLogger
    >>> from atmospyre.loggers.strategies.savers import JSONMetadataSaver
    >>>
    >>> logger = SensorLogger(
    ...     sensor=sensor,
    ...     tags=[CO2, TEMPERATURE],
    ...     interval_seconds=60,
    ...     output_path='./data',
    ...     metadata_saver=JSONMetadataSaver()  # Explicit, but this is default
    ... )

    Custom indentation:

    >>> # Compact JSON (no indentation)
    >>> compact_saver = JSONMetadataSaver(indent=0)
    >>>
    >>> # Wide indentation
    >>> wide_saver = JSONMetadataSaver(indent=4)

    Direct usage:

    >>> from pathlib import Path
    >>> saver = JSONMetadataSaver(indent=2)
    >>>
    >>> metadata = {
    ...     'date': '2025-10-24',
    ...     'interval_seconds': 60,
    ...     'sensor_type': 'GMP252',
    ...     'tags': {'CO2': {'unit': 'ppm', 'precision': 1}}
    ... }
    >>>
    >>> saver.save(Path('./metadata.json'), metadata)
    >>> # Creates formatted JSON file
    """

    def __init__(self, indent: int = 2):
        """Initialize JSON metadata saver.

        Parameters
        ----------
        indent : int, optional
            Number of spaces for JSON indentation (default: 2). Set to 0
            or None for compact output without whitespace formatting.

        Examples
        --------
        >>> saver = JSONMetadataSaver()  # Default 2-space indent
        >>> saver = JSONMetadataSaver(indent=4)  # 4-space indent
        >>> saver = JSONMetadataSaver(indent=0)  # Compact format
        """
        self.indent = indent

    def save(self, filepath: Path, metadata: Dict[str, Any]) -> None:
        """Save metadata dictionary to JSON file.

        Parameters
        ----------
        filepath : Path
            Path where the JSON file should be saved. Will be created or
            overwritten if it exists.
        metadata : Dict[str, Any]
            Complete metadata dictionary to serialize. Must contain only
            JSON-serializable types (dict, list, str, int, float, bool, None).

        Raises
        ------
        TypeError
            If metadata contains non-JSON-serializable objects.

        Examples
        --------
        >>> saver = JSONMetadataSaver(indent=2)
        >>> metadata = {
        ...     'date': '2025-10-24',
        ...     'sensor_type': 'GMP252',
        ...     'tags': {'CO2': {'unit': 'ppm'}}
        ... }
        >>> saver.save(Path('./metadata.json'), metadata)
        """
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=self.indent)

    def get_extension(self) -> str:
        """Get file extension for JSON format.

        Returns
        -------
        str
            Returns 'json'.

        Examples
        --------
        >>> saver = JSONMetadataSaver()
        >>> saver.get_extension()
        'json'
        """
        return 'json'