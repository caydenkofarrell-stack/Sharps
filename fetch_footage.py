#!/usr/bin/env python3
"""
LockedIn — Fetch Footage.

Downloads source video from a URL (YouTube, etc.) into ./footage/ using yt-dlp,
ready to feed into clip_finder.py. Thin, friendly wrapper that also reminds you
to only pull footage you're actually licensed to use — because monetization and
staying un-banned both depend on it.

SETUP (once):
    py -m pip install -U yt-dlp

USAGE
    py fetch_footage.py <URL>
    py fetch_footage.py <URL> -o myfolder
    py fetch_footage.py <URL> --then-clip 5     # download, then auto-cut 5 clips

WHERE TO GET FOOTAGE YOU CAN ACTUALLY USE & MONETIZE
  - YouTube, filtered to Creative Commons: search a topic, click Filters ->
    Features -> Creative Commons. Those creators license reuse. (Still credit them.)
  - Free stock (licensed for commercial use): pexels.com/videos,
    pixabay.com/videos, mixkit.co — download straight from the site.
  - Your own phone footage from training. This is the strongest: 100% yours.

Reposting random copyrighted clips = copyright strikes + no payout. Don't.
"""

import argparse
import os
import shutil
import subprocess
import sys


LICENSE_REMINDER = (
    "  Reminder: only use footage you own, filmed yourself, or that's\n"
    "  Creative Commons / royalty-free. That's what keeps you monetizable\n"
    "  and un-banned. (See the notes at the top of this file.)"
)


def have_yt_dlp():
    """yt-dlp may be a standalone exe or a python module."""
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    # fall back to `python -m yt_dlp`
    probe = subprocess.run([sys.executable, "-m", "yt_dlp", "--version"],
                           capture_output=True, text=True)
    if probe.returncode == 0:
        return [sys.executable, "-m", "yt_dlp"]
    return None


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Download source footage from a URL into ./footage/.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("url", help="video URL to download")
    p.add_argument("-o", "--out", default="footage", help="output folder (default footage/)")
    p.add_argument("--then-clip", type=int, metavar="N",
                   help="after download, run clip_finder.py for N clips")
    args = p.parse_args(argv)

    base = have_yt_dlp()
    if base is None:
        sys.exit("ERROR: yt-dlp not installed. Run:\n  py -m pip install -U yt-dlp")

    os.makedirs(args.out, exist_ok=True)
    print("\n" + LICENSE_REMINDER + "\n")

    # mp4-friendly output, predictable filename for the next step
    out_tmpl = os.path.join(args.out, "%(title).80s.%(ext)s")
    cmd = base + [
        "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
        "--merge-output-format", "mp4",
        "-o", out_tmpl,
        "--print", "after_move:filepath",
        args.url,
    ]
    print("  Downloading -> {}/ ...".format(args.out))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit("ERROR: download failed:\n" + (proc.stderr.strip() or proc.stdout.strip()))

    downloaded = proc.stdout.strip().splitlines()
    path = downloaded[-1] if downloaded else None
    if path and os.path.isfile(path):
        print("  Saved: {}".format(path))
    else:
        print("  Done (saved into {}/).".format(args.out))

    if args.then_clip and path and os.path.isfile(path):
        print("\n  Auto-cutting {} clip(s)...".format(args.then_clip))
        subprocess.run([sys.executable, "clip_finder.py", path, "-n", str(args.then_clip)])

    print("\n  Next:  py clip_finder.py \"{}\" -n 5\n".format(path or args.out + "/<file>.mp4"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
