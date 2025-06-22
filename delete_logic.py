from __future__ import annotations
import os, shutil
from pathlib import Path
from typing import List, Set


def move_dupes(
    folder: str,
    groups: List[Set[str]],
    strategy: str = "keep-largest",
) -> int:
    """
    Move duplicates to <folder>/duplicates/, keeping the first (largest) image.
    Returns number of files moved.
    """
    dup_dir = Path(folder) / "duplicates"
    dup_dir.mkdir(exist_ok=True)

    moved = 0
    for grp in groups:
        sorted_files = sorted(
            grp, key=lambda f: os.path.getsize(os.path.join(folder, f)), reverse=True
        )
        keep = sorted_files[0] if strategy == "keep-largest" else None
        for f in sorted_files:
            if f == keep:
                continue
            src = Path(folder) / f
            dst = dup_dir / f
            # avoid name collision
            if dst.exists():
                dst = dup_dir / f"{dst.stem}_{moved}{dst.suffix}"
            shutil.move(src, dst)
            moved += 1
    return moved
