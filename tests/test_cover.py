"""Tests for cover entities of hahomematic."""

from __future__ import annotations

from typing import cast
from unittest.mock import Mock, call

import pytest

from hahomematic.central import CentralUnit
from hahomematic.client import Client
from hahomematic.config import WAIT_FOR_CALLBACK
from hahomematic.const import EntityUsage
from hahomematic.platforms.custom.cover import (
    _CLOSED_LEVEL,
    _OPEN_LEVEL,
    _OPEN_TILT_LEVEL,
    _WD_CLOSED_LEVEL,
    CeBlind,
    CeCover,
    CeGarage,
    CeIpBlind,
    CeWindowDrive,
    GarageDoorActivity,
)

from tests import const, helper

TEST_DEVICES: dict[str, str] = {
    "VCU0000045": "HM-LC-Bl1-FM.json",
    "VCU0000145": "HM-LC-JaX.json",
    "VCU0000350": "HM-Sec-Win.json",
    "VCU1223813": "HmIP-FBL.json",
    "VCU3560967": "HmIP-HDM1.json",
    "VCU3574044": "HmIP-MOD-HO.json",
    "VCU6166407": "HmIP-MOD-TM.json",
    "VCU7807849": "HmIPW-DRBL4.json",
    "VCU8537918": "HmIP-BROLL.json",
}

