import csv
from pathlib import Path
from typing import Dict, Any

from ..writer import WriterStrategy

class CSVWriter(WriterStrategy):
    """Write sensor data in CSV format.

    The CSVWriter class implements the Writer interface for comma-separated
    values (CSV) output. It creates human-readable text files with headers
    and handles automatic column ordering based on the data dictionary keys.

    CSV files are the default format for SensorLogger and are suitable for:

    - Easy manual inspection and editing
    - Import into spreadsheet applications
    - Analysis with pandas or similar tools
    - Long-term archival (text-based format)

    Methods
    -------
    write(filepath: Path, data: Dict[str, Any], is_first: bool)
        Write data point to CSV file with automatic header generation.
    get_extension() -> str
        Return 'csv' as the file extension.

    Notes
    -----
    File Format
    ~~~~~~~~~~~
    The CSV format uses:

    - Comma as field delimiter
    - Double quotes for text containing commas/newlines
    - Column headers on the first line
    - One row per data point
    - UTF-8 encoding

    Example output::

        timestamp,CO2,TEMPERATURE
        2025-10-24T14:30:00.123456,415.2,23.5
        2025-10-24T14:31:00.234567,415.8,23.6

    Column Ordering
    ~~~~~~~~~~~~~~~
    Columns are written in the order they appear in the data dictionary.
    To ensure consistent ordering, use Python 3.7+ where dictionaries
    maintain insertion order, or pass an OrderedDict.

    Examples
    --------
    Basic usage with SensorLogger:

    >>> from atmospyre.loggers import SensorLogger
    >>> from atmospyre.loggers.strategies.writers.csv_writer import CSVWriter
    >>>
    >>> logger = SensorLogger(
    ...     sensor=sensor,
    ...     tags=[CO2, TEMPERATURE],
    ...     interval_seconds=60,
    ...     output_path='./data',
    ...     writer=CSVWriter()  # Explicit, but this is the default
    ... )

    Direct usage:

    >>> from pathlib import Path
    >>> writer = CSVWriter()
    >>>
    >>> data = {
    ...     'timestamp': '2025-10-24T14:30:00.123456',
    ...     'CO2': 415.2,
    ...     'TEMPERATURE': 23.5
    ... }
    >>>
    >>> writer.write(Path('./output.csv'), data, is_first=True)
    >>> # Creates: timestamp,CO2,TEMPERATURE
    >>> #          2025-10-24T14:30:00.123456,415.2,23.5
    >>>
    >>> writer.write(Path('./output.csv'), data, is_first=False)
    >>> # Appends without header
    """

    def write(self, filepath: Path, data: Dict[str, Any], is_first: bool):
        """Write data point to CSV file.

        Parameters
        ----------
        filepath : Path
            Path to the CSV output file. Will be created if it doesn't exist.
        data : Dict[str, Any]
            Dictionary containing the data point. Keys become column names,
            values are written as the row data. All values are converted to
            strings automatically.
        is_first : bool
            If True, writes the CSV header row before the data. If False or
            if the file already exists, only the data row is written.

        Notes
        -----
        The method checks both ``is_first`` flag and file existence to determine
        whether to write headers. This ensures headers are written exactly once
        even if the file was manually deleted between calls.

        Examples
        --------
        >>> writer = CSVWriter()
        >>> data = {'timestamp': '2025-10-24T14:30:00', 'value': 42}
        >>> writer.write(Path('./data.csv'), data, is_first=True)
        >>> # File contents:
        >>> # timestamp,value
        >>> # 2025-10-24T14:30:00,42
        """
        file_exists = filepath.exists()
        with open(filepath, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if is_first or not file_exists:
                writer.writeheader()
            writer.writerow(data)

    def get_extension(self) -> str:
        """Get file extension for CSV format.

        Returns
        -------
        str
            Returns 'csv'.

        Examples
        --------
        >>> writer = CSVWriter()
        >>> writer.get_extension()
        'csv'
        """
        return 'csv'