#!/usr/bin/env python3
"""Optimize source images into site-ready derivatives."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps

from tools.site_framework import STATIC_DIR


ORIGINALS_DIR = STATIC_DIR / "images" / "originals"
OUTPUT_IMAGES_DIR = STATIC_DIR / "images"
SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_WIDTHS = (600, 900, 1200)
DEFAULT_MAX_WIDTH = 1600
WEBP_QUALITY = 82
JPEG_QUALITY = 85


@dataclass(frozen=True)
class OptimizedImage:
    source: Path
    outputs: tuple[Path, ...]


def iter_originals(source_dir: Path = ORIGINALS_DIR) -> list[Path]:
    if not source_dir.exists():
        return []

    return [
        path
        for path in sorted(source_dir.rglob("*"))
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    ]


def needs_update(source: Path, destination: Path, *, force: bool) -> bool:
    return force or not destination.exists() or source.stat().st_mtime > destination.stat().st_mtime


def target_stem(source: Path, source_dir: Path = ORIGINALS_DIR) -> Path:
    relative = source.relative_to(source_dir).with_suffix("")
    return OUTPUT_IMAGES_DIR / relative


def resized(image: Image.Image, width: int) -> Image.Image:
    if image.width <= width:
        return image.copy()

    height = round(image.height * (width / image.width))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def flatten_for_jpeg(image: Image.Image) -> Image.Image:
    if image.mode in {"RGBA", "LA"} or (image.mode == "P" and "transparency" in image.info):
        background = Image.new("RGB", image.size, "white")
        background.paste(image.convert("RGBA"), mask=image.convert("RGBA").getchannel("A"))
        return background

    return image.convert("RGB")


def save_webp(image: Image.Image, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "WEBP", quality=WEBP_QUALITY, method=6)


def save_jpeg(image: Image.Image, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    flatten_for_jpeg(image).save(destination, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)


def optimize_one(
    source: Path,
    *,
    widths: tuple[int, ...] = DEFAULT_WIDTHS,
    max_width: int = DEFAULT_MAX_WIDTH,
    force: bool = False,
) -> OptimizedImage:
    stem = target_stem(source)
    outputs: list[Path] = []

    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened)
        base_width = min(image.width, max_width)
        variants = [(base_width, "")]
        variants.extend((width, f"_{width}w") for width in widths if width < base_width)

        for width, suffix in variants:
            variant = resized(image, width)
            webp_path = stem.with_name(f"{stem.name}{suffix}.webp")
            jpg_path = stem.with_name(f"{stem.name}{suffix}.jpg")

            if needs_update(source, webp_path, force=force):
                save_webp(variant, webp_path)
            if needs_update(source, jpg_path, force=force):
                save_jpeg(variant, jpg_path)

            outputs.extend([webp_path, jpg_path])

    return OptimizedImage(source=source, outputs=tuple(outputs))


def optimize_all(*, force: bool = False) -> list[OptimizedImage]:
    return [optimize_one(path, force=force) for path in iter_originals()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Optimize static image originals into publishable assets")
    parser.add_argument("--force", action="store_true", help="Regenerate derivatives even when outputs are current")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = optimize_all(force=args.force)

    if not results:
        print("No image originals found; skipping optimization")
        return 0

    output_count = sum(len(result.outputs) for result in results)
    print(f"Optimized {len(results)} image original(s), {output_count} derivative file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
