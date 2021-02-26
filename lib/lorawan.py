import logging
import usocket
import ubinascii

from network import LoRa

def get_device_eui():
    lora = LoRa(mode=LoRa.LORAWAN)
    print(ubinascii.hexlify(lora.mac()).upper().decode("utf-8"))


def lora_erase():
    lora = LoRa(mode=LoRa.LORAWAN)
    lora.nvram_erase()


class LoRaWAN:
    def __init__(self, app_eui, app_key, region=LoRa.EU868, sf=7, adr=True, dr=5, timeout=15):
        """Setup LoRaWAN"""
        self._timeout = timeout
        self._app_eui = ubinascii.unhexlify(app_eui)
        self._app_key = ubinascii.unhexlify(app_key)
        self._socket = None
        self._dr = dr
        self.log = logging.getLogger("lorawan")
        self.lora = LoRa(mode=LoRa.LORAWAN, region=region, sf=sf, adr=adr)
        self.setup()

    def setup(self):
        """Try to restore from nvram or join the network with OTAA"""
        self.lora.nvram_restore()

        if not self.lora.has_joined():
            self.join()
        else:
            self.open_socket()

    def join(self):
        self.log.debug("Send join request")
        timeout = self._timeout * 1000
        self.lora.join(
            activation=LoRa.OTAA,
            auth=(self._app_eui, self._app_key),
            timeout=timeout,
            dr=self._dr,
        )

        if self.lora.has_joined():
            self.lora.nvram_save()
            self.open_socket()
            self.log.debug("Joined network")

    def open_socket(self, timeout=6):
        self._socket = usocket.socket(usocket.AF_LORA, usocket.SOCK_RAW)
        self._socket.setsockopt(usocket.SOL_LORA, usocket.SO_DR, self._dr)
        self._socket.settimeout(timeout)

    def reset(self):
        """Reset socket, clear on device stored LoRaWAN session and re-join the network"""
        self._socket.close()
        self.lora.lora_erase()
        self.join()

    def send(self, payload, port=1):
        """Send out uplink data as bytes"""
        self._socket.bind(port)
        if self.lora.has_joined():
            if isinstance(payload, (float, str, int)):
                payload = bytes([payload])
            self.log.debug("Send payload: {}".format(payload))
            self._socket.setblocking(True)
            self._socket.send(payload)
            self._socket.setblocking(False)
            self.lora.nvram_save()

    def recv(self, rbytes=1):
        """Receive bytes from downlink"""
        retval = self._socket.recvfrom(rbytes)
        self.log.debug("Recv payload: {}, port: {}".format(retval[0], retval[1]))
        return retval

    def shutdown(self):
        """Shutdown LoRa modem"""
        self._socket.close()
        self.lora.power_mode(LoRa.SLEEP)
