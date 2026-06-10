"""timeline / breakdown 备份与恢复（切换聚合方式时可回退）。"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

# 切换 rank0 前默认备份 trimmed_mean 产物
DEFAULT_BACKUP_TAG = "trimmed_mean_duration"

_ARTIFACTS = (
    "breakdown.json",
    "BREAKDOWN.md",
    "timeline.png",
    "timeline_focus.png",
)


def _tag_path(case_dir: Path, name: str, tag: str) -> Path:
    stem, suffix = name.rsplit(".", 1)
    return case_dir / f"{stem}.{tag}.{suffix}"


def backup_timeline_artifacts(case_dir: Path, tag: str = DEFAULT_BACKUP_TAG) -> list[Path]:
    """备份当前 breakdown / timeline；已存在同名备份则跳过。"""
    saved: list[Path] = []
    for name in _ARTIFACTS:
        src = case_dir / name
        if not src.is_file():
            continue
        dst = _tag_path(case_dir, name, tag)
        if dst.is_file():
            continue
        shutil.copy2(src, dst)
        saved.append(dst)
    return saved


def restore_timeline_artifacts(case_dir: Path, tag: str = DEFAULT_BACKUP_TAG) -> list[Path]:
    """从备份恢复 breakdown / timeline。"""
    restored: list[Path] = []
    for name in _ARTIFACTS:
        dst = case_dir / name
        src = _tag_path(case_dir, name, tag)
        if not src.is_file():
            continue
        shutil.copy2(src, dst)
        restored.append(dst)
    return restored


def write_aggregation_marker(case_dir: Path, meta: dict[str, Any]) -> Path:
    fp = case_dir / ".timeline_aggregation.json"
    fp.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return fp


def backup_tag_from_marker(case_dir: Path, default: str = DEFAULT_BACKUP_TAG) -> str:
    """切换前备份 tag：优先用当前 marker 记录的聚合方式。"""
    marker = read_aggregation_marker(case_dir)
    if marker and marker.get("timeline_aggregation"):
        return str(marker["timeline_aggregation"])
    return default


def read_aggregation_marker(case_dir: Path) -> dict[str, Any] | None:
    fp = case_dir / ".timeline_aggregation.json"
    if not fp.is_file():
        return None
    return json.loads(fp.read_text(encoding="utf-8"))


_SWEEP_SUMMARIES = ("summary_timeline.png", "summary_timeline_focus.png")


def backup_sweep_summaries(sweep_dir: Path, tag: str = DEFAULT_BACKUP_TAG) -> list[Path]:
    saved: list[Path] = []
    for name in _SWEEP_SUMMARIES:
        src = sweep_dir / name
        if not src.is_file():
            continue
        dst = _tag_path(sweep_dir, name, tag)
        if dst.is_file():
            continue
        shutil.copy2(src, dst)
        saved.append(dst)
    return saved


def restore_sweep_summaries(sweep_dir: Path, tag: str = DEFAULT_BACKUP_TAG) -> list[Path]:
    restored: list[Path] = []
    for name in _SWEEP_SUMMARIES:
        dst = sweep_dir / name
        src = _tag_path(sweep_dir, name, tag)
        if not src.is_file():
            continue
        shutil.copy2(src, dst)
        restored.append(dst)
    return restored
