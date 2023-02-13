"""Constants used by hahomematic custom entities."""
from __future__ import annotations

from typing import Final

from hahomematic.backport import StrEnum


class HmEntityDefinition(StrEnum):
    """Enum for entity definitions."""

    IP_COVER = "IPCover"
    IP_DIMMER = "IPDimmer"
    IP_FIXED_COLOR_LIGHT = "IPFixedColorLight"
    IP_GARAGE = "IPGarage"
    IP_LOCK = "IPLock"
    IP_SIMPLE_FIXED_COLOR_LIGHT = "IPSimpleFixedColorLight"
    IP_SIREN = "IPSiren"
    IP_SIREN_SMOKE = "IPSirenSmoke"
    IP_SWITCH = "IPSwitch"
    IP_THERMOSTAT = "IPThermostat"
    IP_THERMOSTAT_GROUP = "IPThermostatGroup"
    RF_COVER = "RfCover"
    RF_DIMMER = "RfDimmer"
    RF_DIMMER_COLOR = "RfDimmer_Color"
    RF_DIMMER_COLOR_TEMP = "RfDimmer_Color_Temp"
    RF_DIMMER_WITH_VIRT_CHANNEL = "RfDimmerWithVirtChannel"
    RF_LOCK = "RfLock"
    RF_SIREN = "RfSiren"
    RF_SWITCH = "RfSwitch"
    RF_THERMOSTAT = "RfThermostat"
    RF_THERMOSTAT_GROUP = "RfThermostatGroup"
    SIMPLE_RF_THERMOSTAT = "SimpleRfThermostat"


FIELD_ACOUSTIC_ALARM_ACTIVE: Final = "acoustic_alarm_active"
FIELD_ACOUSTIC_ALARM_SELECTION: Final = "acoustic_alarm_selection"
FIELD_ACTIVE_PROFILE: Final = "active_profile"
FIELD_AUTO_MODE: Final = "auto_mode"
FIELD_BOOST_MODE: Final = "boost_mode"
FIELD_CHANNEL_COLOR: Final = "channel_color"
FIELD_CHANNEL_LEVEL: Final = "channel_level"
FIELD_CHANNEL_LEVEL_2: Final = "channel_level_2"
FIELD_CHANNEL_OPERATION_MODE: Final = "channel_operation_mode"
FIELD_CHANNEL_STATE: Final = "channel_state"
FIELD_COLOR: Final = "color"
FIELD_COLOR_LEVEL: Final = "color_temp"
FIELD_COMFORT_MODE: Final = "comfort_mode"
FIELD_CONTROL_MODE: Final = "control_mode"
FIELD_CURRENT: Final = "current"
FIELD_DIRECTION: Final = "direction"
FIELD_DOOR_COMMAND: Final = "door_command"
FIELD_DOOR_STATE: Final = "door_state"
FIELD_DURATION: Final = "duration"
FIELD_DURATION_UNIT: Final = "duration_unit"
FIELD_DUTYCYCLE: Final = "dutycycle"
FIELD_DUTY_CYCLE: Final = "duty_cycle"
FIELD_ENERGY_COUNTER: Final = "energy_counter"
FIELD_ERROR: Final = "error"
FIELD_FREQUENCY: Final = "frequency"
FIELD_HEATING_COOLING: Final = "heating_cooling"
FIELD_HUMIDITY: Final = "humidity"
FIELD_INHIBIT: Final = "inhibit"
FIELD_LEVEL: Final = "level"
FIELD_LEVEL_2: Final = "level_2"
FIELD_LOCK_STATE: Final = "lock_state"
FIELD_LOCK_TARGET_LEVEL: Final = "lock_target_level"
FIELD_LOWBAT: Final = "lowbat"
FIELD_LOWERING_MODE: Final = "lowering_mode"
FIELD_LOW_BAT: Final = "low_bat"
FIELD_MANU_MODE: Final = "manu_mode"
FIELD_ON_TIME_UNIT: Final = "on_time_unit"
FIELD_ON_TIME_VALUE: Final = "on_time_value"
FIELD_OPEN: Final = "open"
FIELD_OPERATING_VOLTAGE: Final = "operating_voltage"
FIELD_OPTICAL_ALARM_ACTIVE: Final = "optical_alarm_active"
FIELD_OPTICAL_ALARM_SELECTION: Final = "optical_alarm_selection"
FIELD_PARTY_MODE: Final = "party_mode"
FIELD_POWER: Final = "power"
FIELD_PROGRAM: Final = "program"
FIELD_RAMP_TIME_UNIT: Final = "ramp_time_unit"
FIELD_RAMP_TIME_VALUE: Final = "ramp_time_value"
FIELD_RSSI_DEVICE: Final = "rssi_device"
FIELD_RSSI_PEER: Final = "rssi_peer"
FIELD_SABOTAGE: Final = "sabotage"
FIELD_SECTION: Final = "section"
FIELD_SETPOINT: Final = "setpoint"
FIELD_SET_POINT_MODE: Final = "set_point_mode"
FIELD_SMOKE_DETECTOR_ALARM_STATUS = "smoke_detector_alarm_status"
FIELD_SMOKE_DETECTOR_COMMAND = "smoke_detector_command"
FIELD_STATE: Final = "state"
FIELD_STOP: Final = "stop"
FIELD_SWITCH_MAIN: Final = "switch_main"
FIELD_SWITCH_V1: Final = "vswitch_1"
FIELD_SWITCH_V2: Final = "vswitch_2"
FIELD_TEMPERATURE: Final = "temperature"
FIELD_TEMPERATURE_MAXIMUM: Final = "temperature_maximum"
FIELD_TEMPERATURE_MINIMUM: Final = "temperature_minimum"
FIELD_VALVE_STATE: Final = "valve_state"
FIELD_VOLTAGE: Final = "voltage"
