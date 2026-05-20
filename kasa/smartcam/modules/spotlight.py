"""Implementation of spotlight (white lamp) module."""

from __future__ import annotations

import logging

from ...feature import Feature
from ...smart.smartmodule import allow_update_after
from ..smartcammodule import SmartCamModule

_LOGGER = logging.getLogger(__name__)

INTENSITY_MIN = 1
INTENSITY_MAX = 100


class Spotlight(SmartCamModule):
    """Implementation of spotlight (white lamp) controls."""

    REQUIRED_COMPONENT = "whiteLamp"

    QUERY_GETTER_NAME = "getWhitelampConfig"
    QUERY_MODULE_NAME = "light_control"
    QUERY_SECTION_NAMES = "white_lamp"

    def _initialize_features(self) -> None:
        """Initialize features after the initial update."""
        self._add_feature(
            Feature(
                self._device,
                id="spotlight_turn_on",
                name="Turn on spotlight",
                container=self,
                attribute_setter="turn_on",
                type=Feature.Type.Action,
                category=Feature.Category.Config,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="spotlight_turn_off",
                name="Turn off spotlight",
                container=self,
                attribute_setter="turn_off",
                type=Feature.Type.Action,
                category=Feature.Category.Config,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="spotlight_intensity",
                name="Spotlight intensity",
                container=self,
                attribute_getter="intensity",
                attribute_setter="set_intensity",
                type=Feature.Type.Number,
                range_getter=lambda: (INTENSITY_MIN, INTENSITY_MAX),
                category=Feature.Category.Config,
            )
        )

    @property
    def intensity(self) -> int:
        """Return current spotlight intensity level (1-100)."""
        return int(self.data.get("white_lamp", {}).get("wtl_intensity_level", 1))

    @allow_update_after
    async def set_intensity(self, intensity: int) -> dict:
        """Set spotlight intensity level (1-100)."""
        if not INTENSITY_MIN <= intensity <= INTENSITY_MAX:
            raise ValueError(
                f"Intensity must be between {INTENSITY_MIN} and {INTENSITY_MAX},"
                + f" got {intensity}"
            )
        return await self._device._query_setter_helper(
            "setWhitelampConfig",
            self.QUERY_MODULE_NAME,
            "white_lamp",
            {"wtl_intensity_level": str(intensity)},
        )

    async def turn_on(self) -> dict:
        """Turn the spotlight on.

        The device will automatically turn off after the configured timeout
        (``time_limit_max_sec``, typically 300 s / 5 min).
        """
        return await self.call(
            "white_lamp_start", {"light_control": {"white_lamp_start": {}}}
        )

    async def turn_off(self) -> dict:
        """Turn the spotlight off immediately."""
        return await self.call(
            "white_lamp_stop", {"light_control": {"white_lamp_stop": {}}}
        )
