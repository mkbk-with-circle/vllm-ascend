#!/usr/bin/env python3
"""从 rank profile 计算 dispatch/combine 有效带宽。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.dffc_profile.lib.paths import DFFC_ROOT, REPO_ROOT, ensure_repo_on_path, script_path

ensure_repo_on_path()

from tools.dffc_profile.lib.bandwidth import compute_bandwidth_from_dir


def _fmt_gbps(v: float | None) -> str:
    if v is None:
        return "N/A"
    return f"{v:.2f}"


def write_bandwidth_md(agg: dict, out_path: Path) -> None:
    job = agg["job"]
    cp = agg.get("case_params", {})
    lines = [
        "# dispatch/combine 有效带宽",
        "",
        f"- hidden (K): {cp.get('k')}, imhidden: {cp.get('imhidden')}, numtokens: {cp.get('m')}, topk: {cp.get('topk')}",
        f"- bytes/token dispatch: {agg['bytes_per_token']['dispatch']}, combine: {agg['bytes_per_token']['combine']}",
        "",
        "## Job 级（sum(bytes) / max(time)）",
        "",
        "| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |",
        "|------|--------|---------------|-----------------|",
        f"| dispatch | {job['total_bytes_dispatch']:,} | {job['time_dispatch_us_max']:.1f} | {_fmt_gbps(job['bw_dispatch_gbps'])} |",
        f"| combine | {job['total_bytes_combine']:,} | {job['time_combine_us_max']:.1f} | {_fmt_gbps(job['bw_combine_gbps'])} |",
        "",
        "## Per-rank 带宽 (GB/s)",
        "",
        f"- dispatch: median={_fmt_gbps(agg['per_rank_bw_dispatch_gbps']['median'])}, "
        f"min={_fmt_gbps(agg['per_rank_bw_dispatch_gbps']['min'])}, "
        f"max={_fmt_gbps(agg['per_rank_bw_dispatch_gbps']['max'])}",
        f"- combine: median={_fmt_gbps(agg['per_rank_bw_combine_gbps']['median'])}, "
        f"min={_fmt_gbps(agg['per_rank_bw_combine_gbps']['min'])}, "
        f"max={_fmt_gbps(agg['per_rank_bw_combine_gbps']['max'])}",
    ]
    if agg.get("truncation_warning_ranks"):
        lines.extend([
            "",
            "## 警告",
            "",
            f"- 可能触及 max_output_size 截断: ranks {agg['truncation_warning_ranks']}",
        ])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--indir", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    args = parser.parse_args()

    agg = compute_bandwidth_from_dir(args.indir)
    out_json = args.out_json or (args.indir / "bandwidth.json")
    out_md = args.out_md or (args.indir / "BANDWIDTH.md")

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(agg, f, indent=2)
    write_bandwidth_md(agg, out_md)
    print(f"[bandwidth] {out_json}")
    print(f"[bandwidth] {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
