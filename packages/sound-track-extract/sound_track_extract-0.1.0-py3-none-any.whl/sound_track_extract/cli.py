from __future__ import annotations

import json
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List, Dict

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
app = typer.Typer(
    no_args_is_help=True,
    help="Extract clean audio tracks from video containers via ffmpeg.",
)


@dataclass(frozen=True)
class AudioProfile:
    label: str
    default_bitrate: Optional[str]
    lossless: bool


AUDIO_FORMATS: dict[str, AudioProfile] = {
    "mp3": AudioProfile("MP3 (320 kbps)", "320k", False),
    "aac": AudioProfile("AAC (256 kbps)", "256k", False),
    "ogg": AudioProfile("Ogg Vorbis (192 kbps)", "192k", False),
    "wav": AudioProfile("WAV (PCM 16-bit)", None, True),
    "flac": AudioProfile("FLAC (lossless)", None, True),
}


@dataclass(frozen=True)
class AudioTrack:
    order: int
    stream_index: int
    codec: str
    channels: int
    sample_rate: int
    bitrate: Optional[int]
    language: Optional[str]
    title: Optional[str]


def _require_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        console.print(
            "[bold red]ffmpeg was not found on PATH.[/]\n"
            "Install it via Homebrew (`brew install ffmpeg`) or your package manager."
        )
        raise typer.Exit(code=2)
    return ffmpeg


def _require_ffprobe() -> str:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        console.print(
            "[bold red]ffprobe was not found on PATH.[/]\n"
            "Install it alongside ffmpeg (`brew install ffmpeg`)."
        )
        raise typer.Exit(code=2)
    return ffprobe


def _parse_timecode(raw: Optional[str], label: str) -> Optional[Tuple[str, float]]:
    if raw is None:
        return None
    raw = raw.strip()
    if not raw:
        raise typer.BadParameter(f"{label} cannot be empty")

    def _format_seconds(total_seconds: float) -> str:
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = total_seconds % 60
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".rstrip("0").rstrip(".")
        if minutes:
            return f"{minutes:02d}:{seconds:06.3f}".rstrip("0").rstrip(".")
        return f"{seconds:.3f}".rstrip("0").rstrip(".")

    def _to_seconds(value: str) -> float:
        if ":" not in value:
            try:
                seconds = float(value)
            except ValueError as exc:  # noqa: B904
                raise typer.BadParameter(
                    f"{label} must be numeric seconds or HH:MM:SS, got '{value}'"
                ) from exc
            if seconds < 0:
                raise typer.BadParameter(f"{label} must be >= 0.")
            return seconds
        segments = value.split(":")
        if len(segments) > 3:
            raise typer.BadParameter(
                f"{label} supports up to HH:MM:SS precision, got '{value}'"
            )
        seconds = 0.0
        multiplier = 1.0
        for part in reversed(segments):
            try:
                seconds += float(part) * multiplier
            except ValueError as exc:  # noqa: B904
                raise typer.BadParameter(
                    f"{label} has an invalid time component '{part}'."
                ) from exc
            multiplier *= 60
        return seconds

    seconds = _to_seconds(raw)
    return _format_seconds(seconds), seconds


def _human_size(num_bytes: int) -> str:
    step = 1024.0
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for unit in units:
        if size < step:
            return f"{size:.1f} {unit}"
        size /= step
    return f"{size:.1f} PB"


def _build_command(
    ffmpeg_bin: str,
    input_path: Path,
    output_path: Path,
    profile: AudioProfile,
    bitrate: Optional[str],
    sample_rate: Optional[int],
    channels: Optional[int],
    start_time: Optional[str],
    end_time: Optional[str],
    force: bool,
    audio_track_index: Optional[int],
    metadata: Dict[str, str],
) -> list[str]:
    cmd = [
        ffmpeg_bin,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y" if force else "-n",
        "-i",
        str(input_path),
    ]

    if audio_track_index is not None:
        cmd.extend(["-map", f"0:a:{audio_track_index}"])

    if start_time:
        cmd.extend(["-ss", start_time])
    if end_time:
        cmd.extend(["-to", end_time])
    if sample_rate:
        cmd.extend(["-ar", str(sample_rate)])
    if channels:
        cmd.extend(["-ac", str(channels)])
    if not profile.lossless:
        chosen_bitrate = bitrate or profile.default_bitrate
        if chosen_bitrate:
            cmd.extend(["-b:a", chosen_bitrate])

    for key, value in metadata.items():
        cmd.extend(["-metadata", f"{key}={value}"])

    cmd.extend(["-vn", str(output_path)])
    return cmd


