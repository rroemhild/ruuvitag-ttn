=========================================
Publish RuuviTag sensor data with LoRaWAN
=========================================

This repository contains the up to date snippets for the `Publish RuuviTag sensor data on The Things Network <https://ruuvitag-ttn.readthedocs.io>`_ tutorial.

This PoC uses settings specifically for connecting to LoRaWAN networks within the European 868 MHz region. For other regions usage, please see the `settings.py` and `lib/lorawan.py` file for relevant sections that need to be changed.


Uplink data format
------------------

For each RuuviTag we send 8 bytes. The RuuviTag ID is the index from the mac address in the `settings.py` list. We match this later in the decoder.

+--------+---------------------------------------------+
| Offset | Description                                 |
+========+=============================================+
| 0      | Tag ID (8bit)                               |
+--------+---------------------------------------------+
| 1-2    | Temperature in 0.005 degrees (16bit signed) |
+--------+---------------------------------------------+
| 3-4    | Humidity in 0.0025% (16bit unsigned)        |
+--------+---------------------------------------------+
| 5-6    | Batter voltage + 1600 (16bit unsigned)      |
+--------+---------------------------------------------+
| 7-8    | RSSI * -1 (8bit)                            |
+--------+---------------------------------------------+

In example for 2 RuuviTags the following payload will be send:

.. code-block:: python

    b'\x00\x05$\x8e\xf8\x04\x8f[\x01\x11d/@\x05\rB'

+----+------+--------+---------+------+----+------+--------+---------+------+
| ID | Temp | Humid  | Voltage | RSSI | ID | Temp | Humid  | Voltage | RSSI |
+====+======+========+=========+======+====+======+========+=========+======+
| 00 | 0524 | 8EF8   | 048F    | 5B   | 01 | 1164 | 2F40   | 050D    | 42   |
+----+------+--------+---------+------+----+------+--------+---------+------+

Read more about the data format used in this project in the `Ruuvi Sensor Data Format 5 Protocol Specification <https://github.com/ruuvi/ruuvi-sensor-protocols#data-format-5-protocol-specification>`_.



Downlink format
---------------

The device can be configured by downlink. Currently only the settings ``NODE_DEEPSLEEP`` and ``NODE_SCAN_TIMEOUT`` are supported.


Config downlink
+++++++++++++++

Port 1 is used to configure the device settings. Every setting has a bytes that identifies the payload.

Device deepsleep timer
~~~~~~~~~~~~~~~~~~~~~~

The deepsleep timer setting use 3 bytes. First byte indicates the deepsleep timer config and must be set to ``1``, followed by 2 bytes (16bit unsigned) for the seconds. Minimum sleeptime is 30 seconds.

**Example:** Set the deepsleep timer to 30 seconds ``01001e``.

+----+---------+
| ID | Seconds |
+====+=========+
| 01 | 001e    |
+----+---------+


Device scan timeout
~~~~~~~~~~~~~~~~~~~

The bluetooth scan timeout defines how long the lib should listen for Ruuvitag data. Higher timeout may find Ruuvitags that are farer away from the device, with the cost of more energy consumtion.

The scan timeout settings use 2 bytes. Teh first byte indicates the scan timeout and must be set to ``2``, follow by 1 byte for for the seconds. Minimum scan timeout is 1 second.

**Example:** Set the bluetooth scan timeout to 4 seconds ``0205``.

+----+---------+
| ID | Seconds |
+====+=========+
| 01 | 001e    |
+----+---------+


Combined downlink
~~~~~~~~~~~~~~~~~

The config downlinks can be combined in one downlink.

***Example:** Set the sleeptimer to 30 seconds and the scan timeout to 5 seconds ``01001e0205``

+----+---------+-----+---------+
| ID | Seconds | ID  | Seconds |
+====+=========+=====+=========+
| 01 | 001e    | 02  | 05      |
+----+---------+-----+---------+


Payload Format Decoder
----------------------

Example payload format decoder for the The Things Network Console. The var `map` is used to identify each Ruuvitag by name. The oder must match the order in the `RUUVITAG` list in the `settings.py`.

.. code-block:: javascript

    var map = ["outdoor", "livingroom"];

    function Decoder(bytes, port) {
      var ruuvitags = {};
      var tags = bytes.length / 8;

      for (i=0;i<tags;i+=1) {
        var temperature = (bytes[1] << 8) | bytes[2];
        var humidity = (bytes[3] << 8) | bytes[4];
        var battery = (bytes[5] << 8) | bytes[6];
        var rssi = bytes[7];

        var name = map[bytes[0]];
        ruuvitags[name] = {
            "humidity": parseFloat((humidity * 0.0025).toFixed(2)),
            "temperature": parseFloat((temperature * 0.005).toFixed(2)),
            "battery": battery + 1600,
            "rssi": rssi * -1
        };

        bytes.splice(0, 8);
      }

      return ruuvitags;
    }

    // TTNv3
    function decodeUplink(input) {
      return {
        data: Decoder(input.bytes, input.fPort),
        warnings: [],
        errors: []
      };
    }
