from __future__ import annotations
import base64, os, warnings
from io import BytesIO
from pathlib import Path
from typing import Tuple

from PIL import Image


def kb(path: str | Path) -> int:
    """Return file size in KB (rounded)."""
    return round(os.path.getsize(path) / 1024)


def thumb_b64(path: str | Path, size: Tuple[int, int] = (150, 150)) -> str:
    """Return base-64 thumbnail for inline <img> tags."""
    try:
        img = Image.open(path)
        img.thumbnail(size)
        buf = BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as exc:  # noqa: BLE001
        warnings.warn(f"Thumbnail failed for {path}: {exc}")
        return ""
