#!/usr/bin/env python3
"""将 dispatch_ffn_combine_kernel.hpp 固化为 v5 GMM/Combine 打点（可重复执行）。"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KERNEL = ROOT / "csrc/mc2/dispatch_ffn_combine/op_kernel/dispatch_ffn_combine_kernel.hpp"


def _replace(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"missing block: {label}")
    return text.replace(old, new, 1)


def patch(text: str) -> str:
    text = _replace(
        text,
        """        if (params.profileGmOffset != 0) {
            profileStageBuf_ =
                reinterpret_cast<__gm__ int32_t*>(params.ptrWorkspace + params.profileGmOffset);
            if ASCEND_IS_AIV {
                if (DffcProfileIsAivWriter(coreIdx)) {
                    DffcProfileInit(profileStageBuf_);
                }
            }
        }""",
        """        if (params.profileGmOffset != 0) {
            profileStageBuf_ =
                reinterpret_cast<__gm__ int32_t*>(params.ptrWorkspace + params.profileGmOffset);
        }""",
        "initBuffer",
    )

    if "DffcGmm1ProfileCommitEnd" not in text:
        insert_at = "    CATLASS_DEVICE\n    void GMM1(Params const &params){"
        helpers = """
#if DISPATCH_FFN_COMBINE_PROFILE
    // GMM1 墙钟 END：从 operator 调用，避免大函数尾部 profile 被编译器裁剪
    CATLASS_DEVICE
    void DffcGmm1ProfileCommitEnd()
    {
        if (profileStageBuf_ == nullptr) {
            return;
        }
        uint32_t now = DffcProfileRelUs(profileStageBuf_);
        DffcGmmProfileMarkEnd(profileStageBuf_, DFFC_PROFILE_SLOT_GMM1_END, now);
    }

    CATLASS_DEVICE
    void DffcGmm1ProfileAtFirstMatmul()
    {
        if (profileStageBuf_ == nullptr) {
            return;
        }
        DffcGmmProfileMarkBegin(
            profileStageBuf_, DFFC_PROFILE_SLOT_GMM1_BEGIN, DffcProfileRelUs(profileStageBuf_));
    }
#endif

"""
        text = text.replace(insert_at, helpers + insert_at, 1)

    text = _replace(
        text,
        """    void operator()<AscendC::AIC>(Params const &params)
    {
        GMM1(params);
        AscendC::CrossCoreWaitFlag<0x2>(SYNCFLAGV2C);
        GMM2(params);
    }""",
        """    void operator()<AscendC::AIC>(Params const &params)
    {
        GMM1(params);
#if DISPATCH_FFN_COMBINE_PROFILE
        DffcGmm1ProfileCommitEnd();
#endif
        AscendC::CrossCoreWaitFlag<0x2>(SYNCFLAGV2C);
        GMM2(params);
    }""",
        "operator AIC",
    )

    # 清理历史诊断写
    for frag in (
        "DffcProfileWrite(profileStageBuf_, DFFC_PROFILE_SLOT_GMM1_END, 0xD4000000);\n        }\n        ",
        "            DffcProfileWrite(profileStageBuf_, DFFC_PROFILE_SLOT_GMM1_END, 0xE5000000);\n        }\n#endif\n        AscendC::CrossCoreWaitFlag",
        "DffcProfileWrite(profileStageBuf_, DFFC_PROFILE_SLOT_GMM1_BEGIN, 0xB2000000",
        "0xA1000000 + coreIdx",
        "0xC3000000",
    ):
        if frag in text:
            text = text.replace(frag, "")

    # GMM1 首 matmul：调用 helper
    text = text.replace(
        """                    if (gmm1Prof) {
                        DffcGmmProfileMarkBegin(
                            profileStageBuf_, DFFC_PROFILE_SLOT_GMM1_BEGIN,
                            DffcProfileRelUs(profileStageBuf_));
                    }""",
        """                    DffcGmm1ProfileAtFirstMatmul();""",
    )

    # GMM1 尾部去掉内联 END（改由 operator 提交）
    text = text.replace(
        """#if DISPATCH_FFN_COMBINE_PROFILE
        if (profileStageBuf_ != nullptr && DffcProfileIsAicWriter(coreIdx)) {
            DffcProfileWrite(profileStageBuf_, DFFC_PROFILE_SLOT_GMM1_END, 0xD4000000);
        }
        if (gmm1Prof) {
            uint32_t now = DffcProfileRelUs(profileStageBuf_);
            DffcGmmProfileMarkEnd(profileStageBuf_, DFFC_PROFILE_SLOT_GMM1_END, now);
            if (gmm1DurWriter && gmm1ProfBegun != 0) {
                uint32_t dur = gmm1Tm.Stop(now);
                if (dur > 0) {
                    DffcProfileWrite(profileStageBuf_,
                        DFFC_PROFILE_SLOT_GMM1_DUR_BASE + static_cast<int32_t>(coreIdx),
                        static_cast<int32_t>(dur));
                }
            }
        }
#endif
    }

    CATLASS_DEVICE
    void GMM2(Params const &params) {""",
        """#if DISPATCH_FFN_COMBINE_PROFILE
        if (gmm1DurWriter && gmm1ProfBegun != 0) {
            uint32_t now = DffcProfileRelUs(profileStageBuf_);
            uint32_t dur = gmm1Tm.Stop(now);
            if (dur > 0) {
                DffcProfileWrite(profileStageBuf_,
                    DFFC_PROFILE_SLOT_GMM1_DUR_BASE + static_cast<int32_t>(coreIdx),
                    static_cast<int32_t>(dur));
            }
        }
#endif
    }

    CATLASS_DEVICE
    void GMM2(Params const &params) {""",
    )

    return text


def main() -> None:
    text = KERNEL.read_text()
    if "gmm1ProfBegun" not in text:
        raise SystemExit("run full v5 patch first (gmm1ProfBegun missing)")
    KERNEL.write_text(patch(text))
    print(f"patched {KERNEL}")


if __name__ == "__main__":
    main()
