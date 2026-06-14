#!/usr/bin/env python3
"""
LockedIn — Scheduler (your posting routine).

Keeps a simple queue of posts and builds a posting calendar so you always know
exactly what to post and when. Pure Python stdlib — no dependencies, runs
anywhere. State lives in a local queue.json.

This does NOT auto-post (see the README for why that risks your account). It
makes posting a 60-second daily habit: it tells you the next thing to publish,
you tap publish, you mark it done.

USAGE
    py scheduler.py add clips/raw_clip1_post.mp4 --note "5AM hook"
    py scheduler.py plan --per-day 2 --time 18:00 --days 7   # schedule the queue
    py scheduler.py today        # what to post today
    py scheduler.py next         # the single next post
    py scheduler.py list         # the whole queue
    py scheduler.py done 1       # mark item #1 posted
    py scheduler.py calendar -o calendar.md   # export a markdown calendar

Typical loop:
    py clip_finder.py raw.mp4 -n 5           # cut clips
    py make_post.py clips/raw_clip1.mp4      # add captions (repeat per clip)
    py scheduler.py add clips/raw_clip1_post.mp4
    py scheduler.py plan --per-day 2 --time 18:00 --days 7
    py scheduler.py today                    # every day: post what it says
"""

import argparse
import datetime as dt
import json
import os
import sys

QUEUE_FILE = "queue.json"


def load_queue(path):
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError:
            sys.exit("ERROR: {} is corrupted. Fix or delete it.".format(path))


def save_queue(path, items):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(items, fh, indent=2)


def next_id(items):
    return (max((it["id"] for it in items), default=0)) + 1


def cmd_add(args, items):
    if not os.path.isfile(args.video):
        print("  ! warning: file not found ({}); adding anyway.".format(args.video))
    item = {
        "id": next_id(items),
        "video": args.video,
        "note": args.note or "",
        "scheduled": None,
        "status": "queued",
    }
    items.append(item)
    save_queue(args.file, items)
    print("  Added #{}: {}".format(item["id"], args.video))


def cmd_plan(args, items):
    pending = [it for it in items if it["status"] == "queued"]
    if not pending:
        print("  Nothing queued to schedule. Add clips first with: add <file>")
        return
    try:
        hh, mm = (int(x) for x in args.time.split(":"))
    except ValueError:
        sys.exit("ERROR: --time must look like 18:00")

    start = dt.date.today()
    slot = 0
    scheduled_count = 0
    for day in range(args.days):
        date = start + dt.timedelta(days=day)
        for n in range(args.per_day):
            if slot >= len(pending):
                break
            # space multiple daily posts a few hours apart
            when = dt.datetime(date.year, date.month, date.day, hh, mm) + \
                dt.timedelta(hours=n * 3)
            pending[slot]["scheduled"] = when.strftime("%Y-%m-%d %H:%M")
            pending[slot]["status"] = "scheduled"
            slot += 1
            scheduled_count += 1
        if slot >= len(pending):
            break

    save_queue(args.file, items)
    print("  Scheduled {} post(s): {}/day at {} starting {}."
          .format(scheduled_count, args.per_day, args.time, start.isoformat()))
    if slot < len(pending):
        print("  {} clip(s) still queued — add more days or run plan again later."
              .format(len(pending) - slot))


def _print_item(it):
    when = it["scheduled"] or "unscheduled"
    note = ("  — " + it["note"]) if it["note"] else ""
    print("   #{:<3} [{:^9}] {}  {}{}".format(
        it["id"], it["status"], when, os.path.basename(it["video"]), note))


def cmd_list(args, items):
    if not items:
        print("  Queue is empty. Add clips with: add <file>")
        return
    print("\n  Your queue ({} item(s)):".format(len(items)))
    print("  " + "-" * 60)
    for it in sorted(items, key=lambda x: (x["scheduled"] or "9999", x["id"])):
        _print_item(it)
    print()


def cmd_today(args, items):
    today = dt.date.today().isoformat()
    due = [it for it in items
           if it["status"] == "scheduled" and (it["scheduled"] or "").startswith(today)]
    if not due:
        print("  Nothing scheduled for today. Run plan, or enjoy the rest day.")
        return
    print("\n  POST THESE TODAY ({}):".format(today))
    print("  " + "-" * 60)
    for it in sorted(due, key=lambda x: x["scheduled"]):
        _print_item(it)
        txt = os.path.splitext(it["video"])[0] + ".txt"
        if txt.endswith("_post.txt") and os.path.isfile(txt):
            print("        caption file: {}".format(txt))
    print("\n  After posting each one:  py scheduler.py done <id>\n")


def cmd_next(args, items):
    upcoming = [it for it in items if it["status"] == "scheduled" and it["scheduled"]]
    if not upcoming:
        print("  No scheduled posts. Run: plan")
        return
    nxt = min(upcoming, key=lambda x: x["scheduled"])
    print("\n  NEXT UP:")
    _print_item(nxt)
    print()


def cmd_done(args, items):
    for it in items:
        if it["id"] == args.id:
            it["status"] = "posted"
            save_queue(args.file, items)
            print("  Marked #{} as posted. Keep the streak alive.".format(args.id))
            return
    sys.exit("ERROR: no item with id {}".format(args.id))


def cmd_calendar(args, items):
    scheduled = [it for it in items if it["scheduled"]]
    lines = ["# Posting Calendar\n"]
    if not scheduled:
        lines.append("_Nothing scheduled yet. Run `plan` first._\n")
    else:
        by_day = {}
        for it in scheduled:
            day = it["scheduled"].split(" ")[0]
            by_day.setdefault(day, []).append(it)
        for day in sorted(by_day):
            lines.append("## {}\n".format(day))
            for it in sorted(by_day[day], key=lambda x: x["scheduled"]):
                mark = "x" if it["status"] == "posted" else " "
                time = it["scheduled"].split(" ")[1]
                note = (" — " + it["note"]) if it["note"] else ""
                lines.append("- [{}] {} `{}`{}".format(
                    mark, time, os.path.basename(it["video"]), note))
            lines.append("")
    text = "\n".join(lines)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("  Calendar written to {}".format(args.out))
    else:
        print(text)


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Queue and schedule your posts into a daily routine.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--file", default=QUEUE_FILE, help="queue file (default queue.json)")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="add a video to the queue")
    a.add_argument("video")
    a.add_argument("--note", help="optional label")

    pl = sub.add_parser("plan", help="schedule queued items across upcoming days")
    pl.add_argument("--per-day", type=int, default=1)
    pl.add_argument("--time", default="18:00", help="first-post time HH:MM")
    pl.add_argument("--days", type=int, default=7)

    sub.add_parser("today", help="what to post today")
    sub.add_parser("next", help="the single next post")
    sub.add_parser("list", help="show the whole queue")

    d = sub.add_parser("done", help="mark an item posted")
    d.add_argument("id", type=int)

    cal = sub.add_parser("calendar", help="export a markdown calendar")
    cal.add_argument("-o", "--out", help="write to a file instead of stdout")

    args = p.parse_args(argv)
    items = load_queue(args.file)

    dispatch = {
        "add": cmd_add, "plan": cmd_plan, "list": cmd_list, "today": cmd_today,
        "next": cmd_next, "done": cmd_done, "calendar": cmd_calendar,
    }
    dispatch[args.cmd](args, items)
    return 0


if __name__ == "__main__":
    sys.exit(main())
