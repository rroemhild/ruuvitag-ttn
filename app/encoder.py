from ustruct import pack


def encode_battery(bat):
    return pack("!H", bat - 1600)


def encode_humid(hum):
    """Humidity in 0.0025 percent as unsigned short"""
    hum_conv = round(round(hum, 2) / 0.0025)
    return pack("!H", hum_conv)


def encode_temp(temp):
    """Temperature in 0.005 degrees as signed short"""
    temp_conv = round(round(temp, 2) / 0.005)
    return pack("!h", temp_conv)
