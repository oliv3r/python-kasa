"""Implementation of firmware module for smartcam devices."""

from __future__ import annotations

import logging

from ...feature import Feature
from ...smart.smartmodule import allow_update_after
from ..smartcammodule import SmartCamModule

_LOGGER = logging.getLogger(__name__)


class Firmware(SmartCamModule):
    """Implementation of firmware update controls."""

    REQUIRED_COMPONENT = "firmware"

    QUERY_GETTER_NAME = "getFirmwareAutoUpgradeConfig"
    QUERY_MODULE_NAME = "auto_upgrade"
    QUERY_SECTION_NAMES = "common"

    def _initialize_features(self) -> None:
        """Initialize features after the initial update."""
        self._add_feature(
            Feature(
                self._device,
                id="auto_update_enabled",
                name="Auto update",
                container=self,
                attribute_getter="auto_update_enabled",
                attribute_setter="set_auto_update",
                type=Feature.Type.Switch,
                category=Feature.Category.Config,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="check_firmware",
                name="Check for update",
                container=self,
                attribute_setter="check_latest_firmware",
                type=Feature.Type.Action,
                category=Feature.Category.Config,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="start_firmware_upgrade",
                name="Start firmware upgrade",
                container=self,
                attribute_setter="start_upgrade",
                type=Feature.Type.Action,
                category=Feature.Category.Config,
            )
        )

    @property
    def auto_update_enabled(self) -> bool:
        """Return True if automatic firmware updates are enabled."""
        return self.data.get("common", {}).get("enabled", "off") == "on"

    @allow_update_after
    async def set_auto_update(self, enable: bool) -> dict:
        """Enable or disable automatic firmware updates."""
        return await self._device._query_setter_helper(
            "setFirmwareAutoUpgradeConfig",
            self.QUERY_MODULE_NAME,
            "common",
            {"enabled": "on" if enable else "off"},
        )

    async def check_latest_firmware(self) -> dict:
        """Trigger a cloud check for available firmware updates."""
        return await self.call(
            "checkFirmwareVersionByCloud",
            {self.QUERY_MODULE_NAME: {"check_fw_version": {}}},
        )

    async def start_upgrade(self) -> dict:
        """Start a firmware upgrade. Device will reboot after completion."""
        return await self.call(
            "startFirmwareUpgrade",
            {self.QUERY_MODULE_NAME: {"fw_download": {}}},
        )
