#!/usr/bin/env python

import logging
import signal
import subprocess
from pathlib import Path

from RPi import GPIO

GPIO_BUTTON: int = 3
SHUTDOWN_DELAY_DEFAULT: int = 1  # min
TIME_BOUNCE = 3000  # ms

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def _schedule_shutdown(time: int = SHUTDOWN_DELAY_DEFAULT) -> None:
    logger.info("scheduling shutdown")
    subprocess.call(
        ["shutdown", "--poweroff", str(time), "shutdown scheduled via power button"],
        shell=False,
    )


def _cancel_shutdown() -> None:
    logger.info("cancelling shutdown")
    subprocess.call(
        ["shutdown", "-c", "shutdown cancelled via power button"], shell=False
    )


def _is_shutdown_scheduled() -> bool:
    return Path("/run/systemd/shutdown/scheduled").exists()


def _on_press(channel: int) -> None:
    logger.debug("button pressed (channel %s)!", channel)
    if _is_shutdown_scheduled():
        logger.info("shutdown already scheduled")
        _cancel_shutdown()
        return

    _schedule_shutdown()


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(
        GPIO_BUTTON, GPIO.FALLING, callback=_on_press, bouncetime=TIME_BOUNCE
    )

    signal.pause()
    logger.info("stopping listener...")
