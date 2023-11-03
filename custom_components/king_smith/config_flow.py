"""Config flow for Walkingpad."""
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import bluetooth
from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_entry_flow, device_registry

from .const import DOMAIN

KNOWN_UUIDS = [
    "00001800-0000-1000-8000-00805f9b34fb",
    "0000180a-0000-1000-8000-00805f9b34fb",
    "00010203-0405-0607-0809-0a0b0c0d1912",
    "0000fe00-0000-1000-8000-00805f9b34fb",
    "00002902-0000-1000-8000-00805f9b34fb",
    "00010203-0405-0607-0809-0a0b0c0d1912",
    "00002901-0000-1000-8000-00805f9b34fb",
    "00002a00-0000-1000-8000-00805f9b34fb",
    "00002a01-0000-1000-8000-00805f9b34fb",
    "00002a04-0000-1000-8000-00805f9b34fb",
    "00002a25-0000-1000-8000-00805f9b34fb",
    "00002a26-0000-1000-8000-00805f9b34fb",
    "00002a28-0000-1000-8000-00805f9b34fb",
    "00002a24-0000-1000-8000-00805f9b34fb",
    "00002a29-0000-1000-8000-00805f9b34fb",
    "0000fe01-0000-1000-8000-00805f9b34fb",
    "0000fe02-0000-1000-8000-00805f9b34fb",
    "00010203-0405-0607-0809-0a0b0c0d2b12",
]


class WalkingpadConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Walkingpad."""

    VERSION = 0.1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_bluetooth(
        self, discovery_info: bluetooth.BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle the bluetooth discovery step."""
        await self.async_set_unique_id(
            device_registry.format_mac(discovery_info.address)
        )
        self._abort_if_unique_id_configured()

        self.devices = [f"{discovery_info.address} ({discovery_info.name})"]
        return await self.async_step_device()

    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle setting up a device."""
        if not user_input:
            schema_mac = str
            if self.devices:
                schema_mac = vol.In(self.devices)
            schema = vol.Schema(
                {vol.Required(CONF_NAME): str, vol.Required(CONF_MAC): schema_mac}
            )
            return self.async_show_form(step_id="device", data_schema=schema)

        user_input[CONF_MAC] = user_input[CONF_MAC][:17]
        unique_id = device_registry.format_mac(user_input[CONF_MAC])
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)
