#!/usr/bin/env python3

import logging
import signal
import subprocess
from pathlib import Path

import systemd.daemon
from RPi import GPIO
from systemd.journal import JournalHandler

GPIO_BUTTON: int = 3
SHUTDOWN_DELAY_DEFAULT: int = 1  # min
TIME_BOUNCE = 500  # ms

log = logging.getLogger(__name__)
log.addHandler(JournalHandler())
log.setLevel(logging.DEBUG)


def _schedule_shutdown(time: int = SHUTDOWN_DELAY_DEFAULT) -> None:
    log.info("scheduling shutdown")
    subprocess.call(
        ["shutdown", "--poweroff", str(time), "shutdown scheduled via power button"],
        shell=False,
    )


def _cancel_shutdown() -> None:
    log.info("cancelling shutdown")
    subprocess.call(
        ["shutdown", "-c", "shutdown cancelled via power button"], shell=False
    )


def _is_shutdown_scheduled() -> bool:
    return Path("/run/systemd/shutdown/scheduled").exists()


def _on_press(channel: int) -> None:
    log.debug("button pressed (channel %s)", channel)
    if _is_shutdown_scheduled():
        log.info("found scheduled shutdown")
        _cancel_shutdown()
        return

    _schedule_shutdown()


def main():
    GPIO.setmode(GPIO.BCM)
    # To silence warning about using hardware pullup - this is deliberate.
    GPIO.setwarnings(False)
    GPIO.setup(GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(
        GPIO_BUTTON, GPIO.FALLING, callback=_on_press, bouncetime=TIME_BOUNCE
    )
    systemd.daemon.notify("READY=1")

    signal.pause()
    log.info("stopping listener...")


if __name__ == "__main__":
    main()
