# -*- coding: utf-8 -*-
"""
Module for the Tinkerforge Temperature Bricklet 2.0
(https://www.tinkerforge.com/en/doc/Hardware/Bricklets/Temperature_V2.html)
implemented using Python AsyncIO. It does the low-lvel communication with the
Tinkerforge ip connection and also handles conversion of raw units to SI units.
"""
from collections import namedtuple
from decimal import Decimal
from enum import Enum, unique

from .devices import DeviceIdentifier, BrickletWithMCU, ThresholdOption
from .ip_connection_helper import pack_payload, unpack_payload

GetTemperatureCallbackConfiguration = namedtuple('TemperatureCallbackConfiguration', ['period', 'value_has_to_change', 'option', 'minimum', 'maximum'])


@unique
class CallbackID(Enum):
    """
    The callbacks available to this bricklet
    """
    TEMPERATURE = 4


@unique
class FunctionID(Enum):
    """
    The function calls available to this bricklet
    """
    GET_TEMPERATURE = 1
    SET_TEMPERATURE_CALLBACK_CONFIGURATION = 2
    GET_TEMPERATURE_CALLBACK_CONFIGURATION = 3
    SET_HEATER_CONFIGURATION = 5
    GET_HEATER_CONFIGURATION = 6


@unique
class HeaterConfig(Enum):
    """
    The builtin heater can be used for testing purposes
    """
    DISABLED = 0
    ENABLED = 1


class BrickletTemperatureV2(BrickletWithMCU):
    """
    Measures ambient temperature with 0.2 K accuracy
    """
    DEVICE_IDENTIFIER = DeviceIdentifier.BRICKLET_TEMPTERATURE_V2
    DEVICE_DISPLAY_NAME = 'Temperature Bricklet 2.0'

    # Convenience imports, so that the user does not need to additionally import them
    CallbackID = CallbackID
    FunctionID = FunctionID
    ThresholdOption = ThresholdOption
    HeaterConfig = HeaterConfig

    CALLBACK_FORMATS = {
        CallbackID.TEMPERATURE: 'h',
    }

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        super().__init__(self.DEVICE_DISPLAY_NAME, uid, ipcon)

        self.api_version = (2, 0, 0)

    async def get_temperature(self):
        """
        Returns the temperature of the sensor. The value
        has a range of -2500 to 8500 and is given in °C/100,
        e.g. a value of 4223 means that a temperature of 42.23 °C is measured.

        If you want to get the temperature periodically, it is recommended
        to use the :cb:`Temperature` callback and set the period with
        :func:`Set Temperature Callback Period`.
        """
        _, payload = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.GET_TEMPERATURE,
            response_expected=True
        )
        return self.__value_to_si(unpack_payload(payload, 'h'))

    async def set_temperature_callback_configuration(self, period=0, value_has_to_change=False, option=ThresholdOption.OFF, minimum=0, maximum=0, response_expected=True):  # pylint: disable=too-many-arguments
        """
        The period in ms is the period with which the :cb:`Temperature` callback is triggered
        periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after the value has changed. If the value didn't change
        within the period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        It is furthermore possible to constrain the callback with thresholds.

        The `option`-parameter together with min/max sets a threshold for the :cb:`Temperature` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Threshold is turned off"
         "'o'",    "Threshold is triggered when the value is *outside* the min and max values"
         "'i'",    "Threshold is triggered when the value is *inside* the min and max values"
         "'<'",    "Threshold is triggered when the value is smaller than the min value (max is ignored)"
         "'>'",    "Threshold is triggered when the value is greater than the min value (max is ignored)"


        If the option is set to 'x' (threshold turned off) the callback is triggered with the fixed period.

        The default value is (0, false, 'x', 0, 0).
        """
        if not isinstance(option, ThresholdOption):
            option = ThresholdOption(option)
        assert period >= 0

        await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.SET_TEMPERATURE_CALLBACK_CONFIGURATION,
            data=pack_payload(
              (
                int(period),
                bool(value_has_to_change),
                option.value.encode('ascii'),
                self.__si_to_value(minimum),
                self.__si_to_value(maximum)
              ), 'I ! c h h'),
            response_expected=response_expected
        )

    async def get_temperature_callback_configuration(self):
        """
        Returns the callback configuration as set by :func:`Set Temperature Callback Configuration`.
        """
        _, payload = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.GET_TEMPERATURE_CALLBACK_CONFIGURATION,
            response_expected=True
        )
        period, value_has_to_change, option, minimum, maximum = unpack_payload(payload, 'I ! c h h')
        option = ThresholdOption(option)
        minimum, maximum = self.__value_to_si(minimum), self.__value_to_si(maximum)
        return GetTemperatureCallbackConfiguration(period, value_has_to_change, option, minimum, maximum)

    async def set_heater_configuration(self, heater_config=HeaterConfig.DISABLED, response_expected=True):
        """
        Enables/disables the heater. The heater can be used to test the sensor.
        """
        if not isinstance(heater_config, HeaterConfig):
            heater_config = HeaterConfig(int(heater_config))

        await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.SET_HEATER_CONFIGURATION,
            data=pack_payload((heater_config.value,), 'B'),
            response_expected=response_expected
        )

    async def get_heater_configuration(self):
        """
        Returns the heater configuration as set by :func:`Set Heater Configuration`.
        """
        _, payload = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.GET_HEATER_CONFIGURATION,
            response_expected=True
        )

        return HeaterConfig(unpack_payload(payload, 'B'))

    @staticmethod
    def __value_to_si(value):
        """
        Convert to the sensor value to SI units
        """
        return Decimal(value) / 100

    @staticmethod
    def __si_to_value(value):
        return int(value * 100)

    def _process_callback_payload(self, header, payload):
        payload = unpack_payload(payload, self.CALLBACK_FORMATS[header['function_id']])
        return self.__value_to_si(payload), True    # payload, done
