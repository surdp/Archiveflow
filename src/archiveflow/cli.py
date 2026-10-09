"""Command-line tools for inspecting and organizing a local media export."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import shutil
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Iterable, Iterator

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".heif",
    ".avif", ".bmp", ".tif", ".tiff",
}
VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".m4v", ".webm", ".avi", ".3gp", ".mkv", ".mpeg", ".mpg",
}
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


@dataclass(frozen=True)
class MediaItem:
    source_path: str
    filename: str
    extension: str
    category: str
    size_bytes: int


def category_for(extension: str) -> str | None:
    ext = extension.lower()
    if ext in IMAGE_EXTENSIONS:
        return "images"
    if ext in VIDEO_EXTENSIONS:
        return "videos"
    return None


def _zip_items(path: Path) -> Iterator[MediaItem]:
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            name = info.filename.replace("\\", "/")
            filename = PurePosixPath(name).name
            category = category_for(Path(filename).suffix)
            if not category:
                continue
            yield MediaItem(name, filename, Path(filename).suffix.lower(), category, info.file_size)


def _folder_items(path: Path, excluded_output: Path | None = None) -> Iterator[MediaItem]:
    base = path.resolve()
    excluded = excluded_output.resolve() if excluded_output else None
    for current, dirs, files in os.walk(base):
        current_path = Path(current).resolve()
        # Do not re-scan generated output when it lives under the input directory.
        if excluded and (current_path == excluded or excluded in current_path.parents):
            dirs[:] = []
            continue
        # Prune the output folder before descending into it.
        if excluded:
            dirs[:] = [d for d in dirs if (current_path / d).resolve() != excluded and excluded not in (current_path / d).resolve().parents]
        for filename in files:
            file_path = current_path / filename
            category = category_for(file_path.suffix)
            if not category:
                continue
            try:
                size = file_path.stat().st_size
            except OSError:
                continue
            yield MediaItem(file_path.relative_to(base).as_posix(), filename, file_path.suffix.lower(), category, size)


def iter_media(input_path: Path, excluded_output: Path | None = None) -> Iterator[MediaItem]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")
    if input_path.is_file() and zipfile.is_zipfile(input_path):
        yield from _zip_items(input_path)
        return
    if input_path.is_dir():
        yield from _folder_items(input_path, excluded_output)
        return
    if input_path.is_file():
        raise ValueError("Input file must be a ZIP archive, or a directory of extracted files.")
    raise ValueError("Input must be a ZIP archive or an extracted directory.")


def _size_label(size: int) -> str:
    amount = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if amount < 1024 or unit == "TB":
            return f"{amount:.1f} {unit}" if unit != "B" else f"{int(amount)} B"
        amount /= 1024
    return f"{size} B"


def inspect_source(input_path: Path) -> int:
    items = list(iter_media(input_path))
    if not items:
        print("No supported image or video files were found.")
        print("The export layout may use different formats, or the selected ZIP/folder may not contain media.")
        return 0
    by_ext = Counter(item.extension for item in items)
    by_cat = Counter(item.category for item in items)
    total_bytes = sum(item.size_bytes for item in items)
    print(f"Input: {input_path}")
    print(f"Supported media files: {len(items)}")
    print(f"Images: {by_cat['images']} | Videos: {by_cat['videos']}")
    print(f"Estimated total media size: {_size_label(total_bytes)}")
    print("\nBy extension:")
    for ext, count in sorted(by_ext.items()):
        print(f"  {ext or '[no extension]':8} {count:>6}")
    return len(items)


def _safe_stem(source_path: str, filename: str) -> str:
    """Make collisions unlikely while avoiding writing source path components."""
    path_hash = hashlib.sha256(source_path.encode("utf-8", errors="replace")).hexdigest()[:10]
    stem = Path(filename).stem
    safe_stem = "".join(ch if ch.isalnum() or ch in "-_ ." else "_" for ch in stem).strip(" .") or "media"
    return f"{safe_stem[:100]}_{path_hash}{Path(filename).suffix.lower()}"


def _open_source(input_path: Path, item: MediaItem) -> BinaryIO:
    if input_path.is_file() and zipfile.is_zipfile(input_path):
        # Open the specific zip member through the organizer's context below instead.
        raise RuntimeError("ZIP members are opened via ZipFile.open.")
    return (input_path / Path(item.source_path)).open("rb")


def organize_source(input_path: Path, output_path: Path, dry_run: bool = False) -> tuple[int, int]:
    if input_path.resolve() == output_path.resolve() or input_path.resolve() in output_path.resolve().parents:
        # Output inside input is allowed only for directory inputs and is excluded from scanning.
        if not input_path.is_dir():
            raise ValueError("Output folder cannot be the input ZIP file or a child of it.")
    items = list(iter_media(input_path, excluded_output=output_path if input_path.is_dir() else None))
    print(f"Found {len(items)} supported media file(s).")
    if not items:
        print("Nothing to copy. No output files were created.")
        return 0, 0
    if dry_run:
        for item in items[:25]:
            name = _safe_stem(item.source_path, item.filename)
            print(f"[DRY RUN] {item.source_path} -> {item.category}/{name} ({_size_label(item.size_bytes)})")
        if len(items) > 25:
            print(f"... and {len(items) - 25} more file(s).")
        print(f"\nDry run only. Planned output: {output_path}")
        return len(items), 0

    output_path.mkdir(parents=True, exist_ok=True)
    manifest_path = output_path / "manifest.csv"
    rows: list[dict[str, str | int]] = []
    copied = 0
    hashes = set()

    if input_path.is_file() and zipfile.is_zipfile(input_path):
        with zipfile.ZipFile(input_path) as archive:
            for item in items:
                out_name = _safe_stem(item.source_path, item.filename)
                out_path = output_path / item.category / out_name
                out_path.parent.mkdir(parents=True, exist_ok=True)
                digest = hashlib.sha256()
                with archive.open(item.source_path, "r") as src, out_path.open("wb") as dst:
                    while True:
                        chunk = src.read(1024 * 1024)
                        if not chunk:
                            break
                        digest.update(chunk)
                        dst.write(chunk)
                file_hash = digest.hexdigest()
                hashes.add(file_hash)
                rows.append({
                    "source_path": item.source_path,
                    "category": item.category,
                    "output_path": f"{item.category}/{out_name}",
                    "extension": item.extension,
                    "size_bytes": item.size_bytes,
                    "sha256": file_hash,
                })
                copied += 1
    else:
        base = input_path.resolve()
        for item in items:
            source = base / Path(item.source_path)
            out_name = _safe_stem(item.source_path, item.filename)
            out_path = output_path / item.category / out_name
            out_path.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            with source.open("rb") as src, out_path.open("wb") as dst:
                while True:
                    chunk = src.read(1024 * 1024)
                    if not chunk:
                        break
                    digest.update(chunk)
                    dst.write(chunk)
            file_hash = digest.hexdigest()
            hashes.add(file_hash)
            rows.append({
                "source_path": item.source_path,
                "category": item.category,
                "output_path": f"{item.category}/{out_name}",
                "extension": item.extension,
                "size_bytes": item.size_bytes,
                "sha256": file_hash,
            })
            copied += 1

    with manifest_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_path", "category", "output_path", "extension", "size_bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Copied: {copied} file(s)")
    print(f"Unique SHA-256 content hashes: {len(hashes)} (identical contents may still exist as separate copies)")
    print(f"Images: {sum(1 for item in items if item.category == 'images')} | Videos: {sum(1 for item in items if item.category == 'videos')}")
    print(f"Manifest: {manifest_path}")
    print(f"Output: {output_path}")
    return copied, len(hashes)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="archiveflow", description="Organize media from a local export ZIP or extracted folder.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subparsers.add_parser("inspect", help="count supported media by extension")
    inspect_parser.add_argument("input", help="path to export ZIP or extracted directory")
    organize_parser = subparsers.add_parser("organize", help="copy detected photos/videos and write a CSV manifest")
    organize_parser.add_argument("input", help="path to export ZIP or extracted directory")
    organize_parser.add_argument("--output", required=True, help="destination folder for organized copies")
    organize_parser.add_argument("--dry-run", action="store_true", help="preview the planned copies without writing files")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        input_path = Path(args.input).expanduser()
        if args.command == "inspect":
            inspect_source(input_path)
            return 0
        output_path = Path(args.output).expanduser()
        organize_source(input_path, output_path, dry_run=args.dry_run)
        return 0
    except (OSError, zipfile.BadZipFile, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
