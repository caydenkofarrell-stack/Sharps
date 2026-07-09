"""processor.py - Phase 1

Takes downloaded long-form videos and produces short vertical 9:16 clips with
Uncommon Hours branding using FFmpeg. For each candidate clip it renders a
master, then platform variants (shorts / tiktok / reels), and records the clip
in the database with status 'pending_review'.

Segment strategy (config: processing.segment_strategy):
    even_split  - evenly spaced clips across the middle of the video
    (extend here with scene detection later)

Usage:
    python processor.py                 # process every downloaded, unprocessed video
    python processor.py --video ID      # process one video
    python processor.py --dry-run       # print the ffmpeg plan, render nothing
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from config_loader import ensure_dirs, get_logger, get_settings, resolve
import db

log = get_logger("processor")

FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")


def ffmpeg_available() -> bool:
    return FFMPEG is not None and FFPROBE is not None


def _escape_drawtext(text: str) -> str:
    """Escape a string for FFmpeg drawtext."""
    text = text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")
    return text


def probe_duration(path: str) -> float:
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def plan_segments(duration: float, settings: dict) -> list[tuple[float, float]]:
    """Return a list of (start, end) segments across the middle of the video.

    We avoid the first/last 8% (intros/outros) and space clips evenly.
    """
    p = settings["processing"]
    target = p["clip_length_seconds"]["target"]
    n_max = p["clips_per_video_max"]
    n_min = p["clips_per_video_min"]

    usable_start = duration * 0.08
    usable_end = duration * 0.92
    usable = max(0.0, usable_end - usable_start)

    if usable < p["clip_length_seconds"]["min"]:
        return []

    # How many target-length clips fit without overlapping, capped at n_max.
    # A short video legitimately yields fewer than n_min clips; we don't force
    # extras because that would make them overlap.
    fit = int(usable // target)
    n = max(1, min(n_max, fit))
    if fit >= n_min:
        n = max(n_min, n)

    segments: list[tuple[float, float]] = []
    if n == 1:
        mid = usable_start + usable / 2
        start = max(usable_start, mid - target / 2)
        segments.append((start, min(usable_end, start + target)))
        return segments

    stride = usable / n
    for i in range(n):
        center = usable_start + stride * (i + 0.5)
        start = max(usable_start, center - target / 2)
        end = min(usable_end, start + target)
        length = end - start
        if length >= p["clip_length_seconds"]["min"]:
            segments.append((round(start, 2), round(end, 2)))
    return segments


def _vertical_filter(settings: dict, hook_text: str | None) -> tuple[str, str]:
    """Build the FFmpeg filter_complex graph + output label: 9:16 canvas + branding."""
    p = settings["processing"]
    w = p["output_resolution"]["width"]
    h = p["output_resolution"]["height"]
    brand = settings["brand"]

    if p["vertical_style"] == "blurred_background":
        # Blurred, filled 9:16 background with the source centered on top.
        base = (
            f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},boxblur=20:5[bg];"
            f"[0:v]scale={w}:-2:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
        )
    else:  # simple pad on black
        base = (
            f"[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black[v]"
        )

    filters = [base]
    label = "[v]"

    if p.get("add_text_overlay") and hook_text:
        txt = _escape_drawtext(hook_text)
        color = brand.get("text_color", "#FFFFFF")
        font = brand.get("font_file") or ""
        fontfile = f"fontfile='{font}':" if font else ""
        drawtext = (
            f"{label}drawtext={fontfile}text='{txt}':fontcolor={color}:fontsize=54:"
            f"box=1:boxcolor=black@0.5:boxborderw=18:"
            f"x=(w-text_w)/2:y=h*0.10:line_spacing=8[vt]"
        )
        filters.append(drawtext)
        label = "[vt]"

    if p.get("add_watermark") and brand.get("watermark_text"):
        wm = _escape_drawtext(brand["watermark_text"])
        color = brand.get("primary_color", "#F5C518")
        watermark = (
            f"{label}drawtext=text='{wm}':fontcolor={color}:fontsize=34:"
            f"x=(w-text_w)/2:y=h*0.90[out]"
        )
        filters.append(watermark)
        label = "[out]"

    return ";".join(filters), label


def render_clip(video_path: str, start: float, end: float, out_path: Path,
                settings: dict, hook_text: str | None, max_duration: float | None = None,
                dry_run: bool = False) -> bool:
    length = end - start
    if max_duration:
        length = min(length, max_duration)

    filtergraph, out_label = _vertical_filter(settings, hook_text)
    cmd = [
        FFMPEG, "-y",
        "-ss", f"{start:.2f}", "-t", f"{length:.2f}",
        "-i", video_path,
        "-filter_complex", filtergraph,
        "-map", out_label, "-map", "0:a?",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        "-r", "30",
        str(out_path),
    ]
    if dry_run:
        log.info("DRY-RUN ffmpeg: %s", " ".join(cmd))
        return True

    out_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log.error("ffmpeg failed for %s:\n%s", out_path.name, result.stderr[-1500:])
        return False
    return True


def render_thumbnail(clip_path: Path, thumb_path: Path) -> bool:
    cmd = [FFMPEG, "-y", "-i", str(clip_path), "-ss", "1", "-vframes", "1",
           "-q:v", "3", str(thumb_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def _pending_videos(video_id: str | None):
    conn = db.connect()
    try:
        if video_id:
            rows = conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM videos WHERE status = 'downloaded' ORDER BY downloaded_at"
            ).fetchall()
        return rows
    finally:
        conn.close()


def _record_clip(video, seq, start, end, master_path, variant_paths, thumb_path, hook_text):
    conn = db.connect()
    try:
        cur = conn.execute(
            """
            INSERT INTO clips
                (video_id, source_id, seq, start_seconds, end_seconds, length_seconds,
                 master_path, variant_paths, thumbnail_path, hook_text, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending_review')
            """,
            (
                video["id"], video["source_id"], seq, start, end, round(end - start, 2),
                master_path, json.dumps(variant_paths), thumb_path, hook_text,
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _mark_video(video_id: str, status: str) -> None:
    conn = db.connect()
    try:
        conn.execute("UPDATE videos SET status = ? WHERE id = ?", (status, video_id))
        conn.commit()
    finally:
        conn.close()


def process_video(video, settings, dry_run: bool = False) -> int:
    path = video["file_path"]
    if not path or not Path(path).exists():
        log.error("Video file missing for %s (%s)", video["id"], path)
        _mark_video(video["id"], "error")
        return 0

    try:
        duration = probe_duration(path)
    except Exception as exc:
        log.error("ffprobe failed for %s: %s", video["id"], exc)
        _mark_video(video["id"], "error")
        return 0

    segments = plan_segments(duration, settings)
    if not segments:
        log.warning("No usable segments in %s (%.0fs)", video["id"], duration)
        _mark_video(video["id"], "processed")
        return 0

    date_dir = datetime.now().strftime("%Y-%m-%d")
    out_root = resolve("processed") / date_dir / (video["source_id"] or "unknown")
    variants = settings["processing"]["platform_variants"]
    specs = settings["platform_specs"]
    made = 0

    for i, (start, end) in enumerate(segments, start=1):
        hook = (video["title"] or "").strip()[:70] or None
        master = out_root / f"{video['id']}_clip{i}_master.mp4"
        ok = render_clip(path, start, end, master, settings, hook, dry_run=dry_run)
        if not ok:
            continue

        variant_paths = {}
        for platform in variants:
            max_dur = specs.get(platform, {}).get("max_duration_seconds")
            vpath = out_root / f"{video['id']}_clip{i}_{platform}.mp4"
            if render_clip(path, start, end, vpath, settings, hook, max_duration=max_dur, dry_run=dry_run):
                variant_paths[platform] = str(vpath)

        thumb = out_root / f"{video['id']}_clip{i}.jpg"
        if not dry_run:
            render_thumbnail(master, thumb)
            _record_clip(video, i, start, end, str(master), variant_paths, str(thumb), hook)
        made += 1
        log.info("  clip %d: %.1fs-%.1fs -> %d variant(s)", i, start, end, len(variant_paths))

    if not dry_run:
        _mark_video(video["id"], "processed")
    log.info("Processed %s: %d clip(s)", video["id"], made)
    return made


def run(video_id: str | None = None, dry_run: bool = False) -> int:
    ensure_dirs()
    db.init_db()
    if not ffmpeg_available() and not dry_run:
        log.error("FFmpeg/ffprobe not found on PATH. Install with: winget install ffmpeg")
        return 0

    settings = get_settings()
    videos = _pending_videos(video_id)
    if not videos:
        log.info("No videos waiting to be processed.")
        return 0

    total = 0
    for video in videos:
        try:
            total += process_video(video, settings, dry_run=dry_run)
        except Exception as exc:
            log.exception("Error processing %s: %s", video["id"], exc)
            _mark_video(video["id"], "error")
    log.info("Processing run complete: %d clip(s) from %d video(s)", total, len(videos))
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Segment and format downloaded videos into clips.")
    parser.add_argument("--video", help="Process a single video id")
    parser.add_argument("--dry-run", action="store_true", help="Print ffmpeg plan without rendering")
    args = parser.parse_args()
    run(video_id=args.video, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
