Publish RuuviTag sensor data on The Things Network
==================================================

In this tutorial we use a LoPy or FiPy to track temperature and humidity from a location with no WiFi and (in my case) no power supply socket and publish the `RuuviTag <https://tag.ruuvi.com/>`_ sensor data on `The Things Network <https://www.thethingsnetwork.org/>`_ with the `MicroPython RuuviTag Scanner <https://github.com/rroemhild/micropython-ruuvitag>`_.

This tutorial use settings specifically for connecting to The Things Network within the European 868 MHz region. For another usage, please see the ``lib/lorawan.py`` files for relevant sections that need to be changed.

.. note:: The code in this tutorial is not bounded to The Things Network and can also be used with other LoRaWAN networks.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

This tutorial is made available under the `Creative Commons Attribution 4.0 International (CC BY 4.0) <https://creativecommons.org/licenses/by/4.0/>`_  license. Example code is made available under the MIT License.


Hardware
--------

.. image:: ruuvitag-lorawan.jpg
    :scale: 20%
    :align: right

* 1 x LoPy or FiPy from `pycom <https://pycom.io>`_
* 1 x LoRa Antena
* 1 x Expansion Board
* 1 x Case
* 1 x Lithium Ion Polymer Battery or battery pack
* 1 or more `RuuviTags <https://tag.ruuvi.com/>`_


TL;DR
-----

If you are familiar with MicroPython, LoPy, RuuviTag, TTN or just want to get started now, you can get the up to date snippets from the `tutorial repository <https://github.com/rroemhild/ruuvitag-ttn>`_ on GitHub. Modify the settings.py file and copy all \*.py files to your device.


LoRaWAN limitations
-------------------

LoRaWAN is limited on how much data can be send over the network. You can read more about the limitations on:

* `Best practices to limit application payloads <https://www.thethingsnetwork.org/forum/t/best-practices-to-limit-application-payloads/1302>`_
* `Limitations: data rate, packet size, 30 seconds uplink and 10 messages downlink per day Fair Access Policy <https://www.thethingsnetwork.org/forum/t/limitations-data-rate-packet-size-30-seconds-uplink-and-10-messages-downlink-per-day-fair-access-policy/1300>`_

In this tutorial we only use temperature, humidity, battery voltage and RSSI from our tags. To save space we use the `RuuviTag Data Format 5 <https://github.com/ruuvi/ruuvi-sensor-protocols#data-format-5-protocol-specification>`_. But you can pack the data in any format you like or add more sensor data.

.. note:: A good goal is to keep the payload small as possbile. For our 4 data types we need 7 bytes for each RuuviTag and one extra byte as a identifier. In sum we have 8 bytes for each tag. As we don't need to send updates every minute we can add two or three more tags to the payload and send the measurements every 5 or 10 minutes.


Device setup
------------

If you are new to LoPy/FiPy, I recommend you start with `updating your device firmware <https://docs.pycom.io/chapter/gettingstarted/installation/firmwaretool.html>`_ and go on with `REPL & uploading code <https://docs.pycom.io/chapter/toolsandfeatures/repl/>`_. To upload code you can use `FTP <https://docs.pycom.io/chapter/toolsandfeatures/FTP.html>`_, the `Pymakr Plugins <https://docs.pycom.io/chapter/pymakr/>`_ or use something like the `mpfshell <https://github.com/wendlers/mpfshell>`_. I prefer the pymakr plugin for the Pycom modules.

After your are familiar with your device and updated to the latest firmware, it's time to install the `MicroPython RuuviTag Scanner <https://github.com/rroemhild/micropython-ruuvitag>`_. Copy the ``ruuvitag`` directory and all files from the ``lib`` directory from the repository to your device ``/flash/lib/`` directory. With the pymakr plugin you can just "Upload project" the ``pymakr.conf`` file makes sure that only relevant files will be uploaded to your Pycom module.


TTN Device Registration
-----------------------

Before we can start hacking, we need to add our new device to The Things Network. For this we nedd to know the Devicde EUi from the Pycom module we use:

1. Start a MicroPython REPL prompt, i.e. from the pymakr plugin.
2. And run the following commands in the REPL:

    >>> import ubinascii
    >>> from network import LoRa
    >>> lora = LoRa(mode=LoRa.LORAWAN)
    >>> print(ubinascii.hexlify(lora.mac()).upper().decode('utf-8'))

This should print your Device EUI like::

    70B3D5499C89D4CE

3. Follow the steps to `register your device <https://www.thethingsnetwork.org/docs/devices/registration.html>`_.

.. note:: We'll use the Over The Air Activation (OTAA) to negotiate session keys for further communication.


Disable WiFi
------------

