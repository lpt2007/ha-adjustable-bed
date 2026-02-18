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
