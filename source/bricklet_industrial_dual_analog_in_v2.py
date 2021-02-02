# -*- coding: utf-8 -*-
from collections import namedtuple
from decimal import Decimal
from enum import Enum, unique

from .devices import DeviceIdentifier, BrickletWithMCU, ThresholdOption
from .ip_connection import Flags
from .ip_connection_helper import pack_payload, unpack_payload

GetVoltageCallbackConfiguration = namedtuple('VoltageCallbackConfiguration', ['period', 'value_has_to_change', 'option', 'minimum', 'maximum'])
GetCalibration = namedtuple('Calibration', ['offset', 'gain'])
GetChannelLEDStatusConfig = namedtuple('ChannelLEDStatusConfig', ['minimum', 'maximum', 'config'])
GetAllVoltagesCallbackConfiguration = namedtuple('AllVoltagesCallbackConfiguration', ['period', 'value_has_to_change'])

@unique
class CallbackID(Enum):
    VOLTAGE = 4
    ALL_VOLTAGES = 17

@unique
class FunctionID(Enum):
    GET_VOLTAGE = 1
    SET_VOLTAGE_CALLBACK_CONFIGURATION = 2
    GET_VOLTAGE_CALLBACK_CONFIGURATION = 3
    SET_SAMPLE_RATE = 5
    GET_SAMPLE_RATE = 6
    SET_CALIBRATION = 7
    GET_CALIBRATION = 8
    GET_ADC_VALUES = 9
    SET_CHANNEL_LED_CONFIG = 10
    GET_CHANNEL_LED_CONFIG = 11
    SET_CHANNEL_LED_STATUS_CONFIG = 12
    GET_CHANNEL_LED_STATUS_CONFIG = 13
    GET_ALL_VOLTAGES = 14
    SET_ALL_VOLTAGES_CALLBACK_CONFIGURATION = 15
    GET_ALL_VOLTAGES_CALLBACK_CONFIGURATION = 16

@unique
class ChannelLedConfig(Enum):
    OFF = 0
    ON = 1
    HEARTBEAT = 2
    CHANNEL_STATUS = 3

@unique
class ChannelLedStatusConfig(Enum):
    THRESHOLD = 0
    INTENSITY = 1

@unique
class SamplingRate(Enum):
    RATE_976_SPS = 0
    RATE_488_SPS = 1
    RATE_244_SPS = 2
    RATE_122_SPS = 3
    RATE_61_SPS = 4
    RATE_4_SPS = 5
    RATE_2_SPS = 6
    RATE_1_SPS = 7


