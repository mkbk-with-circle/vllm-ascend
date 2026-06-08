/*
 * dispatch_ffn_combine 分阶段打点：编译期开关，PROFILE=0 时零开销。
 * v11: combine per-expert barrier（slot68-83，CrossCoreWait 前 / SyncAll 后）。
 * v10: unpermute 墙钟（slot66/67，CrossRankSync 后→Process+SyncAll）。
 * v9: per-expert wall_begin/wall_end/active（dispatch/combine/gmm1/gmm2，e<=8）。
 * v8: combine 墙钟；GMM2 首 tile→末 tile。
 * v7: SwiGLU 墙钟 + 两波 BEGIN/END；v6 GMM1/2 墙钟不变。
 */
#ifndef DISPATCH_FFN_COMBINE_PROFILE_H
#define DISPATCH_FFN_COMBINE_PROFILE_H

#include "kernel_operator.h"

#define DFFC_PROFILE_MAGIC 0x44504643  // 'DPFC'
#define DFFC_PROFILE_VERSION 11
#define DFFC_PROFILE_NUM_PHASES 6
#define DFFC_AIC_MAX_CORES 20
#define DFFC_PROFILE_T0_SLOT 2
// AIC 辅助槽：GMM1_BEGIN 放尾部，避免旧 slot15 与 AIV phase 区 cache 冲突
#define DFFC_PROFILE_SLOT_GMM1_DUR_BASE 16
#define DFFC_PROFILE_SLOT_GMM2_BEGIN 36
#define DFFC_PROFILE_SLOT_GMM2_DUR_BASE 37
#define DFFC_PROFILE_SLOT_GMM1_BEGIN 57
#define DFFC_PROFILE_SLOT_GMM1_END 58
#define DFFC_PROFILE_SLOT_GMM2_END 59
#define DFFC_PROFILE_SLOT_SWIGLU_W1_BEGIN 60
#define DFFC_PROFILE_SLOT_SWIGLU_W1_END 61
#define DFFC_PROFILE_SLOT_SWIGLU_W2_BEGIN 62
#define DFFC_PROFILE_SLOT_SWIGLU_W2_END 63
#define DFFC_PROFILE_SLOT_COMBINE_WALL_END 64
#define DFFC_PROFILE_SLOT_DEBUG_PROBE 65  // 探针：export 时镜像 sidecar[0]
#define DFFC_PROFILE_SLOT_UNPERMUTE_BEGIN 66
#define DFFC_PROFILE_SLOT_UNPERMUTE_END 67
// v11：combine barrier 探针（8 expert × 2：wait 前 / SyncAll 后）
#define DFFC_PROFILE_COMBINE_BARRIER_BASE 68
#define DFFC_PROFILE_COMBINE_BARRIER_FIELDS 2
// v9：AIV/AIC 分块各占 512B(128×int32)，避免 Cube/Vector false sharing
#define DFFC_PROFILE_V9_LINE_WORDS 128
#define DFFC_PROFILE_V9_AIV_BASE 128   // dispatch + combine
#define DFFC_PROFILE_V9_AIC_BASE 256   // gmm1 + gmm2
#define DFFC_PROFILE_MAX_EXPERTS 8
#define DFFC_PROFILE_V9_EXPERT_FIELDS 3  // wall_begin, wall_end, active_us
#define DFFC_PROFILE_WORDS \
    (DFFC_PROFILE_V9_AIC_BASE + 2 * DFFC_PROFILE_MAX_EXPERTS * DFFC_PROFILE_V9_EXPERT_FIELDS)
#define DFFC_PROFILE_GM_BYTES (DFFC_PROFILE_WORDS * sizeof(int32_t))

enum DffcProfilePhase : int32_t {
    DFFC_PHASE_PREP = 0,
    DFFC_PHASE_DISPATCH = 1,
    DFFC_PHASE_SWIGLU = 2,
    DFFC_PHASE_COMBINE = 3,
    DFFC_PHASE_GMM1 = 4,
    DFFC_PHASE_GMM2 = 5,
};

