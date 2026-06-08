#!/usr/bin/env python3
"""多 rank profile JSON → 阶段聚合表（mean/median/max）。"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

_TOOLS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TOOLS_DIR.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.dffc_profile.profile_constants import PHASE_NAMES


def load_rank_profiles(indir: Path) -> list[dict[str, Any]]:
    files = sorted(indir.glob("rank*_profile.json"))
    if not files:
        raise FileNotFoundError(f"未找到 profile JSON: {indir}")
    out = []
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def aggregate(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    # t0 = 全局 prep begin 最小值
    prep_begins = [p["phases"]["prep"]["begin_us"] for p in profiles]
    t0 = min(prep_begins)

    rows = {}
    anomalies = []
    for name in PHASE_NAMES:
        begins = [p["phases"][name]["begin_us"] for p in profiles]
        ends = [p["phases"][name]["end_us"] for p in profiles]
        durs = [max(0, e - b) for b, e in zip(begins, ends)]

        timeline_start = statistics.median(begins) - t0
        timeline_dur = max(durs)

        rows[name] = {
            "begin_us_mean": statistics.mean(begins),
            "begin_us_median": statistics.median(begins),
            "begin_us_max": max(begins),
            "end_us_mean": statistics.mean(ends),
            "end_us_median": statistics.median(ends),
            "end_us_max": max(ends),
            "duration_us_mean": statistics.mean(durs),
            "duration_us_median": statistics.median(durs),
            "duration_us_max": max(durs),
            "timeline_start_us": timeline_start,
            "timeline_duration_us": timeline_dur,
        }
        if timeline_dur < 1 or any(b == e for b, e in zip(begins, ends)):
            anomalies.append(name)

    return {"t0_us": t0, "phases": rows, "anomalies": anomalies, "num_ranks": len(profiles)}


def write_breakdown_md(agg: dict[str, Any], out_path: Path) -> None:
    lines = [
        "# dispatch_ffn_combine BREAKDOWN",
        "",
        f"- ranks: {agg['num_ranks']}",
        f"- t0 (min prep begin): {agg['t0_us']} µs",
        "",
        "| phase | median dur (µs) | max dur (µs) | timeline start (µs) | timeline block (µs) |",
        "|-------|-----------------|--------------|---------------------|---------------------|",
    ]
    for name in PHASE_NAMES:
        r = agg["phases"][name]
        lines.append(
            f"| {name} | {r['duration_us_median']:.1f} | {r['duration_us_max']:.1f} | "
            f"{r['timeline_start_us']:.1f} | {r['timeline_duration_us']:.1f} |"
        )
    if agg["anomalies"]:
        lines.extend(["", "## 异常阶段", ""])
        for a in agg["anomalies"]:
            lines.append(f"- `{a}`: duration < 1µs 或 begin==end")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--indir", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    args = parser.parse_args()

    profiles = load_rank_profiles(args.indir)
    agg = aggregate(profiles)

    out_json = args.out_json or (args.indir / "breakdown.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(agg, f, indent=2)

    out_md = args.out_md or (args.indir / "BREAKDOWN.md")
    write_breakdown_md(agg, out_md)
    print(f"[parse] {out_json}")
    print(f"[parse] {out_md}")
    if agg["anomalies"]:
        print(f"[parse] WARN anomalies: {agg['anomalies']}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
