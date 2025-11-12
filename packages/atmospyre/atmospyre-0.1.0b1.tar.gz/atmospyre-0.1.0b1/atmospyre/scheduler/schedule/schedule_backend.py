"""Schedule library backend for LoggerScheduler.

This module provides a backend implementation using the 'schedule' library,
a simple, lightweight job scheduling library for Python.

This uses multipledispatch with a tag-based dispatch pattern. Functions are
dispatched based on a ScheduleTag type rather than the actual argument types,
allowing the dispatch mechanism to work with any scheduler/logger types.

Install with: pip install schedule
"""

import schedule
import time
from typing import Dict
from multipledispatch import dispatch

from atmospyre.loggers import SensorLogger
from atmospyre.scheduler.logger_scheduler import (
    SchedulerDispatchTag,
    scheduler_dispatch_namespace
)


class ScheduleTag(SchedulerDispatchTag):
    """Tag class for schedule backend type dispatch.

    This class inherits from SchedulerDispatchTag and serves as a type marker
    for multipledispatch, allowing functions to be dispatched to the schedule
    backend without requiring specific types for all arguments.

    Examples
    --------
    >>> from atmospyre.scheduler import LoggerScheduler, ScheduleTag
    >>> scheduler = LoggerScheduler(scheduler_dispatch_tag=ScheduleTag)
    >>> print(scheduler)
    LoggerScheduler(backend=schedule, loggers=0)
    """
    pass


@dispatch(ScheduleTag, namespace=scheduler_dispatch_namespace)
def _create_scheduler(tag: ScheduleTag):
    """Create and return a schedule scheduler instance.

    Parameters
    ----------
    tag : ScheduleTag
        Tag for dispatch (not used in implementation).

    Returns
    -------
    schedule.Scheduler
        A new scheduler instance from the schedule library.

    Examples
    --------
    >>> tag = ScheduleTag()
    >>> sched = _create_scheduler(tag)
    >>> print(type(sched).__name__)
    Scheduler
    """
    return schedule.Scheduler()


@dispatch(ScheduleTag, object, object, int, namespace=scheduler_dispatch_namespace)
def _add_logger(
    tag: ScheduleTag,
    scheduler_instance,
    logger: SensorLogger,
    interval_seconds: int
):
    """Add a logger to the schedule-based scheduler.

    Parameters
    ----------
    tag : ScheduleTag
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
    >>> from atmospyre.scheduler import LoggerScheduler, ScheduleTag
    >>> from atmospyre.loggers import SensorLogger
    >>> scheduler = LoggerScheduler(scheduler_dispatch_tag=ScheduleTag)
    >>> logger = SensorLogger(sensor=my_sensor, interval_seconds=60)
    >>> scheduler.add_logger(logger)
    Added logger <SensorLogger> with interval 60s

    Notes
    -----
    A reference to the scheduled job is stored on the logger instance as
    ``_schedule_job`` for later removal. This is an internal implementation
    detail and should not be accessed directly.
    """
    # Check if logger already exists
    if logger in scheduler_instance.loggers:
        raise ValueError(f"Logger {logger} is already registered")

    # Add logger to the list
    scheduler_instance.loggers.append(logger)

    # Schedule the logger's log method
    job = scheduler_instance.schedule.every(interval_seconds).seconds.do(logger.log)

    # Store job reference on logger for later removal
    logger._schedule_job = job

    if hasattr(scheduler_instance, 'verbose') and scheduler_instance.verbose:
        print(f"Added logger {logger} with interval {interval_seconds}s")


@dispatch(ScheduleTag, object, object, namespace=scheduler_dispatch_namespace)
def _remove_logger(
    tag: ScheduleTag,
    scheduler_instance,
    logger: SensorLogger
) -> bool:
    """Remove a logger from the schedule-based scheduler.

    Parameters
    ----------
    tag : ScheduleTag
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

    Notes
    -----
    This function cancels the scheduled job and removes the ``_schedule_job``
    attribute from the logger instance.
    """
    if logger not in scheduler_instance.loggers:
        return False

    # Cancel the scheduled job
    if hasattr(logger, '_schedule_job'):
        scheduler_instance.schedule.cancel_job(logger._schedule_job)
        delattr(logger, '_schedule_job')

    # Remove from logger list
    scheduler_instance.loggers.remove(logger)

    if hasattr(scheduler_instance, 'verbose') and scheduler_instance.verbose:
        print(f"Removed logger {logger}")

    return True


