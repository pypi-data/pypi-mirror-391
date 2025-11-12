from typing import List, Dict, NewType
from pathlib import Path

from atmospyre.loggers import SensorLogger
from atmospyre.scheduler.scheduler_dispatch_tag import SchedulerDispatchTag

# Global namespace for all scheduler backends
scheduler_dispatch_namespace = {}


class LoggerScheduler:
    """Scheduler for managing multiple SensorLogger instances with pluggable backends.

    The LoggerScheduler class provides a unified interface for scheduling and
    running multiple SensorLogger instances, using a tag-based dispatch system
    to select different scheduling backends.

    All execution is blocking and serial, ensuring safe Modbus communication
    when multiple sensors share a bus.

    Parameters
    ----------
    scheduler_dispatch_tag : SchedulerDispatchTag subclass, optional
        Tag class for backend selection. Currently supported:
        - ScheduleTag: For 'schedule' library (simple, lightweight).
        If None, defaults to ScheduleTag.
    log_path : str or Path, optional
        Path where scheduler logs should be written (default: ".").
    verbose : bool, optional
        Whether to print scheduler events to stdout (default: True).
    check_interval : float, optional
        Time in seconds between schedule checks (default: 1.0).
        Only applies to schedule backend.

    Attributes
    ----------
    schedule : Backend-specific scheduler
        The underlying scheduler instance used for job management.
    loggers : List[SensorLogger]
        List of registered sensor loggers.

    Raises
    ------
    ValueError
        If attempting to add a logger that is already registered.

    Examples
    --------
    Basic usage with the schedule library backend:

    >>> from atmospyre.scheduler import LoggerScheduler, ScheduleTag
    >>> from atmospyre.loggers import SensorLogger
    >>> scheduler = LoggerScheduler(
    ...     scheduler_dispatch_tag=ScheduleTag,
    ...     log_path='./logs'
    ... )
    >>> scheduler.add_logger(logger1)
    >>> scheduler.add_logger(logger2)
    >>> scheduler.run()  # Blocking

    Manual execution of pending jobs:

    >>> import time
    >>> scheduler = LoggerScheduler(scheduler_dispatch_tag=ScheduleTag)
    >>> scheduler.add_logger(logger1)
    >>> while True:
    ...     scheduler.run_pending()
    ...     time.sleep(1)

    Context manager usage:

    >>> with LoggerScheduler(scheduler_dispatch_tag=ScheduleTag) as scheduler:
    ...     scheduler.add_logger(logger1)
    ...     scheduler.add_logger(logger2)
    ...     scheduler.run()

    Notes
    -----
    The LoggerScheduler class uses ``multipledispatch`` to implement type-based dispatch.
    Each backend has its own implementation registered in the shared
    scheduler_dispatch_namespace. When you call methods like ``add_logger()``, the
    scheduler dispatches to the appropriate backend-specific function based on the
    tag's type.
    """

    def __init__(
        self,
        scheduler_dispatch_tag: SchedulerDispatchTag | None = None,
        log_path: Path = Path("."),
        verbose: bool = True,
        check_interval: float = 1.0
    ):
        """Initialize scheduler with backend tag and configuration.

        See class docstring for parameter details.
        """
        # Store the tag class and create an instance
        if scheduler_dispatch_tag is None:
            scheduler_dispatch_tag = self._default_tag()
        self.scheduler_dispatch_tag = scheduler_dispatch_tag

        # Store configuration
        self.log_path = Path(log_path)
        self.check_interval = check_interval
        self.verbose = verbose
        self.loggers: List[SensorLogger] = []

        # Create log directory if needed
        if self.log_path:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Create the scheduler using the tag for dispatch
        _create_scheduler = scheduler_dispatch_namespace['_create_scheduler']
        self.schedule = _create_scheduler(self.scheduler_dispatch_tag)

    def add_logger(
        self,
        logger: SensorLogger,
    ):
        """Add a logger to the scheduler.

        Parameters
        ----------
        logger : SensorLogger
            The sensor logger to schedule.

        Raises
        ------
        ValueError
            If the logger is already registered.

        Examples
        --------
        >>> scheduler = LoggerScheduler(scheduler_dispatch_tag=ScheduleTag)
        >>> logger = SensorLogger(sensor=my_sensor, interval_seconds=60)
        >>> scheduler.add_logger(logger)
        """
        _add_logger = scheduler_dispatch_namespace['_add_logger']
        _add_logger(self.scheduler_dispatch_tag, self, logger, logger.interval_seconds)

    def remove_logger(self, logger: SensorLogger) -> bool:
        """Remove a logger from the scheduler.

        Parameters
        ----------
        logger : SensorLogger
            The logger instance to remove.

        Returns
        -------
        bool
            True if logger was found and removed, False otherwise.

        Examples
        --------
        >>> scheduler.remove_logger(logger1)
        True
        >>> scheduler.remove_logger(nonexistent_logger)
        False
        """
        _remove_logger = scheduler_dispatch_namespace['_remove_logger']
        return _remove_logger(self.scheduler_dispatch_tag, self, logger)

    def clear(self):
        """Remove all loggers and clear the schedule.

        Examples
        --------
        >>> scheduler.add_logger(logger1)
        >>> scheduler.add_logger(logger2)
        >>> scheduler.clear()
        >>> print(len(scheduler.loggers))
        0
        """
        _clear = scheduler_dispatch_namespace['_clear']
        _clear(self.scheduler_dispatch_tag, self)

    def get_status(self) -> Dict:
        """Get current scheduler status.

        Returns
        -------
        dict
            Dictionary containing backend name, logger counts, and details.

        Examples
        --------
        >>> status = scheduler.get_status()
        >>> print(f"Backend: {status['backend']}")
        Backend: schedule
        >>> print(f"Total loggers: {status['total_loggers']}")
        Total loggers: 3
        """
        _get_status = scheduler_dispatch_namespace['_get_status']
        return _get_status(self.scheduler_dispatch_tag, self)

    def run_pending(self):
        """Run all pending jobs manually.

        Notes
        -----
        Not all backends support this operation.

        Examples
        --------
        >>> import time
        >>> scheduler = LoggerScheduler(scheduler_dispatch_tag=ScheduleTag)
        >>> scheduler.add_logger(logger1)
        >>> while True:
        ...     scheduler.run_pending()
        ...     time.sleep(1)
        """
        _run_pending = scheduler_dispatch_namespace['_run_pending']
        _run_pending(self.scheduler_dispatch_tag, self)

    def run(self):
        """Start the scheduler in a blocking loop.

        This method blocks indefinitely, running scheduled jobs.
        Press Ctrl+C to stop.

        Examples
        --------
        >>> scheduler = LoggerScheduler(scheduler_dispatch_tag=ScheduleTag)
        >>> scheduler.add_logger(logger1)
        >>> scheduler.add_logger(logger2)
        >>> scheduler.run()  # Blocks until Ctrl+C
        """
        _run = scheduler_dispatch_namespace['_run']
        _run(self.scheduler_dispatch_tag, self)

    def _default_tag(self) -> SchedulerDispatchTag:
        """Get the default scheduler backend tag.

        Returns
        -------
        SchedulerDispatchTag
            Default ScheduleTag instance.
        """
        from atmospyre.scheduler.schedule.schedule_backend import ScheduleTag
        return ScheduleTag()

    def __repr__(self) -> str:
        """Return string representation of the scheduler.

        Returns
        -------
        str
            String showing backend type and number of loggers.

        Examples
        --------
        >>> scheduler = LoggerScheduler(scheduler_dispatch_tag=ScheduleTag)
        >>> scheduler.add_logger(logger1)
        >>> print(scheduler)
        LoggerScheduler(backend=schedule, loggers=1)
        """
        status = self.get_status()
        return (
            f"LoggerScheduler("
            f"backend={status.get('backend', 'unknown')}, "
            f"loggers={status['total_loggers']})"
        )

    def __enter__(self):
        """Context manager entry.

        Returns
        -------
        LoggerScheduler
            This scheduler instance.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit.

        Clears all loggers when exiting the context.

        Parameters
        ----------
        exc_type : type or None
            Exception type if an exception occurred.
        exc_val : Exception or None
            Exception instance if an exception occurred.
        exc_tb : traceback or None
            Exception traceback if an exception occurred.
        """
        self.clear()