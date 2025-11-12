from typing import Dict, Any
from abc import ABC, abstractmethod
from pathlib import Path

class WriterStrategy(ABC):
    """Abstract base class for data file writers.

    The Writer class defines the interface for writing sensor measurement data
    to files in various formats (CSV, Parquet, JSON, etc.). Implementations
    handle format-specific serialization and file operations while maintaining
    a consistent interface for the SensorLogger.

    This class uses the Strategy pattern to allow runtime selection of data
    output formats without modifying the logger code.

    Methods
    -------
    write(filepath: Path, data: Dict[str, Any], is_first: bool)
        Write a single data point to the specified file.
    get_extension() -> str
        Return the file extension for this writer's format.

    Examples
    --------
    Implementing a custom writer:

    >>> from pathlib import Path
    >>> from typing import Dict, Any
    >>>
    >>> class CustomWriter(Writer):
    ...     def write(self, filepath: Path, data: Dict[str, Any], is_first: bool):
    ...         with open(filepath, 'a') as f:
    ...             f.write(f"{data}\\n")
    ...
    ...     def get_extension(self) -> str:
    ...         return 'txt'
    >>>
    >>> writer = CustomWriter()
    >>> writer.write(Path('output.txt'), {'value': 42}, True)
    """

    @abstractmethod
    def write(self, filepath: Path, data: Dict[str, Any], is_first: bool):
        """Write data point to file.

        Parameters
        ----------
        filepath : Path
            Path to the output file. Parent directories must exist.
        data : Dict[str, Any]
            Dictionary containing the data point to write. Keys are column/field
            names, values are the measurement values. Typically includes a
            'timestamp' key with ISO format datetime string.
        is_first : bool
            True if this is the first write to the file today, False otherwise.
            Used to determine whether to write headers/schema.

        Notes
        -----
        Implementations should:

        - Create the file if it doesn't exist
        - Append to existing files
        - Write headers/schema when ``is_first`` is True
        - Handle data type conversion as needed for the format
        - Ensure atomic writes to prevent data corruption

        Examples
        --------
        >>> data = {
        ...     'timestamp': '2025-10-24T14:30:00.123456',
        ...     'CO2': 415.2,
        ...     'TEMPERATURE': 23.5
        ... }
        >>> writer.write(Path('./data/20251024/data.csv'), data, is_first=True)
        """

    @abstractmethod
    def get_extension(self) -> str:
        """Get file extension for this writer's format.

        Returns
        -------
        str
            File extension without leading dot (e.g., 'csv', 'parquet', 'json').

        Examples
        --------
        >>> writer = CSVWriter()
        >>> writer.get_extension()
        'csv'
        """