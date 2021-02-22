import machine
import settings

from lorawan import LoRaWAN
from ruuvitag.scanner import RuuviTagScanner

from app.encoder import encode_battery, encode_humid, encode_temp


LoRaWAN.DEBUG = settings.DEBUG


def main():
    # Payload buffer
    payload = b""

    # Initialize  bluetooth and ruuvitag scanner
    rts = RuuviTagScanner(settings.RUUVITAGS)

    # Scan for whitelisted RuuviTags and add sensor data as bytes to the payload buffer.
    # Each tag wil be identified by his index from the whitelist
    # Sensor data: termperature, humidity, battery voltage and RSSI
    print("Scan for ruuvitags")
    for ruuvitag in rts.find_ruuvitags(timeout=settings.TIMEOUT):
        ruuvitag_id = settings.RUUVITAGS.index(ruuvitag.mac.encode())
        payload = (
            payload
            + bytes([ruuvitag_id])
            + encode_temp(ruuvitag.temperature)
            + encode_humid(ruuvitag.humidity)
            + encode_battery(ruuvitag.battery_voltage)
            + bytes([ruuvitag.rssi * -1])  # rssi
        )

    print("Setup LoRaWAN node")
    node = LoRaWAN(settings.NODE_APP_EUI, settings.NODE_APP_KEY)

    print("Send payload on port=1")
    node.send(payload, port=1)

    print("Shutdown LoRaWAN node")
    node.shutdown()

    # Do not enter deepsleep if DEBUG is true
    if not settings.DEBUG:
        print("Enter deepsleep for {} seconds".format(settings.NODE_DEEPSLEEP))
        machine.deepsleep(settings.NODE_DEEPSLEEP * 1000)


if __name__ == "__main__":
    main()
