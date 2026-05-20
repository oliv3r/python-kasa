"""Implementation of OSD (on-screen display) module."""

from __future__ import annotations

import logging

from ...feature import Feature
from ...smart.smartmodule import allow_update_after
from ..smartcammodule import SmartCamModule

_LOGGER = logging.getLogger(__name__)


class OSD(SmartCamModule):
    """Implementation of OSD (on-screen display) module.

    Controls overlay text, timestamps and logo on the camera video feed.

    Note: The exact wire structure for ``getOsd`` / ``setOsd`` varies by
    firmware.  Properties access data defensively with ``.get()`` so that
    missing fields return safe defaults rather than raising exceptions.
    """

    REQUIRED_COMPONENT = "osd"

    QUERY_GETTER_NAME = "getOsd"
    QUERY_MODULE_NAME = "OSD"
    QUERY_SECTION_NAMES = ["date_info", "label_info"]

    def _initialize_features(self) -> None:
        """Initialize features after the initial update."""
        self._add_feature(
            Feature(
                self._device,
                id="osd_date",
                name="OSD date/time",
                container=self,
                attribute_getter="date_enabled",
                attribute_setter="set_date_enabled",
                type=Feature.Type.Switch,
                category=Feature.Category.Config,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="osd_label",
                name="OSD label",
                container=self,
                attribute_getter="label_enabled",
                attribute_setter="set_label_enabled",
                type=Feature.Type.Switch,
                category=Feature.Category.Config,
            )
        )

    @property
    def _date_info(self) -> dict:
        return self.data.get("date_info", {})

    @property
    def _label_info(self) -> dict:
        labels = self.data.get("label_info", [])
        if isinstance(labels, list) and labels:
            return labels[0] if isinstance(labels[0], dict) else {}
        return labels if isinstance(labels, dict) else {}

    @property
    def date_enabled(self) -> bool:
        """Return True if the date/time overlay is enabled."""
        return self._date_info.get("enabled", "off") == "on"

    @allow_update_after
    async def set_date_enabled(self, enable: bool) -> dict:
        """Enable or disable the date/time overlay."""
        return await self._device._query_setter_helper(
            "setOsd",
            self.QUERY_MODULE_NAME,
            "date_info",
            {"enabled": "on" if enable else "off"},
        )

    @property
    def label_enabled(self) -> bool:
        """Return True if the name/label overlay is enabled."""
        enabled = self._label_info.get("enabled", "off")
        return enabled == "on"

    @allow_update_after
    async def set_label_enabled(self, enable: bool) -> dict:
        """Enable or disable the name/label overlay."""
        return await self._device._query_setter_helper(
            "setOsd",
            self.QUERY_MODULE_NAME,
            "label_info",
            {"enabled": "on" if enable else "off"},
        )

    @property
    def label_text(self) -> str:
        """Return the custom label text shown on the video overlay."""
        return self._label_info.get("text", "")

    @allow_update_after
    async def set_label_text(self, text: str) -> dict:
        """Set the custom label text shown on the video overlay."""
        return await self._device._query_setter_helper(
            "setOsd",
            self.QUERY_MODULE_NAME,
            "label_info_1",
            {"text": text},
        )
