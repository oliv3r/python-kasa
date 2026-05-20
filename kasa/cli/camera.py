"""Module for cli camera control commands."""

from __future__ import annotations

from datetime import datetime, timezone

import asyncclick as click

from kasa import Credentials, Device, Module

from .common import echo, error, pass_dev_or_child


def _require_module(dev: Device, module_name, label: str):
    mod = dev.modules.get(module_name)
    if not mod:
        error(f"Device does not support {label}.")
    return mod


@click.group()
@pass_dev_or_child
def camera(dev) -> None:
    """Commands to control camera settings."""


@camera.command()
@click.option("--username", required=True, prompt=True)
@click.option("--password", required=True, prompt=True)
@pass_dev_or_child
async def update_third_account_credentials(dev: Device, username: str, password: str):
    """Update camera third-account credentials."""
    cam = _require_module(dev, Module.Camera, "camera module")
    if cam is None:
        return
    if not hasattr(cam, "update_third_account_credentials"):
        error("Camera module does not support third-account credential updates.")
        return
    await cam.update_third_account_credentials(username, password)
    echo("Third-account credentials updated and verified.")


@camera.command(name="stream_rtsp_url")
@click.option("--username", required=True, prompt=True)
@click.option("--password", required=True, prompt=True)
@click.option(
    "--stream-resolution",
    type=click.Choice(["hd", "sd"], case_sensitive=False),
    default="hd",
    show_default=True,
)
@pass_dev_or_child
async def stream_rtsp_url(dev: Device, username: str, password: str, stream_resolution: str):
    """Print the RTSP URL for the camera stream."""
    cam = _require_module(dev, Module.Camera, "camera module")
    if cam is None:
        return
    from kasa.smartcam.modules.camera import StreamResolution

    url = cam.stream_rtsp_url(
        Credentials(username, password),
        stream_resolution=StreamResolution(stream_resolution.upper()),
    )
    if url is None:
        error("Unable to generate RTSP URL.")
        return
    echo(url)




@camera.command(name="night-vision")
@click.argument("mode", required=False)
@pass_dev_or_child
async def night_vision(dev: Device, mode: str | None):
    """Get or set night vision mode.

    MODE values: inf_night_vision, wtl_night_vision, md_night_vision,
    shed_night_vision, lamp_closed_vision.
    Run without MODE to see the current setting and available choices.
    """
    mod = _require_module(dev, Module.NightVision, "night vision")
    if mod is None:
        return
    if mode is None:
        echo(f"Night vision mode: {mod.mode}")
        echo(f"Available modes:   {', '.join(mod.modes)}")
        return
    if mode not in mod.modes:
        error(f"Invalid mode {mode!r}. Valid: {', '.join(mod.modes)}")
        return
    await mod.set_mode(mode)
    echo(f"Night vision mode set to {mode!r}.")




@camera.group()
@pass_dev_or_child
def osd(dev) -> None:
    """Commands to control on-screen display."""


@osd.command(name="date")
@click.argument("state", type=click.Choice(["on", "off"]))
@pass_dev_or_child
async def osd_date(dev: Device, state: str):
    """Enable or disable the date/time overlay (on/off)."""
    mod = _require_module(dev, Module.OSD, "OSD")
    if mod is None:
        return
    await mod.set_date_enabled(state == "on")
    echo(f"OSD date overlay {'enabled' if state == 'on' else 'disabled'}.")


@osd.command(name="label")
@click.argument("state", type=click.Choice(["on", "off"]))
@pass_dev_or_child
async def osd_label(dev: Device, state: str):
    """Enable or disable the name/label overlay (on/off)."""
    mod = _require_module(dev, Module.OSD, "OSD")
    if mod is None:
        return
    await mod.set_label_enabled(state == "on")
    echo(f"OSD label overlay {'enabled' if state == 'on' else 'disabled'}.")




@camera.group()
@pass_dev_or_child
def audio(dev) -> None:
    """Commands to control audio settings."""


@audio.command(name="microphone")
@click.option("--volume", type=click.IntRange(0, 100), default=None)
@pass_dev_or_child
async def audio_microphone(dev: Device, volume: int | None):
    """Get or set microphone volume.

    Run without options to see current state.  Mute is read-only on this device.
    """
    mod = _require_module(dev, Module.AudioConfig, "audio config")
    if mod is None:
        return
    if volume is None:
        echo(f"Microphone volume: {mod.microphone_volume}")
        echo(f"Microphone muted:  {mod.microphone_muted}")
        return
    await mod.set_microphone_volume(volume)
    echo(f"Microphone volume set to {volume}.")


