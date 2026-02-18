# added by LPT2007 18.2.2026
"""Relay-based transport helpers for Adjustable Bed integration.

This module contains ONLY the RelayBed helper which pulses HA switch entities.
Controller implementation lives under beds/ (see beds/relay.py).
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Final

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DEFAULT_PULSE_SECONDS: Final[float] = 0.25


@dataclass(slots=True)
class RelayBed:
    """Helper to control a bed via HA switch entities (relays).

    This is a thin transport wrapper that:
    - turns a switch ON
    - waits pulse_seconds
    - turns it OFF (best-effort)

    The mapping from bed actions to entity_ids is handled by RelayController.
    """

    hass: HomeAssistant
    pulse_seconds: float = DEFAULT_PULSE_SECONDS

    async def pulse(self, entity_id: str) -> None:
        """Pulse a relay switch entity (turn on then off)."""
        if not entity_id:
            raise ValueError("entity_id is required")

        _LOGGER.debug("Pulsing relay %s for %.3fs", entity_id, self.pulse_seconds)

        await self.hass.services.async_call(
            "switch",
            "turn_on",
            {"entity_id": entity_id},
            blocking=True,
        )

        try:
            await asyncio.sleep(self.pulse_seconds)
        finally:
            # Best effort OFF - don't crash if entity disappears mid-call
            try:
                await self.hass.services.async_call(
                    "switch",
                    "turn_off",
                    {"entity_id": entity_id},
                    blocking=True,
                )
            except Exception:  # noqa: BLE001
                _LOGGER.debug("Failed to turn off relay %s", entity_id, exc_info=True)
