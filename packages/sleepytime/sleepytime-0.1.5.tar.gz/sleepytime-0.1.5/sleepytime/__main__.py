from tendo.singleton import SingleInstance, SingleInstanceException

from sleepytime.__version__ import __version__
from sleepytime.log import setup_logging
from sleepytime.window import SleepyTimeWindow

base_logger = setup_logging()

if __name__ == "__main__":
    # you must give a var for SingleInstance to live in... otherwise
    # __del__ is likely to get called in it and delete the instance file.
    try:
        t = SingleInstance()
    except SingleInstanceException:
        base_logger.error("Another instance of sleepytime is already running.")
        raise RuntimeError(
            "Another instance of sleepytime is already running, quitting."
        )

    base_logger.info(f"Starting sleepytime {__version__}.")
    SleepyTimeWindow().run()
