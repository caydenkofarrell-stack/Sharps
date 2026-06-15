# LockedIn — Discipline/Mindset Content Engine

Tools to grow an intense **discipline / mental-toughness** channel (TikTok,
YouTube Shorts, Reels) in the "no excuses, stay hard" lane — built for
**platform payouts**.

Your own venture. Run it on your machine, build the brand, scale the channels.

---

## ⚡ New here? Read [`QUICKSTART.md`](QUICKSTART.md) — every command, in order.

## 🚀 The one command that does everything

```bash
py pipeline.py footage/yourvideo.mp4 -n 6
```

One video in → **6 finished, captioned, scheduled posts** out, in about a minute.
That's the whole machine in a single line. Everything below is the parts it runs.

## ✅ First time? Verify your machine in 10 seconds

```bash
py selftest.py
```

Runs the entire system on a throwaway clip and prints `ALL SYSTEMS GO` when
you're ready. Do this once before you start so nothing wastes your time.

## The toolkit (all working today)

| Tool | What it does | Needs |
|------|-------------|-------|
| `pipeline.py` | **One video → batch of finished, scheduled posts** | Python + ffmpeg |
| `selftest.py` | Verifies every tool works on your machine | Python |
| `fetch_footage.py` | Download source video from a URL into `footage/` | Python + yt-dlp |
| `clip_finder.py` | Long video → best vertical clips | Python + ffmpeg |
| `make_post.py` | Burns hook caption onto a clip + writes post text | Python + ffmpeg |
| `generate.py` | Writes scripts, captions, hashtags | Python only |
| `scheduler.py` | Queues clips into a daily posting routine | Python only |

### The full pipeline (one channel, end to end)

```bash
py clip_finder.py raw.mp4 -n 5            # 1. cut 5 clips from a long video
py make_post.py clips/raw_clip1.mp4      # 2. add caption overlay + post text (repeat per clip)
py scheduler.py add clips/raw_clip1_post.mp4   # 3. queue each finished post
py scheduler.py plan --per-day 2 --days 7      # 4. spread them over a week
py scheduler.py today                    # 5. every day: post what it lists, then `done <id>`
```

> ⚠️ **On Windows use `py`, not `python`.** All examples below say `python`;
> just swap in `py`.

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

## ⚠️ Where the clips come from (read before you repost anything)

The plan of "pull viral TikToks/YouTube clips and repost them" has a wall, and
it's the difference between a channel that earns and one that gets killed:

- **You can't monetize content you don't own.** TikTok Creator Rewards and the
  YouTube Partner Program both require *original* content. Reuploading someone
  else's clip = no payout, even if it goes viral.
- **Reposting gets struck and banned.** Copyright owners file claims; platforms
  remove videos and ban repeat-offender accounts. Pure "repost" channels live
  on borrowed time.

**The version that actually works — and what these tools are built for:**

1. **Film your own** gym/discipline b-roll on your phone (you train anyway —
   record it). `clip_finder.py` pulls the best moments automatically.
2. **Use royalty-free / Creative-Commons footage** you're licensed to use:
   Pexels, Pixabay, Mixkit (free), or a stock subscription. Your voice + your
   edit + your script = original content you own and can monetize.
3. **Your edge is the words and the edit, not the raw clip.** The script engine
   is your moat — the same gym footage with *your* hook is yours.

So: source footage you're allowed to use, run it through the pipeline, and the
output is monetizable and ban-proof. That's the whole strategy.

---

## Scaling to multiple channels (your goal)

Nail ONE channel to ~10k followers first — that proves the system. Then cloning
is mechanical:

1. **Copy the playbook, swap the niche.** Duplicate `content_banks.py` themes
   for a new lane (e.g. `mindset/`, `gym/`, `hustle/`). Same tools, new voice.
2. **One queue per channel.** `scheduler.py --file gym_queue.json` keeps each
   channel's routine separate.
3. **Stagger, don't split.** Run channel #2 only once #1 is on autopilot
   (batched + scheduled). Two half-built channels beat zero finished ones.
4. **Cross-post the winners.** A clip that pops on TikTok goes to Shorts +
   Reels for free reach before you make anything new.

---

## Roadmap — the "auto-clip + auto-post" tool you asked about

Your bigger idea: **feed in a video → it finds the best parts → posts it for
you everywhere.** Here's the honest breakdown of what's buildable and what
isn't, so we build the real thing instead of a fantasy.

### Phase 1 — Script engine ✅ DONE
This repo. The "what to say" layer.

### Phase 2 — Clip finder ✅ DONE (`clip_finder.py`)
Feed in a longer video → it ranks the loudest/highest-energy moments, cuts the
top ones into vertical 9:16 clips ready to post. Pure Python stdlib; the only
requirement is **ffmpeg** installed on your machine.

```bash
python clip_finder.py raw.mp4            # top 3 vertical clips → ./clips/
python clip_finder.py raw.mp4 -n 5       # top 5 moments
python clip_finder.py raw.mp4 --len 25   # ~25s clips
python clip_finder.py raw.mp4 --dry-run  # just show the moments, cut nothing
```

> Runs on **your machine**, not the cloud — it needs your video files and
> ffmpeg. Install ffmpeg first: `brew install ffmpeg` (macOS),
> `winget install ffmpeg` (Windows), `sudo apt install ffmpeg` (Linux).

**The full local pipeline:**
```bash
python clip_finder.py raw.mp4 -n 5   # cut 5 clips from a long video
python generate.py -n 5              # generate 5 captions + hashtag sets
# pair each clip with a caption → post (one tap each)
```

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
