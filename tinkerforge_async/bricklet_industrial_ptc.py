# -*- coding: utf-8 -*-
"""
Module for the Tinkerforge Industrial PTC Bricklet
(https://www.tinkerforge.com/en/doc/Hardware/Bricklets/Industrial_PTC.html)
implemented using Python AsyncIO. It does the low-lvel communication with the
Tinkerforge ip connection and also handles conversion of raw units to SI units.
"""
from .devices import DeviceIdentifier
from .bricklet_ptc_v2 import BrickletPtcV2


class BrickletIndustrialPtc(BrickletPtcV2):
    """
    Reads temperatures from Pt100 und Pt1000 sensors
    """
    DEVICE_IDENTIFIER = DeviceIdentifier.BRICKLET_INDUSTRIAL_PTC
    DEVICE_DISPLAY_NAME = 'Industrial PTC Bricklet'
