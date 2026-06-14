#!/usr/bin/env python3
"""
Sharps — Discipline/Mindset short-form script generator.

Generates ready-to-record scripts for TikTok / YouTube Shorts / Reels in the
intense "no excuses, stay hard" lane. Each script comes with a hook, escalating
body lines, a closer, a caption, hashtags, and production notes (visual + audio)
so you can film or repost without thinking.

USAGE
    python generate.py                 # 3 random scripts
    python generate.py -n 10           # 10 scripts (a week+ of content)
    python generate.py -t consistency  # only the "consistency" theme
    python generate.py --list          # show available themes
    python generate.py -n 14 -o batch.md   # save 14 scripts to a markdown file
    python generate.py --seed 42       # reproducible output

Run it daily, film the batch, schedule the posts. That's the whole engine.
"""

import argparse
import random
import sys
import textwrap

import content_banks as cb


def _pick(rng, items, k):
    """Pick k unique items if possible, else sample with repetition."""
    if k <= len(items):
        return rng.sample(items, k)
    return [rng.choice(items) for _ in range(k)]


def build_script(rng, theme_key):
    """Assemble one fresh script from a theme's banks."""
    theme = cb.THEMES[theme_key]

    hook = rng.choice(theme["hooks"])
    n_body = rng.randint(3, 4)
    body = _pick(rng, theme["body"], n_body)
    closer = rng.choice(theme["closers"])
    cta = rng.choice(cb.CTA_LINES)

    caption = "{}\n\n{}".format(rng.choice(cb.CAPTION_HOOKS), hook)

    tags = _pick(rng, cb.HASHTAGS_BROAD, 4) + _pick(rng, cb.HASHTAGS_NICHE, 4)
    rng.shuffle(tags)

    return {
        "theme": theme["label"],
        "hook": hook,
        "body": body,
        "closer": closer,
        "cta": cta,
        "caption": caption,
        "hashtags": " ".join(tags),
        "visual": rng.choice(cb.VISUAL_SUGGESTIONS),
        "audio": rng.choice(cb.AUDIO_SUGGESTIONS),
        "runtime": "{}-{}s".format(15 + n_body * 3, 22 + n_body * 4),
    }


def render(script, index):
    """Format one script as a clean, copy-pasteable block."""
    line = "=" * 60
    out = []
    out.append(line)
    out.append("  SCRIPT #{}   —   {}   (~{})".format(index, script["theme"], script["runtime"]))
    out.append(line)
    out.append("")
    out.append("  HOOK (first 3 sec — make it count):")
    out.append("    " + script["hook"])
    out.append("")
    out.append("  BODY (one line per beat, let each land):")
    for i, b in enumerate(script["body"], 1):
        out.append("    {}. {}".format(i, b))
    out.append("")
    out.append("  CLOSER (the punch):")
    out.append("    " + script["closer"])
    out.append("")
    out.append("  CTA (drives follows = payout):")
    out.append("    " + script["cta"])
    out.append("")
    out.append("  ── POST KIT ──────────────────────────────────────")
    out.append("  Caption:")
    for cl in textwrap.wrap(script["caption"].replace("\n\n", "  //  "), 56):
        out.append("    " + cl)
    out.append("  Hashtags:")
    for hl in textwrap.wrap(script["hashtags"], 56):
        out.append("    " + hl)
    out.append("")
    out.append("  ── PRODUCTION ────────────────────────────────────")
    out.append("  Visual:  " + script["visual"])
    out.append("  Audio:   " + script["audio"])
    out.append("")
    return "\n".join(out)


def render_markdown(script, index):
    """Markdown version for the --output file (batch/scheduling friendly)."""
    lines = []
    lines.append("## Script {} — {} (~{})".format(index, script["theme"], script["runtime"]))
    lines.append("")
    lines.append("**Hook:** {}".format(script["hook"]))
    lines.append("")
    lines.append("**Body:**")
    for b in script["body"]:
        lines.append("- {}".format(b))
    lines.append("")
    lines.append("**Closer:** {}".format(script["closer"]))
    lines.append("")
    lines.append("**CTA:** {}".format(script["cta"]))
    lines.append("")
    lines.append("**Caption:** {}".format(script["caption"].replace("\n\n", " // ")))
    lines.append("")
    lines.append("**Hashtags:** {}".format(script["hashtags"]))
    lines.append("")
    lines.append("**Visual:** {}  ".format(script["visual"]))
    lines.append("**Audio:** {}".format(script["audio"]))
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate intense discipline/mindset short-form video scripts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-n", "--number", type=int, default=3,
                        help="how many scripts to generate (default: 3)")
    parser.add_argument("-t", "--theme", choices=sorted(cb.THEMES.keys()),
                        help="restrict to a single theme (default: random mix)")
    parser.add_argument("-o", "--output", metavar="FILE",
                        help="also save the batch to a markdown file")
    parser.add_argument("--seed", type=int, help="seed for reproducible output")
    parser.add_argument("--list", action="store_true",
                        help="list available themes and exit")
    args = parser.parse_args(argv)

    if args.list:
        print("Available themes:")
        for key in sorted(cb.THEMES.keys()):
            print("  {:<22} {}".format(key, cb.THEMES[key]["label"]))
        return 0

    if args.number < 1:
        parser.error("-n/--number must be at least 1")

    rng = random.Random(args.seed)
    theme_keys = list(cb.THEMES.keys())

    scripts = []
    for i in range(args.number):
        tk = args.theme if args.theme else rng.choice(theme_keys)
        scripts.append(build_script(rng, tk))

    banner = "\n  STAY HARD. {} script(s) loaded. Go film.\n".format(len(scripts))
    print(banner)
    for i, s in enumerate(scripts, 1):
        print(render(s, i))

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write("# Content Batch — Discipline/Mindset\n\n")
            fh.write("_Generated by Sharps script engine. Film, schedule, post._\n\n")
            for i, s in enumerate(scripts, 1):
                fh.write(render_markdown(s, i))
        print("  Saved {} scripts to {}\n".format(len(scripts), args.output))

    return 0


if __name__ == "__main__":
    sys.exit(main())
