class SchedulerDispatchTag:
    """Base class for scheduler backend dispatch tags.

    All backend-specific tags should inherit from this class.

    The Logger Scheduler uses a **tag-based dispatch system** to support multiple
    scheduling backends. This allows you to plug in different scheduling libraries
    (like `schedule`, `APScheduler`, etc.) without modifying the core scheduler code.

    How It Works
    ------------
    The scheduler uses `multipledispatch` to route method calls to backend-specific
    implementations:

    1. **User calls** a method like `scheduler.add_logger(logger)`
    2. **LoggerScheduler** looks up `_add_logger` in the dispatch namespace
    3. **Dispatcher** routes to the correct implementation based on the backend tag type
    4. **Backend function** executes with the scheduler's configuration

    Required Backend Functions
    --------------------------
    To create a custom scheduler backend, you must implement these 7 functions using
    the `@dispatch` decorator:

    - **_create_scheduler** - Initialize backend (tag: YourTag) → Scheduler instance
    - **_add_logger** - Add logger to schedule (tag, scheduler, logger, interval) → None
    - **_remove_logger** - Remove logger (tag, scheduler, logger) → bool
    - **_clear** - Clear all loggers (tag, scheduler) → None
    - **_get_status** - Get scheduler status (tag, scheduler) → Dict
    - **_run_pending** - Run pending jobs (tag, scheduler) → None
    - **_run** - Start scheduler loop (tag, scheduler) → None

    Function: _create_scheduler
    ---------------------------
    **Purpose:** Initialize the backend scheduler instance.

    **Signature:**

        @dispatch(YourTag, namespace=scheduler_dispatch_namespace)
        def _create_scheduler(tag: YourTag):
            return YourScheduler()

    **Expectations:**

    - Return a new scheduler instance from your library
    - Do NOT start the scheduler yet (that happens in `_run`)
    - The returned object will be stored in `scheduler_instance.schedule`

    Function: _add_logger
    ---------------------
    **Purpose:** Schedule a logger to run periodically.

    **Signature:**

        @dispatch(YourTag, object, object, int, namespace=scheduler_dispatch_namespace)
        def _add_logger(tag, scheduler_instance, logger, interval_seconds):
            pass

    **Expectations:**

    - Check if `logger in scheduler_instance.loggers` → raise `ValueError` if True
    - Add logger to `scheduler_instance.loggers` list
    - Schedule `logger.log()` to run every `interval_seconds` seconds
    - Store a job reference on the logger instance (e.g., `logger._mybackend_job`)
    - Print status if `scheduler_instance.verbose` is True

    **Access to:**

    - `scheduler_instance.schedule` - Your scheduler from `_create_scheduler`
    - `scheduler_instance.loggers` - List of registered loggers
    - `scheduler_instance.verbose` - Boolean flag for printing
    - `logger.log` - Method to schedule
    - `interval_seconds` - How often to run

    Function: _remove_logger
    ------------------------
    **Purpose:** Remove a logger from the schedule.

    **Signature:**

        @dispatch(YourTag, object, object, namespace=scheduler_dispatch_namespace)
        def _remove_logger(tag, scheduler_instance, logger) -> bool:
            pass

    **Expectations:**

    - Return `False` if logger not in `scheduler_instance.loggers`
    - Cancel/remove the scheduled job using your backend's API
    - Remove logger from `scheduler_instance.loggers` list
    - Delete the job reference from the logger instance
    - Return `True` on successful removal

    Function: _clear
    ----------------
    **Purpose:** Remove all loggers and clear all scheduled jobs.

    **Signature:**

        @dispatch(YourTag, object, namespace=scheduler_dispatch_namespace)
        def _clear(tag, scheduler_instance):
            pass

    **Expectations:**

    - Clear all jobs from your backend scheduler
    - Loop through `scheduler_instance.loggers` and delete job references
    - Clear the `scheduler_instance.loggers` list

    Function: _get_status
    ---------------------
    **Purpose:** Return current scheduler status information.

    **Signature:**

        @dispatch(YourTag, object, namespace=scheduler_dispatch_namespace)
        def _get_status(tag, scheduler_instance) -> Dict:
            return {'backend': 'mybackend', 'total_loggers': 0}

    **Required return keys:**

    - `'backend'` (str): Your backend name (e.g., 'mybackend')
    - `'total_loggers'` (int): `len(scheduler_instance.loggers)`

    **Optional return keys:**

    - `'total_jobs'` (int): Number of scheduled jobs
    - `'logger_details'` (list): Per-logger information

    Function: _run_pending
    ----------------------
    **Purpose:** Execute jobs that are currently due (non-blocking).

    **Signature:**

        @dispatch(YourTag, object, namespace=scheduler_dispatch_namespace)
        def _run_pending(tag, scheduler_instance):
            pass

    **Expectations:**

    - Check your backend for jobs that should run now
    - Execute those jobs
    - Return immediately (don't block)
    - If not supported: implement as `pass` or raise `NotImplementedError`

    Function: _run
    --------------
    **Purpose:** Start the scheduler and run indefinitely until interrupted.

    **Signature:**

        @dispatch(YourTag, object, namespace=scheduler_dispatch_namespace)
        def _run(tag, scheduler_instance):
            try:
                while True:
                    # Check and run pending jobs
                    time.sleep(scheduler_instance.check_interval)
            except KeyboardInterrupt:
                pass

    **Expectations:**

    - Print startup message if `scheduler_instance.verbose` is True
    - Start running scheduled jobs (blocking)
    - Catch `KeyboardInterrupt` gracefully
    - Print shutdown message if verbose

    Backend State Management
    ------------------------
    The `scheduler_instance` parameter provides access to:

    - `.loggers` (List[SensorLogger]): Registered loggers
    - `.schedule` (object): Backend scheduler (from `_create_scheduler`)
    - `.check_interval` (float): Seconds between schedule checks
    - `.verbose` (bool): Whether to print status messages
    - `.log_path` (Path): Path for scheduler logs

    Examples
    --------
    Creating a custom backend tag:

    >>> from atmospyre.scheduler.logger_scheduler import SchedulerDispatchTag
    >>> class MyBackendTag(SchedulerDispatchTag):
    ...     '''Tag for my custom backend.'''
    ...     pass

    Using a backend tag:

    >>> from atmospyre.scheduler import LoggerScheduler
    >>> from my_backend import MyBackendTag
    >>> scheduler = LoggerScheduler(scheduler_dispatch_tag=MyBackendTag())

    See Also
    --------
    scheduler_dispatch_namespace : Global namespace for dispatch functions
    LoggerScheduler : Main scheduler class that uses these tags
    """
    pass