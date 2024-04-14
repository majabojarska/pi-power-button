#!/usr/bin/env python

import logging
import signal
import subprocess
from pathlib import Path

from gpiozero import Button

GPIO_BUTTON: int = 3
SHUTDOWN_DELAY_DEFAULT: int = 30
TIME_BOUNCE = 0.8

logger = logging.getLogger(__name__)


def _schedule_shutdown(time: int = SHUTDOWN_DELAY_DEFAULT) -> None:
    logger.info("scheduling shutdown")
    subprocess.call(["shutdown", "--poweroff", str(time)], shell=False)


def _cancel_shutdown() -> None:
    logger.info("cancelling shutdown")
    subprocess.call(["shutdown", "-c"], shell=False)


def _is_shutdown_scheduled() -> bool:
    return Path("/run/systemd/shutdown/scheduled").exists()


def _on_click() -> None:
    if _is_shutdown_scheduled():
        logger.info("shutdown already scheduled")
        _cancel_shutdown()
        return

    _schedule_shutdown()


if __name__ == "__main__":
    button = Button(
        pin=GPIO_BUTTON, pull_up=True, bounce_time=TIME_BOUNCE, when_pressed=_on_click
    )
    logger.info("button listener configured")
    signal.pause()
