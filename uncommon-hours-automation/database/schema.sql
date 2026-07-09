-- Uncommon Hours Clip Engine - SQLite schema
-- Tables: sources, videos, clips, decisions, posts, performance

PRAGMA foreign_keys = ON;

-- Source channels pulled by the downloader (mirrors config/sources.json, kept
-- here so we can join and track per-source stats over time).
CREATE TABLE IF NOT EXISTS sources (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    url           TEXT NOT NULL,
    category      TEXT,
    attribution   TEXT,
    enabled       INTEGER DEFAULT 1,
    created_at    TEXT DEFAULT (datetime('now'))
);

-- Raw long-form videos pulled by yt-dlp.
CREATE TABLE IF NOT EXISTS videos (
    id            TEXT PRIMARY KEY,            -- youtube video id
    source_id     TEXT,
    title         TEXT,
    channel       TEXT,
    duration      INTEGER,                     -- seconds
    upload_date   TEXT,
    url           TEXT,
    file_path     TEXT,                        -- local path in downloads/
    status        TEXT DEFAULT 'downloaded',   -- downloaded | processed | error
    downloaded_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- Short vertical clips produced by the processor. One row per clip (a clip may
-- have several platform variant files - stored as JSON in variant_paths).
CREATE TABLE IF NOT EXISTS clips (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id        TEXT NOT NULL,
    source_id       TEXT,
    seq             INTEGER,                   -- clip index within the video
    start_seconds   REAL,
    end_seconds     REAL,
    length_seconds  REAL,
    master_path     TEXT,                      -- the branded 9:16 master
    variant_paths   TEXT,                      -- JSON: {"shorts": "...", "tiktok": "...", "reels": "..."}
    thumbnail_path  TEXT,
    hook_text       TEXT,                      -- overlay hook used
    status          TEXT DEFAULT 'pending_review', -- pending_review | approved | rejected | posted
    transformed     INTEGER DEFAULT 0,         -- 1 once UH transformation layer applied
    created_at      TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (video_id) REFERENCES videos(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- Every review decision. This is the training data for the learning agent.
CREATE TABLE IF NOT EXISTS decisions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    clip_id       INTEGER NOT NULL,
    decision      TEXT NOT NULL,               -- approved | rejected | edited
    tags          TEXT,                        -- JSON array: ["strong hook","too long",...]
    length_seconds REAL,
    hook_type     TEXT,
    pacing        TEXT,
    overlay_style TEXT,
    notes         TEXT,
    decided_at    TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (clip_id) REFERENCES clips(id)
);

-- Phase 4 - scheduled/actual posts per platform.
CREATE TABLE IF NOT EXISTS posts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    clip_id       INTEGER NOT NULL,
    platform      TEXT NOT NULL,               -- shorts | tiktok | reels
    scheduled_for TEXT,
    posted_at     TEXT,
    platform_post_id TEXT,
    status        TEXT DEFAULT 'scheduled',    -- scheduled | posted | failed | skipped
    error         TEXT,
    FOREIGN KEY (clip_id) REFERENCES clips(id)
);

-- Phase 4 - performance data pulled back from platforms, feeds learning layer.
CREATE TABLE IF NOT EXISTS performance (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id       INTEGER NOT NULL,
    views         INTEGER,
    likes         INTEGER,
    comments      INTEGER,
    shares        INTEGER,
    completion_rate REAL,
    pulled_at     TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE INDEX IF NOT EXISTS idx_clips_status ON clips(status);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_decisions_clip ON decisions(clip_id);
CREATE INDEX IF NOT EXISTS idx_posts_clip ON posts(clip_id);
