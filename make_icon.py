#!/usr/bin/env python3
"""Generate Notebook Importer.icns from scratch using Pillow."""

import subprocess
import shutil
from pathlib import Path
from PIL import Image, ImageDraw

SIZES = [16, 32, 64, 128, 256, 512, 1024]


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size

    # Background: Jupyter orange
    bg_color = (210, 100, 20, 255)
    r = s * 0.22
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=r, fill=bg_color)

    # Notebook body (white, portrait)
    doc_x0 = s * 0.20
    doc_y0 = s * 0.12
    doc_x1 = s * 0.74
    doc_y1 = s * 0.80
    fold = s * 0.15
    doc_color = (255, 255, 255, 255)
    pts = [
        (doc_x0, doc_y0),
        (doc_x1 - fold, doc_y0),
        (doc_x1, doc_y0 + fold),
        (doc_x1, doc_y1),
        (doc_x0, doc_y1),
    ]
    d.polygon(pts, fill=doc_color)

    # Fold triangle
    fold_color = (240, 200, 160, 255)
    fold_pts = [
        (doc_x1 - fold, doc_y0),
        (doc_x1, doc_y0 + fold),
        (doc_x1 - fold, doc_y0 + fold),
    ]
    d.polygon(fold_pts, fill=fold_color)

    # Spine bar on left edge (notebook look)
    spine_w = s * 0.06
    spine_color = (220, 120, 30, 255)
    d.rectangle([doc_x0, doc_y0, doc_x0 + spine_w, doc_y1], fill=spine_color)

    # Code-style lines: alternating lengths with a colored "keyword" block
    line_x0 = doc_x0 + spine_w + s * 0.05
    line_x1_full = doc_x1 - s * 0.08
    lh = s * 0.048
    gap = s * 0.038
    line_color = (180, 130, 80, 255)
    keyword_color = (210, 100, 20, 200)

    y = doc_y0 + s * 0.16
    line_configs = [
        (0.35, True),   # short keyword block
        (0.80, False),
        (0.60, False),
        (0.45, True),   # short keyword block
        (0.70, False),
    ]
    for frac, is_keyword in line_configs:
        x1 = line_x0 + (line_x1_full - line_x0) * frac
        color = keyword_color if is_keyword else line_color
        d.rounded_rectangle([line_x0, y, x1, y + lh], radius=lh / 2, fill=color)
        y += lh + gap

    # Arrow (right-pointing, bottom-right, white)
    ax = s * 0.70
    ay = s * 0.62
    aw = s * 0.20
    ah = s * 0.18
    arrow_color = (255, 255, 255, 220)
    shaft_h = ah * 0.40
    shaft_y0 = ay + (ah - shaft_h) / 2
    shaft_y1 = shaft_y0 + shaft_h
    head_w = aw * 0.42
    shaft_x1 = ax + aw - head_w
    d.rectangle([ax, shaft_y0, shaft_x1, shaft_y1], fill=arrow_color)
    d.polygon([(shaft_x1, ay), (ax + aw, ay + ah / 2), (shaft_x1, ay + ah)], fill=arrow_color)

    return img


def make_icns(out_path: Path):
    iconset = out_path.with_suffix(".iconset")
    iconset.mkdir(exist_ok=True)

    for size in SIZES:
        img = draw_icon(size)
        img.save(iconset / f"icon_{size}x{size}.png")
        if size <= 512:
            img2 = draw_icon(size * 2)
            img2.save(iconset / f"icon_{size}x{size}@2x.png")

    subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(out_path)], check=True)
    shutil.rmtree(iconset)
    print(f"Created {out_path}")


if __name__ == "__main__":
    here = Path(__file__).parent
    make_icns(here / "icon.icns")
