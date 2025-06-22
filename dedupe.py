"""
photo-deduper
=============

Group visually-similar images, preview them in an HTML gallery, and (optionally)
move the lower-quality copies into a **duplicates/** sub-folder.

Typical one-liners
------------------
# 1) Preview only (pHash, distance ≤ 10)
python dedupe.py /path/to/folder --method phash --threshold 10

# 2) Keep the largest image in every group, move the rest → duplicates/
python dedupe.py /path/to/folder --delete keep-largest
"""
from __future__ import annotations

import argparse
import html
import json
import os
import sys
import warnings
from pathlib import Path
from typing import List, Set

from helpers import kb, thumb_b64
from finder import dupes_cnn, dupes_phash, build_groups
from delete_logic import move_dupes

# ───────────────── hide a noisy RuntimeWarning from imagededup ─────────────
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    module="imagededup.methods.cnn",
)

# ─────────────────── escaping helpers ──────────────────────────────────────
def esc_html(text: str) -> str:
    """Escape text for safe insertion in HTML content/attributes."""
    return html.escape(text, quote=True)


def esc_js_str(text: str) -> str:
    """Return a JavaScript-safe string literal via JSON encoding."""
    return json.dumps(text, ensure_ascii=False)


# ─────────────────── HTML builder ──────────────────────────────────────────
def make_html(
    groups: List[Set[str]],
    folder: str,
    method: str,
    threshold: float,
    moved: int,
) -> str:
    """Return a ready-to-write HTML string."""
    group_html: list[str] = []

    for idx, grp in enumerate(groups, 1):
        # collect only files that still exist
        existing = [
            (fname, os.path.getsize(os.path.join(folder, fname)))
            for fname in grp
            if os.path.exists(os.path.join(folder, fname))
        ]
        if not existing:
            continue

        # sort largest → smallest
        existing.sort(key=lambda t: t[1], reverse=True)

        # build cards safely
        cards: list[str] = []
        for fname, _ in existing:
            abs_path = os.path.join(folder, fname)
            thumb = thumb_b64(abs_path)
            file_url = f"file://{abs_path}"

            cards.append(
                f'<div class="card">'
                f'<img class="thumb" '
                f'src="data:image/png;base64,{thumb}" '
                f'onclick=\'enlarge({esc_js_str(file_url)})\'>'
                f'<div class="size">{kb(abs_path)} KB</div></div>'
            )

        group_html.append(
            f'<section class="group"><h2>Group {idx} · {len(cards)} file'
            f'{"s" if len(cards)!=1 else ""}</h2><div class="row">'
            f'{"".join(cards)}</div></section>'
        )

    notice = (
        '<p style="color:#9f9">Duplicates were moved to '
        '<code>duplicates/</code></p>'
        if moved
        else ""
    )

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Similar Images</title>
<style>
 body{{margin:0;padding:1rem;background:#333;color:#eee;font-family:Arial,Helvetica,sans-serif}}
 h2{{margin:0 0 .5rem 0;font-size:1.1rem}}
 .group{{border:1px solid #555;border-radius:8px;margin-bottom:1.5rem;padding:1rem}}
 .row{{display:flex;flex-wrap:wrap;gap:12px}}
 .card{{text-align:center;font-size:.8rem}}
 .thumb{{max-width:150px;max-height:150px;border-radius:4px;cursor:zoom-in}}
 .size{{margin-top:.25rem}}
 #overlay{{position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,.85);
          display:none;align-items:center;justify-content:center;z-index:9999}}
 #overlay img{{max-width:95vw;max-height:95vh;border-radius:8px;box-shadow:0 0 20px #000}}
</style></head><body>
<h1>Duplicates grouped — {method.upper()} (thr={threshold})</h1>
{notice}
{''.join(group_html)}
<div id="overlay" onclick="this.style.display='none'"><img></div>
<script>
 function enlarge(src){{const o=document.getElementById('overlay');
   o.style.display='flex';o.querySelector('img').src=src;}}
 window.addEventListener('keydown',e=>e.key==='Escape'&&(
   document.getElementById('overlay').style.display='none'));
</script></body></html>"""


# ─────────────────── main ─────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description="Group / preview / delete duplicates.")
    ap.add_argument("folder", help="Directory with images")
    ap.add_argument("--method", choices=["cnn", "phash"], default="cnn")
    ap.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="CNN: cosine ≥ threshold   |   pHash: Hamming ≤ threshold",
    )
    # Original destructive flag
    ap.add_argument(
        "--delete",
        choices=["keep-largest"],
        help="Move duplicates → duplicates/ and KEEP the largest per group",
    )
    # New alias (identical behaviour)
    ap.add_argument(
        "--move",
        choices=["keep-largest"],
        help="Alias for --delete keep-largest (keeps best quality, moves the rest)",
    )
    args = ap.parse_args()

    folder = os.path.abspath(args.folder)
    if not os.path.isdir(folder):
        sys.exit(f"❌ Not a directory: {folder}")
    print(f"🔍 Scanning {folder}")

    # Duplicate detection
    dupes = (
        dupes_phash(folder, int(args.threshold))
        if args.method == "phash"
        else dupes_cnn(folder, float(args.threshold))
    )
    groups = build_groups(dupes)
    if not groups:
        print("✅ No duplicates found.")
        return

    # Optional move/delete
    moved = 0
    if args.delete or args.move:
        moved = move_dupes(folder, groups, strategy="keep-largest")
        # Remove now-missing files from the groups
        groups = [g for g in groups if any(Path(folder, f).exists() for f in g)]

    # Generate and save HTML in the *same* folder
    html_doc = make_html(groups, folder, args.method, args.threshold, moved)
    out = Path(folder) / "similar_images_preview.html"      # ← changed location
    out.write_text(html_doc, encoding="utf-8")
    print(f"✅ Preview saved → {out}")


if __name__ == "__main__":
    main()
