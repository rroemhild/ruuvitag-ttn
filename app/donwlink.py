import logging

from pycom import nvs_set
from ustruct import unpack

from .constants import (
    DONWLINK_CFG_PORT,
    DOWNLINK_DSTIME,
    DOWNLINK_SCAN_TIMEOUT,
    NVS_DSTIME,
    NVS_BTOUT,
)


log = logging.getLogger("main")


def set_deepsleep(dstime):
    dstime = max(dstime, 30)  # Minimum is 30 seconds
    log.debug("Set deepsleep timer to {} seconds".format(dstime))
    nvs_set(NVS_DSTIME, dstime)


def set_bt_timeout(timeout):
    timeout = max(timeout, 1)  # Minimum is 1 seconds
    log.debug("Set bluetooth scan timeout to {} seconds".format(timeout))
    nvs_set(NVS_BTOUT, timeout)


def process_downlink(payload, port):
    if port == DONWLINK_CFG_PORT:
        # Max 5 bytes are allowed for config payload
        if len(payload) > 5:
            return

        while len(payload) > 0:
            dtype = payload[0]  # downlink config type

            # Deeplseep time requiere two bytes
            if dtype == DOWNLINK_DSTIME and len(payload) > 2:
                dstime = unpack("!H", payload[1:3])[0]
                set_deepsleep(dstime)
                payload = payload[3:]
            # Bluetooth timeout requiere one byte
            elif dtype == DOWNLINK_SCAN_TIMEOUT and len(payload) > 1:
                set_bt_timeout(payload[1])
                payload = payload[2:]
            # Stop if type or length does not match
            else:
                break
