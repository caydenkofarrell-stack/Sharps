#!/usr/bin/env python3
"""
LockedIn — Make Post (editor).

Turns a raw vertical clip into a post-ready video: burns a bold hook caption
onto it and writes a matching post-text file (caption + hashtags) next to it.

Runs on YOUR machine. Needs ffmpeg installed. No Python dependencies.

USAGE
    py make_post.py clips/raw_clip1.mp4
    py make_post.py clip.mp4 -t consistency           # force a theme
    py make_post.py clip.mp4 --text "Your own hook"    # use your own line
    py make_post.py clip.mp4 --no-caption              # skip overlay, just post-text
    py make_post.py clip.mp4 --font "C:/Windows/Fonts/impact.ttf"
    py make_post.py clip.mp4 --dry-run                 # print the ffmpeg command only

Output (next to the clip):
    <name>_post.mp4   — video with the hook burned on
    <name>_post.txt   — caption + hashtags to paste when you upload
"""

import argparse
import os
import random
import shutil
import subprocess
import sys
import tempfile
import textwrap

import content_banks as cb
import generate


# Common bold fonts per OS. First one that exists wins. Override with --font.
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\impact.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def require_ffmpeg():
    if shutil.which("ffmpeg") is None:
        sys.exit("ERROR: ffmpeg not found on PATH. Install it first "
                 "(winget install Gyan.FFmpeg on Windows).")


def find_font(override):
    if override:
        if not os.path.isfile(override):
            sys.exit("ERROR: font not found: {}".format(override))
        return override
    for f in FONT_CANDIDATES:
        if os.path.isfile(f):
            return f
    sys.exit("ERROR: no default font found. Pass one with --font, e.g.\n"
             '  --font "C:/Windows/Fonts/arialbd.ttf"')


def escape_for_filter(path):
    """Escape a filesystem path so ffmpeg's filtergraph parser accepts it."""
    # Forward slashes are safe on all platforms; the drive colon must be escaped.
    p = path.replace("\\", "/")
    return p.replace(":", r"\:")


def build_caption_text(hook, width=18):
    """Wrap the hook into short ALL-CAPS lines that read well as an overlay."""
    wrapped = textwrap.fill(hook.upper(), width=width)
    return wrapped


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Burn a hook caption onto a clip and write its post text.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("clip", help="path to the vertical clip (mp4)")
    p.add_argument("-t", "--theme", choices=sorted(cb.THEMES.keys()),
                   help="force a theme (default: random)")
    p.add_argument("--text", help="use your own hook instead of a generated one")
    p.add_argument("--font", help="path to a .ttf/.otf font to use")
    p.add_argument("--no-caption", action="store_true",
                   help="don't burn text; still write the post-text file")
    p.add_argument("--seed", type=int, help="reproducible script choice")
    p.add_argument("--dry-run", action="store_true",
                   help="print the ffmpeg command without running it")
    args = p.parse_args(argv)

    if not os.path.isfile(args.clip):
        sys.exit("ERROR: clip not found: {}".format(args.clip))

    rng = random.Random(args.seed)
    theme_key = args.theme or rng.choice(list(cb.THEMES.keys()))
    script = generate.build_script(rng, theme_key)
    hook = args.text or script["hook"]

    base, _ext = os.path.splitext(args.clip)
    out_video = base + "_post.mp4"
    out_text = base + "_post.txt"

    # Write the post-text file (caption + hashtags + CTA) regardless of mode.
    with open(out_text, "w", encoding="utf-8") as fh:
        fh.write(script["caption"] + "\n\n")
        fh.write(script["cta"] + "\n\n")
        fh.write(script["hashtags"] + "\n")
    print("  Wrote post text  -> {}".format(out_text))

    if args.no_caption:
        print("  Skipped overlay (--no-caption). Post the raw clip with the text above.\n")
        return 0

    if not args.dry_run:
        require_ffmpeg()
    font = find_font(args.font)

    # drawtext reads the caption from a temp file so quotes/apostrophes in the
    # hook never break the filtergraph.
    tmp_dir = tempfile.mkdtemp(prefix="sharps_post_")
    text_path = os.path.join(tmp_dir, "caption.txt")
    try:
        with open(text_path, "w", encoding="utf-8") as fh:
            fh.write(build_caption_text(hook))

        drawtext = (
            "drawtext=fontfile='{font}':textfile='{txt}':"
            "fontcolor=white:fontsize=72:line_spacing=14:"
            "box=1:boxcolor=black@0.55:boxborderw=28:"
            "x=(w-text_w)/2:y=h*0.10"
        ).format(font=escape_for_filter(font), txt=escape_for_filter(text_path))

        cmd = ["ffmpeg", "-v", "error", "-y", "-i", args.clip,
               "-vf", drawtext, "-c:v", "libx264", "-preset", "veryfast",
               "-crf", "20", "-c:a", "copy", "-movflags", "+faststart", out_video]

        if args.dry_run:
            print("\n  DRY RUN — would run:\n   " + " ".join(
                ('"%s"' % c if " " in c else c) for c in cmd) + "\n")
            return 0

        print("  Burning hook    -> {}".format(out_video))
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            sys.exit("ERROR: ffmpeg failed:\n" + proc.stderr.strip())
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("\n  Post-ready: {}".format(out_video))
    print("  Caption/hashtags in: {}\n".format(out_text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
