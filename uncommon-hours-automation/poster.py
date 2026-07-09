"""poster.py - Phase 4 (scaffold)

Schedules and posts approved clips to YouTube Shorts, Instagram Reels, and
TikTok. This is intentionally a safe scaffold: posting is DISABLED by default
and runs in dry-run mode. Wire up the real API calls only once Phases 1-3 are
solid and you've added the UH transformation layer to clips.

Guard rails:
    - settings.posting.enabled must be true AND settings.posting.dry_run false
      before anything actually posts.
    - only clips with status 'approved' AND transformed = 1 are eligible, so a
      straight re-upload can never post by accident (the monetization rule).

Platform notes:
    shorts  - YouTube Data API v3 (videos.insert). Primary monetization target.
    reels   - Instagram Graph API (requires a Business/Creator account + FB app).
    tiktok  - No open publish API for most creators; browser automation to start.

Usage:
    python poster.py --queue            # build a posting schedule from approved clips
    python poster.py --run              # process due posts (respects dry-run)
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime

from config_loader import get_logger, get_settings
import db

log = get_logger("poster")


def _eligible_clips() -> list[dict]:
    """Approved clips that carry the UH transformation and aren't posted yet."""
    conn = db.connect()
    try:
        rows = conn.execute(
            """
            SELECT * FROM clips
            WHERE status = 'approved' AND transformed = 1
            ORDER BY created_at
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def queue_posts() -> int:
    """Create scheduled post rows for eligible clips across enabled platforms."""
    settings = get_settings()
    platforms = settings["processing"]["platform_variants"]
    clips = _eligible_clips()
    if not clips:
        log.info("No eligible clips to queue. Clips must be approved AND transformed=1.")
        return 0

    conn = db.connect()
    created = 0
    try:
        for clip in clips:
            variants = json.loads(clip.get("variant_paths") or "{}")
            for platform in platforms:
                if platform not in variants:
                    continue
                exists = conn.execute(
                    "SELECT 1 FROM posts WHERE clip_id = ? AND platform = ?",
                    (clip["id"], platform),
                ).fetchone()
                if exists:
                    continue
                conn.execute(
                    "INSERT INTO posts (clip_id, platform, status) VALUES (?, ?, 'scheduled')",
                    (clip["id"], platform),
                )
                created += 1
        conn.commit()
    finally:
        conn.close()
    log.info("Queued %d post(s).", created)
    return created


def _post_to_platform(platform: str, clip: dict, variant_path: str, dry_run: bool) -> dict:
    """Return {'ok': bool, 'post_id': str|None, 'error': str|None}.

    Real API integrations go here. For now this is a stub that logs intent.
    """
    if dry_run:
        log.info("[DRY-RUN] would post clip %s to %s (%s)", clip["id"], platform, variant_path)
        return {"ok": True, "post_id": None, "error": None}

    # TODO: implement per platform.
    #   shorts -> YouTube Data API v3 videos.insert
    #   reels  -> Instagram Graph API media + media_publish
    #   tiktok -> browser automation (Playwright) until API access granted
    log.warning("Real posting for %s is not implemented yet.", platform)
    return {"ok": False, "post_id": None, "error": "not_implemented"}


def run_posting() -> int:
    settings = get_settings()
    posting = settings["posting"]
    dry_run = posting.get("dry_run", True)

    if not posting.get("enabled"):
        log.info("Posting is disabled (settings.posting.enabled = false). Nothing to do.")
        return 0

    conn = db.connect()
    try:
        due = conn.execute(
            "SELECT * FROM posts WHERE status = 'scheduled' LIMIT ?",
            (posting.get("posts_per_day", 3),),
        ).fetchall()
    finally:
        conn.close()

    posted = 0
    for post in due:
        post = dict(post)
        conn = db.connect()
        try:
            clip = conn.execute("SELECT * FROM clips WHERE id = ?", (post["clip_id"],)).fetchone()
        finally:
            conn.close()
        if not clip:
            continue
        clip = dict(clip)
        variants = json.loads(clip.get("variant_paths") or "{}")
        variant_path = variants.get(post["platform"], clip.get("master_path"))

        result = _post_to_platform(post["platform"], clip, variant_path, dry_run)

        conn = db.connect()
        try:
            if result["ok"]:
                conn.execute(
                    "UPDATE posts SET status = ?, posted_at = ?, platform_post_id = ? WHERE id = ?",
                    ("posted" if not dry_run else "scheduled",
                     datetime.now().isoformat(timespec="seconds") if not dry_run else None,
                     result["post_id"], post["id"]),
                )
                if not dry_run:
                    conn.execute("UPDATE clips SET status = 'posted' WHERE id = ?", (clip["id"],))
                    posted += 1
            else:
                conn.execute(
                    "UPDATE posts SET status = 'failed', error = ? WHERE id = ?",
                    (result["error"], post["id"]),
                )
            conn.commit()
        finally:
            conn.close()

    log.info("Posting run complete. %d posted (dry_run=%s).", posted, dry_run)
    return posted


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 4 posting scaffold.")
    parser.add_argument("--queue", action="store_true", help="Schedule eligible clips")
    parser.add_argument("--run", action="store_true", help="Process due posts (respects dry-run)")
    args = parser.parse_args()

    db.init_db()
    if args.queue:
        queue_posts()
    if args.run:
        run_posting()
    if not (args.queue or args.run):
        parser.print_help()


if __name__ == "__main__":
    main()
