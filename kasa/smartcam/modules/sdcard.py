"""Implementation of SD card status module."""

from __future__ import annotations

import logging

from ...feature import Feature
from ..smartcammodule import SmartCamModule

_LOGGER = logging.getLogger(__name__)


class SDCard(SmartCamModule):
    """Implementation of SD card / local storage status module.

    Exposes read-only status and capacity information for the first
    installed SD card.  When no card is present every value reflects
    the ``"offline"`` / ``"0B"`` defaults the device returns.
    """

    REQUIRED_COMPONENT = "sdCard"

    QUERY_GETTER_NAME = "getSdCardStatus"
    QUERY_MODULE_NAME = "harddisk_manage"
    QUERY_SECTION_NAMES = None

    def _initialize_features(self) -> None:
        """Initialize features after the initial update."""
        self._add_feature(
            Feature(
                self._device,
                id="sd_status",
                name="SD card status",
                container=self,
                attribute_getter="status",
                type=Feature.Type.Sensor,
                category=Feature.Category.Info,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="sd_total_space",
                name="SD card total space",
                container=self,
                attribute_getter="total_space",
                type=Feature.Type.Sensor,
                category=Feature.Category.Info,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="sd_free_space",
                name="SD card free space",
                container=self,
                attribute_getter="free_space",
                type=Feature.Type.Sensor,
                category=Feature.Category.Info,
            )
        )

        self._add_feature(
            Feature(
                self._device,
                id="sd_format",
                name="Format SD card",
                container=self,
                attribute_setter="format",
                type=Feature.Type.Action,
                category=Feature.Category.Config,
            )
        )

    @property
    def _hd_info(self) -> dict:
        """Return the first disk's info dict, or empty dict when offline."""
        hd_list = self.data.get("hd_info", [])
        if not hd_list:
            return {}
        entry = hd_list[0]
        if not isinstance(entry, dict) or not entry:
            return {}
        return next(iter(entry.values()), {})

    @property
    def status(self) -> str:
        """Return SD card status string (e.g. ``"normal"``, ``"offline"``)."""
        return self._hd_info.get("status", "offline")

    @property
    def total_space(self) -> str:
        """Return total SD card capacity string as reported by device (e.g. ``"32GB"``)."""
        return self._hd_info.get("total_space", "0B")

    @property
    def free_space(self) -> str:
        """Return free SD card space string as reported by device (e.g. ``"28GB"``)."""
        return self._hd_info.get("free_space", "0B")

    @property
    def write_protected(self) -> bool:
        """Return True if the SD card is write-protected."""
        return self._hd_info.get("write_protect", "0") != "0"

    async def format(self) -> dict:
        """Trigger an SD card format. All recorded data will be erased."""
        return await self.call(
            "formatSdCard", {"harddisk_manage": {"harddisk_format": {}}}
        )
