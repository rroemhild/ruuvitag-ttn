import logging
import settings

from pycom import nvs_get
from lorawan import LoRaWAN
from machine import reset, deepsleep
from network import LoRa
from ruuvitag.scanner import RuuviTagScanner

from app.encoder import encode_battery, encode_humid, encode_temp
from app.donwlink import process_downlink
from app.constants import NVS_DSTIME, NVS_BTOUT


def main():
    log = logging.getLogger("main")

    try:
        log.debug("Setup LoRaWAN node")
        node = LoRaWAN(settings.NODE_APP_EUI, settings.NODE_APP_KEY)

        # Overwrite bluetooth scan timeout from nvs ram
        scan_timeout = nvs_get(NVS_BTOUT, settings.NODE_SCAN_TIMEOUT)

        # Payload buffer
        payload = b""

        # Initialize bluetooth and ruuvitag scanner
        rts = RuuviTagScanner(settings.RUUVITAGS)

        # Scan for whitelisted RuuviTags and add sensor data as bytes to the payload buffer.
        # Each tag wil be identified by his index from the whitelist
        # Sensor data: termperature, humidity, battery voltage and RSSI
        log.debug("Scan {} seconds for ruuvitags".format(scan_timeout))
        for ruuvitag in rts.find_ruuvitags(timeout=scan_timeout):
            ruuvitag_id = settings.RUUVITAGS.index(ruuvitag.mac.encode())
            payload = (
                payload
                + bytes([ruuvitag_id])
                + encode_temp(ruuvitag.temperature)
                + encode_humid(ruuvitag.humidity)
                + encode_battery(ruuvitag.battery_voltage)
                + bytes([ruuvitag.rssi * -1])  # rssi
            )

        log.debug("Send payload on port 1")
        node.send(payload, port=1)

        log.debug("Get downlink")
        payload, port = node.recv(rbytes=60)
        process_downlink(payload, port)

        log.debug("Shutdown LoRaWAN node")
        node.shutdown()

        # Overwrite deepleep timer from nvs ram
        deepsleep_time = nvs_get(NVS_DSTIME, settings.NODE_DEEPSLEEP)

    except LoRa.timeout:
        log.warning("LoRaWAN join timed out. Retry in 30 seconds.")
        deepsleep_time = 30

    except KeyboardInterrupt:
        log.info("Keyboard interrupt")
        settings.DEBUG = True

    finally:
        # Do not enter deepsleep if DEBUG is true
        if not settings.DEBUG:
            log.debug("Enter deepsleep for {} seconds".format(deepsleep_time))
            deepsleep(deepsleep_time * 1000)

        # When not in debug mode, this will never print to REPL
        print("Enter REPL. Type reset() to restart.")


if __name__ == "__main__":
    main()
