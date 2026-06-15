#!/usr/bin/env python3
"""
LockedIn — Pipeline (the one-command batch maker).

ONE command turns a single source video into a batch of finished, captioned,
scheduled posts. This is the speed play: what takes others two hours, you do in
about a minute.

    py pipeline.py footage/video.mp4              # 6 posts, captioned + queued
    py pipeline.py footage/video.mp4 -n 10        # make 10
    py pipeline.py footage/video.mp4 --per-day 2  # then post 2/day
    py pipeline.py footage/video.mp4 --no-schedule # cut + caption only

What it does, back to back:
    1. clip_finder  -> cuts the N best moments into vertical clips
    2. make_post    -> burns a hook caption + writes caption/hashtags for EACH
    3. scheduler    -> adds them all to your queue and plans the calendar

You end with N *_post.mp4 files ready to upload, each with its own *_post.txt.
"""

import argparse
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import clip_finder
import make_post
import scheduler as sched


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Turn one video into a batch of finished, scheduled posts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("video", help="source video (e.g. footage/raw.mp4)")
    p.add_argument("-n", "--number", type=int, default=6, help="how many posts (default 6)")
    p.add_argument("--len", type=float, default=22.0, help="clip length seconds (default 22)")
    p.add_argument("-o", "--out", default="clips", help="clips folder (default clips/)")
    p.add_argument("--theme", help="force one theme for every caption (default: varied)")
    p.add_argument("--per-day", type=int, default=2, help="posts/day when scheduling (default 2)")
    p.add_argument("--time", default="18:00", help="first-post time (default 18:00)")
    p.add_argument("--days", type=int, default=14, help="days to spread over (default 14)")
    p.add_argument("--queue", default="queue.json", help="queue file (default queue.json)")
    p.add_argument("--no-schedule", action="store_true", help="skip queueing/scheduling")
    args = p.parse_args(argv)

    if not os.path.isfile(args.video):
        sys.exit("ERROR: video not found: {}".format(args.video))

    base = os.path.splitext(os.path.basename(args.video))[0]

    # 1) CUT ---------------------------------------------------------------
    print("\n========== STEP 1/3 : CUTTING {} CLIPS ==========".format(args.number))
    rc = clip_finder.main([args.video, "-n", str(args.number),
                           "--len", str(args.len), "-o", args.out])
    if rc != 0:
        sys.exit("  Pipeline stopped: clip cutting failed.")

    clips = sorted(glob.glob(os.path.join(args.out, base + "_clip*.mp4")))
    clips = [c for c in clips if not c.endswith("_post.mp4")]
    if not clips:
        sys.exit("  No clips were produced — nothing to caption.")

    # 2) CAPTION -----------------------------------------------------------
    print("\n========== STEP 2/3 : CAPTIONING {} CLIPS ==========".format(len(clips)))
    posts = []
    for i, clip in enumerate(clips, 1):
        print("  ({}/{}) {}".format(i, len(clips), os.path.basename(clip)))
        mp_args = [clip, "--seed", str(i)]
        if args.theme:
            mp_args += ["--theme", args.theme]
        if make_post.main(mp_args) == 0:
            post = os.path.splitext(clip)[0] + "_post.mp4"
            if os.path.isfile(post):
                posts.append(post)

    if not posts:
        sys.exit("  No captioned posts were produced.")

    # 3) SCHEDULE ----------------------------------------------------------
    if not args.no_schedule:
        print("\n========== STEP 3/3 : QUEUE + SCHEDULE ==========")
        for post in posts:
            sched.main(["--file", args.queue, "add", post])
        sched.main(["--file", args.queue, "plan",
                    "--per-day", str(args.per_day),
                    "--time", args.time, "--days", str(args.days)])
    else:
        print("\n  (Skipped scheduling — clips + captions are ready.)")

    # DONE -----------------------------------------------------------------
    print("\n==================================================")
    print("  DONE. {} post(s) ready in '{}/'.".format(len(posts), args.out))
    for post in posts:
        print("   - {}".format(os.path.basename(post)))
    if not args.no_schedule:
        print("\n  See your plan:   py scheduler.py today")
    print("  Each video has a matching _post.txt with caption + hashtags.")
    print("==================================================\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