// v9：per-expert 打点阶段（与 dispatch/combine/gmm1/gmm2 对应）
enum DffcProfileExpertPhase : int32_t {
    DFFC_EXPERT_PHASE_DISPATCH = 0,
    DFFC_EXPERT_PHASE_COMBINE = 1,
    DFFC_EXPERT_PHASE_GMM1 = 2,
    DFFC_EXPERT_PHASE_GMM2 = 3,
};

constexpr int32_t DFFC_PROFILE_V9_FIELD_WALL_BEGIN = 0;
constexpr int32_t DFFC_PROFILE_V9_FIELD_WALL_END = 1;
constexpr int32_t DFFC_PROFILE_V9_FIELD_ACTIVE = 2;

#define DFFC_PROFILE_EXPORT_WORDS DFFC_PROFILE_WORDS

#ifndef DISPATCH_FFN_COMBINE_PROFILE
#define DISPATCH_FFN_COMBINE_PROFILE 0
#endif

#if DISPATCH_FFN_COMBINE_PROFILE

constexpr uint32_t DFFC_TIME_CYCLE = 50;

__aicore__ inline uint32_t DffcProfileNowAbsUs()
{
    return static_cast<uint32_t>(AscendC::GetSystemCycle() / DFFC_TIME_CYCLE);
}

__aicore__ inline uint32_t DffcProfileRelUs(__gm__ int32_t* buf)
{
    if (buf == nullptr) {
        return 0;
    }
    return DffcProfileNowAbsUs() - static_cast<uint32_t>(buf[DFFC_PROFILE_T0_SLOT]);
}

__aicore__ inline int32_t DffcProfileSlotBegin(int32_t phase)
{
    return 3 + phase * 2;
}

__aicore__ inline int32_t DffcProfileSlotEnd(int32_t phase)
{
    return 3 + phase * 2 + 1;
}

__aicore__ inline int32_t DffcProfileV9ExpertSlot(int32_t phase, int32_t expert, int32_t field)
{
    constexpr int32_t kPhaseWords =
        DFFC_PROFILE_MAX_EXPERTS * DFFC_PROFILE_V9_EXPERT_FIELDS;
    int32_t base = (phase <= DFFC_EXPERT_PHASE_COMBINE)
        ? DFFC_PROFILE_V9_AIV_BASE
        : DFFC_PROFILE_V9_AIC_BASE;
    int32_t phaseInBlock = (phase <= DFFC_EXPERT_PHASE_COMBINE)
        ? phase
        : (phase - DFFC_EXPERT_PHASE_GMM1);
    return base + phaseInBlock * kPhaseWords + expert * DFFC_PROFILE_V9_EXPERT_FIELDS + field;
}

// workspace 独立 sidecar（512B）：AIC 组边界流式写，export 前 AIV relay 到 v9@256+
#define DFFC_SIDECAR_WORDS (2 * DFFC_PROFILE_MAX_EXPERTS * DFFC_PROFILE_V9_EXPERT_FIELDS)
#define DFFC_SIDECAR_GM_BYTES 512
#define DFFC_SIDECAR_PROBE_SLOT 127  // 512B 区末字，不与 per-expert 槽冲突

#ifndef DFFC_PROFILE_SIDECAR_PROBE
#define DFFC_PROFILE_SIDECAR_PROBE 0
#endif

__aicore__ inline int32_t DffcSidecarSlot(int32_t phase, int32_t expert, int32_t field)
{
    constexpr int32_t kPhaseWords =
        DFFC_PROFILE_MAX_EXPERTS * DFFC_PROFILE_V9_EXPERT_FIELDS;
    int32_t phaseInBlock = phase - DFFC_EXPERT_PHASE_GMM1;
    return phaseInBlock * kPhaseWords + expert * DFFC_PROFILE_V9_EXPERT_FIELDS + field;
}

__aicore__ inline void DffcProfileInitSidecar(__gm__ int32_t* sidecar)
{
    if (sidecar == nullptr) {
        return;
    }
    for (int32_t i = 0; i < DFFC_SIDECAR_WORDS; ++i) {
        sidecar[i] = 0;
    }
}

