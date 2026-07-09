# Uncommon Hours Clip Engine

Automated short-form clip pipeline: source long-form YouTube videos → cut them
into vertical 9:16 clips → brand them in the Uncommon Hours style → review and
approve in a local dashboard → (later) auto-post to YouTube Shorts, TikTok, and
Instagram Reels. The system logs every review decision and learns your taste so
agents can take over the repetitive work.

Built by CO / Uncommon Hours. Runs locally on Windows first.

---

## The four phases

| Phase | What it does | Modules |
|------|---------------|---------|
| 1 – Core pipeline | Pull uploads, segment, format 9:16, brand | `downloader.py`, `processor.py` |
| 2 – Review + logging | Local dashboard, approve/reject/tag, SQLite | `dashboard.py` |
| 3 – Learning layer | Build preference profile, pre-score clips | `learning_agent.py` |
| 4 – Autonomous posting | Schedule + post across platforms, track performance | `poster.py` |

`orchestrator.py` ties it together and runs on a schedule.

---

## Install (Windows, one time)

1. **Python 3.11+** — https://python.org → check **"Add Python to PATH"** during install.
2. **FFmpeg** — in PowerShell: `winget install ffmpeg`
3. **Python packages** — from this folder:
   ```powershell
   pip install -r requirements.txt
   ```
4. **Verify** both are on PATH:
   ```powershell
   python --version
   ffmpeg -version
   ```

---

## First run

```powershell
# 1. Initialize the database (also happens automatically on first use)
python db.py

# 2. Add your sources: edit config/sources.json
#    - put in 8-12 real motivational channel URLs
#    - set "enabled": true on the ones you want pulled
python downloader.py --list          # confirm your enabled sources

# 3. Pull new uploads
python downloader.py

# 4. Cut + brand clips (use --dry-run first to see the ffmpeg plan)
python processor.py --dry-run
python processor.py

# 5. Review
python dashboard.py                  # open http://localhost:5000

# Or run the whole pull->process pass in one shot:
python orchestrator.py --once
python orchestrator.py --status      # see where everything stands
```

---

## Configuration

Everything lives in `config/`:

- **`settings.json`** — clip lengths, output resolution, branding, platform specs,
  schedule times, posting guard rails.
- **`sources.json`** — your source channels. Each entry:
  ```json
  {
    "id": "unique_id",
    "name": "Speaker Name",
    "url": "https://www.youtube.com/@handle",
    "category": "motivational",
    "enabled": true,
    "max_clips_per_video": 4,
    "attribution_text": "Clip: Speaker Name - shared with credit",
    "clipping_permission": "granted"
  }
  ```

Secrets (API keys for Phase 4) go in `config/secrets.json` — **gitignored**, never commit them.

---

## ⚠️ The money rule — read before Phase 4

Straight re-uploads of other people's clips **do not get monetized** and get
copyright-struck. This is baked into the pipeline, not left to willpower:

- `poster.py` will only post clips that are **approved AND `transformed = 1`**.
  A raw re-upload can't post by accident.
- The dashboard reminds you on every approve to add UH captions / commentary
  before posting.
- **UFC/MMA is excluded from v1** (aggressive rights-holder). Add later only as
  genuine breakdown/analysis with your commentary.
- **Motivational speaker content is the lowest-risk lane** — prioritize creators
  who permit clipping with attribution (`clipping_permission` in `sources.json`).

Monetization targets: **YouTube Shorts pays best per view** (primary), TikTok
Creator Rewards needs 10K followers + videos over 1 min, Instagram Reels builds
audience but has no direct pay program for most creators.

---

## Scheduling (Windows Task Scheduler)

Run the pipeline daily without keeping a window open:

- **Program/script:** `python`
- **Arguments:** `orchestrator.py --once`
- **Start in:** this project folder

Or run resident: `python orchestrator.py --serve` (fires on the times in
`settings.json`).

---

## Project layout

```
uncommon-hours-automation/
├── config/
│   ├── sources.json        source channels + pull rules
│   └── settings.json       clip lengths, branding, schedule, posting
├── downloads/              raw video from yt-dlp (gitignored)
├── processed/              finished clips, by date/source (gitignored)
├── database/
│   ├── schema.sql          table definitions
│   └── clips.db            SQLite - metadata, decisions, performance (gitignored)
├── logs/
├── config_loader.py        shared config + logging + paths
├── db.py                   shared SQLite helpers
├── downloader.py           Phase 1 - yt-dlp channel pulls
├── processor.py            Phase 1 - FFmpeg segment + format + brand
├── dashboard.py            Phase 2 - Flask review interface
├── learning_agent.py       Phase 3 - approval pattern analysis
├── poster.py               Phase 4 - platform posting (scaffold, disabled)
└── orchestrator.py         main runner + scheduler
```

---

## Status of this build

Phases 1–3 are implemented and runnable. Phase 4 (`poster.py`) is a safe
scaffold — posting is disabled by default and runs dry-run only until you wire
up the platform APIs. Next real step: fill `sources.json` with 8–12 motivational
channels and do a first `python orchestrator.py --once`.
