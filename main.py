import machine

import settings

from ustruct import pack
from lorawan import LoRaWAN
from ruuvitag.scanner import RuuviTagScanner


LoRaWAN.DEBUG = settings.DEBUG


def pack_temp(temp):
    """Temperature in 0.005 degrees as signed short"""
    temp_conv = round(round(temp, 2) / 0.005)
    return pack("!h", temp_conv)


def pack_humid(hum):
    """Humidity in 0.0025 percent as unsigned short"""
    hum_conv = round(round(hum, 2) / 0.0025)
    return pack("!H", hum_conv)


def main():
    payload = b""

    rts = RuuviTagScanner(settings.RUUVITAGS)

    # get all data and prepare payload and add them to the payload
    print("Scan for ruuvitags")
    for ruuvitag in rts.find_ruuvitags(timeout=settings.TIMEOUT):
        id_payload = settings.RUUVITAGS.index(ruuvitag.mac.encode())
        payload = (
            payload
            + bytes([id_payload])
            + pack_temp(ruuvitag.temperature)
            + pack_humid(ruuvitag.humidity)
            + pack("!H", ruuvitag.battery_voltage - 1600)  # battery
            + bytes([ruuvitag.rssi * -1])  # rssi
        )

    print("Setup lorawan")
    node = LoRaWAN(settings.NODE_APP_EUI, settings.NODE_APP_KEY)

    print("Send payload")
    node.send(payload)
    node.shutdown()

    if settings.DEBUG is False:
        print("Enter deepsleep for {} seconds".format(settings.NODE_DEEPSLEEP))
        machine.deepsleep(settings.NODE_DEEPSLEEP * 1000)


if __name__ == "__main__":
    main()
