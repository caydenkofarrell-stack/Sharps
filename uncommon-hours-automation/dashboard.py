"""dashboard.py - Phase 2

Local Flask review interface. Shows clips with status 'pending_review', plays
each variant, and records approve / reject / edit decisions with tags into the
decisions table. Every decision is the training data for learning_agent.py.

Run:
    python dashboard.py
Then open http://localhost:5000

Notes:
    - Serves video/thumbnail files straight from processed/ (read-only).
    - "Approve" flips the clip to 'approved'; "Reject" to 'rejected'.
    - Tags are free-form chips plus quick presets (strong hook, too long, etc.).
    - The transformation reminder is shown on every approve: straight re-uploads
      don't monetize - add UH captions/commentary before posting (Phase 4).
"""
from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, abort, jsonify, render_template_string, request, send_file

from config_loader import get_settings, project_root
import db

app = Flask(__name__)

QUICK_TAGS = [
    "strong hook", "weak hook", "too long", "too short", "great pacing",
    "slow start", "wrong music", "clean cut", "needs caption", "on brand",
]


def _pending():
    conn = db.connect()
    try:
        rows = conn.execute(
            """
            SELECT c.*, v.title AS video_title, v.channel AS channel, s.name AS source_name
            FROM clips c
            LEFT JOIN videos v ON c.video_id = v.id
            LEFT JOIN sources s ON c.source_id = s.id
            WHERE c.status = 'pending_review'
            ORDER BY c.created_at
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _counts():
    conn = db.connect()
    try:
        rows = conn.execute(
            "SELECT status, COUNT(*) AS n FROM clips GROUP BY status"
        ).fetchall()
        return {r["status"]: r["n"] for r in rows}
    finally:
        conn.close()


@app.route("/")
def index():
    clips = _pending()
    for c in clips:
        try:
            c["variants"] = json.loads(c.get("variant_paths") or "{}")
        except json.JSONDecodeError:
            c["variants"] = {}
    return render_template_string(
        PAGE, clips=clips, counts=_counts(), quick_tags=QUICK_TAGS,
        brand=get_settings()["brand"],
    )


def _safe_media(rel_or_abs: str) -> Path:
    """Only allow serving files that live under the project's processed/ dir."""
    processed = (project_root() / get_settings()["paths"]["processed"]).resolve()
    p = Path(rel_or_abs).resolve()
    if processed not in p.parents and p != processed:
        abort(403)
    if not p.exists():
        abort(404)
    return p


@app.route("/media")
def media():
    path = request.args.get("path", "")
    return send_file(_safe_media(path))


@app.route("/decide", methods=["POST"])
def decide():
    data = request.get_json(force=True)
    clip_id = int(data["clip_id"])
    decision = data["decision"]
    if decision not in ("approved", "rejected", "edited"):
        abort(400)
    tags = data.get("tags", [])
    notes = data.get("notes", "")

    conn = db.connect()
    try:
        clip = conn.execute("SELECT * FROM clips WHERE id = ?", (clip_id,)).fetchone()
        if not clip:
            abort(404)
        conn.execute(
            """
            INSERT INTO decisions
                (clip_id, decision, tags, length_seconds, hook_type, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (clip_id, decision, json.dumps(tags), clip["length_seconds"],
             clip["hook_text"], notes),
        )
        new_status = "approved" if decision != "rejected" else "rejected"
        conn.execute("UPDATE clips SET status = ? WHERE id = ?", (new_status, clip_id))
        conn.commit()
    finally:
        conn.close()
    return jsonify({"ok": True})


PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Uncommon Hours - Clip Review</title>
<style>
  :root { --brand: {{ brand.primary_color }}; }
  * { box-sizing: border-box; }
  body { margin:0; background:#0d0d0f; color:#f2f2f2; font-family:-apple-system,Segoe UI,Roboto,sans-serif; }
  header { padding:16px 24px; border-bottom:1px solid #222; display:flex; align-items:center; gap:20px; position:sticky; top:0; background:#0d0d0f; z-index:5; }
  header h1 { font-size:18px; margin:0; letter-spacing:1px; }
  header .brand { color:var(--brand); font-weight:700; }
  .counts { margin-left:auto; font-size:13px; color:#999; display:flex; gap:16px; }
  .counts b { color:#f2f2f2; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:20px; padding:24px; }
  .card { background:#161619; border:1px solid #242428; border-radius:12px; overflow:hidden; display:flex; flex-direction:column; }
  .card video { width:100%; background:#000; aspect-ratio:9/16; object-fit:contain; }
  .card .body { padding:14px; display:flex; flex-direction:column; gap:10px; }
  .meta { font-size:12px; color:#8a8a90; line-height:1.5; }
  .meta .title { color:#e8e8ea; font-weight:600; font-size:13px; }
  .variants { display:flex; gap:6px; flex-wrap:wrap; }
  .variants button { font-size:11px; padding:3px 8px; border-radius:6px; border:1px solid #333; background:#1e1e22; color:#bbb; cursor:pointer; }
  .variants button.active { border-color:var(--brand); color:var(--brand); }
  .tags { display:flex; gap:6px; flex-wrap:wrap; }
  .tag { font-size:11px; padding:4px 9px; border-radius:14px; border:1px solid #333; background:#1a1a1e; color:#aaa; cursor:pointer; user-select:none; }
  .tag.on { background:var(--brand); color:#000; border-color:var(--brand); }
  .actions { display:flex; gap:8px; margin-top:4px; }
  .actions button { flex:1; padding:10px; border:none; border-radius:8px; font-weight:600; cursor:pointer; }
  .approve { background:#1f8f4e; color:#fff; }
  .reject { background:#333; color:#eee; }
  .note { color:#c98a2b; font-size:11px; margin-top:6px; }
  .empty { text-align:center; color:#666; padding:80px 20px; }
  .done { opacity:0.35; pointer-events:none; }
</style>
</head>
<body>
<header>
  <h1><span class="brand">UNCOMMON HOURS</span> - Clip Review</h1>
  <div class="counts">
    <span>pending <b>{{ counts.get('pending_review', 0) }}</b></span>
    <span>approved <b>{{ counts.get('approved', 0) }}</b></span>
    <span>rejected <b>{{ counts.get('rejected', 0) }}</b></span>
  </div>
</header>

{% if not clips %}
  <div class="empty">
    <h2>Queue is empty</h2>
    <p>Run <code>python downloader.py</code> then <code>python processor.py</code> to fill the queue.</p>
  </div>
{% else %}
<div class="grid">
  {% for c in clips %}
  <div class="card" id="card-{{ c.id }}">
    <video id="vid-{{ c.id }}" controls preload="metadata"
           poster="/media?path={{ c.thumbnail_path|urlencode }}"
           src="/media?path={{ c.master_path|urlencode }}"></video>
    <div class="body">
      <div class="meta">
        <div class="title">{{ c.hook_text or c.video_title or 'Untitled clip' }}</div>
        {{ c.source_name or c.channel or 'unknown source' }} &middot;
        clip #{{ c.seq }} &middot; {{ '%.0f'|format(c.length_seconds or 0) }}s
      </div>
      <div class="variants" data-clip="{{ c.id }}">
        <button class="active" onclick="setSrc({{ c.id }}, '{{ c.master_path|urlencode }}', this)">master</button>
        {% for name, path in c.variants.items() %}
        <button onclick="setSrc({{ c.id }}, '{{ path|urlencode }}', this)">{{ name }}</button>
        {% endfor %}
      </div>
      <div class="tags" data-clip="{{ c.id }}">
        {% for t in quick_tags %}
        <span class="tag" onclick="toggleTag(this)">{{ t }}</span>
        {% endfor %}
      </div>
      <div class="actions">
        <button class="approve" onclick="decide({{ c.id }}, 'approved')">Approve</button>
        <button class="reject" onclick="decide({{ c.id }}, 'rejected')">Reject</button>
      </div>
      <div class="note">Before posting: add UH captions / commentary. Straight re-uploads don't monetize.</div>
    </div>
  </div>
  {% endfor %}
</div>
{% endif %}

<script>
function setSrc(id, path, btn) {
  const v = document.getElementById('vid-' + id);
  v.src = '/media?path=' + path;
  v.play().catch(()=>{});
  btn.parentNode.querySelectorAll('button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}
function toggleTag(el) { el.classList.toggle('on'); }
async function decide(id, decision) {
  const tags = [...document.querySelectorAll('.tags[data-clip="'+id+'"] .tag.on')].map(t => t.textContent);
  const res = await fetch('/decide', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({clip_id: id, decision, tags})
  });
  if (res.ok) document.getElementById('card-' + id).classList.add('done');
}
</script>
</body>
</html>
"""


def main() -> None:
    db.init_db()
    print("Uncommon Hours review dashboard -> http://localhost:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
