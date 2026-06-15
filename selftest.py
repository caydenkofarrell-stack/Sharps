#!/usr/bin/env python3
"""
LockedIn — Self Test.

Runs the WHOLE system end to end on a tiny throwaway video and tells you, in
plain English, whether everything works on your machine. Run this once before
you start so you never waste time on a broken setup.

    py selftest.py

It checks Python, ffmpeg, yt-dlp, the script engine, the clip cutter, the
caption editor, and the scheduler — then cleans up after itself.
"""

import os
import shutil
import subprocess
import sys
import tempfile

PY = sys.executable
HERE = os.path.dirname(os.path.abspath(__file__))

OK = "  [ OK ]  "
FAIL = "  [FAIL]  "
WARN = "  [WARN]  "

results = []


def record(name, passed, detail=""):
    tag = OK if passed else FAIL
    print(tag + name + (("  — " + detail) if detail else ""))
    results.append(passed)
    return passed


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def main():
    print("\n=== LockedIn self-test ===\n")

    # 1. Python
    record("Python {}.{}.{}".format(*sys.version_info[:3]), sys.version_info >= (3, 7))

    # 2. ffmpeg + ffprobe
    has_ff = shutil.which("ffmpeg") is not None
    has_fp = shutil.which("ffprobe") is not None
    record("ffmpeg installed", has_ff,
           "" if has_ff else "install: winget install Gyan.FFmpeg")
    record("ffprobe installed", has_fp,
           "" if has_fp else "comes with ffmpeg")

    # 3. yt-dlp (optional — only needed for fetch_footage)
    has_ytdlp = shutil.which("yt-dlp") is not None or \
        run([PY, "-m", "yt_dlp", "--version"]).returncode == 0
    if has_ytdlp:
        record("yt-dlp installed (for downloading footage)", True)
    else:
        print(WARN + "yt-dlp not installed (optional) — only needed for "
              "fetch_footage.py. Install: py -m pip install -U yt-dlp")

    # 4. Script engine
    try:
        sys.path.insert(0, HERE)
        import generate, content_banks  # noqa
        import random
        s = generate.build_script(random.Random(0), list(content_banks.THEMES)[0])
        record("Script engine (generate.py)", bool(s.get("hook")))
    except Exception as e:
        record("Script engine (generate.py)", False, str(e))

    if not (has_ff and has_fp):
        print("\n  Skipping video tests — install ffmpeg first, then re-run.\n")
        return summarize()

    # 5. Full video pipeline in a temp sandbox
    tmp = tempfile.mkdtemp(prefix="lockedin_selftest_")
    try:
        test_vid = os.path.join(tmp, "test.mp4")
        make = run(["ffmpeg", "-v", "error", "-y",
                    "-f", "lavfi", "-i", "testsrc=size=640x360:rate=24:duration=6",
                    "-f", "lavfi", "-i", "sine=frequency=300:duration=6",
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-shortest", test_vid])
        if not record("Built a test video", os.path.isfile(test_vid), make.stderr.strip()[:120]):
            return summarize()

        clips_dir = os.path.join(tmp, "clips")
        cf = run([PY, os.path.join(HERE, "clip_finder.py"), test_vid,
                  "-n", "1", "--len", "4", "-o", clips_dir])
        clip = os.path.join(clips_dir, "test_clip1.mp4")
        record("Clip cutter (clip_finder.py)", os.path.isfile(clip),
               cf.stderr.strip()[:120] if not os.path.isfile(clip) else "")

        if os.path.isfile(clip):
            mp = run([PY, os.path.join(HERE, "make_post.py"), clip, "--seed", "1"])
            post = os.path.join(clips_dir, "test_clip1_post.mp4")
            txt = os.path.join(clips_dir, "test_clip1_post.txt")
            ok_post = os.path.isfile(post) and os.path.isfile(txt)
            record("Caption editor (make_post.py)", ok_post,
                   mp.stderr.strip()[:160] if not ok_post else "")

            if ok_post:
                q = os.path.join(tmp, "queue.json")
                sc = os.path.join(HERE, "scheduler.py")
                run([PY, sc, "--file", q, "add", post])
                run([PY, sc, "--file", q, "plan", "--per-day", "1", "--days", "1"])
                today = run([PY, sc, "--file", q, "today"])
                run([PY, sc, "--file", q, "done", "1"])
                record("Scheduler (scheduler.py)", "POST THESE TODAY" in today.stdout)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return summarize()


def summarize():
    print()
    if all(results):
        print("  ========================================")
        print("   ALL SYSTEMS GO. You're ready to roll. 🔒")
        print("  ========================================\n")
        return 0
    failed = results.count(False)
    print("  ----------------------------------------")
    print("   {} check(s) failed — see [FAIL] lines above.".format(failed))
    print("   Fix those, then run  py selftest.py  again.")
    print("  ----------------------------------------\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
