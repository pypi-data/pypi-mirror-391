"""
Home to functionality related to watching the mouse.
"""
import logging
from datetime import timedelta
from threading import Event
from time import sleep, time

from pyautogui import position

log = logging.getLogger(__name__)


def is_moving(max_wait: timedelta = timedelta(minutes=5)) -> bool:
    """
    Returns whether or not the mouse is moving at least once. Will wait up to max_wait for the mouse to move.
    """

    last_positions = set()
    death_time = time() + max_wait.total_seconds()

    while time() < death_time:
        last_positions.add(position())

        if len(last_positions) > 1:
            log.debug("Mouse movement detected")
            return True

        sleep(1)

    return len(last_positions) > 1


def wait_for_no_movement(
    give_up_event: Event, min_time_of_no_movement: timedelta = timedelta(minutes=5)
) -> None:
    """
    Waits for the mouse to stop moving. Will wait for a period of min_time_of_no_movement before returning.
    """
    while is_moving(min_time_of_no_movement):
        sleep(1)
        if give_up_event.is_set():
            log.debug(
                "Give up event for the mouse watcher was set.. acting like the mouse didn't move."
            )
            break

    log.debug("Exiting wait_for_no_movement()")