@audio.command(name="speaker")
@click.option("--volume", type=click.IntRange(0, 100), default=None)
@pass_dev_or_child
async def audio_speaker(dev: Device, volume: int | None):
    """Get or set speaker volume.

    Run without options to see current state.  Mute is read-only on this device.
    """
    mod = _require_module(dev, Module.AudioConfig, "audio config")
    if mod is None:
        return
    if volume is None:
        echo(f"Speaker volume: {mod.speaker_volume}")
        echo(f"Speaker muted:  {mod.speaker_muted}")
        return
    await mod.set_speaker_volume(volume)
    echo(f"Speaker volume set to {volume}.")




@camera.command(name="video")
@click.option("--resolution", default=None, help="e.g. 1920*1080")
@click.option("--fps", type=int, default=None, help="e.g. 15, 20, 25")
@click.option("--codec", default=None, type=click.Choice(["H264", "H265"]))
@click.option(
    "--bitrate-type", "bitrate_type", default=None, type=click.Choice(["cbr", "vbr"])
)
@click.option("--smart-codec/--no-smart-codec", "smart_codec", default=None)
@pass_dev_or_child
async def video_quality(
    dev: Device,
    resolution: str | None,
    fps: int | None,
    codec: str | None,
    bitrate_type: str | None,
    smart_codec: bool | None,
):
    """Get or set video quality settings.

    Run without options to see current settings and available choices.
    """
    mod = _require_module(dev, Module.VideoQuality, "video quality")
    if mod is None:
        return

    if all(v is None for v in [resolution, fps, codec, bitrate_type, smart_codec]):
        echo(f"Resolution:   {mod.resolution}  (available: {', '.join(mod.resolutions)})")
        echo(f"Frame rate:   {mod.fps} fps  (available: {', '.join(str(f) for f in mod.fps_choices)})")
        echo(f"Codec:        {mod.encode_type}  (available: {', '.join(mod.encode_types)})")
        echo(f"Bitrate type: {mod.bitrate_type}  (available: {', '.join(mod.bitrate_types)})")
        echo(f"Smart codec:  {mod.smart_codec}")
        return

    if resolution is not None:
        await mod.set_resolution(resolution)
        echo(f"Resolution set to {resolution}.")
    if fps is not None:
        await mod.set_fps(fps)
        echo(f"Frame rate set to {fps} fps.")
    if codec is not None:
        await mod.set_encode_type(codec)
        echo(f"Codec set to {codec}.")
    if bitrate_type is not None:
        await mod.set_bitrate_type(bitrate_type)
        echo(f"Bitrate type set to {bitrate_type}.")
    if smart_codec is not None:
        await mod.set_smart_codec(smart_codec)
        echo(f"Smart codec {'enabled' if smart_codec else 'disabled'}.")




@camera.command(name="sdcard")
@pass_dev_or_child
async def sdcard(dev: Device):
    """Show SD card status and storage info."""
    mod = _require_module(dev, Module.SDCard, "SD card")
    if mod is None:
        return
    echo(f"Status:          {mod.status}")
    echo(f"Total space:     {mod.total_space}")
    echo(f"Free space:      {mod.free_space}")
    echo(f"Write protected: {mod.write_protected}")




@camera.group()
@pass_dev_or_child
def recording(dev) -> None:
    """Commands to control SD card recording."""


@recording.command(name="status")
@pass_dev_or_child
async def recording_status(dev: Device):
    """Show current recording configuration."""
    rec = _require_module(dev, Module.RecordingConfig, "recording config")
    if rec is None:
        return
    sd = dev.modules.get(Module.SDCard)
    echo(f"Recording enabled: {rec.recording_enabled}")
    echo(f"Recording mode:    {rec.recording_mode}")
    echo(f"Loop recording:    {rec.loop_recording}")
    if sd:
        echo(f"SD card status:    {sd.status}")
        echo(f"Free / Total:      {sd.free_space} / {sd.total_space}")


@recording.command(name="enable")
@click.option(
    "--mode",
    type=click.Choice(["continuous", "motion"]),
    default="continuous",
    show_default=True,
    help="continuous: record always; motion: record on motion events only",
)
@click.option("--audio/--no-audio", default=None, help="Enable or disable audio recording")
@pass_dev_or_child
async def recording_enable(dev: Device, mode: str, audio: bool | None):
    """Enable SD card recording (24/7 by default).

    Sets an all-day schedule for every day of the week and turns on loop
    recording so the oldest footage is overwritten when the card fills up.
    """
    rec = _require_module(dev, Module.RecordingConfig, "recording config")
    if rec is None:
        return
    await rec.enable_recording(mode=mode)
    echo(f"Recording enabled ({mode} mode, loop on).")
    if audio is not None:
        audio_mod = dev.modules.get(Module.AudioConfig)
        if audio_mod:
            from kasa.smartcam.modules.recordingconfig import RecordingConfig as RC
            if hasattr(rec._device, "_query_setter_helper"):
                await rec._device._query_setter_helper(
                    "setRecordAudio", "audio_config", "record_audio",
                    {"enabled": "on" if audio else "off"},
                )
            echo(f"Audio recording {'enabled' if audio else 'disabled'}.")
        else:
            echo("Note: device does not report audio recording support.")


