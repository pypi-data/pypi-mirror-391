import time
from typing import Dict
from multipledispatch import dispatch

from atmospyre.loggers import SensorLogger
from atmospyre.scheduler.logger_scheduler import (
    SchedulerDispatchTag,
    scheduler_dispatch_namespace
)


class YourBackendTag(SchedulerDispatchTag):
    """Tag class for [YourBackend] backend type dispatch.

    This class inherits from SchedulerDispatchTag and serves as a type marker
    for multipledispatch, allowing functions to be dispatched to the [YourBackend]
    backend without requiring specific types for all arguments.

    Examples
    --------
    >>> from atmospyre.scheduler import LoggerScheduler
    >>> from atmospyre.scheduler.yourbackend.yourbackend_backend import YourBackendTag
    >>> scheduler = LoggerScheduler(scheduler_dispatch_tag=YourBackendTag())
    >>> print(scheduler)
    LoggerScheduler(backend=yourbackend, loggers=0)
    """
    pass


@dispatch(YourBackendTag, namespace=scheduler_dispatch_namespace)
def _create_scheduler(tag: YourBackendTag):
    """Create and return a [YourBackend] scheduler instance.

    Parameters
    ----------
    tag : YourBackendTag
        Tag for dispatch (not used in implementation).

    Returns
    -------
    [YourSchedulerType]
        A new scheduler instance from the [your-library] library.

    Examples
    --------
    >>> tag = YourBackendTag()
    >>> sched = _create_scheduler(tag)
    >>> print(type(sched).__name__)
    [YourSchedulerType]
    """



@dispatch(YourBackendTag, object, object, int, namespace=scheduler_dispatch_namespace)
def _add_logger(
    tag: YourBackendTag,
    scheduler_instance,
    logger: SensorLogger,
    interval_seconds: int
):
    """Add a logger to the [YourBackend]-based scheduler.

    Parameters
    ----------
    tag : YourBackendTag
        Tag for dispatch (not used in implementation).
    scheduler_instance : LoggerScheduler
        The scheduler instance to add the logger to.
    logger : SensorLogger
        The sensor logger to schedule.
    interval_seconds : int
        Interval in seconds between logger executions.

    Raises
    ------
    ValueError
        If the logger is already registered.

    Examples
    --------
    >>> from atmospyre.scheduler import LoggerScheduler
    >>> from atmospyre.loggers import SensorLogger
    >>> scheduler = LoggerScheduler(scheduler_dispatch_tag=YourBackendTag())
    >>> logger = SensorLogger(sensor=my_sensor, tags=[...], interval_seconds=60, output_path=".")
    >>> scheduler.add_logger(logger)
    Added logger <SensorLogger> with interval 60s
    """


@dispatch(YourBackendTag, object, object, namespace=scheduler_dispatch_namespace)
def _remove_logger(
    tag: YourBackendTag,
    scheduler_instance,
    logger: SensorLogger
) -> bool:
    """Remove a logger from the [YourBackend]-based scheduler.

    Parameters
    ----------
    tag : YourBackendTag
        Tag for dispatch (not used in implementation).
    scheduler_instance : LoggerScheduler
        The scheduler instance to remove the logger from.
    logger : SensorLogger
        The logger instance to remove.

    Returns
    -------
    bool
        True if logger was found and removed, False otherwise.

    Examples
    --------
    >>> scheduler.add_logger(logger1)
    >>> scheduler.remove_logger(logger1)
    Removed logger <SensorLogger>
    True
    >>> scheduler.remove_logger(logger1)
    False
    """



@dispatch(YourBackendTag, object, namespace=scheduler_dispatch_namespace)
def _clear(tag: YourBackendTag, scheduler_instance):
    """Remove all loggers and clear the schedule.

    Parameters
    ----------
    tag : YourBackendTag
        Tag for dispatch (not used in implementation).
    scheduler_instance : LoggerScheduler
        The scheduler instance to clear.

    Examples
    --------
    >>> scheduler.add_logger(logger1)
    >>> scheduler.add_logger(logger2)
    >>> scheduler.clear()
    Cleared all loggers from scheduler
    >>> print(len(scheduler.loggers))
    0
    """


@dispatch(YourBackendTag, object, namespace=scheduler_dispatch_namespace)
def _get_status(tag: YourBackendTag, scheduler_instance) -> Dict:
    """Get current scheduler status.

    Parameters
    ----------
    tag : YourBackendTag
        Tag for dispatch (not used in implementation).
    scheduler_instance : LoggerScheduler
        The scheduler instance to get status from.

    Returns
    -------
    dict
        Dictionary containing backend name, logger counts, and details.
        Keys include:
        - 'backend' (str): Name of the backend ('yourbackend')
        - 'total_loggers' (int): Number of registered loggers
        - 'total_jobs' (int): Number of scheduled jobs
        - 'logger_details' (list): List of dicts with logger information

    Examples
    --------
    >>> scheduler.add_logger(logger1)
    >>> status = scheduler.get_status()
    >>> print(f"Backend: {status['backend']}")
    Backend: yourbackend
    >>> print(f"Total loggers: {status['total_loggers']}")
    Total loggers: 1
    >>> print(status['logger_details'][0]['interval'])
    60
    """



@dispatch(YourBackendTag, object, namespace=scheduler_dispatch_namespace)
def _run_pending(tag: YourBackendTag, scheduler_instance):
    """Run all pending jobs manually.

    Parameters
    ----------
    tag : YourBackendTag
        Tag for dispatch (not used in implementation).
    scheduler_instance : LoggerScheduler
        The scheduler instance to run pending jobs on.

    Examples
    --------
    >>> import time
    >>> scheduler = LoggerScheduler(scheduler_dispatch_tag=YourBackendTag())
    >>> scheduler.add_logger(logger1)
    >>> while True:
    ...     scheduler.run_pending()
    ...     time.sleep(1)
    """


@dispatch(YourBackendTag, object, namespace=scheduler_dispatch_namespace)
def _run(tag: YourBackendTag, scheduler_instance):
    """Start the scheduler in a blocking loop.

    This method blocks indefinitely, running scheduled jobs at the configured
    check interval. Press Ctrl+C to stop.

    Parameters
    ----------
    tag : YourBackendTag
        Tag for dispatch (not used in implementation).
    scheduler_instance : LoggerScheduler
        The scheduler instance to run.

    Examples
    --------
    >>> scheduler = LoggerScheduler(scheduler_dispatch_tag=YourBackendTag())
    >>> scheduler.add_logger(logger1)
    >>> scheduler.add_logger(logger2)
    >>> scheduler.run()  # Blocks until Ctrl+C
    Starting scheduler with 2 logger(s)
    Press Ctrl+C to stop
    ^C
    Scheduler stopped by user
    """