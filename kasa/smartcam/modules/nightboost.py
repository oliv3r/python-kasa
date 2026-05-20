"""Implementation of night boost (smart white lamp) module."""

from __future__ import annotations

import logging

from ...feature import Feature
from ...smart.smartmodule import allow_update_after
from ..smartcammodule import SmartCamModule

_LOGGER = logging.getLogger(__name__)


class NightBoost(SmartCamModule):
    """Implementation of night boost (smart white lamp auto-activation) controls."""

    REQUIRED_COMPONENT = "whiteLamp"

    QUERY_GETTER_NAME = "getSmartWhitelampConfig"
    QUERY_MODULE_NAME = "light_control"
    QUERY_SECTION_NAMES = "smart_white_lamp"

    def _initialize_features(self) -> None:
        """Initialize features after the initial update."""
        self._add_feature(
            Feature(
                self._device,
                id="night_boost_enabled",
                name="Night boost",
                container=self,
                attribute_getter="night_boost_enabled",
                attribute_setter="set_night_boost",
                type=Feature.Type.Switch,
                category=Feature.Category.Config,
            )
        )

    @property
    def night_boost_enabled(self) -> bool:
        """Return True if night boost (smart white lamp) is enabled."""
        return (
            self.data.get("smart_white_lamp", {}).get("enabled", "off") == "on"
        )

    @allow_update_after
    async def set_night_boost(self, enable: bool) -> dict:
        """Enable or disable night boost (automatic white lamp activation at night)."""
        return await self._device._query_setter_helper(
            "setSmartWhitelampConfig",
            self.QUERY_MODULE_NAME,
            "smart_white_lamp",
            {"enabled": "on" if enable else "off"},
        )
