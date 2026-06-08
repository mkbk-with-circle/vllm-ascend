#!/usr/bin/env python3
"""将单 case 各 rank 的 timeline_expert_focus.png 拼成一张高清大图。"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from tools.dffc_profile.lib.paths import DFFC_ROOT, REPO_ROOT, ensure_repo_on_path, script_path

ensure_repo_on_path()

IMAGE_NAME = "timeline_expert_focus.png"
OUT_NAME = "all_ranks_expert_focus.png"
_RANK_DIR_RE = re.compile(r"^rank(\d+)$")

# 常见 Linux 字体路径
_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/google-noto/NotoSansCJK-Bold.ttc",
)


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for fp in _FONT_CANDIDATES:
        p = Path(fp)
        if p.is_file():
            try:
                return ImageFont.truetype(str(p), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def _collect_rank_images(case_dir: Path) -> list[tuple[int, Path]]:
    pr = case_dir / "per_rank_timeline"
    if not pr.is_dir():
        return []
    out: list[tuple[int, Path]] = []
    for rank_dir in pr.iterdir():
        if not rank_dir.is_dir():
            continue
        m = _RANK_DIR_RE.match(rank_dir.name)
        if not m:
            continue
        img = rank_dir / IMAGE_NAME
        if img.is_file():
            out.append((int(m.group(1)), img))
    out.sort(key=lambda x: x[0])
    return out


def _grid_shape(n: int, ncol_max: int) -> tuple[int, int]:
    if n <= 0:
        return 0, 0
    ncol = min(ncol_max, max(1, math.ceil(math.sqrt(n))))
    if n > ncol_max and n <= ncol_max * 2:
        ncol = ncol_max
    nrow = math.ceil(n / ncol)
    return nrow, ncol


def compose_case_mosaic(
    case_dir: Path,
    *,
    ncol_max: int = 4,
    pad: int = 12,
    label_h: int = 52,
    font_size: int = 40,
    border: int = 3,
) -> Path | None:
    """拼接并写入 per_rank_timeline/all_ranks_expert_focus.png。"""
    ranks = _collect_rank_images(case_dir)
    if not ranks:
        return None

    images: list[tuple[int, Image.Image]] = []
    for rank, path in ranks:
        im = Image.open(path)
        # 统一为 RGB，保留原始像素（各 rank 宽可能差数个像素）
        if im.mode != "RGB":
            im = im.convert("RGB")
        images.append((rank, im))

    w = max(im.size[0] for _, im in images)
    h = max(im.size[1] for _, im in images)

    n = len(images)
    nrow, ncol = _grid_shape(n, ncol_max)
    font = _load_font(font_size)

    cell_w = w + 2 * pad
    cell_h = label_h + h + 2 * pad
    canvas_w = ncol * cell_w
    canvas_h = nrow * cell_h
    canvas = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    for idx, (rank, im) in enumerate(images):
        r, c = divmod(idx, ncol)
        x0 = c * cell_w + pad
        y0 = r * cell_h + label_h + pad
        canvas.paste(im, (x0, y0))
        label = f"rank {rank}"
        # 标签背景条，提升可读性
        lx = c * cell_w
        ly = r * cell_h
        draw.rectangle([lx, ly, lx + cell_w - 1, ly + label_h - 4], fill=(245, 245, 250))
        draw.rectangle([lx, ly + label_h - 4, lx + cell_w - 1, ly + label_h], fill=(80, 80, 100))
        draw.text((lx + pad, ly + 6), label, fill=(20, 20, 30), font=font)
        # 细边框
        draw.rectangle(
            [x0 - border, y0 - border, x0 + w + border - 1, y0 + h + border - 1],
            outline=(180, 180, 190),
            width=border,
        )

    out_path = case_dir / "per_rank_timeline" / OUT_NAME
    # compress_level=1：大 PNG 体积与清晰度折中
    canvas.save(out_path, format="PNG", compress_level=1)
    return out_path


def iter_case_dirs(root: Path) -> list[Path]:
    """遍历 sweeps 下含 per_rank_timeline 的 case 目录。"""
    cases: list[Path] = []
    for ws_dir in sorted(root.glob("ws*")):
        if not ws_dir.is_dir():
            continue
        for axis_dir in sorted(ws_dir.glob("by_*")):
            if not axis_dir.is_dir():
                continue
            for case_dir in sorted(axis_dir.iterdir()):
                if case_dir.is_dir() and (case_dir / "per_rank_timeline").is_dir():
                    cases.append(case_dir)
    return cases


def iter_debug_dirs(debug_root: Path) -> list[Path]:
    """遍历 results/debug/{slug}/{baseline|barrier_v11}/ 含 per_rank_timeline 的目录。"""
    cases: list[Path] = []
    if not debug_root.is_dir():
        return cases
    for slug_dir in sorted(debug_root.iterdir()):
        if not slug_dir.is_dir():
            continue
        for sub in ("baseline", "barrier_v11"):
            case_dir = slug_dir / sub
            if (case_dir / "per_rank_timeline").is_dir():
                cases.append(case_dir)
    return cases


def main() -> int:
    parser = argparse.ArgumentParser(description="各 rank expert_focus 拼图")
    parser.add_argument(
        "--sweeps-root",
        type=Path,
        default=REPO_ROOT / "results" / "sweeps",
    )
    parser.add_argument(
        "--debug-root",
        type=Path,
        default=None,
        help="results/debug：为各 slug 下 baseline/barrier_v11 拼图",
    )
    parser.add_argument("--case-dir", type=Path, default=None, help="仅处理单个 case")
    parser.add_argument("--ncol-max", type=int, default=4)
    parser.add_argument("--font-size", type=int, default=40)
    args = parser.parse_args()

    if args.case_dir is not None:
        case_dirs = [args.case_dir if args.case_dir.is_absolute() else REPO_ROOT / args.case_dir]
    elif args.debug_root is not None:
        root = args.debug_root if args.debug_root.is_absolute() else REPO_ROOT / args.debug_root
        case_dirs = iter_debug_dirs(root)
    else:
        root = args.sweeps_root if args.sweeps_root.is_absolute() else REPO_ROOT / args.sweeps_root
        case_dirs = iter_case_dirs(root)

    ok, skip = 0, 0
    for case_dir in case_dirs:
        case_dir = case_dir.resolve()
        try:
            out = compose_case_mosaic(
                case_dir,
                ncol_max=args.ncol_max,
                font_size=args.font_size,
            )
        except Exception as exc:
            print(f"[mosaic] FAIL {case_dir.name}: {exc}", file=sys.stderr)
            continue
        if out is None:
            skip += 1
            continue
        ok += 1
        print(f"[mosaic] {out} ({out.stat().st_size // 1024} KB)")

    print(f"[mosaic] done {ok} cases, skipped {skip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
