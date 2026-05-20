"""Implementation of image flip/rotation module."""

from __future__ import annotations

import logging

from ...feature import Feature
from ...smart.smartmodule import allow_update_after
from ..smartcammodule import SmartCamModule

_LOGGER = logging.getLogger(__name__)

#: Known valid values for ``flip_type``.
FLIP_TYPES = ["off", "flip_h", "flip_v", "flip_hv"]


class ImageFlip(SmartCamModule):
    """Implementation of image flip and rotation controls."""

    REQUIRED_COMPONENT = "image"

    QUERY_GETTER_NAME = "getImageLumaConfig"
    QUERY_MODULE_NAME = "image"
    QUERY_SECTION_NAMES = "flip"

    def _initialize_features(self) -> None:
        """Initialize features after the initial update."""
        self._add_feature(
            Feature(
                self._device,
                id="flip_type",
                name="Image flip",
                container=self,
                attribute_getter="flip_type",
                attribute_setter="set_flip_type",
                choices_getter=lambda: FLIP_TYPES,
                type=Feature.Type.Choice,
                category=Feature.Category.Config,
            )
        )

    @property
    def flip_type(self) -> str:
        """Return the current image flip type."""
        return self.data.get("flip", {}).get("flip_type", "off")

    @allow_update_after
    async def set_flip_type(self, flip_type: str) -> dict:
        """Set image flip type (``off``, ``flip_h``, ``flip_v``, ``flip_hv``)."""
        return await self._device._query_setter_helper(
            "setImageLumaConfig",
            self.QUERY_MODULE_NAME,
            "flip",
            {"flip_type": flip_type},
        )
