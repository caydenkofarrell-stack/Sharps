"""downloader.py - Phase 1

Pulls recent uploads from the approved source channels in config/sources.json
using yt-dlp, downloads new long-form videos into downloads/, and records their
metadata in the database so the processor can pick them up.

Usage:
    python downloader.py                 # pull from all enabled sources
    python downloader.py --source ID     # pull from one source only
    python downloader.py --list          # show enabled sources, download nothing
    python downloader.py --limit 1       # override max videos per source
"""
from __future__ import annotations

import argparse

from config_loader import ensure_dirs, enabled_sources, get_logger, get_settings, get_sources, resolve
import db

log = get_logger("downloader")

try:
    import yt_dlp  # type: ignore
except ImportError:  # pragma: no cover - dependency check
    yt_dlp = None


def _already_downloaded(video_id: str) -> bool:
    conn = db.connect()
    try:
        row = conn.execute("SELECT 1 FROM videos WHERE id = ?", (video_id,)).fetchone()
        return row is not None
    finally:
        conn.close()


def _record_video(info: dict, source_id: str, file_path: str) -> None:
    conn = db.connect()
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO videos
                (id, source_id, title, channel, duration, upload_date, url, file_path, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'downloaded')
            """,
            (
                info.get("id"),
                source_id,
                info.get("title"),
                info.get("channel") or info.get("uploader"),
                info.get("duration"),
                info.get("upload_date"),
                info.get("webpage_url"),
                file_path,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def _duration_ok(duration, settings) -> bool:
    if not duration:
        return True  # let it through; processor will re-check
    d = settings["download"]
    return d["min_duration_seconds"] <= duration <= d["max_duration_seconds"]


def download_source(source: dict, limit: int | None = None) -> int:
    """Download up to `limit` new videos from one source. Returns count downloaded."""
    if yt_dlp is None:
        log.error("yt-dlp is not installed. Run: pip install yt-dlp")
        return 0

    settings = get_settings()
    max_videos = limit or settings["download"]["max_videos_per_source_per_run"]
    out_dir = resolve("downloads") / source["id"]
    out_dir.mkdir(parents=True, exist_ok=True)

    # First pass: cheaply list recent uploads without downloading.
    list_opts = {
        "quiet": True,
        "extract_flat": True,
        "playlistend": max_videos * 3,  # over-fetch, we filter below
        "ignoreerrors": True,
    }
    log.info("Checking %s (%s)", source["name"], source["url"])
    with yt_dlp.YoutubeDL(list_opts) as ydl:
        listing = ydl.extract_info(source["url"], download=False)

    entries = (listing or {}).get("entries") or []
    downloaded = 0

    dl_opts = {
        "quiet": True,
        "noprogress": True,
        "format": settings["download"]["video_format"],
        "outtmpl": str(out_dir / "%(id)s.%(ext)s"),
        "merge_output_format": "mp4",
        "ignoreerrors": True,
        "writeinfojson": False,
    }

    for entry in entries:
        if downloaded >= max_videos:
            break
        if not entry:
            continue
        video_id = entry.get("id")
        if not video_id:
            continue
        if settings["download"]["skip_already_downloaded"] and _already_downloaded(video_id):
            log.info("  skip %s (already downloaded)", video_id)
            continue

        url = entry.get("url") or entry.get("webpage_url") or f"https://www.youtube.com/watch?v={video_id}"
        with yt_dlp.YoutubeDL(dl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        if not info:
            log.warning("  failed to download %s", video_id)
            continue
        if not _duration_ok(info.get("duration"), settings):
            log.info("  skip %s (duration %ss outside range)", video_id, info.get("duration"))
            continue

        file_path = str(out_dir / f"{info['id']}.mp4")
        _record_video(info, source["id"], file_path)
        downloaded += 1
        log.info("  downloaded %s - %s", video_id, info.get("title"))

    log.info("%s: %d new video(s)", source["name"], downloaded)
    return downloaded


def run(source_id: str | None = None, limit: int | None = None) -> int:
    ensure_dirs()
    db.init_db()
    db.sync_sources(get_sources())

    sources = enabled_sources()
    if source_id:
        sources = [s for s in get_sources() if s["id"] == source_id]
        if not sources:
            log.error("No source with id '%s'", source_id)
            return 0

    if not sources:
        log.warning(
            "No enabled sources. Edit config/sources.json, set real channel URLs, "
            "and flip 'enabled' to true."
        )
        return 0

    total = 0
    for source in sources:
        try:
            total += download_source(source, limit=limit)
        except Exception as exc:  # keep going through the source list
            log.exception("Error on source %s: %s", source.get("id"), exc)
    log.info("Download run complete: %d new video(s) across %d source(s)", total, len(sources))
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Pull new uploads from source channels.")
    parser.add_argument("--source", help="Only pull this source id")
    parser.add_argument("--limit", type=int, help="Max videos per source this run")
    parser.add_argument("--list", action="store_true", help="List enabled sources and exit")
    args = parser.parse_args()

    if args.list:
        for s in enabled_sources():
            print(f"  {s['id']:30} {s['name']:30} {s['url']}")
        if not enabled_sources():
            print("  (no enabled sources - edit config/sources.json)")
        return

    run(source_id=args.source, limit=args.limit)


if __name__ == "__main__":
    main()
