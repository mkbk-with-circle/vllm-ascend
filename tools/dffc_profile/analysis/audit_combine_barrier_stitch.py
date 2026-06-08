#!/usr/bin/env python3
"""审计 combine expert 拼接缝：wall_end[e] vs barrier_begin[e+1]（tail_gap）。"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any

from tools.dffc_profile.lib.paths import DFFC_ROOT, REPO_ROOT, ensure_repo_on_path, script_path

ensure_repo_on_path()

from tools.dffc_profile.lib.profile_constants import DFFC_PROFILE_VERSION

_WS_RE = re.compile(r"/ws(\d+)/")
_TAIL_PASS_US_DEFAULT = 2  # tail_gap 不超过此值视为 stitch 正常


def _world_size_from_path(case_dir: Path) -> int | None:
    m = _WS_RE.search(case_dir.as_posix())
    return int(m.group(1)) if m else None


def _load_profiles(case_dir: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in sorted(case_dir.glob("rank*_profile.json")):
        out.append(json.loads(p.read_text(encoding="utf-8")))
    return out


def _stitch_stats_for_rank(profile: dict[str, Any], *, tail_pass_us: float) -> dict[str, Any] | None:
    segs = sorted(
        (profile.get("expert_segments") or {}).get("combine") or [],
        key=lambda s: int(s.get("expert", 0)),
    )
    if len(segs) < 2:
        return None
    tails: list[float] = []
    barrier_ws: list[float] = []
    head_mm: list[float] = []
    for i in range(1, len(segs)):
        prev, cur = segs[i - 1], segs[i]
        pwe = float(prev.get("wall_end_us", 0))
        bb = cur.get("barrier_begin_us")
        be = cur.get("barrier_end_us")
        wb = float(cur.get("wall_begin_us", 0))
        if bb is None:
            return None
        bb_f = float(bb)
        tails.append(bb_f - pwe)
        if be is not None:
            be_f = float(be)
            if be_f > bb_f:
                barrier_ws.append(be_f - bb_f)
            head_mm.append(wb - be_f)
    if not tails:
        return None
    return {
        "rank": int(profile.get("rank", -1)),
        "n_transitions": len(tails),
        "tail_min": min(tails),
        "tail_max": max(tails),
        "tail_median": statistics.median(tails),
        "barrier_w_median": statistics.median(barrier_ws) if barrier_ws else 0.0,
        "head_mm_max": max(abs(x) for x in head_mm) if head_mm else 0.0,
        "pass": max(tails) <= tail_pass_us,
    }


def audit_case_dir(case_dir: Path, *, tail_pass_us: float = _TAIL_PASS_US_DEFAULT) -> dict[str, Any]:
    profiles = _load_profiles(case_dir)
    if not profiles:
        return {"path": str(case_dir), "error": "no rank*_profile.json"}
    ver = int(profiles[0].get("version", 0))
    rank_stats: list[dict[str, Any]] = []
    missing_barrier = False
    for p in profiles:
        st = _stitch_stats_for_rank(p, tail_pass_us=tail_pass_us)
        if st is None:
            missing_barrier = True
            continue
        rank_stats.append(st)
    all_tails: list[float] = []
    for st in rank_stats:
        all_tails.extend([st["tail_min"], st["tail_max"], st["tail_median"]])
    case_pass = bool(rank_stats) and all(st["pass"] for st in rank_stats) and not missing_barrier
    return {
        "path": str(case_dir.relative_to(REPO_ROOT) if case_dir.is_relative_to(REPO_ROOT) else case_dir),
        "world_size": _world_size_from_path(case_dir),
        "version": ver,
        "version_ok": ver >= DFFC_PROFILE_VERSION,
        "n_ranks": len(profiles),
        "n_ranks_audited": len(rank_stats),
        "missing_barrier": missing_barrier,
        "tail_gap_max": max(all_tails) if all_tails else None,
        "tail_gap_median": statistics.median(all_tails) if all_tails else None,
        "pass": case_pass,
        "ranks": rank_stats,
    }


def discover_case_dirs(sweeps_root: Path) -> list[Path]:
    dirs: list[Path] = []
    for case_json in sorted(sweeps_root.rglob("case.json")):
        d = case_json.parent
        if (d / "rank0_profile.json").is_file():
            dirs.append(d)
    return dirs


def _md_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| case | ws | ver | ranks | tail_med | tail_max | barrier_med | pass |",
        "|------|----|----|-------|----------|----------|-------------|------|",
    ]
    for r in rows:
        if r.get("error"):
            lines.append(f"| `{r['path']}` | ? | ? | 0 | — | — | — | ERR |")
            continue
        # 取 rank0 barrier 中位作代表
        rs = r.get("ranks") or []
        r0 = next((x for x in rs if x.get("rank") == 0), rs[0] if rs else {})
        bw = r0.get("barrier_w_median", 0)
        slug = Path(r["path"]).name[:48]
        lines.append(
            f"| `{slug}` | {r.get('world_size','?')} | {r.get('version','?')} | "
            f"{r.get('n_ranks_audited',0)}/{r.get('n_ranks',0)} | "
            f"{r.get('tail_gap_median',0):.1f} | {r.get('tail_gap_max',0):.1f} | "
            f"{bw:.0f} | {'Y' if r.get('pass') else 'N'} |"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="审计 combine barrier 拼接缝 tail_gap")
    parser.add_argument(
        "--sweeps-root",
        type=Path,
        default=REPO_ROOT / "results" / "sweeps",
    )
    parser.add_argument("--case-dir", type=Path, default=None, help="仅审计单个 case")
    parser.add_argument("-o", "--output", type=Path, default=None, help="写 JSON+MD 报告")
    parser.add_argument("--tail-pass-us", type=float, default=_TAIL_PASS_US_DEFAULT)
    args = parser.parse_args()
    tail_pass = float(args.tail_pass_us)

    if args.case_dir is not None:
        case_dirs = [args.case_dir.resolve()]
    else:
        root = args.sweeps_root.resolve()
        case_dirs = discover_case_dirs(root)

    results = [audit_case_dir(d, tail_pass_us=tail_pass) for d in case_dirs]
    n_pass = sum(1 for r in results if r.get("pass"))
    n_fail = sum(1 for r in results if not r.get("pass") and not r.get("error"))
    n_err = sum(1 for r in results if r.get("error") or r.get("missing_barrier"))

    summary = {
        "profile_version_expected": DFFC_PROFILE_VERSION,
        "tail_pass_threshold_us": tail_pass,
        "n_cases": len(results),
        "n_pass": n_pass,
        "n_fail": n_fail,
        "n_missing_barrier_or_error": n_err,
        "cases": results,
    }

    md = [
        "# Combine barrier stitch 审计",
        "",
        f"- 期望 profile version: **v{DFFC_PROFILE_VERSION}**",
        f"- `tail_gap = barrier_begin[e+1] - wall_end[e]`，pass 阈值 ≤ **{tail_pass} µs**",
        f"- cases: {len(results)}，pass: **{n_pass}**，fail: **{n_fail}**，缺 barrier/错误: **{n_err}**",
        "",
        "## 汇总表",
        "",
        _md_table(results),
        "",
        "## 解读",
        "",
        "- `tail_gap ≈ 0–1 µs`：writer 串行循环拼接正常，计时逻辑未在 expert 间造缝。",
        "- `barrier_med`：expert 间真实等待（CrossCoreWait+SyncAll），与旧 timeline gap 同量级。",
        "- `pass=N` 且 `ver<11`：需用 `pipeline/run_one_case.py` 或 `maintain/rerun_profile_cases.py` 重跑 profile。",
        "",
    ]

    out_base = args.output or (args.sweeps_root.resolve() / "COMBINE_BARRIER_STITCH_AUDIT")
    if out_base.suffix in (".json", ".md"):
        out_json = out_base.with_suffix(".json")
        out_md = out_base.with_suffix(".md")
    else:
        out_json = Path(str(out_base) + ".json")
        out_md = Path(str(out_base) + ".md")

    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"[audit] {out_json}")
    print(f"[audit] {out_md}")
    print(f"[audit] pass {n_pass}/{len(results)} fail {n_fail} missing/err {n_err}")
    return 0 if n_fail == 0 and n_err == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