__aicore__ inline void DffcProfileCacheTouch(__gm__ int32_t* addr)
{
    AscendC::GlobalTensor<uint8_t> global;
    global.SetGlobalBuffer(reinterpret_cast<GM_ADDR>(addr));
    AscendC::DataCacheCleanAndInvalid<uint8_t, AscendC::CacheLine::SINGLE_CACHE_LINE,
        AscendC::DcciDst::CACHELINE_OUT>(global);
}

// AIV 读 AIC 写的 GM 戳前必须 invalidate，否则会命中 init 时的脏 cache
__aicore__ inline void DffcProfileCacheInvalidate(__gm__ int32_t* addr)
{
    AscendC::GlobalTensor<uint8_t> global;
    global.SetGlobalBuffer(reinterpret_cast<GM_ADDR>(addr));
    AscendC::DataCacheCleanAndInvalid<uint8_t, AscendC::CacheLine::SINGLE_CACHE_LINE,
        AscendC::DcciDst::CACHELINE_ALL>(global);
}

__aicore__ inline int32_t DffcProfileReadGm(__gm__ int32_t* buf, int32_t slot)
{
    if (buf == nullptr) {
        return 0;
    }
    DffcProfileCacheInvalidate(buf + slot);
    return buf[slot];
}

__aicore__ inline void DffcProfileWrite(__gm__ int32_t* buf, int32_t slot, int32_t val)
{
    if (buf == nullptr) {
        return;
    }
    buf[slot] = val;
    DffcProfileCacheTouch(buf + slot);
}

// export 前由 AIV 将 sidecar relay 到 v9 AIC 槽位
__aicore__ inline void DffcProfileRelaySidecarToV9(__gm__ int32_t* buf, __gm__ int32_t* sidecar)
{
    if (buf == nullptr || sidecar == nullptr) {
        return;
    }
    for (int32_t phase = DFFC_EXPERT_PHASE_GMM1; phase <= DFFC_EXPERT_PHASE_GMM2; ++phase) {
        for (int32_t e = 0; e < DFFC_PROFILE_MAX_EXPERTS; ++e) {
            for (int32_t f = 0; f < DFFC_PROFILE_V9_EXPERT_FIELDS; ++f) {
                int32_t sc = DffcSidecarSlot(phase, e, f);
                int32_t v = DffcProfileReadGm(sidecar, sc);
                if (v != 0) {
                    DffcProfileWrite(buf, DffcProfileV9ExpertSlot(phase, e, f), v);
                }
            }
        }
    }
#if DFFC_PROFILE_SIDECAR_PROBE
    int32_t probe = DffcProfileReadGm(sidecar, DFFC_SIDECAR_PROBE_SLOT);
    if (probe != 0) {
        DffcProfileWrite(buf, DFFC_PROFILE_SLOT_DEBUG_PROBE, probe);
    }
#endif
}

__aicore__ inline void DffcProfileInit(__gm__ int32_t* buf)
{
    if (buf == nullptr) {
        return;
    }
    // 已初始化则跳过，避免 AIC 写入 GMM 戳后被迟到的 AIV init 清零
    if (DffcProfileReadGm(buf, 0) == DFFC_PROFILE_MAGIC &&
        DffcProfileReadGm(buf, 1) == DFFC_PROFILE_VERSION) {
        return;
    }
    // 清零阶段槽 + AIC GMM 辅助槽（含 BEGIN / per-core duration）
    for (int32_t i = 0; i < DFFC_PROFILE_WORDS; ++i) {
        buf[i] = 0;
    }
    buf[0] = DFFC_PROFILE_MAGIC;
    buf[1] = DFFC_PROFILE_VERSION;
    buf[DFFC_PROFILE_T0_SLOT] = static_cast<int32_t>(DffcProfileNowAbsUs());
}

// AIV 仅 subblock0 的 core0 写戳
__aicore__ inline bool DffcProfileIsAivWriter(uint32_t coreIdx)
{
    return coreIdx == 0 && get_subblockid() == 0;
}

// AIC 使用构造时写入的 coreIdx（GetBlockIdx）
__aicore__ inline bool DffcProfileIsAicWriter(uint32_t coreIdx)
{
    return coreIdx == 0;
}

struct DffcActiveTimer {
    uint32_t accUs;
    uint32_t t0Us;
    bool running;

