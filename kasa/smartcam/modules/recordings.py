"""Recording search and stream-URL module for SMARTCAM devices."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from urllib.parse import urlencode

from ..smartcammodule import SmartCamModule

_LOGGER = logging.getLogger(__name__)

_STREAM_PORT = 8800
_PAGE_SIZE = 99


@dataclass
class Recording:
    """A single recording clip stored on the SD card.

    ``stream_url`` is an MPEG-TS stream endpoint on port 8800.
    Authenticate with HTTP Digest using the same credentials as the
    JSON API (username ``admin``, device password).  Pass it directly
    to ffmpeg/VLC::

        ffmpeg -i "<stream_url>" -c copy clip.mp4
    """

    start_time: int
    """Unix timestamp of the clip start."""

    end_time: int
    """Unix timestamp of the clip end."""

    video_type: str
    """Recording trigger type as reported by the device (e.g. ``"2"``)."""

    stream_url: str
    """
    ``http://<camera>:8800/stream?...`` URL for this clip.

    Fetched via ``POST`` with HTTP Digest auth.  The response body is a
    ``video/mp2t`` stream that ends when the device sends a
    ``stream_status=finished`` notification.
    """

    @property
    def start(self) -> datetime:
        """Return clip start as a UTC :class:`~datetime.datetime`."""
        return datetime.fromtimestamp(self.start_time, tz=timezone.utc)

    @property
    def end(self) -> datetime:
        """Return clip end as a UTC :class:`~datetime.datetime`."""
        return datetime.fromtimestamp(self.end_time, tz=timezone.utc)

    @property
    def duration(self) -> int:
        """Return clip duration in seconds."""
        return self.end_time - self.start_time


class Recordings(SmartCamModule):
    """Search SD-card recordings and obtain stream URLs.

    All methods query the device on demand — there is no periodic
    background update for this module.

    Example::

        await device.update()
        rec_module = device.modules[SmartCamModule.SmartCamRecordings]

        dates = await rec_module.get_recording_dates(start, end)
        clips = await rec_module.get_recordings(dates[0])
        print(clips[0].stream_url)   # hand to ffmpeg / VLC
    """

    REQUIRED_COMPONENT = "recordDownload"

    QUERY_GETTER_NAME = None
    QUERY_MODULE_NAME = "playback"

    def _initialize_features(self) -> None:
        """No persistent features for a search-only module."""

    def _build_stream_url(self, start_time: int, player_id: str) -> str:
        """Construct the port-8800 MPEG-TS stream URL for a clip."""
        params = urlencode(
            {
                "deviceId": self._device.device_id,
                "playerId": player_id,
                "type": "sdvod",
                "start_time": start_time,
            }
        )
        return f"http://{self._device.host}:{_STREAM_PORT}/stream?{params}"

    def _parse_clips(self, items: list[dict], player_id: str) -> list[Recording]:
        """Convert raw playback dicts to :class:`Recording` instances."""
        result = []
        for item in items:
            start_time = item.get("start_time", 0)
            end_time = item.get("end_time", 0)
            video_type = item.get("vedio_type") or item.get("video_type", "2")
            result.append(
                Recording(
                    start_time=start_time,
                    end_time=end_time,
                    video_type=video_type,
                    stream_url=self._build_stream_url(start_time, player_id),
                )
            )
        return result

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_recording_dates(
        self,
        start: datetime,
        end: datetime,
    ) -> list[str]:
        """Return ``YYYYMMDD`` date strings that contain at least one recording.

        Both *start* and *end* should be timezone-aware datetimes.
        """
        resp = await self._device.protocol.query(
            {
                "searchDateWithVideo": {
                    "playback": {
                        "start_time": int(start.timestamp()),
                        "end_time": int(end.timestamp()),
                    }
                }
            }
        )
        data = resp.get("searchDateWithVideo", {}).get("playback", {})
        return data.get("date_list", [])

    async def get_recordings(
        self,
        recording_date: date | str,
        *,
        channel: int = 1,
    ) -> list[Recording]:
        """Return all clips recorded on *recording_date*.

        *recording_date* may be a :class:`datetime.date` or a ``YYYYMMDD``
        string.  Results are sorted by start time (oldest first).
        """
        if isinstance(recording_date, date):
            date_str = recording_date.strftime("%Y%m%d")
        else:
            date_str = recording_date

        player_id = uuid.uuid4().hex.upper()
        resp = await self._device.protocol.query(
            {
                "searchVideoOfDay": {
                    "playback": {
                        "date": date_str,
                        "start_index": 0,
                        "end_index": _PAGE_SIZE,
                        "channel": channel,
                        "id": 1,
                    }
                }
            }
        )
        items = (
            resp.get("searchVideoOfDay", {})
            .get("playback", {})
            .get("recording_list", [])
        )
        return self._parse_clips(items, player_id)

    async def get_recordings_by_time(
        self,
        start: datetime,
        end: datetime,
        *,
        channel: int = 0,
    ) -> list[Recording]:
        """Return clips whose start time falls within *start*–*end* (UTC).

        Both datetimes should be timezone-aware.
        """
        player_id = uuid.uuid4().hex.upper()
        resp = await self._device.protocol.query(
            {
                "searchVideoWithUTC": {
                    "playback": {
                        "start_time": int(start.timestamp()),
                        "end_time": int(end.timestamp()),
                        "start_index": 0,
                        "end_index": _PAGE_SIZE,
                        "channel": channel,
                    }
                }
            }
        )
        items = (
            resp.get("searchVideoWithUTC", {})
            .get("playback", {})
            .get("recording_list", [])
        )
        return self._parse_clips(items, player_id)
