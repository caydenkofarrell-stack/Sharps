#!/usr/bin/env python3
"""
LockedIn — Clip Finder (Phase 2).

Feed in a longer video. It finds the most high-energy moments (by audio
loudness), cuts them into vertical 9:16 clips ready for TikTok / Shorts / Reels,
and prints a report you can pair with captions from generate.py.

This runs ON YOUR MACHINE (not the cloud) because it needs your video files and
ffmpeg. Zero Python dependencies — just ffmpeg + ffprobe installed and on PATH.

INSTALL FFMPEG
    macOS:    brew install ffmpeg
    Windows:  winget install ffmpeg     (or scoop install ffmpeg)
    Linux:    sudo apt install ffmpeg

USAGE
    python clip_finder.py raw.mp4                 # top 3 clips → ./clips/
    python clip_finder.py raw.mp4 -n 5            # top 5 moments
    python clip_finder.py raw.mp4 --len 25        # ~25s clips
    python clip_finder.py raw.mp4 -o exports/     # custom output folder
    python clip_finder.py raw.mp4 --dry-run       # report only, cut nothing
    python clip_finder.py raw.mp4 --no-vertical   # keep original aspect

How it picks moments: decodes the audio, measures loudness (RMS) over short
windows, finds the loudest peaks, spreads them out so you don't get 3 clips
from the same 10 seconds, then cuts a clip centered on each peak.
"""

import argparse
import array
import math
import os
import shutil
import subprocess
import sys
import tempfile
import wave


def require_tools():
    """Fail early with a clear message if ffmpeg/ffprobe aren't installed."""
    missing = [t for t in ("ffmpeg", "ffprobe") if shutil.which(t) is None]
    if missing:
        sys.exit(
            "ERROR: missing required tool(s): {}\n"
            "Install ffmpeg (it includes ffprobe):\n"
            "  macOS:   brew install ffmpeg\n"
            "  Windows: winget install ffmpeg\n"
            "  Linux:   sudo apt install ffmpeg".format(", ".join(missing))
        )