@dispatch(ScheduleTag, object, namespace=scheduler_dispatch_namespace)
def _clear(tag: ScheduleTag, scheduler_instance):
    """Remove all loggers and clear the schedule.

    Parameters
    ----------
    tag : ScheduleTag
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

    Notes
    -----
    This function clears all scheduled jobs from the underlying schedule
    instance and removes all ``_schedule_job`` attributes from logger instances.
    """
    # Clear all jobs from the schedule
    scheduler_instance.schedule.clear()

    # Clear job references from loggers
    for logger in scheduler_instance.loggers:
        if hasattr(logger, '_schedule_job'):
            delattr(logger, '_schedule_job')

    # Clear logger list
    scheduler_instance.loggers.clear()

    if hasattr(scheduler_instance, 'verbose') and scheduler_instance.verbose:
        print("Cleared all loggers from scheduler")


@dispatch(ScheduleTag, object, namespace=scheduler_dispatch_namespace)
def _get_status(tag: ScheduleTag, scheduler_instance) -> Dict:
    """Get current scheduler status.

    Parameters
    ----------
    tag : ScheduleTag
        Tag for dispatch (not used in implementation).
    scheduler_instance : LoggerScheduler
        The scheduler instance to get status from.

    Returns
    -------
    dict
        Dictionary containing backend name, logger counts, and details.
        Keys include:
        - 'backend' (str): Name of the backend ('schedule')
        - 'total_loggers' (int): Number of registered loggers
        - 'total_jobs' (int): Number of scheduled jobs
        - 'logger_details' (list): List of dicts with logger information

    Examples
    --------
    >>> scheduler.add_logger(logger1)
    >>> status = scheduler.get_status()
    >>> print(f"Backend: {status['backend']}")
    Backend: schedule
    >>> print(f"Total loggers: {status['total_loggers']}")
    Total loggers: 1
    >>> print(status['logger_details'][0]['interval'])
    60
    """
    jobs = scheduler_instance.schedule.get_jobs()

    logger_details = []
    for logger in scheduler_instance.loggers:
        if hasattr(logger, '_schedule_job'):
            job = logger._schedule_job
            logger_details.append({
                'logger': str(logger),
                'interval': job.interval,
                'unit': job.unit,
                'next_run': str(job.next_run) if job.next_run else None
            })

    return {
        'backend': 'schedule',
        'total_loggers': len(scheduler_instance.loggers),
        'total_jobs': len(jobs),
        'logger_details': logger_details
    }


@dispatch(ScheduleTag, object, namespace=scheduler_dispatch_namespace)
def _run_pending(tag: ScheduleTag, scheduler_instance):
    """Run all pending jobs manually.

    Parameters
    ----------
    tag : ScheduleTag
        Tag for dispatch (not used in implementation).
    scheduler_instance : LoggerScheduler
        The scheduler instance to run pending jobs on.

    Examples
    --------
    >>> import time
    >>> scheduler = LoggerScheduler(scheduler_dispatch_tag=ScheduleTag)
    >>> scheduler.add_logger(logger1)
    >>> while True:
    ...     scheduler.run_pending()
    ...     time.sleep(1)

    Notes
    -----
    This function checks the schedule for any jobs that should run based on
    their interval and last execution time, then executes them. It does not
    block - it only runs jobs that are currently due.
    """
    scheduler_instance.schedule.run_pending()


@dispatch(ScheduleTag, object, namespace=scheduler_dispatch_namespace)
def _run(tag: ScheduleTag, scheduler_instance):
    """Start the scheduler in a blocking loop.

    This method blocks indefinitely, running scheduled jobs at the configured
    check interval. Press Ctrl+C to stop.

    Parameters
    ----------
    tag : ScheduleTag
        Tag for dispatch (not used in implementation).
    scheduler_instance : LoggerScheduler
        The scheduler instance to run.

    Examples
    --------
    >>> scheduler = LoggerScheduler(scheduler_dispatch_tag=ScheduleTag)
    >>> scheduler.add_logger(logger1)
    >>> scheduler.add_logger(logger2)
    >>> scheduler.run()  # Blocks until Ctrl+C
    Starting scheduler with 2 logger(s)
    Press Ctrl+C to stop
    ^C
    Scheduler stopped by user

    Notes
    -----
    The scheduler continuously checks for pending jobs at intervals specified
    by ``scheduler_instance.check_interval`` (default: 1.0 seconds). When a
    KeyboardInterrupt is received (Ctrl+C), the scheduler prints a stop message
    and exits gracefully.
    """
    if hasattr(scheduler_instance, 'verbose') and scheduler_instance.verbose:
        print(f"Starting scheduler with {len(scheduler_instance.loggers)} logger(s)")
        print("Press Ctrl+C to stop")

    try:
        while True:
            scheduler_instance.schedule.run_pending()
            time.sleep(scheduler_instance.check_interval)
    except KeyboardInterrupt:
        if hasattr(scheduler_instance, 'verbose') and scheduler_instance.verbose:
            print("\nScheduler stopped by user")