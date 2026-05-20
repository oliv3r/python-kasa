"""Implementation of day/night mode module."""

from __future__ import annotations

import logging

from ...feature import Feature
from ...smart.smartmodule import allow_update_after
from ..smartcammodule import SmartCamModule

_LOGGER = logging.getLogger(__name__)

#: Maps wire values to human-readable labels.
DAY_NIGHT_MODE_LABELS: dict[str, str] = {
    "auto": "Auto",
    "off": "Day",
    "on": "Night",
}


class DayNightMode(SmartCamModule):
    """Implementation of day/night mode module.

    Controls the camera's IR cut filter.  Wire values are counter-intuitive:
    ``"off"`` = forced day (colour), ``"on"`` = forced night (B&W + IR),
    ``"auto"`` = sensor-controlled.  Distinct from :class:`NightVision`,
    which picks the supplement lamp type used while in night mode.
    """

    REQUIRED_COMPONENT = "dayNightMode"

    QUERY_GETTER_NAME = "getDayNightModeConfig"
    QUERY_MODULE_NAME = "image"
    QUERY_SECTION_NAMES = "common"

    def _initialize_features(self) -> None:
        """Initialize features after the initial update."""
        self._add_feature(
            Feature(
                self._device,
                id="day_night_mode",
                name="Day/night mode",
                container=self,
                attribute_getter="mode",
                attribute_setter="set_mode",
                choices_getter="modes",
                type=Feature.Type.Choice,
                category=Feature.Category.Config,
            )
        )

    @property
    def _common(self) -> dict:
        return self.data.get("common", {})

    @property
    def mode(self) -> str:
        """Return current day/night mode: ``"auto"``, ``"off"`` (day), ``"on"`` (night)."""
        return self._common.get("inf_type", "auto")

    @property
    def modes(self) -> list[str]:
        """Return supported day/night mode wire values."""
        return list(DAY_NIGHT_MODE_LABELS.keys())

    @allow_update_after
    async def set_mode(self, mode: str) -> dict:
        """Set the day/night mode.

        :param mode: ``"auto"`` (sensor-controlled), ``"off"`` (force day),
            or ``"on"`` (force night).
        """
        if mode not in self.modes:
            raise ValueError(
                f"Invalid day/night mode {mode!r}. "
                f"Valid modes: {self.modes}"
            )
        return await self._device._query_setter_helper(
            "setDayNightModeConfig",
            self.QUERY_MODULE_NAME,
            "common",
            {"inf_type": mode},
        )
