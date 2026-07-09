"""learning_agent.py - Phase 3

Analyzes your approval history and builds a preference profile, then scores new
pending clips so high-confidence ones can be flagged "ready" and low-confidence
ones flagged "needs your eyes."

This is deliberately transparent and rule-based to start (no black box): it
learns weights from the tags and features that correlate with your approvals.
Swap in a real classifier later once there's enough decision data - the CO agent
pattern you already run.

Usage:
    python learning_agent.py --profile     # print your current preference profile
    python learning_agent.py --score       # score pending clips, print ranking
    python learning_agent.py --nightly     # rebuild profile (for the scheduler)
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

from config_loader import get_logger
import db

log = get_logger("learning_agent")

# Clips this close to the target length score best; tune from data over time.
IDEAL_LENGTH = 45.0
MIN_DECISIONS = 10  # below this, we don't trust the profile yet


def _load_decisions() -> list[dict]:
    conn = db.connect()
    try:
        rows = conn.execute("SELECT * FROM decisions").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def build_profile() -> dict:
    """Learn per-tag approval rates and length preference from decision history."""
    decisions = _load_decisions()
    total = len(decisions)
    approved = sum(1 for d in decisions if d["decision"] != "rejected")

    tag_approve = defaultdict(int)
    tag_total = defaultdict(int)
    approved_lengths: list[float] = []

    for d in decisions:
        is_approved = d["decision"] != "rejected"
        try:
            tags = json.loads(d.get("tags") or "[]")
        except json.JSONDecodeError:
            tags = []
        for t in tags:
            tag_total[t] += 1
            if is_approved:
                tag_approve[t] += 1
        if is_approved and d.get("length_seconds"):
            approved_lengths.append(d["length_seconds"])

    base_rate = approved / total if total else 0.0
    tag_scores = {}
    for tag, n in tag_total.items():
        rate = tag_approve[tag] / n
        # signed lift vs base rate, weighted by sample size
        tag_scores[tag] = round((rate - base_rate) * min(1.0, n / 5.0), 3)

    ideal = (sum(approved_lengths) / len(approved_lengths)) if approved_lengths else IDEAL_LENGTH

    return {
        "total_decisions": total,
        "approved": approved,
        "base_approval_rate": round(base_rate, 3),
        "trusted": total >= MIN_DECISIONS,
        "ideal_length": round(ideal, 1),
        "tag_scores": dict(sorted(tag_scores.items(), key=lambda kv: -kv[1])),
    }


def _pending_clips() -> list[dict]:
    conn = db.connect()
    try:
        rows = conn.execute(
            "SELECT * FROM clips WHERE status = 'pending_review'"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def score_clip(clip: dict, profile: dict) -> float:
    """Return a 0..1 confidence that you'll approve this clip."""
    score = profile["base_approval_rate"] or 0.5

    # Length closeness to your learned ideal.
    length = clip.get("length_seconds") or IDEAL_LENGTH
    ideal = profile.get("ideal_length", IDEAL_LENGTH)
    length_penalty = min(0.3, abs(length - ideal) / 90.0)
    score -= length_penalty

    # Hook presence is a small positive prior until we have tag data.
    if clip.get("hook_text"):
        score += 0.05

    return max(0.0, min(1.0, round(score, 3)))


def score_pending(profile: dict | None = None) -> list[dict]:
    profile = profile or build_profile()
    ranked = []
    for clip in _pending_clips():
        conf = score_clip(clip, profile)
        if not profile["trusted"]:
            flag = "needs your eyes"  # not enough data to auto-flag yet
        elif conf >= 0.7:
            flag = "ready"
        elif conf <= 0.4:
            flag = "likely reject"
        else:
            flag = "needs your eyes"
        ranked.append({
            "clip_id": clip["id"],
            "hook": clip.get("hook_text"),
            "length": clip.get("length_seconds"),
            "confidence": conf,
            "flag": flag,
        })
    ranked.sort(key=lambda r: -r["confidence"])
    return ranked


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze approvals and score clips.")
    parser.add_argument("--profile", action="store_true", help="Print preference profile")
    parser.add_argument("--score", action="store_true", help="Score pending clips")
    parser.add_argument("--nightly", action="store_true", help="Rebuild profile (scheduler hook)")
    args = parser.parse_args()

    db.init_db()
    profile = build_profile()

    if args.profile or args.nightly:
        print(json.dumps(profile, indent=2))
        if not profile["trusted"]:
            print(f"\n(Need >= {MIN_DECISIONS} decisions before flags are trusted; "
                  f"have {profile['total_decisions']}.)")

    if args.score:
        ranked = score_pending(profile)
        if not ranked:
            print("No pending clips to score.")
        for r in ranked:
            print(f"  clip {r['clip_id']:>4}  {r['confidence']:.2f}  "
                  f"[{r['flag']:<14}]  {(r['hook'] or '')[:50]}")

    if not any([args.profile, args.score, args.nightly]):
        parser.print_help()


if __name__ == "__main__":
    main()
