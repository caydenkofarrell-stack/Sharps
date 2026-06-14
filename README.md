# Sharps — Discipline/Mindset Content Engine

Tools to grow an intense **discipline / mental-toughness** channel (TikTok,
YouTube Shorts, Reels) in the "no excuses, stay hard" lane — built for
**platform payouts + reposting**.

Built and trained separately from your day-to-day. This is your second engine.

---

## What's here now

### `generate.py` — script generator ✅ (working today)

Spits out ready-to-record video scripts: hook, escalating body lines, closer,
caption, hashtags, and production notes (visual + audio). No internet, no API
keys, no dependencies — just Python 3.

```bash
python generate.py                 # 3 random scripts
python generate.py -n 14           # two weeks of content in one run
python generate.py -t consistency  # lock to one theme
python generate.py --list          # show all themes
python generate.py -n 14 -o batch.md   # save a batch to markdown
python generate.py --seed 42       # reproducible output
```

**Themes:** `wake_up_early`, `no_excuses`, `pain_discomfort`, `consistency`,
`mental_toughness`, `comparison_comfort`.

**Make it yours:** every line lives in `content_banks.py`. Add your own hooks
and closers to any list and the generator uses them instantly. The more *your
voice* is in there, the less generic it sounds.

---

## The growth playbook (read this once)

The script tool is the easy part. Here's how the money actually shows up:

1. **Pick ONE platform to start.** TikTok grows fastest from zero. Master it,
   then repurpose the same clips to Shorts + Reels (free extra reach).
2. **Post daily, batch weekly.** Generate 14 scripts Sunday, film them in one
   sitting, schedule them out. Consistency beats quality early on.
3. **Hook in 3 seconds or you're dead.** The first line on screen + spoken is
   90% of the video's success. The generator front-loads this on purpose.
4. **Every video ends in a CTA.** Follows and saves are what the payout
   algorithms reward — not just views.
5. **Reposting works.** Faceless text-on-black + b-roll + voiceover is a proven
   format you can produce fast. Use the production notes in each script.
6. **Money turns on at scale.** TikTok Creator Rewards needs 10k followers +
   100k views/30 days. YouTube Shorts needs Partner Program thresholds. So the
   first job is **reach**, not monetization. Don't quit before the door opens.

---

## Roadmap — the "auto-clip + auto-post" tool you asked about

Your bigger idea: **feed in a video → it finds the best parts → posts it for
you everywhere.** Here's the honest breakdown of what's buildable and what
isn't, so we build the real thing instead of a fantasy.

### Phase 1 — Script engine ✅ DONE
This repo. The "what to say" layer.

### Phase 2 — Clip finder �üöß BUILDABLE (needs your machine)
Feed in a longer video, auto-rank the best moments, export vertical clips.
Realistic approach: transcribe the audio (Whisper), score segments by
energy/loudness + punchy lines, cut the top moments with `ffmpeg`, add
captions. This is genuinely doable — but it needs **your local machine** with
the video files and ffmpeg installed, because this cloud container is wiped
between sessions and can't hold your media library.

### Phase 3 — Auto-posting ⚠️ READ THIS
Two hard walls, and I won't pretend they aren't there:

- **I can't take control of your computer from here.** I run in an isolated
  cloud container that gets reclaimed after the session. I have no access to
  your desktop, browser, or logged-in accounts. Anything that "controls your
  computer" has to run as a script **on your machine**, that you start.
- **Fully automated posting risks bans.** TikTok and YouTube's terms prohibit
  unofficial automation/bots; browser-puppeteering your logged-in account is
  the fastest way to get it killed. The *safe* path is the **official APIs**
  (YouTube Data API supports uploads; TikTok's Content Posting API exists but
  needs app approval). Those let us build a legit "one-click upload" without
  torching your account.

**The realistic auto-post tool** = a local script that takes a finished clip +
the generated caption/hashtags and pushes it through official APIs (or stages
it in your scheduler). One button, no ban risk. Not "Claude secretly drives
your TikTok," because that path ends in a banned account.

> Want Phase 2/3? I'll build the clip-finder and the API uploader as scripts
> **you run locally** — tell me your setup (Mac/Windows/Linux) and we'll wire
> it up.
