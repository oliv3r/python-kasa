"""Implementation of audio configuration module."""

from __future__ import annotations

import logging

from ...feature import Feature
from ...smart.smartmodule import allow_update_after
from ..smartcammodule import SmartCamModule

_LOGGER = logging.getLogger(__name__)


class AudioConfig(SmartCamModule):
    """Implementation of audio configuration module.

    Mute state is read-only; the device API provides no mute setter.
    """

    REQUIRED_COMPONENT = "audio"

    QUERY_GETTER_NAME = "getAudioConfig"
    QUERY_MODULE_NAME = "audio_config"
    QUERY_SECTION_NAMES = ["microphone", "speaker", "record_audio"]

    def _initialize_features(self) -> None:
        """Initialize features after the initial update."""
        self._add_feature(
            Feature(
                self._device,
                id="microphone_volume",
                name="Microphone volume",
                container=self,
                attribute_getter="microphone_volume",
                attribute_setter="set_microphone_volume",
                type=Feature.Type.Number,
                range_getter=lambda: (0, 100),
                category=Feature.Category.Config,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="microphone_mute",
                name="Microphone mute",
                container=self,
                attribute_getter="microphone_muted",
                type=Feature.Type.Switch,
                category=Feature.Category.Config,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="speaker_volume",
                name="Speaker volume",
                container=self,
                attribute_getter="speaker_volume",
                attribute_setter="set_speaker_volume",
                type=Feature.Type.Number,
                range_getter=lambda: (0, 100),
                category=Feature.Category.Config,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="record_audio",
                name="Record audio",
                container=self,
                attribute_getter="record_audio_enabled",
                attribute_setter="set_record_audio",
                type=Feature.Type.Switch,
                category=Feature.Category.Config,
            )
        )

    @property
    def _microphone(self) -> dict:
        return self.data.get("microphone", {})

    @property
    def _speaker(self) -> dict:
        return self.data.get("speaker", {})

    @property
    def microphone_volume(self) -> int:
        """Return microphone volume (0-100)."""
        return int(self._microphone.get("volume", 50))

    @allow_update_after
    async def set_microphone_volume(self, volume: int) -> dict:
        """Set microphone volume (0-100)."""
        if not 0 <= volume <= 100:
            raise ValueError(f"Volume must be between 0 and 100, got {volume}")
        return await self._device._query_setter_helper(
            "setMicrophoneVolume",
            self.QUERY_MODULE_NAME,
            "microphone",
            {"volume": str(volume)},
        )

    @property
    def microphone_muted(self) -> bool:
        """Return True if the microphone is muted (read-only hardware state)."""
        return self._microphone.get("mute", "off") == "on"

    @property
    def speaker_volume(self) -> int:
        """Return speaker volume (0-100)."""
        return int(self._speaker.get("volume", 50))

    @allow_update_after
    async def set_speaker_volume(self, volume: int) -> dict:
        """Set speaker volume (0-100)."""
        if not 0 <= volume <= 100:
            raise ValueError(f"Volume must be between 0 and 100, got {volume}")
        return await self._device._query_setter_helper(
            "setSpeakerVolume",
            self.QUERY_MODULE_NAME,
            "speaker",
            {"volume": str(volume)},
        )

    @property
    def speaker_muted(self) -> bool:
        """Return True if the speaker is muted (read-only hardware state)."""
        return self._speaker.get("mute", "off") == "on"

    @property
    def _record_audio(self) -> dict:
        return self.data.get("record_audio", {})

    @property
    def record_audio_enabled(self) -> bool:
        """Return True if audio is recorded alongside video."""
        return self._record_audio.get("enabled", "off") == "on"

    @allow_update_after
    async def set_record_audio(self, enable: bool) -> dict:
        """Enable or disable audio recording."""
        return await self._device._query_setter_helper(
            "setRecordAudio",
            self.QUERY_MODULE_NAME,
            "record_audio",
            {"enabled": "on" if enable else "off"},
        )
