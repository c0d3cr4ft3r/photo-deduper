from __future__ import annotations

import logging
import os
from collections import defaultdict, deque
from typing import Dict, List, Set

from imagededup.methods import CNN, PHash

# Silence INFO from imagededup
logging.getLogger("imagededup").setLevel(logging.ERROR)

# ───────────── accepted image extensions ──────────────
_ALLOWED_EXTS = {
    ".jpg", ".jpeg", ".png", ".gif",
    ".bmp", ".tif", ".tiff", ".webp", ".heic",
}


def _list_images(folder: str) -> List[str]:
    """Return filenames in *folder* whose extension looks like an image."""
    return [
        f
        for f in os.listdir(folder)
        if not f.startswith(".")
        and os.path.splitext(f)[1].lower() in _ALLOWED_EXTS
    ]


# ――――――― find duplicates ――――――― #
def dupes_cnn(folder: str, thr: float) -> Dict[str, List[str]]:
    """
    CNN-based near-duplicate search.
    Uses imagededup’s own encoder; bails early if no images.
    """
    if not _list_images(folder):
        return {}

    d = CNN(verbose=False)
    enc = d.encode_images(image_dir=folder)  # library handles filtering/flattening
    raw = d.find_duplicates(encoding_map=enc, scores=True)

    # keep only matches whose cosine similarity ≥ `thr`
    return {k: [m for m, s in v if s >= thr] for k, v in raw.items()}


def dupes_phash(folder: str, max_dist: int) -> Dict[str, List[str]]:
    """
    Perceptual-hash duplicate search (Hamming distance ≤ `max_dist`).
    """
    if not _list_images(folder):
        return {}

    # imagededup’s PHash already ignores non-image files
    return PHash().find_duplicates(
        image_dir=folder,
        max_distance_threshold=max_dist,
    )


# ――――――― group duplicates (connected components) ――――――― #
def build_groups(duplicates: Dict[str, List[str]]) -> List[Set[str]]:
    """
    Convert the *pairwise* duplicate mapping into connected-component groups.
    """
    adj: Dict[str, Set[str]] = defaultdict(set)
    for a, matches in duplicates.items():
        for b in matches:
            adj[a].add(b)
            adj[b].add(a)

    seen: Set[str] = set()
    groups: List[Set[str]] = []

    for node in adj:
        if node in seen:
            continue
        comp, dq = set(), deque([node])
        while dq:
            n = dq.popleft()
            if n in seen:
                continue
            seen.add(n)
            comp.add(n)
            dq.extend(adj[n] - seen)
        if len(comp) > 1:  # ignore singletons
            groups.append(comp)

    return groups
