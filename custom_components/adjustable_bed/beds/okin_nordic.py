"""Okin Nordic UART protocol bed controller implementation.

Reverse-engineered by @kristofferR based on discovery from @Zrau5454.
Source: https://github.com/kristofferR/ha-adjustable-bed/issues/50

This controller handles beds that use the 7-byte command format over Nordic UART service.
Known brands using this protocol:
- Mattress Firm 900 / iFlex

Commands follow the format: 5A 01 03 10 30 [XX] A5
Very similar to Okin 7-byte protocol (okin_7byte.py) but uses Nordic UART service.
See okin_7byte.py for the shared implementation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .okin_7byte import OKIN_NORDIC_CONFIG, Okin7ByteController

if TYPE_CHECKING:
    from ..coordinator import AdjustableBedCoordinator


class OkinNordicController(Okin7ByteController):
    """Controller for beds using Okin protocol over Nordic UART.

    Protocol discovered from Mattress Firm 900 (iFlex) beds.
    Thin subclass of Okin7ByteController using the Nordic UART configuration.
    """

    def __init__(self, coordinator: AdjustableBedCoordinator) -> None:
        """Initialize the Okin Nordic UART controller."""
        super().__init__(coordinator, config=OKIN_NORDIC_CONFIG)
