"""orchestrator.py - main runner

Ties the pipeline together and can run on a schedule. On Windows, point Task
Scheduler at `python orchestrator.py --once` (daily), or run `--serve` to keep a
long-lived process that fires the download/process/learning jobs at the times in
settings.json.

Usage:
    python orchestrator.py --once       # run download -> process once, now
    python orchestrator.py --serve      # stay resident, run on the configured schedule
    python orchestrator.py --status     # print pipeline status and exit
"""
from __future__ import annotations

import argparse

from config_loader import ensure_dirs, get_logger, get_settings, get_sources
import db
import downloader
import learning_agent
import processor

log = get_logger("orchestrator")


def run_once() -> None:
    log.info("=== Pipeline run start ===")
    ensure_dirs()
    db.init_db()
    db.sync_sources(get_sources())

    new_videos = downloader.run()
    settings = get_settings()
    if settings["schedule"].get("process_after_download", True):
        clips = processor.run()
        log.info("Run summary: %d new video(s), %d new clip(s)", new_videos, clips)
    else:
        log.info("Run summary: %d new video(s) (processing deferred)", new_videos)
    log.info("=== Pipeline run end ===")


def status() -> None:
    db.init_db()
    conn = db.connect()
    try:
        videos = conn.execute("SELECT status, COUNT(*) n FROM videos GROUP BY status").fetchall()
        clips = conn.execute("SELECT status, COUNT(*) n FROM clips GROUP BY status").fetchall()
        posts = conn.execute("SELECT status, COUNT(*) n FROM posts GROUP BY status").fetchall()
    finally:
        conn.close()

    print("Videos:")
    for r in videos:
        print(f"  {r['status']:>16}: {r['n']}")
    print("Clips:")
    for r in clips:
        print(f"  {r['status']:>16}: {r['n']}")
    print("Posts:")
    for r in posts:
        print(f"  {r['status']:>16}: {r['n']}")

    profile = learning_agent.build_profile()
    print(f"\nDecisions logged: {profile['total_decisions']} "
          f"(profile trusted: {profile['trusted']})")


def serve() -> None:
    try:
        import schedule  # type: ignore
    except ImportError:
        log.error("The 'schedule' package is required for --serve. Run: pip install schedule")
        return
    import time

    settings = get_settings()
    dl_time = settings["schedule"]["download_time"]
    learn_time = settings["schedule"]["learning_time"]

    schedule.every().day.at(dl_time).do(run_once)
    schedule.every().day.at(learn_time).do(
        lambda: log.info("Nightly profile:\n%s", learning_agent.build_profile())
    )

    log.info("Scheduler started. Download at %s, learning at %s. Ctrl+C to stop.",
             dl_time, learn_time)
    run_once()  # do an immediate pass on startup
    while True:
        schedule.run_pending()
        time.sleep(30)


def main() -> None:
    parser = argparse.ArgumentParser(description="Uncommon Hours clip pipeline runner.")
    parser.add_argument("--once", action="store_true", help="Run the pipeline once now")
    parser.add_argument("--serve", action="store_true", help="Run resident on the schedule")
    parser.add_argument("--status", action="store_true", help="Print pipeline status")
    args = parser.parse_args()

    if args.status:
        status()
    elif args.serve:
        serve()
    else:  # default to a single run
        run_once()


if __name__ == "__main__":
    main()
