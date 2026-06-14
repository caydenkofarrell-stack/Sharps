# LockedIn — Quickstart (do this in order)

Every command for Windows PowerShell. **Use `py`, not `python`.** Run them one
at a time; if anything errors, stop and check the line before moving on.

---

## ONE-TIME SETUP

### 0. You already have: Python (`py`), Git, ffmpeg ✅

### 1. Get the code as its own project (separate from Sharps)

First make an empty private repo: go to **https://github.com/new**, name it
`lockedin-motivation`, choose **Private**, check nothing else, **Create**.

Then in PowerShell:

```powershell
cd ~\Documents
git clone https://github.com/caydenkofarrell-stack/Sharps.git LockedIn
cd LockedIn
git checkout claude/upbeat-cannon-ant0n3
git remote remove origin
git remote add origin https://github.com/caydenkofarrell-stack/lockedin-motivation.git
git branch -M main
git push -u origin main
```

### 2. Install the one extra tool (for downloading footage)

```powershell
py -m pip install -U yt-dlp
```

You're now fully set up. Everything below is the repeatable daily/weekly loop.

---

## THE WEEKLY LOOP (batch once, post all week)

> Always run these from inside the LockedIn folder:
> ```powershell
> cd ~\Documents\LockedIn
> ```

### Step 1 — Get footage you can actually monetize

Pick ONE source:

**A) Your own phone footage (best):** copy the video file into the
`LockedIn\footage` folder. Done — skip to Step 2.

**B) Free stock footage:** download clips from **pexels.com/videos**,
**pixabay.com/videos**, or **mixkit.co** (free, licensed for commercial use).
Save them into `LockedIn\footage`.

**C) Creative Commons YouTube:** on YouTube, search a topic → **Filters** →
**Features** → **Creative Commons**. Copy the video URL, then:

```powershell
py fetch_footage.py "PASTE_THE_URL_HERE"
```

> ⚠️ Only download footage that's yours, stock, or Creative Commons. Reposting
> random copyrighted clips = strikes + zero payout. The whole point is to OWN
> your edit so it earns.

### Step 2 — Cut the best moments into vertical clips

(Replace the filename with your actual file in `footage\`.)

```powershell
py clip_finder.py "footage\YOURVIDEO.mp4" -n 5
```

Output: 5 vertical clips in the `clips\` folder. Want a quick preview without
cutting? Add `--dry-run`.

### Step 3 — Add a caption to each clip + generate post text

Run once per clip (clip1, clip2, ...):

```powershell
py make_post.py "clips\YOURVIDEO_clip1.mp4"
py make_post.py "clips\YOURVIDEO_clip2.mp4"
```

Each makes a `_post.mp4` (caption burned on) and a `_post.txt` (caption +
hashtags to paste when uploading). Want your own hook instead?
`py make_post.py "clips\..._clip1.mp4" --text "YOUR LINE HERE"`

### Step 4 — Queue them and build the schedule

```powershell
py scheduler.py add "clips\YOURVIDEO_clip1_post.mp4"
py scheduler.py add "clips\YOURVIDEO_clip2_post.mp4"
py scheduler.py plan --per-day 2 --time 18:00 --days 7
```

### Step 5 — Need fresh script ideas anytime?

```powershell
py generate.py -n 10
```

---

## THE DAILY HABIT (60 seconds)

```powershell
cd ~\Documents\LockedIn
py scheduler.py today
```

It lists what to post and the caption file for each. Open each `_post.mp4`,
upload it to TikTok, paste the caption from its `_post.txt`. Then mark it done:

```powershell
py scheduler.py done 1
```

That's it. Repeat daily. Consistency is the whole game.

---

## SAVE YOUR WORK (so nothing's lost)

Whenever you've made changes or added scripts you like:

```powershell
git add -A
git commit -m "content update"
git push
```

---

## THE PATH TO MONEY (set expectations)

1. **Reach first, money second.** TikTok Creator Rewards needs ~10k followers +
   100k views/30 days; YouTube Shorts needs Partner Program thresholds. You're
   farming reach until that door opens — don't quit before it does.
2. **Post daily for 30–60 days before judging.** Most channels that "fail" quit
   at week 2. The algorithm rewards consistency it can trust.
3. **Then scale.** Once channel #1 is on autopilot, clone it: copy the repo to a
   new folder, swap the niche in `content_banks.py`, give it its own queue:
   `py scheduler.py --file gym_queue.json today`.
