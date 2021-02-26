# Disable deepsleep
DEBUG = False

# OTAA activation
NODE_APP_EUI = ''
NODE_APP_KEY = ''

# Device deepsleep time in seconds
NODE_DEEPSLEEP = 300

# Bluetooth scan timeout
NODE_SCAN_TIMEOUT = 10

# RuuviTags whitelist, other tags will be ignored, all lowercase
# RUUVITAGS = [b'aa:bb:02:03:04:05', b'aa:ab:12:13:14:15']
RUUVITAGS = [
    b'fc:e7:e3:e6:2f:0c',  # outdoor
    b'c2:0d:d5:a3:b3:54'   # livingroom
]
