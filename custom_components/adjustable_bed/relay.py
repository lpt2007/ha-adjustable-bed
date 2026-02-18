import asyncio
import logging

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class RelayBed:
    """Relay backend for adjustable bed using switch entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        head_up: str,
        head_down: str,
        feet_up: str,
        feet_down: str,
        pulse_time: float = 0.5,
    ):
        self.hass = hass
        self.head_up = head_up
        self.head_down = head_down
        self.feet_up = feet_up
        self.feet_down = feet_down
        self.pulse_time = pulse_time

        _LOGGER.debug(
            "RelayBed initialized: head_up=%s head_down=%s feet_up=%s feet_down=%s",
            head_up,
            head_down,
            feet_up,
            feet_down,
        )

    async def _pulse(self, entity_id: str):
        """Pulse relay."""
        _LOGGER.debug("Pulsing relay: %s", entity_id)

        await self.hass.services.async_call(
            "switch",
            "turn_on",
            {"entity_id": entity_id},
            blocking=True,
        )

        await asyncio.sleep(self.pulse_time)

        await self.hass.services.async_call(
            "switch",
            "turn_off",
            {"entity_id": entity_id},
            blocking=True,
        )

    async def head_up_cmd(self):
        await self._pulse(self.head_up)

    async def head_down_cmd(self):
        await self._pulse(self.head_down)

    async def feet_up_cmd(self):
        await self._pulse(self.feet_up)

    async def feet_down_cmd(self):
        await self._pulse(self.feet_down)

    async def stop_cmd(self):
        await self.hass.services.async_call(
            "switch",
            "turn_off",
            {
                "entity_id": [
                    self.head_up,
                    self.head_down,
                    self.feet_up,
                    self.feet_down,
                ]
            },
            blocking=True,
        )

from __future__ import annotations

import logging

from homeassistant.exceptions import ServiceValidationError

from .beds.base import BedController
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class RelayController(BedController):
    """Relay-based controller that uses HA switch entities instead of BLE."""

    # Capability flags used throughout the integration (checked via getattr()).
    supports_memory_presets = False
    supports_memory_programming = False
    memory_slot_count = 0

    def __init__(
        self,
        coordinator,
        relay_bed,  # instance of RelayBed (your class)
    ) -> None:
        super().__init__(coordinator)
        self._relay = relay_bed

    @property
    def control_characteristic_uuid(self) -> str:
        # Not applicable for relay backend
        return ""

    # --- Motors: map BACK/LEGS to HEAD/FEET so entities don't break ---
    async def move_head_up(self) -> None:
        await self._relay.head_up_cmd()

    async def move_head_down(self) -> None:
        await self._relay.head_down_cmd()

    async def move_head_stop(self) -> None:
        await self._relay.stop_cmd()

    async def move_back_up(self) -> None:
        # Treat back as head (common 2-motor beds)
        await self._relay.head_up_cmd()

    async def move_back_down(self) -> None:
        await self._relay.head_down_cmd()

    async def move_back_stop(self) -> None:
        await self._relay.stop_cmd()

    async def move_legs_up(self) -> None:
        # Treat legs as feet
        await self._relay.feet_up_cmd()

    async def move_legs_down(self) -> None:
        await self._relay.feet_down_cmd()

    async def move_legs_stop(self) -> None:
        await self._relay.stop_cmd()

    async def move_feet_up(self) -> None:
        await self._relay.feet_up_cmd()

    async def move_feet_down(self) -> None:
        await self._relay.feet_down_cmd()

    async def move_feet_stop(self) -> None:
        await self._relay.stop_cmd()

    async def stop_all(self) -> None:
        await self._relay.stop_cmd()

    # --- Presets: without extra relays these are NOT supported ---
    async def preset_flat(self) -> None:
        raise ServiceValidationError(
            "Presets are not supported by relay backend (no preset relays configured).",
            translation_domain=DOMAIN,
        )

    async def preset_memory(self, memory_num: int) -> None:
        raise ServiceValidationError(
            "Memory presets are not supported by relay backend.",
            translation_domain=DOMAIN,
        )

    async def program_memory(self, memory_num: int) -> None:
        raise ServiceValidationError(
            "Programming presets is not supported by relay backend.",
            translation_domain=DOMAIN,
        )
