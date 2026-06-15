# LockedIn — Editing & Format Playbook

How to edit and caption every length of video for max reach. The `pipeline.py`
tool does the heavy lifting (cut + hook + schedule); CapCut adds per-video
polish on the ones worth it. This is the system.

---

## The length → platform → purpose map

| Length | Best platform | Purpose | How to make it |
|--------|--------------|---------|----------------|
| **7–15s** | TikTok / Reels | **Reach.** Quick hooks, max rewatch. Your bread & butter. | `pipeline.py video.mp4 --len 10 -n 8` |
| **20–34s** | TikTok / Shorts | **Depth.** One full idea, builds saves + follows. | `pipeline.py video.mp4 --len 27 -n 6` |
| **45–60s** | TikTok / Shorts | **Story.** A mini-message with a turn. Higher watch-time. | `pipeline.py video.mp4 --len 55 -n 4` |
| **3–5 min** | YouTube / TikTok | **Authority + ad money.** Build the long video, ALSO chop shorts from it. | film/source long → `pipeline.py long.mp4 --len 22 -n 10` |
| **8–10 min** | YouTube long-form | **YouTube ad revenue** (the real money once monetized). | edit in CapCut, upload whole; pull 10+ shorts with pipeline |

**The pro move:** make ONE long piece, then `pipeline.py` slices it into a week
of shorts. One recording → long-form video + 10 clips. Maximum output per effort.

---

## The 5-layer edit (what makes motivational content pop)

Every viral clip in this niche has these. Our tool does 1–2; CapCut does 3–5.

1. **The hook (first 1 sec)** — big bold text, top of screen. ✅ `make_post.py` burns this.
2. **Vertical 9:16, 1080×1920** — ✅ `clip_finder.py` crops this automatically.
3. **Synced captions (karaoke style)** — words pop as they're spoken. Do this in
   **CapCut → Auto-captions** (2 taps). Huge for retention; people watch on mute.
4. **Trending sound** — pair the clip with a hot audio from **TikTok Creative
   Center**. Half of going viral is the sound. Add it in the TikTok app at upload.
5. **Subtle motion + grade** — slow zoom, slight contrast/dark grade. CapCut presets.

---

## The fast workflow (per batch)

```
1. py pipeline.py footage/raw.mp4 --len 22 -n 6     # 6 hook'd vertical posts, scheduled
2. Open the winners in CapCut → Auto-captions + trending sound + zoom
3. py scheduler.py today  → upload, paste caption from the _post.txt, add the sound
```

Don't CapCut-polish all 6 — polish the 2–3 with the strongest hook. Volume on the
rest. Let the algorithm tell you which to invest in.

---

## Caption / text rules (engagement)

- **Hook text:** 3–6 words, ALL CAPS, top third. The tool wraps this for you.
- **On-screen body:** keep synced captions at the *center-bottom*, never covering
  the hook.
- **Post caption (the _post.txt):** 1 punchy line + a question to drive comments
  ("Could you do this?"). The generator writes these; tweak to add a question.
- **Hashtags:** 4 broad + 4 niche (the tool already mixes these). Don't spam 30.

---

## Length presets cheat-sheet

```
py pipeline.py footage/raw.mp4 --len 10 -n 8     # 8 quick 10s reach clips
py pipeline.py footage/raw.mp4 --len 27 -n 6     # 6 standard 27s posts
py pipeline.py footage/raw.mp4 --len 55 -n 4     # 4 longer story posts
py pipeline.py footage/raw.mp4 --len 22 -n 12    # a longer source -> 12 shorts
```

More posts need a longer source video — a 10s clip needs ~12s of source per clip.
