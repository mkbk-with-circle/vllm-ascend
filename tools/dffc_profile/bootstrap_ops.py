"""加载 vllm_ascend_C 与 custom opp，避免依赖完整 vllm 包。"""
from __future__ import annotations

import os
from pathlib import Path


def bootstrap_custom_ops(repo_root: Path | None = None) -> None:
    root = repo_root or Path(__file__).resolve().parents[2]
    vendor = root / "vllm_ascend/_cann_ops_custom/vendors/custom_transformer"
    if vendor.is_dir():
        prev = os.environ.get("ASCEND_CUSTOM_OPP_PATH", "")
        os.environ["ASCEND_CUSTOM_OPP_PATH"] = (
            f"{vendor}:{prev}" if prev else str(vendor)
        )
        lib = vendor / "op_api/lib"
        if lib.is_dir():
            lp = os.environ.get("LD_LIBRARY_PATH", "")
            os.environ["LD_LIBRARY_PATH"] = (
                f"{root / 'vllm_ascend'}:{lib}:{lp}" if lp else f"{root / 'vllm_ascend'}:{lib}"
            )

    # 须在 torch / torch_npu 之后 import
    import vllm_ascend.vllm_ascend_C  # noqa: F401
