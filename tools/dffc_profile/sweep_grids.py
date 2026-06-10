"""参数 sweep 网格定义（EP=8 固定）。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator

from tools.dffc_profile.cases import DffcCase, default_max_output_size, make_case

DEFAULT_EP = 8
DEFAULT_E = 2


@dataclass(frozen=True)
class SweepAxis:
    name: str  # numtokens | hidden | imhidden | topk
    fixed: dict[str, Any]
    values: tuple[int, ...]

    def iter_cases(self, ep: int = DEFAULT_EP) -> Iterator[DffcCase]:
        for i, val in enumerate(self.values):
            params = dict(self.fixed)
            if self.name == "numtokens":
                params["m"] = val
            elif self.name == "hidden":
                params["k"] = val
                params["n"] = val
            elif self.name == "imhidden":
                params["n"] = val * 2
            elif self.name == "topk":
                params["topk"] = val
            else:
                raise ValueError(f"未知轴: {self.name}")

            m = int(params["m"])
            k = int(params["k"])
            n = int(params.get("n", k))
            topk = int(params["topk"])
            mos = int(params.get("max_output_size") or default_max_output_size(m, topk))
            case_name = f"sweep_{self.name}_{val}"
            yield make_case(
                name=case_name,
                m=m,
                k=k,
                n=n,
                e=int(params.get("e", DEFAULT_E)),
                topk=topk,
                max_output_size=mos,
            )


SWEEP_AXES: dict[str, SweepAxis] = {
    "numtokens": SweepAxis(
        name="numtokens",
        fixed={"k": 4096, "n": 4096, "topk": 8, "e": DEFAULT_E},
        values=(1024, 2048, 4096, 8192, 16384),
    ),
    "hidden": SweepAxis(
        name="hidden",
        fixed={"m": 8192, "topk": 8, "e": DEFAULT_E},
        # K>=8064 本机 aicore 异常（VEC UB 对齐/timeout），非 HBM OOM；实测上限约 8000
        values=(2048, 4096, 6144, 7168, 7680, 7936, 7968, 8000),
    ),
    "imhidden": SweepAxis(
        name="imhidden",
        fixed={"m": 8192, "k": 4096, "topk": 8, "e": DEFAULT_E},
        values=(1024, 2048, 3072, 4096),
    ),
    "topk": SweepAxis(
        name="topk",
        fixed={"m": 8192, "k": 4096, "n": 4096, "e": DEFAULT_E},
        values=(4, 8, 16),
    ),
}


def sweep_out_root(repo_root: str | Any, axis: str) -> Any:
    from pathlib import Path

    return Path(repo_root) / "results" / "dffc" / "sweeps" / f"by_{axis}"