class BrickletIndustrialDualAnalogInV2(BrickletWithMCU):
    """
    Measures two DC voltages between -35V and +35V with 24bit resolution each
    """

    DEVICE_IDENTIFIER = DeviceIdentifier.BrickletIndustrialDualAnalogIn_V2
    DEVICE_DISPLAY_NAME = 'Industrial Dual Analog In Bricklet 2.0'
    DEVICE_URL_PART = 'industrial_dual_analog_in_v2' # internal

    # Convenience imports, so that the user does not need to additionally import them
    CallbackID = CallbackID
    FunctionID = FunctionID
    ThresholdOption = ThresholdOption
    ChannelLedConfig = ChannelLedConfig
    ChannelLedStatusConfig = ChannelLedStatusConfig
    SamplingRate = SamplingRate

    CALLBACK_FORMATS = {
        CallbackID.VOLTAGE: 'B i',
        CallbackID.ALL_VOLTAGES: '2i',
    }

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        super().__init__(uid, ipcon)

        self.api_version = (2, 0, 0)

    async def get_voltage(self, channel):
        """
        Returns the voltage for the given channel.


        If you want to get the value periodically, it is recommended to use the
        :cb:`Voltage` callback. You can set the callback configuration
        with :func:`Set Voltage Callback Configuration`.
        """
        assert (channel == 0 or channel == 1)

        _, payload = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.GET_VOLTAGE,
            data=pack_payload((int(channel),), 'B'),
            response_expected=True
        )
        return unpack_payload(payload, 'i')

    async def set_voltage_callback_configuration(self, channel, period=0, value_has_to_change=False, option=ThresholdOption.OFF, minimum=0, maximum=0, response_expected=True):
        """
        The period is the period with which the :cb:`Voltage` callback is triggered
        periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after the value has changed. If the value didn't change
        within the period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        It is furthermore possible to constrain the callback with thresholds.

        The `option`-parameter together with min/max sets a threshold for the :cb:`Voltage` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Threshold is turned off"
         "'o'",    "Threshold is triggered when the value is *outside* the min and max values"
         "'i'",    "Threshold is triggered when the value is *inside* or equal to the min and max values"
         "'<'",    "Threshold is triggered when the value is smaller than the min value (max is ignored)"
         "'>'",    "Threshold is triggered when the value is greater than the min value (max is ignored)"

        If the option is set to 'x' (threshold turned off) the callback is triggered with the fixed period.
        """
        assert (channel == 0 or channel == 1)
        if not type(option) is ThresholdOption:
            option = ThresholdOption(option)
        assert period >= 0
        assert minimum >= 0
        assert maximum >= 0

        result = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.SET_VOLTAGE_CALLBACK_CONFIGURATION,
            data=pack_payload(
              (
                int(channel),
                int(period),
                bool(value_has_to_change),
                option.value.encode('ascii'),
                int(minimum),
                int(maximum),
              ), 'B I ! c i i'),
            response_expected=response_expected
        )
        if response_expected:
            header, _ = result
            # TODO raise errors
            return header['flags'] == Flags.OK

    async def get_voltage_callback_configuration(self, channel):
        """
        Returns the callback configuration as set by :func:`Set Voltage Callback Configuration`.
        """
        _, payload = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.GET_VOLTAGE_CALLBACK_CONFIGURATION,
            data=pack_payload((channel,), 'B'),
            response_expected=True
        )
        period, value_has_to_change, option, minimum, maximum = unpack_payload(payload, 'I ! c i i')
        option = ThresholdOption(option)
        return GetVoltageCallbackConfiguration(period, value_has_to_change, option, minimum, maximum)

    async def get_all_voltages(self):
        """
        Returns the voltage for the given channel.


        If you want to get the value periodically, it is recommended to use the
        :cb:`Voltage` callback. You can set the callback configuration
        with :func:`Set Voltage Callback Configuration`.
        """
        _, payload = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.GET_ALL_VOLTAGES,
            response_expected=True
        )
        return unpack_payload(payload, '2i')

    async def set_all_voltages_callback_configuration(self, period=0, value_has_to_change=False, response_expected=True):
        """
        The period is the period with which the :cb:`All Voltages`
        callback is triggered periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after at least one of the values has changed. If the values didn't
        change within the period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        .. versionadded:: 2.0.6$nbsp;(Plugin)
        """
        assert period >= 0

        result = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.SET_ALL_VOLTAGES_CALLBACK_CONFIGURATION,
            data=pack_payload(
              (
                int(period),
                bool(value_has_to_change),
              ), 'I !'),
            response_expected=response_expected
        )
        if response_expected:
            header, _ = result
            # TODO raise errors
            return header['flags'] == Flags.OK

    async def get_all_voltages_callback_configuration(self):
        """
        Returns the callback configuration as set by
        :func:`Set All Voltages Callback Configuration`.

        .. versionadded:: 2.0.6$nbsp;(Plugin)
        """
        _, payload = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.GET_VOLTAGE_CALLBACK_CONFIGURATION,
            response_expected=True
        )
        return GetAllVoltagesCallbackConfiguration(*unpack_payload(payload, 'I !'))

    async def set_sample_rate(self, rate, response_expected=False):
        """
        Sets the sample rate. The sample rate can be between 1 sample per second
        and 976 samples per second. Decreasing the sample rate will also decrease the
        noise on the data.
        """
        if type(rate) is not SamplingRate:
            rate = SamplingRate(rate)

        result = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.SET_SAMPLE_RATE,
            data=pack_payload((rate.value,), 'B'),
            response_expected=response_expected
        )

        if response_expected:
            header, _ = result
            # TODO raise errors
            return header['flags'] == Flags.OK

    async def get_sample_rate(self):
        """
        Returns the sample rate as set by :func:`Set Sample Rate`.
        """
        _, payload = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.GET_SAMPLE_RATE,
            response_expected=True
        )

        return SamplingRate(unpack_payload(payload, 'B'))

    async def set_calibration(self, offset, gain, response_expected=False):
        """
        Sets offset and gain of MCP3911 internal calibration registers.

        See MCP3911 datasheet 7.7 and 7.8. The Industrial Dual Analog In Bricklet 2.0
        is already factory calibrated by Tinkerforge. It should not be necessary
        for you to use this function
        """
        result = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.SET_CALIBRATION,
            data=pack_payload(
              (
                list(map(int, offset)),
                list(map(int, gain))
              ), '2i 2i'),
            response_expected=response_expected
        )

        if response_expected:
            header, _ = result
            # TODO raise errors
            return header['flags'] == Flags.OK

    async def get_calibration(self):
        """
        Returns the calibration as set by :func:`Set Calibration`.
        """
        _, payload = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.GET_CALIBRATION,
            response_expected=True
        )

        return GetCalibration(*unpack_payload(payload, '2i 2i'))

    async def get_adc_values(self):
        """
        Returns the ADC values as given by the MCP3911 IC. This function
        is needed for proper calibration, see :func:`Set Calibration`.
        """
        _, payload = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.GET_ADC_VALUES,
            response_expected=True
        )

        return unpack_payload(payload, '2i')

    async def set_channel_led_config(self, channel, config, response_expected=False):
        """
        Each channel has a corresponding LED. You can turn the LED off, on or show a
        heartbeat. You can also set the LED to "Channel Status". In this mode the
        LED can either be turned on with a pre-defined threshold or the intensity
        of the LED can change with the measured value.

        You can configure the channel status behavior with :func:`Set Channel LED Status Config`.

        By default all channel LEDs are configured as "Channel Status".
        """
        assert (channel == 0 or channel == 1)
        if not type(config) is ChannelLedConfig:
            config = ChannelLedConfig(config)

        result = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.SET_CHANNEL_LED_CONFIG,
            data=pack_payload(
              (
                int(channel),
                config.value,
              ), 'B B'),
            response_expected=response_expected
        )

        if response_expected:
            header, _ = result
            # TODO raise errors
            return header['flags'] == Flags.OK

    async def get_channel_led_config(self, channel):
        """
        Returns the ADC values as given by the MCP3911 IC. This function
        is needed for proper calibration, see :func:`Set Calibration`.
        """
        assert (channel == 0 or channel == 1)

        _, payload = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.GET_CHANNEL_LED_CONFIG,
            data=pack_payload((int(channel),), 'B'),
            response_expected=True
        )

        return ChannelLedConfig(unpack_payload(payload, 'B'))

    async def set_channel_led_status_config(self, channel, minimum, maximum, config, response_expected=False):
        """
        Sets the channel LED status config. This config is used if the channel LED is
        configured as "Channel Status", see :func:`Set Channel LED Config`.

        For each channel you can choose between threshold and intensity mode.

        In threshold mode you can define a positive or a negative threshold.
        For a positive threshold set the "min" parameter to the threshold value in mV
        above which the LED should turn on and set the "max" parameter to 0. Example:
        If you set a positive threshold of 10V, the LED will turn on as soon as the
        voltage exceeds 10V and turn off again if it goes below 10V.
        For a negative threshold set the "max" parameter to the threshold value in mV
        below which the LED should turn on and set the "min" parameter to 0. Example:
        If you set a negative threshold of 10V, the LED will turn on as soon as the
        voltage goes below 10V and the LED will turn off when the voltage exceeds 10V.

        In intensity mode you can define a range in mV that is used to scale the brightness
        of the LED. Example with min=4V, max=20V: The LED is off at 4V, on at 20V
        and the brightness is linearly scaled between the values 4V and 20V. If the
        min value is greater than the max value, the LED brightness is scaled the other
        way around.
        """
        assert (channel == 0 or channel == 1)
        if not type(config) is ChannelLedStatusConfig:
            config = ChannelLedStatusConfig(config)

        result = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.SET_CHANNEL_LED_STATUS_CONFIG,
            data=pack_payload(
              (
                int(channel),
                int(minimum),
                int(maximum),
                config.value,
              ), 'B i i B'),
            response_expected=response_expected
        )

        if response_expected:
            header, _ = result
            # TODO raise errors
            return header['flags'] == Flags.OK

    async def get_channel_led_status_config(self, channel):
        """
        Returns the channel LED status configuration as set by
        :func:`Set Channel LED Status Config`.
        """
        assert (channel == 0 or channel == 1)

        _, payload = await self.ipcon.send_request(
            device=self,
            function_id=FunctionID.GET_CHANNEL_LED_STATUS_CONFIG,
            data=pack_payload((int(channel),), 'B'),
            response_expected=True
        )

        minimum, maximum, config = unpack_payload(payload, 'i i B')
        config = ChannelLedStatusConfig(config)
        return GetChannelLEDStatusConfig(minimum, maximum, config)

    def __SI_to_value(self, value):
        return int(value * 100)

