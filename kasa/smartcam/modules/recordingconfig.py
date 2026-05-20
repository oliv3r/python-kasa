"""Implementation of recording configuration module."""

from __future__ import annotations

import logging

from ...feature import Feature
from ...smart.smartmodule import allow_update_after
from ..smartcammodule import SmartCamModule

_LOGGER = logging.getLogger(__name__)

WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

#: Maps user-facing mode names to the record-type suffix used in plan strings.
RECORD_MODE_TO_TYPE: dict[str, str] = {
    "continuous": "1",
    "motion": "2",
}

RECORD_TYPE_TO_MODE: dict[str, str] = {v: k for k, v in RECORD_MODE_TO_TYPE.items()}


def _all_day_plan(record_type: str) -> str:
    """Return an all-day plan string for the given record type (``"1"`` or ``"2"``)."""
    return f'["0000-2400:{record_type}"]'


def _mode_from_plan(day_value: str) -> str:
    """Parse the record type from a plan string and return the mode name."""
    try:
        record_type = day_value.strip('["').split(":")[-1].rstrip('"]')
        return RECORD_TYPE_TO_MODE.get(record_type, "continuous")
    except Exception:
        return "continuous"


class RecordingConfig(SmartCamModule):
    """Implementation of SD card recording configuration module.

    Combines two device APIs:

    * ``getRecordPlan`` / ``setRecordPlan`` — per-weekday schedule with
      ``continuous`` (type 1) or ``motion``-triggered (type 2) recording.
    * ``getCircularRecordingConfig`` / ``setCircularRecordingConfig`` — loop
      recording toggle: when ``on`` the oldest footage is overwritten when the
      card is full.

    For simple 24/7 recording use :meth:`enable_recording`. For motion-only
    recording use ``enable_recording(mode="motion")``.
    """

    REQUIRED_COMPONENT = "record"

    QUERY_GETTER_NAME = "getRecordPlan"
    QUERY_MODULE_NAME = "record_plan"
    QUERY_SECTION_NAMES = "chn1_channel"

    def query(self) -> dict:
        """Return queries for plan and circular recording config."""
        q = super().query()
        q["getCircularRecordingConfig"] = {"harddisk_manage": {"harddisk": {}}}
        return q

    def _initialize_features(self) -> None:
        """Initialize features after the initial update."""
        self._add_feature(
            Feature(
                self._device,
                id="recording_enabled",
                name="Recording enabled",
                container=self,
                attribute_getter="recording_enabled",
                attribute_setter="set_recording_enabled",
                type=Feature.Type.Switch,
                category=Feature.Category.Config,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="loop_recording",
                name="Loop recording",
                container=self,
                attribute_getter="loop_recording",
                attribute_setter="set_loop_recording",
                type=Feature.Type.Switch,
                category=Feature.Category.Config,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                id="recording_mode",
                name="Recording mode",
                container=self,
                attribute_getter="recording_mode",
                attribute_setter="set_recording_mode",
                choices_getter="recording_modes",
                type=Feature.Type.Choice,
                category=Feature.Category.Config,
            )
        )

    @property
    def _plan(self) -> dict:
        return (
            self.data.get("getRecordPlan", {})
            .get("record_plan", {})
            .get("chn1_channel", {})
        )

    @property
    def _harddisk(self) -> dict:
        return (
            self.data.get("getCircularRecordingConfig", {})
            .get("harddisk_manage", {})
            .get("harddisk", {})
        )

    @property
    def recording_enabled(self) -> bool:
        """Return True if the recording schedule is active."""
        return self._plan.get("enabled", "off") == "on"

    @allow_update_after
    async def set_recording_enabled(self, enable: bool) -> dict:
        """Enable or disable the recording schedule."""
        return await self._device._query_setter_helper(
            "setRecordPlan",
            "record_plan",
            "chn1_channel",
            {"enabled": "on" if enable else "off"},
        )

    @property
    def loop_recording(self) -> bool:
        """Return True if loop recording (overwrite oldest) is enabled."""
        return self._harddisk.get("loop", "off") == "on"

    @allow_update_after
    async def set_loop_recording(self, enable: bool) -> dict:
        """Enable or disable loop recording."""
        return await self._device._query_setter_helper(
            "setCircularRecordingConfig",
            "harddisk_manage",
            "harddisk",
            {"loop": "on" if enable else "off"},
        )

    @property
    def recording_modes(self) -> list[str]:
        """Return supported recording modes."""
        return list(RECORD_MODE_TO_TYPE.keys())

    @property
    def recording_mode(self) -> str:
        """Return current recording mode (``"continuous"`` or ``"motion"``)."""
        monday = self._plan.get("monday", "")
        return _mode_from_plan(monday)

    @allow_update_after
    async def set_recording_mode(self, mode: str) -> dict:
        """Set recording mode for all days (``"continuous"`` or ``"motion"``)."""
        if mode not in RECORD_MODE_TO_TYPE:
            raise ValueError(
                f"Invalid mode {mode!r}. Valid: {self.recording_modes}"
            )
        record_type = RECORD_MODE_TO_TYPE[mode]
        plan = _all_day_plan(record_type)
        return await self._device._query_setter_helper(
            "setRecordPlan",
            "record_plan",
            "chn1_channel",
            {day: plan for day in WEEKDAYS},
        )

    async def enable_recording(self, mode: str = "continuous") -> None:
        """Enable 24/7 recording to SD card.

        Sets the schedule to all-day on all days, enables loop recording, and
        turns on the plan.  ``mode`` is ``"continuous"`` (default) or
        ``"motion"`` for event-triggered recording only.
        """
        if mode not in RECORD_MODE_TO_TYPE:
            raise ValueError(
                f"Invalid mode {mode!r}. Valid: {self.recording_modes}"
            )
        record_type = RECORD_MODE_TO_TYPE[mode]
        plan = _all_day_plan(record_type)
        await self._device._query_setter_helper(
            "setRecordPlan",
            "record_plan",
            "chn1_channel",
            {"enabled": "on", **{day: plan for day in WEEKDAYS}},
        )
        await self.set_loop_recording(True)

    async def disable_recording(self) -> None:
        """Disable recording (schedule off, loop recording off)."""
        await self.set_recording_enabled(False)
        await self.set_loop_recording(False)
