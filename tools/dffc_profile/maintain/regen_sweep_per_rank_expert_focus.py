#!/usr/bin/env python3
"""批量重生 sweeps 下各 case 的 per_rank expert_focus 图与 all_ranks mosaic（可并行）。"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from tools.dffc_profile.lib.paths import REPO_ROOT, cli_script, ensure_repo_on_path

ensure_repo_on_path()

PER_RANK_MODE_WALL = "pack_intra_wall"
PER_RANK_MODE_SERIAL = "pack_intra_serial"


def _run(script: str, *argv: str) -> None:
    subprocess.run(
        [sys.executable, str(cli_script(script)), *argv],
        check=True,
        cwd=str(REPO_ROOT),
    )


def iter_case_dirs(root: Path) -> list[Path]:
    """含 rank0_profile.json 的 sweep case 目录。"""
    cases: list[Path] = []
    for ws_dir in sorted(root.glob("ws*")):
        if not ws_dir.is_dir():
            continue
        for axis_dir in sorted(ws_dir.glob("by_*")):
            if not axis_dir.is_dir():
                continue
            for case_dir in sorted(axis_dir.iterdir()):
                if case_dir.is_dir() and (case_dir / "rank0_profile.json").is_file():
                    cases.append(case_dir)
    return cases


def _is_done(case_dir: Path, *, target_mode: str) -> bool:
    fp = case_dir / ".per_rank_timeline_mode.json"
    mosaic = case_dir / "per_rank_timeline" / "all_ranks_expert_focus.png"
    if not fp.is_file() or not mosaic.is_file():
        return False
    try:
        meta = json.loads(fp.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return meta.get("mode") == target_mode


def _write_mode_marker(case_dir: Path, *, pack_aic_intra_phase: bool) -> None:
    fp = case_dir / ".per_rank_timeline_mode.json"
    meta = {
        "pack_aic_intra_phase": pack_aic_intra_phase,
        "mode": PER_RANK_MODE_SERIAL if pack_aic_intra_phase else PER_RANK_MODE_WALL,
    }
    fp.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def _regen_one_case(
    case_dir: Path,
    sweeps_root: Path,
    *,
    pack_aic_intra_phase: bool,
    mosaic_only: bool,
) -> tuple[bool, str]:
    target_mode = PER_RANK_MODE_SERIAL if pack_aic_intra_phase else PER_RANK_MODE_WALL
    rel = str(case_dir.relative_to(sweeps_root))
    try:
        if not mosaic_only:
            argv = ["--case-dir", str(case_dir)]
            if pack_aic_intra_phase:
                argv.append("--pack-aic-intra-phase")
            _run("gen_per_rank_timelines.py", *argv)
        _run("gen_all_ranks_expert_focus_mosaic.py", "--case-dir", str(case_dir))
        _write_mode_marker(case_dir, pack_aic_intra_phase=pack_aic_intra_phase)
        return True, f"{rel} ({target_mode})"
    except subprocess.CalledProcessError as exc:
        return False, f"{rel}: {exc}"


def _worker_task(payload: dict) -> tuple[bool, str]:
    ok, msg = _regen_one_case(
        Path(payload["case_dir"]),
        Path(payload["sweeps_root"]),
        pack_aic_intra_phase=payload["pack_aic_intra_phase"],
        mosaic_only=payload["mosaic_only"],
    )
    return ok, msg


def regen_all(
    sweeps_root: Path,
    *,
    pack_aic_intra_phase: bool = False,
    mosaic_only: bool = False,
    jobs: int = 1,
    skip_done: bool = False,
) -> tuple[int, int]:
    cases = iter_case_dirs(sweeps_root)
    target_mode = PER_RANK_MODE_SERIAL if pack_aic_intra_phase else PER_RANK_MODE_WALL
    if skip_done:
        pending = [c for c in cases if not _is_done(c, target_mode=target_mode)]
        print(f"[regen-per-rank] skip-done: {len(cases) - len(pending)} already {target_mode}")
        cases = pending
    if not cases:
        return 0, 0

    payloads = [
        {
            "case_dir": str(c),
            "sweeps_root": str(sweeps_root),
            "pack_aic_intra_phase": pack_aic_intra_phase,
            "mosaic_only": mosaic_only,
        }
        for c in cases
    ]

    ok, skip = 0, 0
    if jobs <= 1:
        for p in payloads:
            success, msg = _worker_task(p)
            if success:
                ok += 1
                print(f"[regen-per-rank] {msg}", flush=True)
            else:
                skip += 1
                print(f"[regen-per-rank] FAIL {msg}", file=sys.stderr, flush=True)
    else:
        print(f"[regen-per-rank] parallel jobs={jobs} cases={len(payloads)}", flush=True)
        with ProcessPoolExecutor(max_workers=jobs) as pool:
            futures = {pool.submit(_worker_task, p): p for p in payloads}
            for fut in as_completed(futures):
                success, msg = fut.result()
                if success:
                    ok += 1
                    print(f"[regen-per-rank] {msg}", flush=True)
                else:
                    skip += 1
                    print(f"[regen-per-rank] FAIL {msg}", file=sys.stderr, flush=True)
    return ok, skip


def main() -> int:
    parser = argparse.ArgumentParser(description="批量重生 per_rank expert_focus + mosaic")
    parser.add_argument("--sweeps-root", type=Path, default=REPO_ROOT / "results" / "sweeps")
    parser.add_argument(
        "--pack-aic-intra-phase",
        action="store_true",
        help="阶段内串行摆条（旧逻辑）；默认阶段内墙钟起点",
    )
    parser.add_argument("--mosaic-only", action="store_true", help="仅重拼 all_ranks mosaic")
    parser.add_argument("-j", "--jobs", type=int, default=None, help="并行 case 数（默认 min(64, CPU)）")
    parser.add_argument("--skip-done", action="store_true", help="跳过已有目标 mode marker 的 case")
    args = parser.parse_args()

    root = args.sweeps_root if args.sweeps_root.is_absolute() else REPO_ROOT / args.sweeps_root
    jobs = args.jobs if args.jobs is not None else min(64, os.cpu_count() or 8)

    ok, skip = regen_all(
        root,
        pack_aic_intra_phase=args.pack_aic_intra_phase,
        mosaic_only=args.mosaic_only,
        jobs=jobs,
        skip_done=args.skip_done,
    )
    mode = PER_RANK_MODE_SERIAL if args.pack_aic_intra_phase else PER_RANK_MODE_WALL
    print(f"[regen-per-rank] finished {ok} ok, {skip} skipped, mode={mode}, jobs={jobs}")
    return 0 if skip == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