@recording.command(name="disable")
@pass_dev_or_child
async def recording_disable(dev: Device):
    """Disable SD card recording (schedule off, loop off)."""
    rec = _require_module(dev, Module.RecordingConfig, "recording config")
    if rec is None:
        return
    await rec.disable_recording()
    echo("Recording disabled.")


@recording.command(name="loop")
@click.argument("state", type=click.Choice(["on", "off"]))
@pass_dev_or_child
async def recording_loop(dev: Device, state: str):
    """Enable or disable loop recording (overwrite oldest footage)."""
    rec = _require_module(dev, Module.RecordingConfig, "recording config")
    if rec is None:
        return
    await rec.set_loop_recording(state == "on")
    echo(f"Loop recording {'enabled' if state == 'on' else 'disabled'}.")


@recording.command(name="mode")
@click.argument("mode", type=click.Choice(["continuous", "motion"]))
@pass_dev_or_child
async def recording_mode(dev: Device, mode: str):
    """Set recording mode: continuous (24/7) or motion (event-triggered)."""
    rec = _require_module(dev, Module.RecordingConfig, "recording config")
    if rec is None:
        return
    await rec.set_recording_mode(mode)
    echo(f"Recording mode set to {mode!r}.")


@camera.group(name="recordings")
@pass_dev_or_child
def recordings_group(dev) -> None:
    """Search and stream SD card recordings."""


@recordings_group.command(name="dates")
@click.option(
    "--start",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Start date (YYYY-MM-DD).",
)
@click.option(
    "--end",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="End date (YYYY-MM-DD).",
)
@pass_dev_or_child
async def recordings_dates(dev: Device, start: datetime, end: datetime):
    """List dates that have recordings in the given range."""
    rec = _require_module(dev, Module.Recordings, "recordings")
    if rec is None:
        return
    dates = await rec.get_recording_dates(
        start.replace(tzinfo=timezone.utc),
        end.replace(tzinfo=timezone.utc),
    )
    if not dates:
        echo("No recordings found in range.")
        return
    for d in dates:
        echo(d)


@recordings_group.command(name="list")
@click.argument("date")
@click.option("--channel", default=1, show_default=True, help="Channel number.")
@pass_dev_or_child
async def recordings_list(dev: Device, date: str, channel: int):
    """List clips for DATE (YYYYMMDD) and print stream URLs.

    Stream URLs require HTTP Digest auth (same credentials as the device).
    To download a clip: ffmpeg -i "<url>" -c copy clip.mp4
    """
    rec = _require_module(dev, Module.Recordings, "recordings")
    if rec is None:
        return
    clips = await rec.get_recordings(date, channel=channel)
    if not clips:
        echo(f"No clips found for {date}.")
        return
    for clip in clips:
        echo(
            f"{clip.start.strftime('%Y-%m-%d %H:%M:%S')} → "
            f"{clip.end.strftime('%H:%M:%S')} "
            f"({clip.duration}s, type={clip.video_type})"
        )
        echo(f"  {clip.stream_url}")


@recordings_group.command(name="list-by-time")
@click.option(
    "--start",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]),
    help="Start datetime (UTC).",
)
@click.option(
    "--end",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]),
    help="End datetime (UTC).",
)
@click.option("--channel", default=0, show_default=True, help="Channel number.")
@pass_dev_or_child
async def recordings_list_by_time(
    dev: Device, start: datetime, end: datetime, channel: int
):
    """List clips in the given UTC time range and print stream URLs.

    Stream URLs require HTTP Digest auth (same credentials as the device).
    To download a clip: ffmpeg -i "<url>" -c copy clip.mp4
    """
    rec = _require_module(dev, Module.Recordings, "recordings")
    if rec is None:
        return
    clips = await rec.get_recordings_by_time(
        start.replace(tzinfo=timezone.utc),
        end.replace(tzinfo=timezone.utc),
        channel=channel,
    )
    if not clips:
        echo("No clips found in range.")
        return
    for clip in clips:
        echo(
            f"{clip.start.strftime('%Y-%m-%d %H:%M:%S')} → "
            f"{clip.end.strftime('%H:%M:%S')} "
            f"({clip.duration}s, type={clip.video_type})"
        )
        echo(f"  {clip.stream_url}")
