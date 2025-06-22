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


## Installation


```bash
# 0) Make sure you have **Python 3.11** installed
#    (3.12/3.13 + NumPy 2 break PyTorch and ImageDedup).
pyenv install 3.11.13        # or: brew install python@3.11
pyenv local 3.11.13

# 1) Create & activate a fresh venv
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel

# 2) Install deps with NumPy pinned <2
pip install -r requirements.txt
pip install "numpy<2"  --upgrade
```

> **Why this pin?**  
> ImageDedup & PyTorch wheels are compiled against NumPy 1.x;  
> importing them with NumPy 2.x crashes with `_ARRAY_API not found`.

---

## 🚀 Usage

```bash
# Preview only (pHash, Hamming ≤ 10)
python dedupe.py FOLDER --method phash --threshold 10

# More precise CNN matcher (cosine ≥ 0.88)
python dedupe.py FOLDER --method cnn --threshold 0.88

# Keep the largest in each dup‑set, move the rest → duplicates/
python dedupe.py FOLDER --move keep-largest
# …identical to:
python dedupe.py FOLDER --delete keep-largest
```

_After every run an_ **`similar_images_preview.html`** _is written **inside
the scanned folder**. Open it in your browser to inspect groups._

### CLI flags

| flag / option           | default | meaning                                                            |
| ----------------------- | ------- | ------------------------------------------------------------------ |
| `--method cnn / phash`  | `cnn`   | CNN = MobileNet‑V3 cosine similarity   ·   pHash = perceptual hash |
| `--threshold`           | `0.85`  | CNN ≥ thr   ·   pHash ≤ thr                                        |
| `--move keep-largest`   | –       | move dupes to `duplicates/`, keep biggest                          |
| `--delete keep-largest` | –       | same as `--move` (alias)                                           |

---

## 🖥️ Example workflow

```bash
# 1) Scan & preview
python dedupe.py ~/Pictures/2023_Trip

# 2) Happy with groups? Clean them:
python dedupe.py ~/Pictures/2023_Trip --move keep-largest
```

The preview is automatically regenerated so you can double‑check the cleaned
folder.

---

## 📂 Project layout

```
photo-deduper/
├── dedupe.py        # CLI, HTML generator
├── finder.py        # duplicate detection & grouping
├── delete_logic.py  # move / delete helpers
├── helpers.py       # thumbnails & utils
└── README.md
```

---

## ⚙️ How it works

1. **finder.py**

   - `_list_images()` filters by extension
   - `dupes_cnn()` ‑ MobileNet‑V3 embeddings → cosine similarity
   - `dupes_phash()` ‑ perceptual hash → Hamming distance
   - `build_groups()` converts pairwise matches → connected components

2. **delete_logic.py**

   - Keeps the largest file (by bytes) in each group and moves others to
     `duplicates/`, creating unique names when needed.

3. **dedupe.py**
   - wraps everything into a nice CLI
   - builds an HTML gallery with embedded base‑64 thumbnails
   - simple JS overlay lets you view originals at 1‑click.

---

## ⚠️ Known issues / notes

| issue                                                | workaround                                  |
| ---------------------------------------------------- | ------------------------------------------- |
| Python 3.12/3.13 + NumPy 2.x crash with PyTorch ≥2.1 | stay on **Python 3.11 + `numpy<2`**         |
| Corrupted / non‑image files                          | skipped and logged (_“Found N bad images”_) |
| Groups of size 1                                     | ignored by design                           |
| Thumbnails may fail for exotic RAW/HEIC              | preview still renders (blank square shown)  |

---

## 📝 License

MIT
