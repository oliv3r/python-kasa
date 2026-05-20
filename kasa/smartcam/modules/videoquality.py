"""Implementation of video quality module."""

from __future__ import annotations

import logging

from ...feature import Feature
from ...smart.smartmodule import allow_update_after
from ..smartcammodule import SmartCamModule

_LOGGER = logging.getLogger(__name__)

_FPS_ENCODE_SHIFT = 16


def _decode_fps(wire_value: int) -> int:
    """Decode wire frame-rate value to frames-per-second integer.

    The device encodes fps as ``(1 << 16) | fps``, e.g. 65551 → 15 fps.
    """
    return wire_value & 0xFFFF


def _encode_fps(fps: int) -> int:
    """Encode frames-per-second integer to wire frame-rate value."""
    return (1 << _FPS_ENCODE_SHIFT) | fps


class VideoQuality(SmartCamModule):
    """Implementation of video quality module.

    Exposes resolution, frame rate, codec, bitrate type, and smart-codec
    toggle for the main video stream.

    Frame-rate wire encoding: the device stores fps as ``(1 << 16) | fps``.
    This class transparently decodes/encodes so callers always work with plain
    integer fps values (e.g. 15, 20, 25).
    """

    REQUIRED_COMPONENT = "video"

    QUERY_GETTER_NAME = "getVideoQualities"
    QUERY_MODULE_NAME = "video"
    QUERY_SECTION_NAMES = "main"

    def query(self) -> dict:
        """Return queries for qualities and capability."""
        q = super().query()
        q["getVideoCapability"] = {"video_capability": {"main": {}}}
        return q

    def _initialize_features(self) -> None:
        """Initialize features after the initial update."""
        self._add_feature(
            Feature(
                self._device,
                id="video_resolution",
                name="Resolution",
                container=self,
                attribute_getter="resolution",
                attribute_setter="set_resolution",
                choices_getter="resolutions",
                type=Feature.Type.Choice,
                category=Feature.Category.Config,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="video_fps",
                name="Frame rate",
                container=self,
                attribute_getter="fps",
                attribute_setter="set_fps",
                choices_getter="fps_choices",
                type=Feature.Type.Choice,
                category=Feature.Category.Config,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="video_encode_type",
                name="Video codec",
                container=self,
                attribute_getter="encode_type",
                attribute_setter="set_encode_type",
                choices_getter="encode_types",
                type=Feature.Type.Choice,
                category=Feature.Category.Config,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="video_bitrate_type",
                name="Bitrate type",
                container=self,
                attribute_getter="bitrate_type",
                attribute_setter="set_bitrate_type",
                choices_getter="bitrate_types",
                type=Feature.Type.Choice,
                category=Feature.Category.Config,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="video_smart_codec",
                name="Smart codec",
                container=self,
                attribute_getter="smart_codec",
                attribute_setter="set_smart_codec",
                type=Feature.Type.Switch,
                category=Feature.Category.Config,
            )
        )

    @property
    def _main(self) -> dict:
        return (
            self.data.get("getVideoQualities", {})
            .get("video", {})
            .get("main", {})
        )

    @property
    def _cap_main(self) -> dict:
        return (
            self.data.get("getVideoCapability", {})
            .get("video_capability", {})
            .get("main", {})
        )

    @property
    def resolution(self) -> str:
        """Return current resolution string, e.g. ``"1920*1080"``."""
        return self._main.get("resolution", "")

    @property
    def resolutions(self) -> list[str]:
        """Return supported resolutions."""
        return self._cap_main.get("resolutions", [self.resolution])

    @allow_update_after
    async def set_resolution(self, resolution: str) -> dict:
        """Set video resolution, e.g. ``"1920*1080"``."""
        if resolution not in self.resolutions:
            raise ValueError(
                f"Invalid resolution {resolution!r}. Valid: {self.resolutions}"
            )
        return await self._device._query_setter_helper(
            "setVideoQualities",
            self.QUERY_MODULE_NAME,
            "main",
            {"resolution": resolution},
        )

    @property
    def fps(self) -> int:
        """Return current frame rate in fps."""
        return _decode_fps(int(self._main.get("frame_rate", 1 << _FPS_ENCODE_SHIFT)))

    @property
    def fps_choices(self) -> list[int]:
        """Return supported frame rates in fps."""
        raw = self._cap_main.get("frame_rates", [])
        return [_decode_fps(int(v)) for v in raw] or [self.fps]

    @allow_update_after
    async def set_fps(self, fps: int) -> dict:
        """Set frame rate in fps (e.g. 15, 20, 25)."""
        if fps not in self.fps_choices:
            raise ValueError(
                f"Invalid fps {fps!r}. Valid: {self.fps_choices}"
            )
        return await self._device._query_setter_helper(
            "setVideoQualities",
            self.QUERY_MODULE_NAME,
            "main",
            {"frame_rate": str(_encode_fps(fps))},
        )

    @property
    def encode_type(self) -> str:
        """Return current video codec, e.g. ``"H264"``."""
        return self._main.get("encode_type", "")

    @property
    def encode_types(self) -> list[str]:
        """Return supported video codecs."""
        return self._cap_main.get("encode_types", [self.encode_type])

    @allow_update_after
    async def set_encode_type(self, encode_type: str) -> dict:
        """Set video codec, e.g. ``"H264"`` or ``"H265"``."""
        if encode_type not in self.encode_types:
            raise ValueError(
                f"Invalid encode_type {encode_type!r}. Valid: {self.encode_types}"
            )
        return await self._device._query_setter_helper(
            "setVideoQualities",
            self.QUERY_MODULE_NAME,
            "main",
            {"encode_type": encode_type},
        )

    @property
    def bitrate_type(self) -> str:
        """Return current bitrate type, e.g. ``"vbr"`` or ``"cbr"``."""
        return self._main.get("bitrate_type", "")

    @property
    def bitrate_types(self) -> list[str]:
        """Return supported bitrate types."""
        return self._cap_main.get("bitrate_types", [self.bitrate_type])

    @allow_update_after
    async def set_bitrate_type(self, bitrate_type: str) -> dict:
        """Set bitrate type, e.g. ``"vbr"`` or ``"cbr"``."""
        if bitrate_type not in self.bitrate_types:
            raise ValueError(
                f"Invalid bitrate_type {bitrate_type!r}. Valid: {self.bitrate_types}"
            )
        return await self._device._query_setter_helper(
            "setVideoQualities",
            self.QUERY_MODULE_NAME,
            "main",
            {"bitrate_type": bitrate_type},
        )

    @property
    def smart_codec(self) -> bool:
        """Return True if smart codec (adaptive bitrate) is enabled."""
        return self._main.get("smart_codec", "off") == "on"

    @allow_update_after
    async def set_smart_codec(self, enable: bool) -> dict:
        """Enable or disable smart codec."""
        return await self._device._query_setter_helper(
            "setVideoQualities",
            self.QUERY_MODULE_NAME,
            "main",
            {"smart_codec": "on" if enable else "off"},
        )
