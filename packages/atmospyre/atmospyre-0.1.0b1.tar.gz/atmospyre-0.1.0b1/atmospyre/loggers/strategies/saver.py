from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod
from atmospyre.sensors.read_tag.read_tag import ReadTag


class SaverStrategy(ABC):
    """Abstract base class for saving logger metadata.

    The MetadataSaver class defines the interface for persisting logging
    configuration and tag metadata to files in various formats (JSON, YAML,
    TOML, etc.). Implementations handle format-specific serialization while
    the base class provides common metadata assembly logic.

    This class uses the Strategy pattern to allow runtime selection of metadata
    file formats without modifying the logger code.

    Methods
    -------
    save(filepath: Path, metadata: Dict[str, Any]) -> None
        Save metadata dictionary to file in the implementation's format.
    get_extension() -> str
        Return the file extension for this saver's format.
    save_logger_metadata(filepath: Path, date: datetime.date, interval_seconds: int,
                         sensor_type: str, tags: List[ReadTag]) -> None
        High-level method that assembles and saves complete logger metadata.

    Notes
    -----
    Metadata Structure
    ~~~~~~~~~~~~~~~~~~
    The metadata dictionary contains:

    - ``date``: ISO format date string (YYYY-MM-DD)
    - ``interval_seconds``: Logging interval as integer
    - ``sensor_type``: Sensor class name as string
    - ``tags``: Dictionary mapping tag names to their metadata dicts

    Example structure::

        {
            "date": "2025-10-24",
            "interval_seconds": 60,
            "sensor_type": "GMP252",
            "tags": {
                "CO2": {
                    "description": "CO2 concentration",
                    "unit": "ppm",
                    "precision": 1,
                    "min_interval": 10
                },
                "TEMPERATURE": {
                    "description": "Sensor temperature",
                    "unit": "°C",
                    "precision": 0.1,
                    "min_interval": 1
                }
            }
        }

    Tag Metadata Extraction
    ~~~~~~~~~~~~~~~~~~~~~~~
    Tags must have a ``metadata`` attribute with a ``to_dict()`` method that
    returns their metadata as a dictionary. If ``to_dict()`` is not available,
    the tag is skipped (no error is raised).

    See Also
    --------
    JSONMetadataSaver : JSON format implementation
    SensorLogger : Uses MetadataSaver for metadata persistence
    ReadTag : Base class for measurement tags

    Examples
    --------
    Implementing a custom metadata saver:

    >>> from pathlib import Path
    >>> from typing import Dict, Any
    >>>
    >>> class CustomMetadataSaver(MetadataSaver):
    ...     def save(self, filepath: Path, metadata: Dict[str, Any]) -> None:
    ...         with open(filepath, 'w') as f:
    ...             for key, value in metadata.items():
    ...                 f.write(f"{key}: {value}\\n")
    ...
    ...     def get_extension(self) -> str:
    ...         return 'txt'
    >>>
    >>> saver = CustomMetadataSaver()
    >>> saver.save_logger_metadata(
    ...     Path('metadata.txt'),
    ...     date=datetime.now().date(),
    ...     interval_seconds=60,
    ...     sensor_type='GMP252',
    ...     tags=[CO2, TEMPERATURE]
    ... )
    """

    @abstractmethod
    def save(self, filepath: Path, metadata: Dict[str, Any]) -> None:
        """Save metadata dictionary to file.

        Parameters
        ----------
        filepath : Path
            Path where the metadata file should be saved. Parent directories
            must exist.
        metadata : Dict[str, Any]
            Complete metadata dictionary to serialize and save. Structure
            is defined by the ``save_logger_metadata`` method.

        Notes
        -----
        Implementations should:

        - Create or overwrite the file at the specified path
        - Handle format-specific encoding and serialization
        - Ensure the file is human-readable when possible
        - Preserve data types where the format supports it

        Examples
        --------
        >>> metadata = {
        ...     'date': '2025-10-24',
        ...     'interval_seconds': 60,
        ...     'sensor_type': 'GMP252',
        ...     'tags': {'CO2': {...}}
        ... }
        >>> saver.save(Path('./metadata.json'), metadata)
        """

    @abstractmethod
    def get_extension(self) -> str:
        """Get file extension for this saver's format.

        Returns
        -------
        str
            File extension without leading dot (e.g., 'json', 'yaml', 'toml').

        Examples
        --------
        >>> saver = JSONMetadataSaver()
        >>> saver.get_extension()
        'json'
        """

    def save_logger_metadata(
        self,
        filepath: Path,
        date: datetime.date,
        interval_seconds: int,
        sensor_type: str,
        tags: List[ReadTag]
    ) -> None:
        """Save complete logger metadata to file.

        Assembles metadata from logger configuration and tag metadata, then
        saves it using the implementation's format. This is the primary method
        used by SensorLogger to persist metadata.

        Parameters
        ----------
        filepath : Path
            Path where the metadata file should be saved.
        date : datetime.date
            Date of the logging session, written in ISO format (YYYY-MM-DD).
        interval_seconds : int
            Logging interval in seconds.
        sensor_type : str
            Name of the sensor class being logged.
        tags : List[ReadTag]
            List of tags being logged. Each tag's metadata is extracted using
            its ``metadata.to_dict()`` method if available.

        Notes
        -----
        Tags without a ``metadata`` attribute or without a ``to_dict()`` method
        on their metadata are silently skipped. This allows mixing tags with
        and without detailed metadata.

        The assembled metadata structure is passed to the ``save()`` method
        for format-specific serialization.

        Examples
        --------
        >>> from datetime import date
        >>> from atmospyre.sensors.implementations.co2.vaisala.gmp252 import GMP252, CO2, TEMPERATURE
        >>>
        >>> saver = JSONMetadataSaver()
        >>> sensor = GMP252(port='/dev/ttyUSB0')
        >>>
        >>> saver.save_logger_metadata(
        ...     filepath=Path('./metadata.json'),
        ...     date=date(2025, 10, 24),
        ...     interval_seconds=60,
        ...     sensor_type='GMP252',
        ...     tags=[CO2, TEMPERATURE]
        ... )
        >>> # Creates metadata.json with complete logging configuration
        """
        # Build base metadata structure
        metadata = {
            'date': date.isoformat(),
            'interval_seconds': interval_seconds,
            'sensor_type': sensor_type,
            'tags': {}
        }

        # Extract each tag's metadata using its to_dict() method
        for tag in tags:
            tag_name = tag.__class__.__name__
            if hasattr(tag, 'metadata') and hasattr(tag.metadata, 'to_dict'):
                # Use the metadata's own to_dict() method
                metadata['tags'][tag_name] = tag.metadata.to_dict()
            elif hasattr(tag, 'metadata'):
                # Fallback: if to_dict() doesn't exist, skip this tag
                # (or you could raise an error here)
                pass

        # Save using the saver's format
        self.save(filepath, metadata)