    __aicore__ inline void Reset()
    {
        accUs = 0;
        t0Us = 0;
        running = false;
    }

    __aicore__ inline void Pause(uint32_t now)
    {
        if (running) {
            accUs += now - t0Us;
            running = false;
        }
    }

    __aicore__ inline void Resume(uint32_t now)
    {
        if (!running) {
            t0Us = now;
            running = true;
        }
    }

    __aicore__ inline uint32_t Stop(uint32_t now)
    {
        Pause(now);
        return accUs;
    }
};

// GMM 墙钟 BEGIN：多 AIC core 竞争写，保留更早的时间戳
__aicore__ inline void DffcGmmProfileMarkBegin(__gm__ int32_t* buf, int32_t beginSlot, uint32_t now)
{
    if (buf == nullptr) {
        return;
    }
    int32_t prev = DffcProfileReadGm(buf, beginSlot);
    if (prev == 0 || static_cast<uint32_t>(now) < static_cast<uint32_t>(prev)) {
        DffcProfileWrite(buf, beginSlot, static_cast<int32_t>(now));
    }
}

// GMM 墙钟 END：多 AIC core 竞争写，保留更晚的时间戳
__aicore__ inline void DffcGmmProfileMarkEnd(__gm__ int32_t* buf, int32_t endSlot, uint32_t now)
{
    if (buf == nullptr) {
        return;
    }
    int32_t prev = DffcProfileReadGm(buf, endSlot);
    if (prev == 0 || static_cast<uint32_t>(now) > static_cast<uint32_t>(prev)) {
        DffcProfileWrite(buf, endSlot, static_cast<int32_t>(now));
    }
}

// GMM 打点：首 expert 计算前等待 Pause；begun 后 expert 间等待计入墙钟
__aicore__ inline void DffcGmmProfilePause(__gm__ int32_t* buf, DffcActiveTimer& tm)
{
    if (buf == nullptr) {
        return;
    }
    tm.Pause(DffcProfileRelUs(buf));
}


// AIC core0 单写者：直写 GM，避免 ReadGm 脏 cache 阻止首次落盘
__aicore__ inline void DffcProfileExpertWriteAic(
    __gm__ int32_t* buf, int32_t phase, int32_t expert, int32_t field, uint32_t val)
{
    if (buf == nullptr || expert < 0 || expert >= DFFC_PROFILE_MAX_EXPERTS || val == 0) {
        return;
    }
    int32_t slot = DffcProfileV9ExpertSlot(phase, expert, field);
    DffcProfileWrite(buf, slot, static_cast<int32_t>(val));
}

// v9：per-expert 墙钟/ active（多核竞争 min begin / max end / max active）
__aicore__ inline void DffcProfileExpertWallBegin(
    __gm__ int32_t* buf, int32_t phase, int32_t expert, uint32_t relUs)
{
    if (buf == nullptr || expert < 0 || expert >= DFFC_PROFILE_MAX_EXPERTS) {
        return;
    }
    int32_t slot = DffcProfileV9ExpertSlot(phase, expert, DFFC_PROFILE_V9_FIELD_WALL_BEGIN);
    int32_t prev = DffcProfileReadGm(buf, slot);
    if (prev == 0 || relUs < static_cast<uint32_t>(prev)) {
        DffcProfileWrite(buf, slot, static_cast<int32_t>(relUs));
    }
}

__aicore__ inline void DffcProfileExpertWallEnd(
    __gm__ int32_t* buf, int32_t phase, int32_t expert, uint32_t relUs)
{
    if (buf == nullptr || expert < 0 || expert >= DFFC_PROFILE_MAX_EXPERTS) {
        return;
    }
    int32_t slot = DffcProfileV9ExpertSlot(phase, expert, DFFC_PROFILE_V9_FIELD_WALL_END);
    int32_t prev = DffcProfileReadGm(buf, slot);
    if (prev == 0 || relUs > static_cast<uint32_t>(prev)) {
        DffcProfileWrite(buf, slot, static_cast<int32_t>(relUs));
    }
}