def _human_duration(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    if hours:
        return f"{hours:d}h {minutes:02d}m {secs:04.1f}s"
    if minutes:
        return f"{minutes:d}m {secs:04.1f}s"
    return f"{secs:.1f}s"


def _probe_audio_tracks(ffprobe_bin: str, input_path: Path) -> Tuple[List[AudioTrack], Optional[float]]:
    command = [
        ffprobe_bin,
        "-hide_banner",
        "-loglevel",
        "error",
        "-select_streams",
        "a",
        "-show_entries",
        "stream=index,codec_name,channels,sample_rate,bit_rate:stream_tags=language,title:format=duration",
        "-print_format",
        "json",
        str(input_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise typer.BadParameter(
            f"Unable to inspect audio tracks for '{input_path}'. ffprobe output:\n{result.stderr.strip()}"
        )
    payload = json.loads(result.stdout or "{}")
    tracks = []
    for order, stream in enumerate(payload.get("streams", [])):
        tags = stream.get("tags", {})
        bitrate = stream.get("bit_rate")
        try:
            bitrate_value = int(bitrate) if bitrate is not None else None
        except ValueError:
            bitrate_value = None
        tracks.append(
            AudioTrack(
                order=order,
                stream_index=int(stream.get("index", order)),
                codec=stream.get("codec_name", "unknown"),
                channels=int(stream.get("channels", 0)),
                sample_rate=int(stream.get("sample_rate", 0)),
                bitrate=bitrate_value,
                language=tags.get("language"),
                title=tags.get("title"),
            )
        )
    duration_raw = payload.get("format", {}).get("duration")
    try:
        duration = float(duration_raw) if duration_raw is not None else None
    except (TypeError, ValueError):
        duration = None
    return tracks, duration


def _render_track_listing(tracks: List[AudioTrack]) -> None:
    if not tracks:
        console.print("[bold red]No audio tracks were found in this file.[/]")
        raise typer.Exit(code=3)
    table = Table(title="Audio tracks", show_lines=False)
    table.add_column("Audio idx", justify="right")
    table.add_column("Stream id", justify="right")
    table.add_column("Codec")
    table.add_column("Channels", justify="right")
    table.add_column("Sample rate", justify="right")
    table.add_column("Bitrate", justify="right")
    table.add_column("Language")
    table.add_column("Title")
    for track in tracks:
        bitrate = f"{track.bitrate // 1000} kbps" if track.bitrate else "-"
        sample_rate = f"{track.sample_rate} Hz" if track.sample_rate else "-"
        channels = str(track.channels) if track.channels else "-"
        table.add_row(
            str(track.order),
            str(track.stream_index),
            track.codec,
            channels,
            sample_rate,
            bitrate,
            track.language or "-",
            track.title or "-",
        )
    console.print(table)


def _resolve_output_path(
    input_video: Path,
    fmt_key: str,
    explicit_output: Optional[Path],
    output_dir: Optional[Path],
    name_template: str,
    audio_track: Optional[int],
) -> Path:
    if explicit_output:
        if output_dir:
            raise typer.BadParameter("--output-dir cannot be combined with --output.")
        return explicit_output

    placeholders: Dict[str, str] = {
        "stem": input_video.stem,
        "format": fmt_key,
        "track": str(audio_track if audio_track is not None else 0),
    }
    try:
        rendered = name_template.format(**placeholders)
    except KeyError as exc:
        keys = ", ".join(placeholders.keys())
        raise typer.BadParameter(
            f"--name-template uses unknown placeholder '{exc.args[0]}'. "
            f"Available placeholders: {keys}."
        ) from exc

    rendered = rendered.strip()
    if not rendered:
        raise typer.BadParameter("--name-template resolved to an empty filename.")

    path = Path(rendered)
    base_dir = output_dir or input_video.parent
    if not path.is_absolute():
        path = base_dir / path

    if not path.suffix:
        path = path.with_suffix(f".{fmt_key}")
    return path


def _print_status(
    src: Path,
    dst: Path,
    fmt_label: str,
    sample_rate: Optional[int],
    channels: Optional[int],
    clip_desc: str,
    dry_run: bool,
    duration: Optional[float],
    metadata: Dict[str, str],
):
    table = Table.grid(padding=(0, 2))
    table.add_row("Source", str(src))
    table.add_row("Output", str(dst))
    table.add_row("Format", fmt_label)
    if duration is not None:
        table.add_row("Duration", _human_duration(duration))
    if clip_desc:
        table.add_row("Range", clip_desc)
    if sample_rate:
        table.add_row("Sample rate", f"{sample_rate} Hz")
    if channels:
        table.add_row("Channels", str(channels))
    if metadata:
        for key, value in metadata.items():
            table.add_row(key.title(), value)
    table.add_row("Mode", "Dry run" if dry_run else "Execute")
    console.print(Panel(table, title="Sound Track Extract", border_style="cyan"))


@app.command()
def extract(
    input_video: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Explicit path for the audio file. Defaults to <video_stem>.<format>.",
        writable=True,
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        help="Directory to place exports when --output is not supplied.",
        file_okay=False,
    ),
    name_template: str = typer.Option(
        "{stem}.{format}",
        "--name-template",
        help="Filename template when deriving output names. Placeholders: {stem}, {format}, {track}.",
    ),
    audio_format: str = typer.Option(
        "mp3",
        "--format",
        "-f",
        case_sensitive=False,
        help="Audio container/codec to export.",
    ),
    bitrate: Optional[str] = typer.Option(
        None,
        "--bitrate",
        "-b",
        help="Audio bitrate (e.g. 192k). Ignored for lossless formats.",
    ),
    sample_rate: Optional[int] = typer.Option(
        None, "--sample-rate", "-r", min=8000, help="Specify target sample rate (Hz)."
    ),
    channels: Optional[int] = typer.Option(
        None,
        "--channels",
        "-c",
        min=1,
        max=8,
        help="Force channel count (e.g. 1 for mono, 2 for stereo).",
    ),
    start: Optional[str] = typer.Option(
        None, "--start", help="Start time (seconds or HH:MM:SS)."
    ),
    end: Optional[str] = typer.Option(
        None, "--end", help="End time (seconds or HH:MM:SS)."
    ),
    audio_track: Optional[int] = typer.Option(
        None,
        "--audio-track",
        "-t",
        min=0,
        help="Select a specific audio stream index (use --list-tracks to inspect).",
    ),
    list_tracks: bool = typer.Option(
        False,
        "--list-tracks",
        help="Print available audio streams and exit without extracting.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-y",
        help="Overwrite the destination file if it already exists.",
    ),
    title: Optional[str] = typer.Option(
        None, "--title", help="Set the title metadata tag on the exported audio."
    ),
    artist: Optional[str] = typer.Option(
        None, "--artist", help="Set the artist metadata tag on the exported audio."
    ),
    album: Optional[str] = typer.Option(
        None, "--album", help="Set the album metadata tag on the exported audio."
    ),
    comment: Optional[str] = typer.Option(
        None, "--comment", help="Attach a free-form comment metadata tag."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show the ffmpeg command without executing it."
    ),
) -> None:
    """Extract the first audio track from a video file."""

    ffmpeg_bin = _require_ffmpeg()
    ffprobe_bin = _require_ffprobe()
    fmt_key = audio_format.lower()
    if fmt_key not in AUDIO_FORMATS:
        valid = ", ".join(AUDIO_FORMATS.keys())
        raise typer.BadParameter(f"Unsupported format '{audio_format}'. Try: {valid}")

    tracks, duration = _probe_audio_tracks(ffprobe_bin, input_video)
    if not tracks:
        raise typer.BadParameter(f"No audio streams found in '{input_video}'.")
    if list_tracks:
        _render_track_listing(tracks)
        raise typer.Exit()

    if audio_track is not None:
        orders = [track.order for track in tracks]
        if audio_track not in orders:
            available = ", ".join(str(i) for i in orders) or "none"
            raise typer.BadParameter(
                f"Audio track {audio_track} not found. Available indexes: {available}"
            )

    parsed_start = _parse_timecode(start, "Start time")
    parsed_end = _parse_timecode(end, "End time")
    if parsed_start and parsed_end:
        if parsed_end[1] <= parsed_start[1]:
            raise typer.BadParameter("End time must be greater than start time.")

    output = _resolve_output_path(
        input_video=input_video,
        fmt_key=fmt_key,
        explicit_output=output,
        output_dir=output_dir,
        name_template=name_template,
        audio_track=audio_track,
    )

    if output.exists() and not force:
        raise typer.BadParameter(
            f"Destination '{output}' already exists. Use --force to overwrite."
        )
    output.parent.mkdir(parents=True, exist_ok=True)

    profile = AUDIO_FORMATS[fmt_key]
    clip_desc = ""
    if parsed_start or parsed_end:
        start_desc = parsed_start[0] if parsed_start else "0"
        end_desc = parsed_end[0] if parsed_end else "end"
        clip_desc = f"{start_desc} -> {end_desc}"

    metadata = {
        key: value
        for key, value in {
            "title": title,
            "artist": artist,
            "album": album,
            "comment": comment,
        }.items()
        if value
    }

    _print_status(
        input_video,
        output,
        profile.label,
        sample_rate,
        channels,
        clip_desc,
        dry_run,
        duration,
        metadata,
    )

    command = _build_command(
        ffmpeg_bin=ffmpeg_bin,
        input_path=input_video,
        output_path=output,
        profile=profile,
        bitrate=bitrate,
        sample_rate=sample_rate,
        channels=channels,
        start_time=parsed_start[0] if parsed_start else None,
        end_time=parsed_end[0] if parsed_end else None,
        force=force,
        audio_track_index=audio_track,
        metadata=metadata,
    )

    quoted = " ".join(shlex.quote(part) for part in command)

    if dry_run:
        console.print(f"[yellow]Dry run:[/] {quoted}")
        raise typer.Exit()

    console.print(f"[cyan]Running ffmpeg:[/] {quoted}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        console.print(
            "[bold red]ffmpeg failed.[/] Check the input file and arguments above."
        )
        raise typer.Exit(exc.returncode) from exc

    size = output.stat().st_size if output.exists() else 0
    console.print(
        Panel(
            f"Created [bold]{output.name}[/] ({_human_size(size)}).",
            title="Success",
            border_style="green",
        )
    )


if __name__ == "__main__":  # pragma: no cover
    app()
