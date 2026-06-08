#!/usr/bin/env python3
"""逐 case 审计 profile 因果序、expert 数量与跨 rank 数值一致性。"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.dffc_profile.lib.paths import DFFC_ROOT, REPO_ROOT, ensure_repo_on_path, script_path

ensure_repo_on_path()

from tools.dffc_profile.lib.profile_constants import (
    COMBINE_V1_M_TOPK_THRESHOLD,
    DFFC_PROFILE_VERSION,
    PHASE_NAMES,
    UNPERMUTE_PHASE_NAME,
)

# 跨 rank duration 离散度阈值（combine 因等 GMM2 允许更宽）
DUR_RATIO_STRICT = 1.35
DUR_RATIO_COMBINE = 2.25
# dispatch 首 expert pull 完成 → GMM1 应已启动（允许 µs 级流水线延迟）
GMM1_AFTER_DISPATCH_E0_US = 8000
# GMM1 第一波 → SwiGLU w1 启动
SWIGLU_AFTER_GMM1_WAVE1_US = 5000


@dataclass
class CaseAudit:
    case_dir: Path
    slug: str
    e: int
    version: int
    combine_v1: bool
    fails: list[str] = field(default_factory=list)
    warns: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.fails


def _is_combine_v1(case_params: dict) -> bool:
    return int(case_params.get("m", 0)) * int(case_params.get("topk", 8)) > COMBINE_V1_M_TOPK_THRESHOLD


def _dur_ratio(values: list[float]) -> float:
    nz = [v for v in values if v >= 1]
    if len(nz) < 2:
        return 1.0
    return max(nz) / min(nz)


def _seg_by_expert(segs: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {int(s["expert"]): s for s in segs}


def audit_case_dir(case_dir: Path) -> CaseAudit | None:
    profiles = sorted(case_dir.glob("rank*_profile.json"))
    if not profiles:
        return None
    ps = [json.loads(p.read_text(encoding="utf-8")) for p in profiles]
    cp = ps[0].get("case_params") or {}
    if case_dir.joinpath("case.json").is_file():
        cp = {**json.loads(case_dir.joinpath("case.json").read_text()), **cp}
    e = int(cp.get("e", 0))
    ver = int(ps[0].get("version", 0))
    out = CaseAudit(
        case_dir=case_dir,
        slug=case_dir.name,
        e=e,
        version=ver,
        combine_v1=_is_combine_v1(cp),
    )

    if ver < DFFC_PROFILE_VERSION:
        out.fails.append(f"profile version={ver} < {DFFC_PROFILE_VERSION}")

    # --- 数值：阶段 duration 非零 + 跨 rank 一致性 ---
    for phase in PHASE_NAMES:
        durs = [float(p["phases"][phase]["duration_us"]) for p in ps]
        zero_ranks = [p["rank"] for p, d in zip(ps, durs) if d < 1]
        if zero_ranks:
            out.fails.append(f"{phase}.duration_us=0 on ranks {zero_ranks}")
        ratio = _dur_ratio(durs)
        limit = DUR_RATIO_COMBINE if phase == "combine" else DUR_RATIO_STRICT
        if ratio > limit:
            out.warns.append(
                f"{phase} cross-rank dur ratio {ratio:.2f} "
                f"(min={min(d for d in durs if d>=1):.0f} max={max(durs):.0f}) > {limit}"
            )

    # --- v10：unpermute 整块 reduce 墙钟 ---
    if ver >= 10:
        durs = [
            float(p["phases"].get(UNPERMUTE_PHASE_NAME, {}).get("duration_us", 0)) for p in ps
        ]
        zero_ranks = [p["rank"] for p, d in zip(ps, durs) if d < 1]
        if zero_ranks:
            out.fails.append(f"{UNPERMUTE_PHASE_NAME}.duration_us=0 on ranks {zero_ranks}")
        ratio = _dur_ratio(durs)
        if ratio > DUR_RATIO_STRICT:
            out.warns.append(
                f"{UNPERMUTE_PHASE_NAME} cross-rank dur ratio {ratio:.2f} > {DUR_RATIO_STRICT}"
            )

    # --- 数量：v9 per-expert 段数 ---
    if ver >= 9 and e > 0:
        expert_phases = ("dispatch", "gmm1", "gmm2")
        if out.combine_v1:
            expert_phases = (*expert_phases, "combine")
        for phase in expert_phases:
            for p in ps:
                rank = p.get("rank")
                segs = (p.get("expert_segments") or {}).get(phase) or []
                if len(segs) != e:
                    out.fails.append(
                        f"rank{rank} {phase} expert_segments={len(segs)} != e={e}"
                    )
                else:
                    for seg in segs:
                        act = int(seg.get("active_us", 0))
                        if act < 1:
                            out.fails.append(
                                f"rank{rank} {phase} e{seg.get('expert')} active_us=0"
                            )

    # --- 时间：per-rank 因果序（相对 prep0）---
    for p in ps:
        rank = p.get("rank")
        ph = p["phases"]
        prep_end = ph["prep"]["begin_us"] + ph["prep"]["duration_us"]
        d_b, g1_b, g2_b = ph["dispatch"]["begin_us"], ph["gmm1"]["begin_us"], ph["gmm2"]["begin_us"]
        sw_b = ph["swiglu"]["begin_us"]
        c_b = ph["combine"]["begin_us"]

        if ph["dispatch"]["duration_us"] >= 1 and d_b < prep_end - 50:
            out.fails.append(f"rank{rank}: dispatch begins before prep ends")
        if ph["gmm1"]["duration_us"] >= 1 and g1_b < d_b - 200:
            out.warns.append(
                f"rank{rank}: gmm1.begin ({g1_b}) < dispatch.begin ({d_b})"
            )
        if ph["gmm2"]["duration_us"] >= 1 and g2_b < g1_b - 200:
            out.warns.append(f"rank{rank}: gmm2.begin ({g2_b}) < gmm1.begin ({g1_b})")

        segs_d = _seg_by_expert((p.get("expert_segments") or {}).get("dispatch") or [])
        segs_g1 = _seg_by_expert((p.get("expert_segments") or {}).get("gmm1") or [])
        if 0 in segs_d and 0 in segs_g1 and ph["gmm1"]["duration_us"] >= 1:
            d0_end = int(segs_d[0].get("wall_end_us", 0))
            g1_0_b = int(segs_g1[0].get("wall_begin_us", 0))
            if g1_0_b > d0_end + GMM1_AFTER_DISPATCH_E0_US:
                out.warns.append(
                    f"rank{rank}: gmm1 e0 starts {g1_0_b - d0_end}µs after dispatch e0 "
                    f"(>{GMM1_AFTER_DISPATCH_E0_US})"
                )

        w1 = p.get("phases", {}).get("swiglu_w1", {})
        if w1.get("duration_us", 0) >= 1 and ph["gmm1"]["duration_us"] >= 1:
            g1_end = g1_b + ph["gmm1"]["duration_us"]
            w1_b = int(w1.get("begin_us", 0))
            if w1_b > g1_end + SWIGLU_AFTER_GMM1_WAVE1_US:
                out.warns.append(
                    f"rank{rank}: swiglu_w1 late {w1_b - g1_end}µs after gmm1 end"
                )
        if ph["swiglu"]["duration_us"] >= 1 and ph["combine"]["duration_us"] >= 1:
            if c_b < sw_b - 200 and out.combine_v1:
                out.warns.append(
                    f"rank{rank}: combine.begin ({c_b}) < swiglu.begin ({sw_b})"
                )
        if ver >= 10:
            up = ph.get(UNPERMUTE_PHASE_NAME, {})
            if up.get("duration_us", 0) >= 1 and ph["combine"]["duration_us"] >= 1:
                c_end = c_b + ph["combine"]["duration_us"]
                if int(up["begin_us"]) < c_end - 50:
                    out.fails.append(
                        f"rank{rank}: {UNPERMUTE_PHASE_NAME}.begin ({up['begin_us']}) "
                        f"< combine.end ({c_end})"
                    )

    return out


def collect_case_dirs(roots: list[Path]) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        for cj in sorted(root.rglob("case.json")):
            d = cj.parent
            if any(d.name.endswith(s) for s in ("_v2", "_v3", "_v4")):
                continue
            out.append(d)
    return out


def write_report(results: list[CaseAudit], out_path: Path) -> None:
    lines = ["# Profile constraint audit", ""]
    n_fail = sum(1 for r in results if not r.ok)
    lines.append(f"- cases: {len(results)}")
    lines.append(f"- fail: {n_fail}")
    lines.append(f"- pass: {len(results) - n_fail}")
    lines.append("")
    for r in results:
        status = "FAIL" if r.fails else "PASS"
        lines.append(f"## [{status}] {r.slug} (e={r.e}, v{r.version}, combine_v1={r.combine_v1})")
        if r.fails:
            lines.append("### FAIL")
            for f in r.fails:
                lines.append(f"- {f}")
        if r.warns:
            lines.append("### WARN")
            for w in r.warns[:12]:
                lines.append(f"- {w}")
            if len(r.warns) > 12:
                lines.append(f"- ... +{len(r.warns) - 12} more")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="审计 sweep case profile 约束")
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--case", type=Path, default=None, help="单 case 目录")
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args()

    if args.case:
        dirs = [args.case]
    else:
        roots = args.root or [REPO_ROOT / "results/sweeps"]
        dirs = collect_case_dirs(roots)

    results: list[CaseAudit] = []
    for d in dirs:
        r = audit_case_dir(d)
        if r:
            results.append(r)

    fail_n = sum(1 for r in results if not r.ok)
    print(f"[audit] {len(results)} cases, {fail_n} fail, {len(results) - fail_n} pass")
    for r in results:
        if not r.ok:
            print(f"\n== {r.slug} ==")
            for f in r.fails[:8]:
                print(f"  FAIL: {f}")
            if len(r.fails) > 8:
                print(f"  ... +{len(r.fails)-8} fails")

    report = args.report or (REPO_ROOT / "results/sweeps/AUDIT_CONSTRAINTS.md")
    write_report(results, report)
    print(f"[audit] report -> {report}")

    if args.json:
        payload = [
            {
                "slug": r.slug,
                "path": str(r.case_dir.relative_to(REPO_ROOT)),
                "e": r.e,
                "version": r.version,
                "ok": r.ok,
                "fails": r.fails,
                "warns": r.warns,
            }
            for r in results
        ]
        args.json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"[audit] json -> {args.json}")

    return 1 if fail_n else 0


if __name__ == "__main__":
    raise SystemExit(main())
