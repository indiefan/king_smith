"""Config flow for Walkingpad."""
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import bluetooth
from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import device_registry

from .const import DOMAIN

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
