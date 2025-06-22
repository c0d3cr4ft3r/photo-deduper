# Photo Deduper – Project Documentation

## Overview

**photo-deduper** is a command-line Python utility that helps identify and manage visually similar or duplicate images in a folder. It supports two algorithms (CNN and pHash) to detect duplicates, groups them intelligently, and generates an interactive HTML gallery for preview. Optionally, it can move lower-quality images to a `duplicates/` subfolder.

---

## Features

- 📷 **Detect duplicates** using:
  - **CNN (Convolutional Neural Network)** – cosine similarity-based.
  - **pHash (Perceptual Hashing)** – Hamming distance-based.
- 📊 **HTML preview** of groups with thumbnails and file sizes.
- 🧹 **Auto-cleanup** by moving duplicates and keeping the best-quality file.
- 🖼️ **Embedded thumbnails** using base64 in a local preview.
- 🔍 **Works locally** with any image directory.

---

## Installation

### Requirements

- Python 3.8+
- Dependencies:
  - `imagededup`
  - `Pillow`

Install dependencies:

```bash
pip install imagededup pillow
```

---

## Usage

### Preview Only

```bash
python dedupe.py /path/to/images --method phash --threshold 10
```

### Auto-Move Duplicates

```bash
python dedupe.py /path/to/images --delete keep-largest
```

### Options

| Flag          | Description                                                    |
| ------------- | -------------------------------------------------------------- |
| `--method`    | `cnn` (default) or `phash`                                     |
| `--threshold` | CNN: cosine ≥ value (e.g., `0.85`) <br> pHash: Hamming ≤ value |
| `--delete`    | Deletes all but largest image in each group                    |
| `--move`      | Alias for `--delete keep-largest`                              |

---

## Output

- **HTML Preview**: `similar_images_preview.html` created in the same folder.
- **Duplicate Files**: moved to `duplicates/` subfolder when `--delete` or `--move` is used.

---

## Project Structure

```
photo-deduper/
├── dedupe.py           # Main CLI script
├── finder.py           # Duplicate detection and grouping logic
├── delete_logic.py     # File-moving logic for cleaning duplicates
└── helpers.py          # Thumbnail generation and utilities
```

---

## How It Works

### 1. Duplicate Detection (`finder.py`)

- `_list_images(folder)` filters valid image files.
- `dupes_cnn(folder, thr)`:
  - Uses cosine similarity via `imagededup.methods.CNN`.
- `dupes_phash(folder, max_dist)`:
  - Uses Hamming distance via `imagededup.methods.PHash`.
- `build_groups()`:
  - Converts flat pairwise matches into connected component groups.

### 2. Duplicate Cleanup (`delete_logic.py`)

- `move_dupes()`:
  - Sorts files by size, keeps the largest.
  - Moves all others to `duplicates/`.

### 3. HTML Output (`dedupe.py`)

- Generates an HTML page with thumbnail previews for each group.
- Uses `thumb_b64()` to embed thumbnails directly (base64).
- Interactive viewer with `onclick` zoom.

---

## Helper Utilities (`helpers.py`)

- `kb(path)`: returns image size in kilobytes.
- `thumb_b64(path)`: returns base64 PNG thumbnail (150×150 px).
- Built with `Pillow` for image resizing and encoding.

---

## Example HTML Output

Each group is displayed in a styled section:

- Group number
- Thumbnail previews
- File size below each image
- Click to enlarge (JS overlay)
- Esc to dismiss enlarged image

---

## Caveats and Notes

- Only standard image formats are supported (`.jpg`, `.png`, `.gif`, `.heic`, etc.).
- You can adjust similarity threshold (`--threshold`) to tune detection sensitivity.
- Groups with only one image (no real duplicates) are excluded.

---

## License

MIT License (add LICENSE file separately if needed)