def probe_duration(path):
    """Return the video duration in seconds via ffprobe."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    )
    if out.returncode != 0 or not out.stdout.strip():
        sys.exit("ERROR: could not read '{}'. Is it a valid video?\n{}"
                 .format(path, out.stderr.strip()))
    return float(out.stdout.strip())


def decode_audio_rms(path, window_s=0.5, sample_rate=16000):
    """
    Decode the file's audio to mono PCM and return a list of per-window RMS
    loudness values. Each entry covers `window_s` seconds.
    """
    tmp_dir = tempfile.mkdtemp(prefix="sharps_")
    wav_path = os.path.join(tmp_dir, "audio.wav")
    try:
        proc = subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", path,
             "-ac", "1", "-ar", str(sample_rate), "-vn", wav_path],
            capture_output=True, text=True,
        )
        if proc.returncode != 0 or not os.path.exists(wav_path):
            sys.exit("ERROR: ffmpeg could not extract audio.\n" + proc.stderr.strip())

        with wave.open(wav_path, "rb") as wf:
            n_frames = wf.getnframes()
            raw = wf.readframes(n_frames)

        samples = array.array("h")  # signed 16-bit
        samples.frombytes(raw)
        if sys.byteorder == "big":
            samples.byteswap()

        win = max(1, int(window_s * sample_rate))
        energies = []
        for start in range(0, len(samples), win):
            chunk = samples[start:start + win]
            if not chunk:
                continue
            acc = 0.0
            for s in chunk:
                acc += float(s) * float(s)
            energies.append(math.sqrt(acc / len(chunk)))
        return energies, window_s
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def find_peaks(energies, window_s, duration, n_clips, clip_len):
    """
    Pick the top `n_clips` loudness peaks, enforcing a minimum spacing so the
    clips don't all come from the same stretch of video. Returns a list of
    (start_s, end_s, score) tuples sorted by where they appear in the video.
    """
    if not energies:
        return []

    # (score, time_seconds) for every window, loudest first.
    ranked = sorted(
        ((e, i * window_s) for i, e in enumerate(energies)),
        key=lambda t: t[0], reverse=True,
    )

    min_gap = clip_len * 0.9  # peaks must be at least ~one clip apart
    chosen = []
    for score, t in ranked:
        if len(chosen) >= n_clips:
            break
        if all(abs(t - c[1]) >= min_gap for c in chosen):
            chosen.append((score, t))

    peak_max = max((c[0] for c in chosen), default=1.0) or 1.0
    clips = []
    half = clip_len / 2.0
    for score, t in chosen:
        start = max(0.0, t - half)
        end = min(duration, start + clip_len)
        start = max(0.0, end - clip_len)  # keep full length near the tail
        clips.append((start, end, score / peak_max))

    clips.sort(key=lambda c: c[0])
    return clips


def cut_clip(src, start, end, dst, vertical=True):
    """Cut [start, end] from src into dst, optionally cropped to vertical 9:16."""
    args = ["ffmpeg", "-v", "error", "-y", "-ss", "{:.3f}".format(start),
            "-i", src, "-t", "{:.3f}".format(end - start)]
    if vertical:
        # Center-crop to 9:16 then scale to 1080x1920. Works for landscape or
        # square sources; already-vertical video is just normalized.
        vf = ("crop='min(iw,ih*9/16)':'min(ih,iw*16/9)',"
              "scale=1080:1920:force_original_aspect_ratio=increase,"
              "crop=1080:1920")
        args += ["-vf", vf]
    args += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
             "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", dst]
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        print("  ! failed to cut {}: {}".format(os.path.basename(dst),
                                                 proc.stderr.strip()[:200]))
        return False
    return True


def fmt_ts(seconds):
    m, s = divmod(int(seconds), 60)
    return "{:d}:{:02d}".format(m, s)


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Find the best moments in a video and cut vertical clips.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("video", help="path to the source video")
    p.add_argument("-n", "--number", type=int, default=3,
                   help="how many clips to extract (default: 3)")
    p.add_argument("--len", type=float, default=22.0, dest="clip_len",
                   help="target clip length in seconds (default: 22)")
    p.add_argument("-o", "--out", default="clips", help="output folder (default: clips/)")
    p.add_argument("--no-vertical", action="store_true",
                   help="keep original aspect ratio (default crops to 9:16)")
    p.add_argument("--dry-run", action="store_true",
                   help="report the chosen moments but don't cut clips")
    args = p.parse_args(argv)

    if not os.path.isfile(args.video):
        sys.exit("ERROR: file not found: {}".format(args.video))
    if args.number < 1:
        p.error("-n/--number must be at least 1")
    require_tools()

    print("\n  Analyzing '{}' ...".format(os.path.basename(args.video)))
    duration = probe_duration(args.video)
    print("  Duration: {} ({:.0f}s)".format(fmt_ts(duration), duration))

    if duration < args.clip_len:
        sys.exit("  Video is shorter than one clip ({}s). Nothing to do."
                 .format(args.clip_len))

    energies, window_s = decode_audio_rms(args.video)
    clips = find_peaks(energies, window_s, duration, args.number, args.clip_len)
    if not clips:
        sys.exit("  No audio energy detected — can't rank moments.")

    print("\n  Best {} moment(s):".format(len(clips)))
    print("  " + "-" * 52)
    for i, (start, end, score) in enumerate(clips, 1):
        bar = "#" * int(round(score * 20))
        print("   Clip {}:  {} → {}   energy [{:<20}]"
              .format(i, fmt_ts(start), fmt_ts(end), bar))
    print("  " + "-" * 52)

    if args.dry_run:
        print("\n  Dry run — no files written. Drop --dry-run to cut them.\n")
        return 0

    os.makedirs(args.out, exist_ok=True)
    base = os.path.splitext(os.path.basename(args.video))[0]
    made = 0
    print()
    for i, (start, end, _score) in enumerate(clips, 1):
        dst = os.path.join(args.out, "{}_clip{}.mp4".format(base, i))
        print("  Cutting clip {} → {}".format(i, dst))
        if cut_clip(args.video, start, end, dst, vertical=not args.no_vertical):
            made += 1

    print("\n  Done. {}/{} clip(s) in '{}/'.".format(made, len(clips), args.out))
    print("  Next: run  python generate.py  for captions + hashtags, then post.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