Disable WiFi on boot to save some battery. Connect to the REPL prompt and run the following commands to disable Wifi on your Pycom module and it will persist between reboots:

>>> import pycom
>>> pycom.wifi_on_boot(False)


Hands on code
-------------

The device is ready, our TTN is setup, finally we can start add our code. We need to create one directory and three files to organice our code a bit. In our **root-direcorty** we create the files ``main.py`` and ``settings.py`` and the directory ``app`` with another file ``encoder.py``. The ``main.py`` is the file that run on each boot, ``settings.py`` to configure our node and ``app/encoder.py`` to seperate the data encoding from our main file.

Configuration
~~~~~~~~~~~~~

The file ``settings.py`` contains settings for the node. As we use the OTAA activation copy the ``Application EUI`` and ``Application Key`` from the TTN console "device overview" to the appropriate variables.

The `RUUVITAGS` variable is used as a device whitelist for the RuuviTags you want to publish data. In our application we use a the list index from the mac addresses as a device id. In example the first mac address is the device on the stable box and the second from the greenfield sites.

.. note:: Keep in mind that we want a small payload, so only allow some tags to publish sensor data.

.. literalinclude:: ../settings.py


LoRaWAN node
~~~~~~~~~~~~

This file contains the LoRaWAN network setup and don't need to be modified for the European 868 MHz region. The LoRaWAN class abstract the network access. I'll not get in details with this code to keep the focus on the RuuviTag code. In short this class handle the LoRaWAN setup, joins the network, prepare a socket and take care of the OTAA session keys. The latest version is published on `GitHub <https://github.com/rroemhild/pycom-lorawan>`_.. Copy the content from this file to ``lib/lorawan.py``.

.. literalinclude:: ../lib/lorawan.py


Main
~~~~

The ``main.py`` file scans the RuuviTags in range, prepare the sensor data and send the payload to The Things Network. To extend the battery life the device goes into deepsleep mode and wake up after 5 minutes, repeats.

We start to import required modules, lorawan , settings and the RuuviTagScanner. We create all files later, just prepare the import.

.. literalinclude:: ../main.py
    :lines: 1-7

Now we need to pack the sensor data. We use the data format from RuuviTag for temperature and humidity and add a tag id:

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

To achieve this we add a ``encoder.py`` file as module to our ``app`` directory and add the following three function:

.. literalinclude:: ../app/encoder.py

We allready included the file in our ``main.py`` with the line from the import section above:

.. literalinclude:: ../main.py
    :lines: 7

It is a good practice to use functions intead of the global context, so we start with our main function and an empty variable as a bytes object for the payload. Later we'll add the packed sensor data to this object

.. literalinclude:: ../main.py
    :lines: 13,15

Now we initialize the `RuuviTagScanner`. Remember to not scan all the tags around you and add just the ones you need. For this we pass the whitelist from our settings to the class init:

.. literalinclude:: ../main.py
    :lines: 18

We are setup and can start scanning for the tags and pack the data together. You can set a higher timeout in the settings.py file if your tag is on a longer range.

The tag id is his index from the whitelist list we set in `settings.RUUVITAGS`. When you unpack the payload on the target platform you have to remember the tag position from the list.

.. literalinclude:: ../main.py
    :lines: 24-33

When all tags where processed and our payload is ready, we setup up LoRaWAN and send out the payload.

.. literalinclude:: ../main.py
    :lines: 36,39

At the end we send the device into deepsleep mode for 5 minutes, as we set in the ``settings.py`` file. Sometimes we want to debug the device and therefore the device should not go into sleep. We add a if clause for this and use the ``DEBUG`` variable from the ``settings.py`` to disable sleep mode when DEBUG is True:

.. literalinclude:: ../main.py
    :lines: 45-47


Now we complete complete our ``main.py`` file with the call to ``main()`` if the file run after the Pycom module has started:

.. literalinclude:: ../main.py
    :lines: 50-51

Now reset your device and watch the incoming application data on the TTN console.


TTN Payload Format Decoder
--------------------------

On The Things Network Console we can decode our payload with the following javascript example. Remember the position from each tag from the settings.RUUVITAGS variable, we will give them names in the decoded output.

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

1. Define a map to name the indexed RuuviTags. This must match the whitelist from our ``settings.py``.

2. Find out how many tags are included in the payload. Since we know that one tag use 8 bytes for payload, we divide the payload length with 8.

2. Iterate over the payload and unpack the data. In position zero we find the tag number from our list and map it to **outdoor** from the map variable.

3. Add the RuuviTag name with the measurements to the ``ruuvitags`` object, remove the first 8 bytes from ``bytes`` and iterate over the next payload data.

4. Return the decoded data.

When you take a look on the TTN Console Device Overview in the data section, you can see the incoming unpacked payload.
