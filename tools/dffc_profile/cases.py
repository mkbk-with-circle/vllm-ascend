"""dffc profile case 网格与 HCCL_BUFFSIZE 计算。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DffcCase:
    name: str
    m: int
    k: int
    e: int
    topk: int
    max_output_size: int

    @property
    def n(self) -> int:
        return self.k

    @property
    def expert_per_rank(self) -> int:
        return self.e


CASES = {
    "S1": DffcCase("S1", m=1024, k=4096, e=2, topk=8, max_output_size=16 * 1024),
    "S2": DffcCase("S2", m=8192, k=4096, e=2, topk=8, max_output_size=64 * 1024),
    "S3": DffcCase("S3", m=8192, k=6144, e=2, topk=8, max_output_size=64 * 1024),
    "S4": DffcCase("S4", m=8192, k=4096, e=2, topk=16, max_output_size=128 * 1024),
}

DEFAULT_CASE = CASES["S1"]


def hccl_buffsize_mb(case: DffcCase) -> int:
    """与 tiling 校验公式对齐：((m*k*topk*1)*3 + 3MB) 向上取整 MB。"""
    raw = case.m * case.k * case.topk * 3 + 3 * 1024 * 1024
    return (raw + 1024 * 1024 - 1) // (1024 * 1024)
