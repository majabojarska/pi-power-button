#!/usr/bin/env python

import logging
import subprocess
import time
from pathlib import Path

import RPi.GPIO as GPIO

GPIO_BUTTON: int = 3
SHUTDOWN_DELAY_DEFAULT: int = 30

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
    else:
        _schedule_shutdown()


def serve():
    while True:
        GPIO.wait_for_edge(GPIO_BUTTON, GPIO.FALLING)
        logger.info("power button pressed")
        _on_click()


def _setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)


if __name__ == "__main__":
    _setup_gpio()
    serve()
