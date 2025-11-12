from typing import List
from pathlib import Path
from datetime import datetime

from atmospyre.sensors.sensor import Sensor
from atmospyre.sensors.read_tag.read_tag import ReadTag
from .strategies import WriterStrategy
from .strategies import SaverStrategy


class SensorLogger:
    """Automated data logger for sensor measurements with daily file organization.

    The SensorLogger class handles periodic reading of sensor data, automatic
    creation of daily directories, metadata generation, and data persistence.
    It validates logging intervals against tag requirements and manages file
    operations through configurable writer strategies.

    Parameters
    ----------
    sensor : Sensor
        Configured sensor instance to read measurements from. Must be properly
        initialized with port and communication settings.
    tags : List[ReadTag]
        List of ReadTag instances to log. All tags must be valid for the sensor.
        Each tag's metadata is used for interval validation and documentation.
    interval_seconds : int
        Logging interval in seconds. Must meet or exceed the minimum interval
        requirement of all tags (specified in tag metadata).
    output_path : str
        Base directory path for log file storage. Daily subdirectories will be
        created under this path with format YYYYMMDD (e.g., '20251024').
    writer : Writer, optional
        Strategy object for writing data files (default: CSVWriter if None).
        Must implement the Writer protocol with write() and get_extension() methods.
    metadata_saver : MetadataSaver, optional
        Strategy object for writing metadata files (default: JSONMetadataSaver if None).
        Must implement the MetadataSaver protocol with save_logger_metadata() method.

    Attributes
    ----------
    sensor : Sensor
        The sensor instance being logged.
    tags : List[ReadTag]
        The list of tags being monitored.
    interval_seconds : int
        The configured logging interval.
    output_path : Path
        Base directory path as a Path object.
    writer : Writer
        The data writing strategy.
    metadata_saver : MetadataSaver
        The metadata writing strategy.

    Raises
    ------
    ValueError
        If ``interval_seconds`` is below the minimum interval required by any tag
        in the tags list. The error message indicates which tag's requirement
        was violated.

    Examples
    --------
    Basic usage with default settings:

    >>> from atmospyre.sensors.implementations.co2.vaisala.gmp252 import GMP252, CO2, TEMPERATURE
    >>> from atmospyre.loggers import SensorLogger
    >>> sensor = GMP252(port='/dev/ttyUSB0', slave_address=1)
    >>> logger = SensorLogger(
    ...     sensor=sensor,
    ...     tags=[CO2, TEMPERATURE],
    ...     interval_seconds=60,
    ...     output_path='./data'
    ... )
    >>> logger.log()  # Single measurement
    >>> # Results in: ./data/20251024/data.csv
    >>> #             ./data/20251024/metadata.json


    Notes
    -----
    Directory Structure:

    The logger creates the following file structure::

        output_path/
        ├── 20251024/
        │   ├── metadata.json      # Created once per day
        │   ├── data.csv           # Appended with each log() call
        │   └── errors.log         # Created if errors occur
        ├── 20251025/
        │   ├── metadata.json
        │   └── data.csv
        └── ...

    Metadata Content:

    The metadata file contains:

    - Logging date and interval
    - Sensor type and configuration
    - Tag descriptions, units, and precision
    - Minimum interval requirements
    - Data file format information

    Error Handling:

    The ``log()`` method catches all exceptions and writes them to an error log
    file in the daily directory. This prevents a single failed reading from
    stopping the entire logging process. Common errors include:

    - Sensor communication failures (IOError)
    - Serial port disconnections
    - Invalid tag readings
    - Disk write failures

    The logger will continue attempting to log on subsequent calls even after
    errors occur.
    """

    def __init__(
        self,
        sensor: Sensor,
        tags: List[ReadTag],
        interval_seconds: int,
        output_path: str,
        writer: WriterStrategy | None = None,
        metadata_saver: SaverStrategy | None = None
    ):
        """Initialize sensor logger with validation.

        See class docstring for parameter details.
        """
        self.sensor = sensor
        self.tags = tags
        self.interval_seconds = interval_seconds
        self.output_path = Path(output_path)
        if writer is None:
            writer = self._default_writer()
        self.writer = writer
        if metadata_saver is None:
            metadata_saver=self._default_saver()
        self.metadata_saver = metadata_saver

        self._validate_interval()
        self._current_date = None
        self._metadata_written = False
        self._first_write_today = True

    def _validate_interval(self):
        """Check if interval meets minimum requirements from tag metadata.

        Raises
        ------
        ValueError
            If the configured interval is below the minimum required by any tag.
        """
        for tag in self.tags:
            if hasattr(tag, 'metadata') and hasattr(tag.metadata, 'min_interval'):
                min_interval = tag.metadata.min_interval
                if min_interval is not None:
                    if self.interval_seconds < min_interval:
                        raise ValueError(
                            f"Interval {self.interval_seconds}s is below minimum "
                            f"{min_interval}s for tag {tag.__class__.__name__}"
                        )

    def _get_daily_dir(self) -> Path:
        """Get or create directory for today's data.

        Creates a subdirectory under ``output_path`` with the current date
        in YYYYMMDD format. The directory and all parent directories are
        created if they don't exist.

        Returns
        -------
        Path
            Path object pointing to today's data directory.

        Examples
        --------
        >>> logger = SensorLogger(sensor, tags, 60, './data')
        >>> daily_dir = logger._get_daily_dir()
        >>> print(daily_dir)
        ./data/20251024
        """
        date_str = datetime.now().strftime('%Y%m%d')
        daily_dir = self.output_path / date_str
        daily_dir.mkdir(parents=True, exist_ok=True)
        return daily_dir

    def _write_metadata_if_needed(self, daily_dir: Path):
        """Write metadata file once per day.

        Checks if the date has changed since the last write. If it's a new day,
        resets the metadata flag and writes a new metadata file. This ensures
        each daily directory has exactly one metadata file documenting the
        logging configuration for that day.

        Parameters
        ----------
        daily_dir : Path
            Path to the current day's data directory.

        Notes
        -----
        The metadata file contains:

        - Date of logging session
        - Logging interval in seconds
        - Sensor type (class name)
        - List of tags with their metadata (units, precision, description)

        The file format is determined by the ``metadata_saver`` strategy's
        ``get_extension()`` method (e.g., 'json', 'yaml', 'toml').
        """
        today = datetime.now().date()

        if self._current_date != today:
            self._current_date = today
            self._metadata_written = False
            self._first_write_today = True

        if not self._metadata_written:
            metadata_file = daily_dir / f'metadata.{self.metadata_saver.get_extension()}'

            self.metadata_saver.save_logger_metadata(
                filepath=metadata_file,
                date=today,
                interval_seconds=self.interval_seconds,
                sensor_type=self.sensor.__class__.__name__,
                tags=self.tags
            )

            self._metadata_written = True

    def _default_writer(self):
        from atmospyre.loggers.strategies.writers import CSVWriter
        return CSVWriter()

    def _default_saver(self):
        from atmospyre.loggers.strategies.savers import JSONMetadataSaver
        return JSONMetadataSaver()

    def log(self):
        """Perform one logging cycle.

        Executes a complete logging operation:

        1. Creates or accesses today's directory
        2. Writes metadata file if this is the first log of the day
        3. Reads all configured tags from the sensor
        4. Formats the data with timestamp
        5. Writes data to the daily data file

        This method is designed to be called repeatedly by a scheduler at the
        configured interval. It handles all file operations and error logging
        internally.

        Raises
        ------
        None
            All exceptions are caught and logged to an error file. The method
            will not raise exceptions to prevent disrupting scheduled logging.

        Examples
        --------
        Manual single log:

        >>> logger.log()
        # Creates/updates:
        # ./data/20251024/metadata.json (if first log today)
        # ./data/20251024/data.csv (appends row)

        Data Format
        ~~~~~~~~~~~
        The data point written includes:

        - ``timestamp``: ISO 8601 formatted timestamp (YYYY-MM-DDTHH:MM:SS.ffffff)
        - One column per tag, named by the tag's class name
        - Values as returned by the sensor (typically float or int)

        Example CSV output::

            timestamp,CO2,TEMPERATURE
            2025-10-24T14:30:00.123456,415.2,23.5
            2025-10-24T14:31:00.234567,415.8,23.6
        """
        try:
            # Get today's directory
            daily_dir = self._get_daily_dir()

            # Write metadata if needed
            self._write_metadata_if_needed(daily_dir)

            # Read sensor
            readings = self.sensor.read(self.tags)

            # Prepare data point
            data_point = {
                'timestamp': datetime.now().isoformat()
            }

            # Add readings
            for tag, value in readings.items():
                tag_name = tag.__class__.__name__
                data_point[tag_name] = value

            # Write to file
            data_file = daily_dir / f'data.{self.writer.get_extension()}'
            self.writer.write(data_file, data_point, self._first_write_today)

            self._first_write_today = False

        except Exception as e:
            # Log error but don't crash
            error_msg = f"Error during logging: {e}"

            # Write to error log file
            daily_dir = self._get_daily_dir()
            error_file = daily_dir / 'errors.log'
            with open(error_file, 'a') as f:
                f.write(f"{datetime.now().isoformat()} - {error_msg}\n")

    def __repr__(self) -> str:
        """Return string representation of the logger.

        Returns
        -------
        str
            Human-readable string describing the logger configuration.

        Examples
        --------
        >>> logger = SensorLogger(sensor, [CO2, TEMPERATURE], 60, './data')
        >>> print(repr(logger))
        SensorLogger(sensor=GMP252, tags=2, interval=60s, output='./data')
        """
        return (
            f"SensorLogger("
            f"sensor={self.sensor.__class__.__name__}, "
            f"tags={len(self.tags)}, "
            f"interval={self.interval_seconds}s, "
            f"output='{self.output_path}')"
        )