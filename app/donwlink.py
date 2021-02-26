import ustruct

from pycom import nvs_get, nvs_set
from ubinascii import hexlify, unhexlify

from .constants import DONWLINK_CFG_PORT, DOWNLINK_DSTIME, DOWNLINK_SCAN_TIMEOUT, NVS_DSTIME, NVS_BTOUT


# Dwonlinks to implement
# . re-join
# . sleep time
# . scan timeout
# add/remove mac


def set_deepsleep(dstime):
    dstime = max(dstime, 30)  # Minimum is 30 seconds
    print("Set delay to {} seconds".format(dstime))
    nvs_set(NVS_DSTIME, dstime)  # Set deepsleep in seconds


def set_bt_timeout(timeout):
    timeout = max(timeout, 1)  # Minimum is 1 seconds
    print("Set bluetooth scan timeout to {} seconds".format(timeout))
    nvs_set(NVS_BTOUT, timeout)  # Set deepsleep in seconds


def process_downlink(payload, port):
    if port == DONWLINK_CFG_PORT:
        # Return if payload is greater than 5 bytes
        if len(payload) > 5:
            return

        while len(payload) > 0:
            dtype = payload[0]  # downlink config type

            # Deeplseep time requeres two bytes
            if dtype == DOWNLINK_DSTIME and len(payload) > 2:
                dstime = ustruct.unpack("!H", payload[1:3])[0]
                set_deepsleep(dstime)
                payload = payload[3:]
            # Bluetooth timeout requers one byte
            elif dtype == DOWNLINK_SCAN_TIMEOUT and len(payload) > 1:
                set_bt_timeout(payload[1])
                payload = payload[2:]
            # Stop if type or length does not match
            else:
                break
