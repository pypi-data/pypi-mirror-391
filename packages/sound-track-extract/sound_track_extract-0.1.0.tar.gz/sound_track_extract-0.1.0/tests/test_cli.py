import shutil
import subprocess
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from sound_track_extract import cli


def test_parse_timecode_seconds():
    formatted, seconds = cli._parse_timecode("90", "Start")
    assert formatted == "01:30"
    assert seconds == pytest.approx(90.0)


def test_parse_timecode_hms():
    formatted, seconds = cli._parse_timecode("00:10:05.250", "Start")
    assert formatted == "10:05.25"
    assert seconds == pytest.approx(605.25)


def test_parse_timecode_invalid_negative():
    with pytest.raises(typer.BadParameter):
        cli._parse_timecode("-5", "Start")


def test_build_command_includes_map_when_track_selected(tmp_path):
    input_video = tmp_path / "input.mp4"
    input_video.write_text("dummy")
    output_audio = tmp_path / "output.mp3"
    profile = cli.AUDIO_FORMATS["mp3"]

    cmd = cli._build_command(
        ffmpeg_bin="ffmpeg",
        input_path=input_video,
        output_path=output_audio,
        profile=profile,
        bitrate="192k",
        sample_rate=48000,
        channels=2,
        start_time="00:00:01",
        end_time="00:00:05",
        force=True,
        audio_track_index=2,
        metadata={"title": "Sample"},
    )

    assert "-map" in cmd
    map_idx = cmd.index("-map")
    assert cmd[map_idx + 1] == "0:a:2"
    assert "-b:a" in cmd


def test_build_command_omits_map_without_track(tmp_path):
    input_video = tmp_path / "input.mp4"
    input_video.write_text("dummy")
    output_audio = tmp_path / "output.mp3"
    profile = cli.AUDIO_FORMATS["flac"]

    cmd = cli._build_command(
        ffmpeg_bin="ffmpeg",
        input_path=input_video,
        output_path=output_audio,
        profile=profile,
        bitrate=None,
        sample_rate=None,
        channels=None,
        start_time=None,
        end_time=None,
        force=False,
        audio_track_index=None,
        metadata={},
    )

    assert "-map" not in cmd
    assert "-b:a" not in cmd  # lossless, so no bitrate flag


def test_human_size_formats_bytes():
    assert cli._human_size(512) == "512.0 B"
    assert cli._human_size(1536) == "1.5 KB"


def test_resolve_output_path_with_template(tmp_path):
    video = tmp_path / "clip.mov"
    video.write_text("x")
    target = cli._resolve_output_path(
        input_video=video,
        fmt_key="mp3",
        explicit_output=None,
        output_dir=tmp_path / "exports",
        name_template="{stem}_track{track}",
        audio_track=2,
    )
    assert target == tmp_path / "exports" / "clip_track2.mp3"


def test_resolve_output_path_rejects_unknown_placeholder(tmp_path):
    video = tmp_path / "clip.mov"
    video.write_text("x")
    with pytest.raises(typer.BadParameter):
        cli._resolve_output_path(
            input_video=video,
            fmt_key="mp3",
            explicit_output=None,
            output_dir=None,
            name_template="{unknown}",
            audio_track=None,
        )


def test_build_command_includes_metadata(tmp_path):
    input_video = tmp_path / "in.mp4"
    input_video.write_text("x")
    output_audio = tmp_path / "out.mp3"
    profile = cli.AUDIO_FORMATS["mp3"]
    cmd = cli._build_command(
        ffmpeg_bin="ffmpeg",
        input_path=input_video,
        output_path=output_audio,
        profile=profile,
        bitrate=None,
        sample_rate=None,
        channels=None,
        start_time=None,
        end_time=None,
        force=True,
        audio_track_index=None,
        metadata={"title": "Foo", "artist": "Bar"},
    )
    meta_flags = [
        (cmd[i + 1])
        for i, arg in enumerate(cmd[:-1])
        if arg == "-metadata"
    ]
    assert "title=Foo" in meta_flags
    assert "artist=Bar" in meta_flags


def test_cli_integration_generates_audio(tmp_path):
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        pytest.skip("ffmpeg/ffprobe not available")

    video = tmp_path / "fixture.mp4"
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=160x90:d=1",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=1000:duration=1",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-shortest",
            str(video),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    tracks, duration = cli._probe_audio_tracks(ffprobe, video)
    assert tracks, "ffprobe should find at least one track"
    if duration is not None:
        assert duration == pytest.approx(1.0, rel=0.2)

    runner = CliRunner()
    out_dir = tmp_path / "out"
    result = runner.invoke(
        cli.app,
        [
            "--output-dir",
            str(out_dir),
            "--name-template",
            "{stem}_audio",
            str(video),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, result.output
    expected = out_dir / "fixture_audio.mp3"
    assert expected.exists()
    assert expected.stat().st_size > 0