__aicore__ inline void DffcProfileExpertActiveMax(
    __gm__ int32_t* buf, int32_t phase, int32_t expert, uint32_t activeUs)
{
    if (buf == nullptr || expert < 0 || expert >= DFFC_PROFILE_MAX_EXPERTS || activeUs == 0) {
        return;
    }
    int32_t slot = DffcProfileV9ExpertSlot(phase, expert, DFFC_PROFILE_V9_FIELD_ACTIVE);
    int32_t prev = DffcProfileReadGm(buf, slot);
    if (activeUs > static_cast<uint32_t>(prev)) {
        DffcProfileWrite(buf, slot, static_cast<int32_t>(activeUs));
    }
}

__aicore__ inline int32_t DffcProfileCombineBarrierSlot(int32_t expert, int32_t field)
{
    return DFFC_PROFILE_COMBINE_BARRIER_BASE + expert * DFFC_PROFILE_COMBINE_BARRIER_FIELDS + field;
}

// v11：combine barrier 墙钟（AIV writer 单核写，与 wall_end 一致）
__aicore__ inline void DffcProfileCombineBarrierBegin(
    __gm__ int32_t* buf, int32_t expert, uint32_t relUs)
{
    if (buf == nullptr || expert < 0 || expert >= DFFC_PROFILE_MAX_EXPERTS || relUs == 0) {
        return;
    }
    DffcProfileWrite(buf, DffcProfileCombineBarrierSlot(expert, 0), static_cast<int32_t>(relUs));
}

__aicore__ inline void DffcProfileCombineBarrierEnd(
    __gm__ int32_t* buf, int32_t expert, uint32_t relUs)
{
    if (buf == nullptr || expert < 0 || expert >= DFFC_PROFILE_MAX_EXPERTS || relUs == 0) {
        return;
    }
    DffcProfileWrite(buf, DffcProfileCombineBarrierSlot(expert, 1), static_cast<int32_t>(relUs));
}

// sidecar per-expert：多 AIC core 竞争 min begin / max end / max active
__aicore__ inline void DffcSidecarWallBegin(
    __gm__ int32_t* sidecar, int32_t phase, int32_t expert, uint32_t relUs)
{
    if (sidecar == nullptr || expert < 0 || expert >= DFFC_PROFILE_MAX_EXPERTS) {
        return;
    }
    int32_t slot = DffcSidecarSlot(phase, expert, DFFC_PROFILE_V9_FIELD_WALL_BEGIN);
    int32_t prev = DffcProfileReadGm(sidecar, slot);
    if (prev == 0 || relUs < static_cast<uint32_t>(prev)) {
        DffcProfileWrite(sidecar, slot, static_cast<int32_t>(relUs));
    }
}

__aicore__ inline void DffcSidecarWallEnd(
    __gm__ int32_t* sidecar, int32_t phase, int32_t expert, uint32_t relUs)
{
    if (sidecar == nullptr || expert < 0 || expert >= DFFC_PROFILE_MAX_EXPERTS) {
        return;
    }
    int32_t slot = DffcSidecarSlot(phase, expert, DFFC_PROFILE_V9_FIELD_WALL_END);
    int32_t prev = DffcProfileReadGm(sidecar, slot);
    if (prev == 0 || relUs > static_cast<uint32_t>(prev)) {
        DffcProfileWrite(sidecar, slot, static_cast<int32_t>(relUs));
    }
}

__aicore__ inline void DffcSidecarActiveMax(
    __gm__ int32_t* sidecar, int32_t phase, int32_t expert, uint32_t activeUs)
{
    if (sidecar == nullptr || expert < 0 || expert >= DFFC_PROFILE_MAX_EXPERTS || activeUs == 0) {
        return;
    }
    int32_t slot = DffcSidecarSlot(phase, expert, DFFC_PROFILE_V9_FIELD_ACTIVE);
    int32_t prev = DffcProfileReadGm(sidecar, slot);
    if (activeUs > static_cast<uint32_t>(prev)) {
        DffcProfileWrite(sidecar, slot, static_cast<int32_t>(activeUs));
    }
}

