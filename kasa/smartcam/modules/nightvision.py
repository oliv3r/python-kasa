"""Implementation of night vision module."""

from __future__ import annotations

import logging

from ...feature import Feature
from ...smart.smartmodule import allow_update_after
from ..smartcammodule import SmartCamModule

_LOGGER = logging.getLogger(__name__)

#: Maps wire values to human-readable labels.
NIGHT_VISION_MODE_LABELS: dict[str, str] = {
    "inf_night_vision": "Infrared",
    "wtl_night_vision": "Full color",
    "md_night_vision": "Smart",
    "shed_night_vision": "Scheduled",
    "lamp_closed_vision": "Off",
}


class NightVision(SmartCamModule):
    """Implementation of night vision / supplement lamp module.

    Exposes a single ``night_vision_mode`` choice feature with the modes
    supported by the device:

    * ``inf_night_vision`` – infrared (IR) LEDs only, black-and-white image
    * ``wtl_night_vision`` – white spotlight / full-color night vision
    * ``md_night_vision`` – smart / automatic (device chooses IR or color)
    * ``shed_night_vision`` – scheduled switch between modes
    * ``lamp_closed_vision`` – supplement lamp off
    """

    REQUIRED_COMPONENT = "nightVisionMode"

    QUERY_GETTER_NAME = "getNightVisionModeConfig"
    QUERY_MODULE_NAME = "image"
    QUERY_SECTION_NAMES = "switch"

    def query(self) -> dict:
        """Return queries for config and capability."""
        q = super().query()
        q["getNightVisionCapability"] = {"image_capability": {}}
        return q

    def _initialize_features(self) -> None:
        """Initialize features after the initial update."""
        self._add_feature(
            Feature(
                self._device,
                id="night_vision_mode",
                name="Night vision mode",
                container=self,
                attribute_getter="mode",
                attribute_setter="set_mode",
                choices_getter="modes",
                type=Feature.Type.Choice,
                category=Feature.Category.Config,
            )
        )

    @property
    def _config(self) -> dict:
        """Return the image.switch section from the config response."""
        return (
            self.data.get("getNightVisionModeConfig", {})
            .get("image", {})
            .get("switch", {})
        )

    @property
    def _capability(self) -> dict:
        """Return supplement_lamp capability dict."""
        return (
            self.data.get("getNightVisionCapability", {})
            .get("image_capability", {})
            .get("supplement_lamp", {})
        )

    @property
    def mode(self) -> str:
        """Return the current night vision mode wire value."""
        return self._config.get("night_vision_mode", "inf_night_vision")

    @property
    def modes(self) -> list[str]:
        """Return the list of supported night vision mode wire values."""
        mode_range = self._capability.get("night_vision_mode_range")
        if mode_range:
            return list(mode_range)
        return list(NIGHT_VISION_MODE_LABELS.keys())

    @allow_update_after
    async def set_mode(self, mode: str) -> dict:
        """Set the night vision mode.

        :param mode: One of the values returned by :attr:`modes`,
            e.g. ``"inf_night_vision"``, ``"wtl_night_vision"``,
            ``"md_night_vision"``.
        """
        if mode not in self.modes:
            raise ValueError(
                f"Invalid night vision mode {mode!r}. "
                f"Valid modes: {self.modes}"
            )
        return await self._device._query_setter_helper(
            "setNightVisionModeConfig",
            "image",
            "switch",
            {"night_vision_mode": mode},
        )
