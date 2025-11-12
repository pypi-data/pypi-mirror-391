"""
Home to specialized exceptions for the Sleepytime application.
"""


class SleepyTimeExit(SystemExit):
    """
    Exception raised when the application is exiting.
    This is used to differentiate between normal exit and other exceptions.
    """

    pass