__aicore__ inline void DffcGmmProfileResumeAfterSignal(
    __gm__ int32_t* buf, DffcActiveTimer& tm, int32_t beginSlot, int32_t& begun)
{
    if (buf == nullptr) {
        return;
    }
    uint32_t now = DffcProfileRelUs(buf);
    if (begun == 0) {
        // 多 AIC core 竞争写 BEGIN，保留更早的时间戳
        int32_t prev = DffcProfileReadGm(buf, beginSlot);
        if (prev == 0 || static_cast<uint32_t>(now) < static_cast<uint32_t>(prev)) {
            DffcProfileWrite(buf, beginSlot, static_cast<int32_t>(now));
        }
        begun = 1;
    }
    tm.Resume(now);
}

__aicore__ inline void DffcProfileCommitSpan(
    __gm__ int32_t* buf, int32_t phase, uint32_t beginRel, uint32_t durUs)
{
    if (buf == nullptr) {
        return;
    }
    DffcProfileWrite(buf, DffcProfileSlotBegin(phase), static_cast<int32_t>(beginRel));
    DffcProfileWrite(buf, DffcProfileSlotEnd(phase), static_cast<int32_t>(durUs));
}

// 将 per-core GMM duration 聚合到 phase 槽（export 前由 AIV writer 调用）
__aicore__ inline void DffcProfileAggregateAicGmms(__gm__ int32_t* buf)
{
    if (buf == nullptr) {
        return;
    }
    uint32_t gmm1Max = 0;
    uint32_t gmm2Max = 0;
    for (int32_t i = 0; i < DFFC_AIC_MAX_CORES; ++i) {
        uint32_t d1 = static_cast<uint32_t>(
            DffcProfileReadGm(buf, DFFC_PROFILE_SLOT_GMM1_DUR_BASE + i));
        uint32_t d2 = static_cast<uint32_t>(
            DffcProfileReadGm(buf, DFFC_PROFILE_SLOT_GMM2_DUR_BASE + i));
        gmm1Max = d1 > gmm1Max ? d1 : gmm1Max;
        gmm2Max = d2 > gmm2Max ? d2 : gmm2Max;
    }
    uint32_t gmm1Begin = static_cast<uint32_t>(
        DffcProfileReadGm(buf, DFFC_PROFILE_SLOT_GMM1_BEGIN));
    uint32_t gmm2Begin = static_cast<uint32_t>(
        DffcProfileReadGm(buf, DFFC_PROFILE_SLOT_GMM2_BEGIN));
    uint32_t gmm1End = static_cast<uint32_t>(
        DffcProfileReadGm(buf, DFFC_PROFILE_SLOT_GMM1_END));
    uint32_t gmm2End = static_cast<uint32_t>(
        DffcProfileReadGm(buf, DFFC_PROFILE_SLOT_GMM2_END));
    uint32_t gmm1PhaseBegin = static_cast<uint32_t>(
        DffcProfileReadGm(buf, DffcProfileSlotBegin(DFFC_PHASE_GMM1)));
    uint32_t gmm1PhaseDur = static_cast<uint32_t>(
        DffcProfileReadGm(buf, DffcProfileSlotEnd(DFFC_PHASE_GMM1)));
    // v6：优先尾部 BEGIN/END；辅助槽缺失时回退 AIC 直写的 phase 槽
    if (gmm1Begin == 0 && gmm1PhaseBegin > 0) {
        gmm1Begin = gmm1PhaseBegin;
    }
    uint32_t gmm1Dur = 0;
    if (gmm1Begin > 0 && gmm1End > gmm1Begin) {
        gmm1Dur = gmm1End - gmm1Begin;
    } else if (gmm1PhaseBegin > 0 && gmm1PhaseDur > 0) {
        gmm1Begin = gmm1PhaseBegin;
        gmm1Dur = gmm1PhaseDur;
    } else {
        gmm1Dur = gmm1Max;
    }
    if (gmm2Begin == 0 && gmm2End > 0 && gmm2Max > 0 && gmm2End > gmm2Max) {
        gmm2Begin = gmm2End - gmm2Max;
    }
    uint32_t gmm2Dur = (gmm2Begin > 0 && gmm2End > gmm2Begin) ? (gmm2End - gmm2Begin) : gmm2Max;
    DffcProfileCommitSpan(buf, DFFC_PHASE_GMM1, gmm1Begin, gmm1Dur);
    DffcProfileCommitSpan(buf, DFFC_PHASE_GMM2, gmm2Begin, gmm2Dur);
}

