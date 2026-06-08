/*
 * dispatch_ffn_combine 分阶段打点：编译期开关，PROFILE=0 时零开销。
 */
#ifndef DISPATCH_FFN_COMBINE_PROFILE_H
#define DISPATCH_FFN_COMBINE_PROFILE_H

#include "kernel_operator.h"

// 与 host tools/dffc_profile 解析脚本保持一致
#define DFFC_PROFILE_MAGIC 0x44504643  // 'DPFC'
#define DFFC_PROFILE_VERSION 1
#define DFFC_PROFILE_NUM_PHASES 6
// [magic, version, 6×(begin,end)]
#define DFFC_PROFILE_WORDS (2 + 2 * DFFC_PROFILE_NUM_PHASES)
#define DFFC_PROFILE_GM_BYTES (64 * sizeof(int32_t))

enum DffcProfilePhase : int32_t {
    DFFC_PHASE_PREP = 0,
    DFFC_PHASE_DISPATCH = 1,
    DFFC_PHASE_SWIGLU = 2,
    DFFC_PHASE_COMBINE = 3,
    DFFC_PHASE_GMM1 = 4,
    DFFC_PHASE_GMM2 = 5,
};

// host 从 expert_token_nums[E:] 读取
#define DFFC_PROFILE_EXPORT_WORDS DFFC_PROFILE_WORDS

#ifndef DISPATCH_FFN_COMBINE_PROFILE
#define DISPATCH_FFN_COMBINE_PROFILE 0
#endif

#if DISPATCH_FFN_COMBINE_PROFILE

constexpr uint32_t DFFC_TIME_CYCLE = 50;

__aicore__ inline int32_t DffcProfileNowUs()
{
    return static_cast<int32_t>(AscendC::GetSystemCycle() / DFFC_TIME_CYCLE);
}

__aicore__ inline int32_t DffcProfileSlotBegin(int32_t phase)
{
    return 2 + phase * 2;
}

__aicore__ inline int32_t DffcProfileSlotEnd(int32_t phase)
{
    return 2 + phase * 2 + 1;
}

__aicore__ inline void DffcProfileWrite(__gm__ int32_t* buf, int32_t slot, int32_t val)
{
    if (buf == nullptr) {
        return;
    }
    buf[slot] = val;
}

__aicore__ inline void DffcProfileInit(__gm__ int32_t* buf)
{
    if (buf == nullptr) {
        return;
    }
    for (int32_t i = 0; i < DFFC_PROFILE_WORDS; ++i) {
        buf[i] = 0;
    }
    buf[0] = DFFC_PROFILE_MAGIC;
    buf[1] = DFFC_PROFILE_VERSION;
}

// AIV core0 判定：coreIdx 含 subblock 维
__aicore__ inline bool DffcProfileIsAivWriter(uint32_t coreIdx)
{
    return coreIdx == 0;
}

__aicore__ inline bool DffcProfileIsAicWriter(uint32_t coreIdx)
{
    return coreIdx == 0;
}

#define DFFC_PROFILE_STAGE_BEGIN(buf, phase)                                              \
    do {                                                                                  \
        if ((buf) != nullptr) {                                                           \
            if (ASCEND_IS_AIV && DffcProfileIsAivWriter(coreIdx)) {                       \
                DffcProfileWrite((buf), DffcProfileSlotBegin(phase), DffcProfileNowUs()); \
            } else if (ASCEND_IS_AIC && DffcProfileIsAicWriter(coreIdx)) {                \
                DffcProfileWrite((buf), DffcProfileSlotBegin(phase), DffcProfileNowUs()); \
            }                                                                             \
        }                                                                                 \
    } while (0)

#define DFFC_PROFILE_STAGE_END(buf, phase)                                                \
    do {                                                                                  \
        if ((buf) != nullptr) {                                                           \
            if (ASCEND_IS_AIV && DffcProfileIsAivWriter(coreIdx)) {                       \
                DffcProfileWrite((buf), DffcProfileSlotEnd(phase), DffcProfileNowUs());   \
            } else if (ASCEND_IS_AIC && DffcProfileIsAicWriter(coreIdx)) {                \
                DffcProfileWrite((buf), DffcProfileSlotEnd(phase), DffcProfileNowUs());   \
            }                                                                             \
        }                                                                                 \
    } while (0)

// 将 workspace 尾部 profile 拷到 expert_token_nums 尾部，供 host 读回
__aicore__ inline void DffcProfileExportToExpertNums(
    GM_ADDR expertTokenNums, uint32_t expertPerRank, __gm__ int32_t* buf)
{
    if (buf == nullptr || expertTokenNums == nullptr) {
        return;
    }
    __gm__ int32_t* dst =
        reinterpret_cast<__gm__ int32_t*>(expertTokenNums) + expertPerRank;
    for (int32_t i = 0; i < DFFC_PROFILE_EXPORT_WORDS; ++i) {
        dst[i] = buf[i];
    }
}

#else

#define DFFC_PROFILE_STAGE_BEGIN(buf, phase) ((void)0)
#define DFFC_PROFILE_STAGE_END(buf, phase) ((void)0)

__aicore__ inline void DffcProfileInit(__gm__ int32_t* buf) { (void)buf; }

__aicore__ inline void DffcProfileExportToExpertNums(
    GM_ADDR expertTokenNums, uint32_t expertPerRank, __gm__ int32_t* buf)
{
    (void)expertTokenNums;
    (void)expertPerRank;
    (void)buf;
}

#endif

#endif  // DISPATCH_FFN_COMBINE_PROFILE_H