# pylint: disable=protected-access


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    (
        "address_device_translation",
        "do_mock_client",
        "add_sysvars",
        "add_programs",
        "ignore_devices_on_create",
        "un_ignore_list",
    ),
    [
        (TEST_DEVICES, True, False, False, None, None),
    ],
)
async def test_cecover(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test CeCover."""
    central, mock_client, _ = central_client_factory
    cover: CeCover = cast(CeCover, helper.get_prepared_custom_entity(central, "VCU8537918", 4))
    assert cover.usage == EntityUsage.CE_PRIMARY

    assert cover.current_position == 0
    assert cover._channel_level == _CLOSED_LEVEL
    assert cover.is_closed is True
    await cover.set_position(position=81)
    assert mock_client.method_calls[-2] == call.set_value(
        channel_address="VCU8537918:4",
        paramset_key="VALUES",
        parameter="LEVEL",
        value=0.81,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert cover.current_position == 81
    assert cover.is_closed is False
    await cover.open()
    assert mock_client.method_calls[-2] == call.set_value(
        channel_address="VCU8537918:4",
        paramset_key="VALUES",
        parameter="LEVEL",
        value=_OPEN_LEVEL,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert cover.current_position == 100
    await cover.close()
    assert mock_client.method_calls[-2] == call.set_value(
        channel_address="VCU8537918:4",
        paramset_key="VALUES",
        parameter="LEVEL",
        value=_CLOSED_LEVEL,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert cover.current_position == 0

    assert cover.is_opening is None
    assert cover.is_closing is None
    await central.event(const.INTERFACE_ID, "VCU8537918:3", "ACTIVITY_STATE", 1)
    assert cover.is_opening is True
    await central.event(const.INTERFACE_ID, "VCU8537918:3", "ACTIVITY_STATE", 2)
    assert cover.is_closing is True
    await central.event(const.INTERFACE_ID, "VCU8537918:3", "ACTIVITY_STATE", 0)

    await central.event(const.INTERFACE_ID, "VCU8537918:3", "LEVEL", 0.5)
    assert cover._channel_level == 0.5
    assert cover.current_position == 50

    await central.event(const.INTERFACE_ID, "VCU8537918:3", "LEVEL", _CLOSED_LEVEL)
    call_count = len(mock_client.method_calls)
    await cover.close()
    assert call_count == len(mock_client.method_calls)

    await central.event(const.INTERFACE_ID, "VCU8537918:3", "LEVEL", _OPEN_LEVEL)
    call_count = len(mock_client.method_calls)
    await cover.open()
    assert call_count == len(mock_client.method_calls)

    await central.event(const.INTERFACE_ID, "VCU8537918:3", "LEVEL", 0.4)
    call_count = len(mock_client.method_calls)
    await cover.set_position(position=40)
    assert call_count == len(mock_client.method_calls)


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    (
        "address_device_translation",
        "do_mock_client",
        "add_sysvars",
        "add_programs",
        "ignore_devices_on_create",
        "un_ignore_list",
    ),
    [
        (TEST_DEVICES, True, False, False, None, None),
    ],
)
async def test_ceipblind_dr(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test CeIpBlind DIN Rail."""
    central, mock_client, _ = central_client_factory
    cover: CeIpBlind = cast(CeIpBlind, helper.get_prepared_custom_entity(central, "VCU7807849", 2))
    assert cover.usage == EntityUsage.CE_PRIMARY

    assert cover.current_position == 0
    assert cover._channel_level == _CLOSED_LEVEL
    assert cover.channel_operation_mode == "SHUTTER"
    assert cover.is_closed is True
    await cover.set_position(position=81)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU7807849:2",
        paramset_key="VALUES",
        parameter="COMBINED_PARAMETER",
        value="L2=0,L=81",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    # test unconfirmed values
    assert cover._e_level.unconfirmed_last_value_send == 0.81
    assert cover._e_level_2.unconfirmed_last_value_send == _CLOSED_LEVEL
    await central.event(const.INTERFACE_ID, "VCU7807849:2", "LEVEL", 0.81)
    await central.event(const.INTERFACE_ID, "VCU7807849:2", "LEVEL_2", _CLOSED_LEVEL)
    assert cover._e_level.unconfirmed_last_value_send is None
    assert cover._e_level_2.unconfirmed_last_value_send is None

    await central.event(const.INTERFACE_ID, "VCU7807849:1", "LEVEL", 0.81)
    await central.event(const.INTERFACE_ID, "VCU7807849:1", "LEVEL_2", _CLOSED_LEVEL)
    assert cover.current_position == 81
    assert cover.is_closed is False
    await cover.open()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU7807849:2",
        paramset_key="VALUES",
        parameter="COMBINED_PARAMETER",
        value="L2=50,L=100",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert cover._e_level.unconfirmed_last_value_send == _OPEN_LEVEL
    assert cover._e_level_2.unconfirmed_last_value_send == _OPEN_TILT_LEVEL
    await central.event(const.INTERFACE_ID, "VCU7807849:1", "LEVEL", _OPEN_LEVEL)
    await central.event(const.INTERFACE_ID, "VCU7807849:1", "LEVEL_2", _OPEN_TILT_LEVEL)
    await central.event(const.INTERFACE_ID, "VCU7807849:2", "LEVEL", _OPEN_LEVEL)
    await central.event(const.INTERFACE_ID, "VCU7807849:2", "LEVEL_2", _OPEN_TILT_LEVEL)
    assert cover._e_level.unconfirmed_last_value_send is None
    assert cover._e_level_2.unconfirmed_last_value_send is None
    assert cover.current_position == 100
    assert cover.current_tilt_position == 50
    await cover.close()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU7807849:2",
        paramset_key="VALUES",
        parameter="COMBINED_PARAMETER",
        value="L2=0,L=0",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU7807849:1", "LEVEL", _CLOSED_LEVEL)
    assert cover.is_opening is None
    assert cover.is_closing is None
    await central.event(const.INTERFACE_ID, "VCU7807849:1", "ACTIVITY_STATE", 1)
    assert cover.is_opening is True
    await central.event(const.INTERFACE_ID, "VCU7807849:1", "ACTIVITY_STATE", 2)
    assert cover.is_closing is True

    await central.event(const.INTERFACE_ID, "VCU7807849:1", "LEVEL", 0.5)
    assert cover._channel_level == 0.5
    assert cover.current_position == 50


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    (
        "address_device_translation",
        "do_mock_client",
        "add_sysvars",
        "add_programs",
        "ignore_devices_on_create",
        "un_ignore_list",
    ),
    [
        (TEST_DEVICES, True, False, False, None, None),
    ],
)
async def test_cewindowdrive(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test CeWindowDrive."""
    central, mock_client, _ = central_client_factory
    cover: CeWindowDrive = cast(
        CeWindowDrive, helper.get_prepared_custom_entity(central, "VCU0000350", 1)
    )
    assert cover.usage == EntityUsage.CE_PRIMARY

    assert cover.current_position == 0
    assert cover._channel_level == _WD_CLOSED_LEVEL
    assert cover.is_closed is True
    await cover.set_position(position=81)
    assert mock_client.method_calls[-2] == call.set_value(
        channel_address="VCU0000350:1",
        paramset_key="VALUES",
        parameter="LEVEL",
        value=0.81,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert cover.current_position == 81
    assert cover.is_closed is False

    await cover.open()
    assert mock_client.method_calls[-2] == call.set_value(
        channel_address="VCU0000350:1",
        paramset_key="VALUES",
        parameter="LEVEL",
        value=_OPEN_LEVEL,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert cover.current_position == 100
    await cover.close()
    assert mock_client.method_calls[-2] == call.set_value(
        channel_address="VCU0000350:1",
        paramset_key="VALUES",
        parameter="LEVEL",
        value=_WD_CLOSED_LEVEL,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    assert cover.current_position == 0
    assert cover._channel_level == _WD_CLOSED_LEVEL
    assert cover.is_closed is True

    await cover.set_position(position=1)
    assert cover.current_position == 1
    assert cover._channel_level == _CLOSED_LEVEL
    assert cover.is_closed is False

    await cover.set_position(position=_WD_CLOSED_LEVEL)
    assert cover.current_position == 0
    assert cover._channel_level == _WD_CLOSED_LEVEL
    assert cover.is_closed is True


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    (
        "address_device_translation",
        "do_mock_client",
        "add_sysvars",
        "add_programs",
        "ignore_devices_on_create",
        "un_ignore_list",
    ),
    [
        (TEST_DEVICES, True, False, False, None, None),
    ],
)
async def test_ceblind(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test CeBlind."""
    central, mock_client, _ = central_client_factory
    cover: CeBlind = cast(CeBlind, helper.get_prepared_custom_entity(central, "VCU0000145", 1))
    assert cover.usage == EntityUsage.CE_PRIMARY
    assert cover.current_position == 0
    assert cover.current_tilt_position == 0

    await cover.set_position(position=81)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000145:1",
        paramset_key="VALUES",
        parameter="LEVEL_COMBINED",
        value="0xa2,0x00",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU0000145:1", "LEVEL", 0.81)
    assert cover.current_position == 81
    assert cover.current_tilt_position == 0

    await cover.open()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000145:1",
        paramset_key="VALUES",
        parameter="LEVEL_COMBINED",
        value="0xc8,0x64",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU0000145:1", "LEVEL", _OPEN_LEVEL)
    await central.event(const.INTERFACE_ID, "VCU0000145:1", "LEVEL_SLATS", _OPEN_TILT_LEVEL)
    assert cover.current_position == 100
    assert cover.current_tilt_position == 50

    await cover.close()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000145:1",
        paramset_key="VALUES",
        parameter="LEVEL_COMBINED",
        value="0x00,0x00",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU0000145:1", "LEVEL", _CLOSED_LEVEL)
    await central.event(const.INTERFACE_ID, "VCU0000145:1", "LEVEL_SLATS", _CLOSED_LEVEL)
    assert cover.current_position == 0
    assert cover.current_tilt_position == 0

    await cover.open_tilt()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000145:1",
        paramset_key="VALUES",
        parameter="LEVEL_COMBINED",
        value="0x00,0x64",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU0000145:1", "LEVEL_SLATS", _OPEN_TILT_LEVEL)
    assert cover.current_position == 0
    assert cover.current_tilt_position == 50

    await cover.set_position(tilt_position=45)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000145:1",
        paramset_key="VALUES",
        parameter="LEVEL_COMBINED",
        value="0x00,0x5a",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU0000145:1", "LEVEL_SLATS", 0.45)
    assert cover.current_position == 0
    assert cover.current_tilt_position == 45

    await cover.close_tilt()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000145:1",
        paramset_key="VALUES",
        parameter="LEVEL_COMBINED",
        value="0x00,0x00",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU0000145:1", "LEVEL_SLATS", _CLOSED_LEVEL)
    assert cover.current_position == 0
    assert cover.current_tilt_position == 0

    await cover.set_position(position=10, tilt_position=20)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000145:1",
        paramset_key="VALUES",
        parameter="LEVEL_COMBINED",
        value="0x14,0x28",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU0000145:1", "LEVEL", 0.1)
    await central.event(const.INTERFACE_ID, "VCU0000145:1", "LEVEL_SLATS", 0.2)
    assert cover.current_position == 10
    assert cover.current_tilt_position == 20

    await cover.stop()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000145:1",
        paramset_key="VALUES",
        parameter="STOP",
        value=True,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await cover.stop_tilt()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU0000145:1",
        paramset_key="VALUES",
        parameter="STOP",
        value=True,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await cover.open_tilt()
    await central.event(const.INTERFACE_ID, "VCU0000145:1", "LEVEL_SLATS", _OPEN_TILT_LEVEL)
    call_count = len(mock_client.method_calls)
    await cover.open_tilt()
    await central.event(const.INTERFACE_ID, "VCU0000145:1", "LEVEL_SLATS", _OPEN_TILT_LEVEL)
    assert call_count == len(mock_client.method_calls) - 2

    await cover.close_tilt()
    await central.event(const.INTERFACE_ID, "VCU0000145:1", "LEVEL_SLATS", _CLOSED_LEVEL)
    call_count = len(mock_client.method_calls)
    await cover.close_tilt()
    await central.event(const.INTERFACE_ID, "VCU0000145:1", "LEVEL_SLATS", _CLOSED_LEVEL)
    assert call_count == len(mock_client.method_calls) - 1

    await central.event(const.INTERFACE_ID, "VCU0000145:1", "LEVEL_SLATS", 0.4)
    call_count = len(mock_client.method_calls)
    await cover.set_position(tilt_position=40)
    assert call_count == len(mock_client.method_calls)


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    (
        "address_device_translation",
        "do_mock_client",
        "add_sysvars",
        "add_programs",
        "ignore_devices_on_create",
        "un_ignore_list",
    ),
    [
        (TEST_DEVICES, True, False, False, None, None),
    ],
)
async def test_ceipblind(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test CeIpBlind."""
    central, mock_client, _ = central_client_factory
    cover: CeIpBlind = cast(CeIpBlind, helper.get_prepared_custom_entity(central, "VCU1223813", 4))
    assert cover.usage == EntityUsage.CE_PRIMARY

    assert cover.current_position == 0
    assert cover.current_tilt_position == 0
    await cover.set_position(position=81)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU1223813:4",
        paramset_key="VALUES",
        parameter="COMBINED_PARAMETER",
        value="L2=0,L=81",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU1223813:4", "LEVEL", 0.81)
    assert cover.current_position == 81
    assert cover.current_tilt_position == 0

    await cover.open()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU1223813:4",
        paramset_key="VALUES",
        parameter="COMBINED_PARAMETER",
        value="L2=50,L=100",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU1223813:4", "LEVEL_2", _OPEN_TILT_LEVEL)
    await central.event(const.INTERFACE_ID, "VCU1223813:4", "LEVEL", _OPEN_LEVEL)
    assert cover.current_position == 100
    assert cover.current_tilt_position == 50

    await cover.close()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU1223813:4",
        paramset_key="VALUES",
        parameter="COMBINED_PARAMETER",
        value="L2=0,L=0",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU1223813:4", "LEVEL_2", _CLOSED_LEVEL)
    await central.event(const.INTERFACE_ID, "VCU1223813:4", "LEVEL", _CLOSED_LEVEL)
    assert cover.current_position == 0
    assert cover.current_tilt_position == 0

    await cover.open_tilt()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU1223813:4",
        paramset_key="VALUES",
        parameter="COMBINED_PARAMETER",
        value="L2=50,L=0",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU1223813:4", "LEVEL_2", 1.0)
    assert cover.current_position == 0
    assert cover.current_tilt_position == 100

    await cover.set_position(tilt_position=45)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU1223813:4",
        paramset_key="VALUES",
        parameter="COMBINED_PARAMETER",
        value="L2=45,L=0",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU1223813:4", "LEVEL_2", 0.45)
    assert cover.current_position == 0
    assert cover.current_tilt_position == 45

    await cover.close_tilt()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU1223813:4",
        paramset_key="VALUES",
        parameter="COMBINED_PARAMETER",
        value="L2=0,L=0",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU1223813:4", "LEVEL_2", _CLOSED_LEVEL)
    await central.event(const.INTERFACE_ID, "VCU1223813:4", "LEVEL", _CLOSED_LEVEL)
    assert cover.current_position == 0
    assert cover.current_tilt_position == 0

    await cover.set_position(position=10, tilt_position=20)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU1223813:4",
        paramset_key="VALUES",
        parameter="COMBINED_PARAMETER",
        value="L2=20,L=10",
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU1223813:4", "LEVEL", 0.1)
    await central.event(const.INTERFACE_ID, "VCU1223813:4", "LEVEL_2", 0.2)
    assert cover.current_position == 10
    assert cover.current_tilt_position == 20

    await central.event(const.INTERFACE_ID, "VCU1223813:3", "LEVEL", 0.5)
    assert cover._channel_level == 0.5
    assert cover.current_position == 50

    await central.event(const.INTERFACE_ID, "VCU1223813:3", "LEVEL_2", 0.8)
    assert cover._channel_tilt_level == 0.8
    assert cover.current_tilt_position == 80

    await central.event(const.INTERFACE_ID, "VCU1223813:3", "LEVEL", _CLOSED_LEVEL)
    assert cover._channel_level == _CLOSED_LEVEL
    assert cover.current_position == 0

    await central.event(const.INTERFACE_ID, "VCU1223813:3", "LEVEL_2", _CLOSED_LEVEL)
    assert cover._channel_tilt_level == _CLOSED_LEVEL
    assert cover.current_tilt_position == 0

    await central.event(const.INTERFACE_ID, "VCU1223813:3", "ACTIVITY_STATE", 1)
    assert cover.is_opening

    await central.event(const.INTERFACE_ID, "VCU1223813:3", "ACTIVITY_STATE", 2)
    assert cover.is_closing

    await central.event(const.INTERFACE_ID, "VCU1223813:3", "ACTIVITY_STATE", 3)
    assert cover.is_opening is False
    assert cover.is_closing is False

    await cover.stop()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU1223813:4",
        paramset_key="VALUES",
        parameter="STOP",
        value=True,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    (
        "address_device_translation",
        "do_mock_client",
        "add_sysvars",
        "add_programs",
        "ignore_devices_on_create",
        "un_ignore_list",
    ),
    [
        (TEST_DEVICES, True, False, False, None, None),
    ],
)
async def test_ceipblind_hdm(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test CeIpBlind HDM."""
    central, mock_client, _ = central_client_factory
    cover: CeIpBlind = cast(CeIpBlind, helper.get_prepared_custom_entity(central, "VCU3560967", 1))
    assert cover.usage == EntityUsage.CE_PRIMARY

    assert cover.current_position == 0
    assert cover.current_tilt_position == 0
    await cover.set_position(position=81)
    assert mock_client.method_calls[-3] == call.put_paramset(
        channel_address="VCU3560967:1",
        paramset_key="VALUES",
        values={"LEVEL_2": _CLOSED_LEVEL, "LEVEL": 0.81},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU3560967:1", "LEVEL", 0.81)
    assert cover.current_position == 81
    assert cover.current_tilt_position == 0

    await cover.open()
    assert mock_client.method_calls[-3] == call.put_paramset(
        channel_address="VCU3560967:1",
        paramset_key="VALUES",
        values={"LEVEL_2": 0.5, "LEVEL": _OPEN_LEVEL},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU3560967:1", "LEVEL_2", _OPEN_TILT_LEVEL)
    await central.event(const.INTERFACE_ID, "VCU3560967:1", "LEVEL", _OPEN_LEVEL)
    assert cover.current_position == 100
    assert cover.current_tilt_position == 50

    await cover.close()
    assert mock_client.method_calls[-3] == call.put_paramset(
        channel_address="VCU3560967:1",
        paramset_key="VALUES",
        values={"LEVEL_2": _CLOSED_LEVEL, "LEVEL": _CLOSED_LEVEL},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU3560967:1", "LEVEL_2", _CLOSED_LEVEL)
    await central.event(const.INTERFACE_ID, "VCU3560967:1", "LEVEL", _CLOSED_LEVEL)
    assert cover.current_position == 0
    assert cover.current_tilt_position == 0

    await cover.open_tilt()
    assert mock_client.method_calls[-3] == call.put_paramset(
        channel_address="VCU3560967:1",
        paramset_key="VALUES",
        values={"LEVEL_2": _OPEN_TILT_LEVEL, "LEVEL": _CLOSED_LEVEL},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU3560967:1", "LEVEL_2", 1.0)
    assert cover.current_position == 0
    assert cover.current_tilt_position == 100

    await cover.set_position(tilt_position=45)
    assert mock_client.method_calls[-3] == call.put_paramset(
        channel_address="VCU3560967:1",
        paramset_key="VALUES",
        values={"LEVEL_2": 0.45, "LEVEL": _CLOSED_LEVEL},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU3560967:1", "LEVEL_2", 0.45)
    assert cover.current_position == 0
    assert cover.current_tilt_position == 45

    await cover.close_tilt()
    assert mock_client.method_calls[-3] == call.put_paramset(
        channel_address="VCU3560967:1",
        paramset_key="VALUES",
        values={"LEVEL_2": _CLOSED_LEVEL, "LEVEL": _CLOSED_LEVEL},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU3560967:1", "LEVEL_2", _CLOSED_LEVEL)
    await central.event(const.INTERFACE_ID, "VCU3560967:1", "LEVEL", _CLOSED_LEVEL)
    assert cover.current_position == 0
    assert cover.current_tilt_position == 0

    await cover.set_position(position=10, tilt_position=20)
    assert mock_client.method_calls[-3] == call.put_paramset(
        channel_address="VCU3560967:1",
        paramset_key="VALUES",
        values={"LEVEL_2": 0.2, "LEVEL": 0.1},
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU3560967:1", "LEVEL", 0.1)
    await central.event(const.INTERFACE_ID, "VCU3560967:1", "LEVEL_2", 0.2)
    assert cover.current_position == 10
    assert cover.current_tilt_position == 20

    await central.event(const.INTERFACE_ID, "VCU3560967:1", "ACTIVITY_STATE", 1)
    assert cover.is_opening

    await central.event(const.INTERFACE_ID, "VCU3560967:1", "ACTIVITY_STATE", 2)
    assert cover.is_closing

    await central.event(const.INTERFACE_ID, "VCU3560967:1", "ACTIVITY_STATE", 3)
    assert cover.is_opening is False
    assert cover.is_closing is False

    await cover.stop()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU3560967:1",
        paramset_key="VALUES",
        parameter="STOP",
        value=True,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    (
        "address_device_translation",
        "do_mock_client",
        "add_sysvars",
        "add_programs",
        "ignore_devices_on_create",
        "un_ignore_list",
    ),
    [
        (TEST_DEVICES, True, False, False, None, None),
    ],
)
async def test_cegarageho(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test CeGarageHO."""
    central, mock_client, _ = central_client_factory
    cover: CeGarage = cast(CeGarage, helper.get_prepared_custom_entity(central, "VCU3574044", 1))
    assert cover.usage == EntityUsage.CE_PRIMARY

    assert cover.current_position is None
    await cover.set_position(position=81)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU3574044:1",
        paramset_key="VALUES",
        parameter="DOOR_COMMAND",
        value=1,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU3574044:1", "DOOR_STATE", 1)
    assert cover.current_position == 100
    await cover.close()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU3574044:1",
        paramset_key="VALUES",
        parameter="DOOR_COMMAND",
        value=3,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU3574044:1", "DOOR_STATE", 0)
    assert cover.current_position == 0
    assert cover.is_closed is True
    await cover.set_position(position=11)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU3574044:1",
        paramset_key="VALUES",
        parameter="DOOR_COMMAND",
        value=4,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU3574044:1", "DOOR_STATE", 2)
    assert cover.current_position == 10

    await cover.set_position(position=5)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU3574044:1",
        paramset_key="VALUES",
        parameter="DOOR_COMMAND",
        value=3,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU3574044:1", "DOOR_STATE", 0)
    assert cover.current_position == 0

    await cover.open()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU3574044:1",
        paramset_key="VALUES",
        parameter="DOOR_COMMAND",
        value=1,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await cover.stop()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU3574044:1",
        paramset_key="VALUES",
        parameter="DOOR_COMMAND",
        value=2,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await central.event(const.INTERFACE_ID, "VCU3574044:1", "DOOR_STATE", 1)
    assert cover.current_position == 100

    await central.event(
        const.INTERFACE_ID, "VCU3574044:1", "SECTION", GarageDoorActivity.OPENING.value
    )
    assert cover.is_opening is True
    await central.event(
        const.INTERFACE_ID, "VCU3574044:1", "SECTION", GarageDoorActivity.CLOSING.value
    )
    assert cover.is_closing is True

    await central.event(const.INTERFACE_ID, "VCU3574044:1", "SECTION", None)
    assert cover.is_opening is None
    await central.event(const.INTERFACE_ID, "VCU3574044:1", "SECTION", None)
    assert cover.is_closing is None
    await central.event(const.INTERFACE_ID, "VCU3574044:1", "DOOR_STATE", None)
    assert cover.is_closed is None

    await central.event(const.INTERFACE_ID, "VCU3574044:1", "DOOR_STATE", 0)
    call_count = len(mock_client.method_calls)
    await cover.close()
    assert call_count == len(mock_client.method_calls)

    await central.event(const.INTERFACE_ID, "VCU3574044:1", "DOOR_STATE", 1)
    call_count = len(mock_client.method_calls)
    await cover.open()
    assert call_count == len(mock_client.method_calls)

    await central.event(const.INTERFACE_ID, "VCU3574044:1", "DOOR_STATE", 2)
    call_count = len(mock_client.method_calls)
    await cover.vent()
    assert call_count == len(mock_client.method_calls)


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    (
        "address_device_translation",
        "do_mock_client",
        "add_sysvars",
        "add_programs",
        "ignore_devices_on_create",
        "un_ignore_list",
    ),
    [
        (TEST_DEVICES, True, False, False, None, None),
    ],
)
async def test_cegaragetm(
    central_client_factory: tuple[CentralUnit, Client | Mock, helper.Factory],
) -> None:
    """Test CeGarageTM."""
    central, mock_client, _ = central_client_factory
    cover: CeGarage = cast(CeGarage, helper.get_prepared_custom_entity(central, "VCU6166407", 1))
    assert cover.usage == EntityUsage.CE_PRIMARY

    assert cover.current_position is None
    await cover.set_position(position=81)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU6166407:1",
        paramset_key="VALUES",
        parameter="DOOR_COMMAND",
        value=1,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU6166407:1", "DOOR_STATE", 1)
    assert cover.current_position == 100
    await cover.close()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU6166407:1",
        paramset_key="VALUES",
        parameter="DOOR_COMMAND",
        value=3,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU6166407:1", "DOOR_STATE", 0)
    assert cover.current_position == 0
    assert cover.is_closed is True
    await cover.set_position(position=11)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU6166407:1",
        paramset_key="VALUES",
        parameter="DOOR_COMMAND",
        value=4,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU6166407:1", "DOOR_STATE", 2)
    assert cover.current_position == 10

    await cover.set_position(position=5)
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU6166407:1",
        paramset_key="VALUES",
        parameter="DOOR_COMMAND",
        value=3,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await central.event(const.INTERFACE_ID, "VCU6166407:1", "DOOR_STATE", 0)
    assert cover.current_position == 0

    await cover.open()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU6166407:1",
        paramset_key="VALUES",
        parameter="DOOR_COMMAND",
        value=1,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )
    await cover.stop()
    assert mock_client.method_calls[-1] == call.set_value(
        channel_address="VCU6166407:1",
        paramset_key="VALUES",
        parameter="DOOR_COMMAND",
        value=2,
        wait_for_callback=WAIT_FOR_CALLBACK,
    )

    await central.event(const.INTERFACE_ID, "VCU6166407:1", "DOOR_STATE", 1)
    assert cover.current_position == 100

    await central.event(const.INTERFACE_ID, "VCU6166407:1", "SECTION", GarageDoorActivity.OPENING)
    assert cover.is_opening is True
    await central.event(const.INTERFACE_ID, "VCU6166407:1", "SECTION", GarageDoorActivity.CLOSING)
    assert cover.is_closing is True

    await central.event(const.INTERFACE_ID, "VCU6166407:1", "SECTION", None)
    assert cover.is_opening is None
    await central.event(const.INTERFACE_ID, "VCU6166407:1", "SECTION", None)
    assert cover.is_closing is None
    await central.event(const.INTERFACE_ID, "VCU6166407:1", "DOOR_STATE", None)
    assert cover.is_closed is None