// v8：combine 墙钟 = 首 expert 通信 BEGIN → COMBINE_WALL_END（含 expert 间等待）
__aicore__ inline void DffcProfileAggregateCombine(__gm__ int32_t* buf)
{
    if (buf == nullptr) {
        return;
    }
    uint32_t combineBegin = static_cast<uint32_t>(
        DffcProfileReadGm(buf, DffcProfileSlotBegin(DFFC_PHASE_COMBINE)));
    uint32_t combineEnd = static_cast<uint32_t>(
        DffcProfileReadGm(buf, DFFC_PROFILE_SLOT_COMBINE_WALL_END));
    if (combineBegin > 0 && combineEnd > combineBegin) {
        DffcProfileCommitSpan(buf, DFFC_PHASE_COMBINE, combineBegin, combineEnd - combineBegin);
    }
}

#define DFFC_PROFILE_STAGE_BEGIN(buf, phase)                                              \
    do {                                                                                  \
        if ((buf) != nullptr && DffcProfileIsAivWriter(coreIdx)) {                        \
            DffcProfileWrite((buf), DffcProfileSlotBegin(phase),                           \
                static_cast<int32_t>(DffcProfileRelUs(buf)));                              \
        }                                                                                 \
    } while (0)

#define DFFC_PROFILE_STAGE_END(buf, phase)                                                \
    do {                                                                                  \
        if ((buf) != nullptr && DffcProfileIsAivWriter(coreIdx)) {                        \
            uint32_t _dffc_b = static_cast<uint32_t>((buf)[DffcProfileSlotBegin(phase)]); \
            uint32_t _dffc_d = DffcProfileRelUs(buf) - _dffc_b;                           \
            DffcProfileWrite((buf), DffcProfileSlotEnd(phase), static_cast<int32_t>(_dffc_d)); \
        }                                                                                 \
    } while (0)

// export 后封印 workspace profile，使同进程下次 forward 可重新 DffcProfileInit
__aicore__ inline void DffcProfileSealAfterExport(__gm__ int32_t* buf)
{
    if (buf == nullptr) {
        return;
    }
    DffcProfileWrite(buf, 0, 0);
    DffcProfileWrite(buf, 1, 0);
}

__aicore__ inline void DffcProfileExportToExpertNums(
    GM_ADDR expertTokenNums, uint32_t expertPerRank, __gm__ int32_t* buf, __gm__ int32_t* sidecar)
{
    if (buf == nullptr || expertTokenNums == nullptr) {
        return;
    }
    DffcProfileAggregateAicGmms(buf);
    DffcProfileAggregateCombine(buf);
    DffcProfileRelaySidecarToV9(buf, sidecar);
    __gm__ int32_t* dst =
        reinterpret_cast<__gm__ int32_t*>(expertTokenNums) + expertPerRank;
    for (int32_t i = 0; i < DFFC_PROFILE_EXPORT_WORDS; ++i) {
        dst[i] = DffcProfileReadGm(buf, i);
        DffcProfileCacheTouch(dst + i);
    }
    // 单次 launch 内 init 幂等不变；export 后清 magic 供 host 同进程多轮 benchmark
    DffcProfileSealAfterExport(buf);
}

#else

#define DFFC_PROFILE_STAGE_BEGIN(buf, phase) ((void)0)
#define DFFC_PROFILE_STAGE_END(buf, phase) ((void)0)

__aicore__ inline void DffcProfileInit(__gm__ int32_t* buf) { (void)buf; }

__aicore__ inline void DffcProfileExportToExpertNums(
    GM_ADDR expertTokenNums, uint32_t expertPerRank, __gm__ int32_t* buf, __gm__ int32_t* sidecar)
{
    (void)expertTokenNums;
    (void)expertPerRank;
    (void)buf;
    (void)sidecar;
}

#endif

#endif  // DISPATCH_FFN_COMBINE_PROFILE_H
