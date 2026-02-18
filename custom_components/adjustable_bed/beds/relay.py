# add by LPT2007 18.2.2026
"""Relay bed controller implementation.

Implements BedController by pulsing HA switch entities instead of BLE commands.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.exceptions import ServiceValidationError

from ..const import CONF_RELAY_FEET_DOWN, CONF_RELAY_FEET_UP, CONF_RELAY_HEAD_DOWN, CONF_RELAY_HEAD_UP
from ..relay import RelayBed
from .base import BedController

if TYPE_CHECKING:
    from ..coordinator import AdjustableBedCoordinator

_LOGGER = logging.getLogger(__name__)


class RelayController(BedController):
    """Controller for relay-driven beds."""

    def __init__(self, coordinator: AdjustableBedCoordinator) -> None:
        super().__init__(coordinator)

        # These should be stored in entry.data (or options) by your config flow.
        data = coordinator.entry.data
        self._head_up = data.get(CONF_RELAY_HEAD_UP, "")
        self._head_down = data.get(CONF_RELAY_HEAD_DOWN, "")
        self._feet_up = data.get(CONF_RELAY_FEET_UP, "")
        self._feet_down = data.get(CONF_RELAY_FEET_DOWN, "")

        # Optional pulse setting could be added later; keep it simple for now
        self._relay = RelayBed(coordinator.hass)

    @property
    def control_characteristic_uuid(self) -> str:
        """Relay backend has no BLE characteristic."""
        return ""

    @property
    def supports_stop_all(self) -> bool:
        """Stop is a no-op for pulse relays (each press is discrete)."""
        return False

    @property
    def has_discrete_motor_control(self) -> bool:
        """Relay is inherently discrete (button-press style)."""
        return True

    @property
    def supports_motor_control(self) -> bool:
        """Yes, via discrete pulses."""
        return True

    @property
    def supports_position_feedback(self) -> bool:
        """No position feedback for relay backend."""
        return False

    def _missing(self, key: str) -> ServiceValidationError:
        return ServiceValidationError(
            f"Relay entity not configured for '{key}'. Reconfigure the integration."
        )

    async def _pulse_or_raise(self, entity_id: str, key: str) -> None:
        if not entity_id:
            raise self._missing(key)
        await self._relay.pulse(entity_id)

    # Motor methods (map to pulses)

    async def move_head_up(self) -> None:
        await self._pulse_or_raise(self._head_up, "head_up")

    async def move_head_down(self) -> None:
        await self._pulse_or_raise(self._head_down, "head_down")

    async def move_head_stop(self) -> None:
        # Discrete pulses: nothing to stop
        return

    async def move_back_up(self) -> None:
        # If you treat "back" as same as head for 2-relay head pair, map it:
        await self.move_head_up()

    async def move_back_down(self) -> None:
        await self.move_head_down()

    async def move_back_stop(self) -> None:
        return

    async def move_legs_up(self) -> None:
        # Treat legs as same as feet for relay mapping
        await self._pulse_or_raise(self._feet_up, "feet_up")

    async def move_legs_down(self) -> None:
        await self._pulse_or_raise(self._feet_down, "feet_down")

    async def move_legs_stop(self) -> None:
        return

    async def move_feet_up(self) -> None:
        await self._pulse_or_raise(self._feet_up, "feet_up")

    async def move_feet_down(self) -> None:
        await self._pulse_or_raise(self._feet_down, "feet_down")

    async def move_feet_stop(self) -> None:
        return

    async def stop_all(self) -> None:
        # No-op for discrete pulses
        return

    # Presets not supported (unless you add extra relays later)

    async def preset_flat(self) -> None:
        raise ServiceValidationError("Relay backend does not support presets")

    async def preset_memory(self, memory_num: int) -> None:  # noqa: ARG002
        raise ServiceValidationError("Relay backend does not support presets")

    async def program_memory(self, memory_num: int) -> None:  # noqa: ARG002
        raise ServiceValidationError("Relay backend does not support memory programming")
