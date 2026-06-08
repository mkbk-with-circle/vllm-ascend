/*
 * Copyright (c) 2025 Huawei Technologies Co., Ltd.
 * This file is a part of the CANN Open Software.
 * Licensed under CANN Open Software License Agreement Version 1.0 (the "License").
 * Please refer to the License for details. You may not use this file except in compliance with the License.
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
 * See LICENSE in the root of the software repository for the full text of the License.
 */

#ifndef DISPATCH_FFN_COMBINE_KERNEL_HPP
#define DISPATCH_FFN_COMBINE_KERNEL_HPP

#include "kernel_operator.h"
#include "dispatch_ffn_combine_profile.h"

#include "catlass/catlass.hpp"
#include "catlass/arch/cross_core_sync.hpp"
#include "catlass/arch/resource.hpp"
#include "catlass/coord.hpp"
#include "catlass/detail/callback.hpp"
#include "catlass/gemm_coord.hpp"
#include "catlass/matrix_coord.hpp"
#include "catlass/epilogue/tile/tile_copy.hpp"

#ifndef HCCL_COMM
    #include "block_mmad_preload_async_fixpipe_quant.hpp"
    #include "copy_gm_to_l1_custom.hpp"
    #include "block_epilogue_pertoken_row.hpp"
    #include "block_epilogue_pertoken_v2.hpp"
    #include "block_epilogue_pertoken_swiglu.hpp"
    #include "hccl_shmem.hpp"
    #include "const_args.hpp"
    #include "layout3d.hpp"
    #include "tiling/moe_init_routing_quant_v2_tiling.h"
    #include "moe_init_routing_quant_v2/moe_init_routing_quant_v2.cpp"
    #include "moe_init_routing_quant_v2/moe_v2_fullload_dynamic_quant.h"
    #include "moe_token_unpermute.h"
    #include "get_tensor_addr.hpp"
    inline __gm__ struct OpSystemRunCfg g_opSystemRunCfg{Catlass::L2_OFFSET};
#else
    #include "utils/block_mmad_preload_async_fixpipe_quant.hpp"
    #include "utils/copy_gm_to_l1_custom.hpp"
    #include "utils/block_epilogue_pertoken_row.hpp"
    #include "utils/block_epilogue_pertoken_v2.hpp"
    #include "utils/block_epilogue_pertoken_swiglu.hpp"
    #include "utils/hccl_shmem.hpp"
    #include "utils/const_args.hpp"
    #include "utils/layout3d.hpp"
    #include "moe_init_routing_quant_v2/moe_init_routing_quant_v2_tiling.h"
    #include "moe_init_routing_quant_v2/moe_init_routing_quant_v2.cpp"
    #include "moe_init_routing_quant_v2/moe_v2_fullload_dynamic_quant.h"
    #include "unpermute/moe_token_unpermute.h"
    #include "utils/get_tensor_addr.hpp"
#endif

using namespace AscendC;

namespace Catlass::Gemm::Kernel {

constexpr uint16_t SYNCFLAGC2V = 9;
constexpr uint16_t SYNCFLAGV2C = 10;

template <
    class BlockMmad_,
    class BlockScheduler_,
    class ElementGroupList_,
    class BlockEpilogue1_,
    class BlockEpilogue2_,
    class BlockEpilogue3_
>
class DispatchFFNCombineKernel {
public:
    using BlockMmad = BlockMmad_;
    using ArchTag = typename BlockMmad::ArchTag;
    using L1TileShape = typename BlockMmad::L1TileShape;
    using ElementA = typename BlockMmad::ElementA;
    using LayoutA = typename BlockMmad::LayoutA;
    using ElementB = typename BlockMmad::ElementB;
    using LayoutB = typename BlockMmad::LayoutB;
    using ElementC = typename BlockMmad::ElementC;
    using LayoutC = typename BlockMmad::LayoutC;
    using ElementAccumulator = typename BlockMmad::ElementAccumulator;
    using ElementScale = uint64_t;
    using LayoutScale = typename layout::VectorLayout;
    using ElementPerTokenScale = float;
    using LayoutPerTokenScale = typename layout::VectorLayout;
    using BlockScheduler = BlockScheduler_;
    
    using BlockEpilogue1 = BlockEpilogue1_;
    using BlockEpilogue2 = BlockEpilogue2_;
    using BlockEpilogue3 = BlockEpilogue3_;

    using ElementD1 = typename BlockEpilogue1::ElementD;
    using LayoutD1 = typename BlockEpilogue1::LayoutD;
    using ElementD2 = typename BlockEpilogue2::ElementD;
    using LayoutD2 = typename BlockEpilogue2::LayoutD;

    /// Parameters structure
    struct Params {
        // Data members
        GemmCoord problemShape;
        __gm__ ElementA *ptrA;
        LayoutA layoutA;
        LayoutA layoutA2;
        GM_ADDR ptrB1;
        LayoutB layoutB1;
        GM_ADDR ptrB2;
        LayoutB layoutB2;
        GM_ADDR ptrScale1;
        LayoutScale layoutScale1;
        GM_ADDR ptrScale2;
        LayoutScale layoutScale2;
        __gm__ ElementD2 *ptrOutput;
        LayoutD1 layoutD1;
        LayoutD2 layoutD2;
        GM_ADDR ptrWorkspace;
        GM_ADDR ptrExpertTokenNums;
        int32_t EP;
        int32_t listLen;
        int32_t expertPerRank;
        uint32_t maxOutputSize;
        uint32_t rank;
        uint32_t rankSize;
        int32_t ubMoveNum;
        GM_ADDR symmetricPtr;
        //--------------
        GM_ADDR expertIdx;
        GM_ADDR moeInitRoutingQuantV2Scale;
        GM_ADDR moeInitRoutingQuantV2Offset;
        GM_ADDR expandedX;
        GM_ADDR expandedRowIdx;
        GM_ADDR expertTokensCountOrCumsum;
        GM_ADDR expertTokensBeforeCapacity;
        GM_ADDR dynamicQuantScale;
        GM_ADDR probs;
        GM_ADDR ptrXActiveMask;
        int64_t topK;
        uint64_t initRoutingQuantTilingKey;
        uint32_t epilogueCoreNum;
        uint32_t epilogueGranularity;
        optiling::MoeInitRoutingQuantV2TilingData moeInitRoutingQuantV2TilingData;
        uint64_t profileGmOffset;
        //--------------

        // Methods
        CATLASS_HOST_DEVICE
        Params() {}

        CATLASS_HOST_DEVICE
        Params(
            GemmCoord problemShape_,
            uint32_t EP_, uint32_t listLen_, uint32_t expertPerRank_, uint32_t maxOutputSize_,
            uint32_t rank_, uint32_t rankSize_, int64_t topK_,
            uint64_t initRoutingQuantTilingKey_, uint32_t epilogueCoreNum_, uint32_t epilogueGranularity_,
            GM_ADDR ptrA_, LayoutA layoutA_, LayoutA layoutA2_,
            GM_ADDR ptrB1_, LayoutB layoutB1_,
            GM_ADDR ptrB2_, LayoutB layoutB2_,
            GM_ADDR ptrScale1_, LayoutScale layoutScale1_,
            GM_ADDR ptrScale2_, LayoutScale layoutScale2_,
            GM_ADDR ptrOutput_, LayoutD2 layoutD1_, LayoutD2 layoutD2_,
            GM_ADDR expertIdx_, GM_ADDR moeInitRoutingQuantV2Scale_,
            GM_ADDR moeInitRoutingQuantV2Offset_,
            GM_ADDR expertTokensBeforeCapacity_, GM_ADDR probs_,
            GM_ADDR ptrWorkspace_, GM_ADDR gmExpertTokenNums_, int32_t ubMoveNum_,
            GM_ADDR ptrXActiveMask_,
            optiling::MoeInitRoutingQuantV2TilingData moeInitRoutingQuantV2TilingData_,
            uint64_t profileGmOffset_ = 0
        ) : problemShape(problemShape_),
            EP(EP_), listLen(listLen_), expertPerRank(expertPerRank_), maxOutputSize(maxOutputSize_),
            rank(rank_), rankSize(rankSize_), topK(topK_),
            initRoutingQuantTilingKey(initRoutingQuantTilingKey_),
            epilogueCoreNum(epilogueCoreNum_), epilogueGranularity(epilogueGranularity_),
            ptrA(reinterpret_cast<__gm__ ElementA *>(ptrA_)), layoutA(layoutA_), layoutA2(layoutA2_),
            ptrB1(ptrB1_), layoutB1(layoutB1_),
            ptrB2(ptrB2_), layoutB2(layoutB2_),
            ptrScale1(ptrScale1_), layoutScale1(layoutScale1_),
            ptrScale2(ptrScale2_), layoutScale2(layoutScale2_),
            ptrOutput(reinterpret_cast<__gm__ ElementD2 *>(ptrOutput_)), layoutD1(layoutD1_), layoutD2(layoutD2_),
            expertIdx(expertIdx_), moeInitRoutingQuantV2Scale(moeInitRoutingQuantV2Scale_),
            moeInitRoutingQuantV2Offset(moeInitRoutingQuantV2Offset_), 
            expertTokensBeforeCapacity(expertTokensBeforeCapacity_), probs(probs_),
            ptrWorkspace(ptrWorkspace_), ptrExpertTokenNums(gmExpertTokenNums_), ubMoveNum(ubMoveNum_),
            ptrXActiveMask(ptrXActiveMask_),
            moeInitRoutingQuantV2TilingData(moeInitRoutingQuantV2TilingData_),
            profileGmOffset(profileGmOffset_)
        {
        }
    };

    // Methods
    CATLASS_DEVICE
    DispatchFFNCombineKernel(Params const &params)
    {
        if ASCEND_IS_AIC {
            coreIdx = AscendC::GetBlockIdx();
            coreNum = AscendC::GetBlockNum();
        }

        if ASCEND_IS_AIV {
            coreIdx = get_block_idx() + get_subblockid() * get_block_num();
            coreNum = get_block_num() * get_subblockdim();
        }

        initBuffer(params);
    }

    CATLASS_DEVICE
    ~DispatchFFNCombineKernel()
    {
    }

    template <int32_t CORE_TYPE = g_coreType>
    CATLASS_DEVICE
    void operator()(Params const &params);

    template <>
    CATLASS_DEVICE
    void operator()<AscendC::AIC>(Params const &params)
    {
        GMM1(params);
        AscendC::CrossCoreWaitFlag<0x2>(SYNCFLAGV2C);
        GMM2(params);
    }


    template <>
    CATLASS_DEVICE
    void operator()<AscendC::AIV>(Params const &params)
    {
        DispatchAndCombine(params);
    }

private:
    CATLASS_DEVICE void initBuffer(Params const &params) {
        #ifndef HCCL_COMM
            shmem.initShmem(params.symmetricPtr, params.rank, params.rankSize);
        #endif
        workspaceInfo = WorkspaceInfo(params);
        peermemInfo = PeermemInfo(params, shmem);
        cumsumMM.SetGlobalBuffer(reinterpret_cast<__gm__ int32_t*>(workspaceInfo.ptrcumsumMM));
        gmA.SetGlobalBuffer(reinterpret_cast<__gm__ ElementA *>(workspaceInfo.ptrA));
        gmC.SetGlobalBuffer(reinterpret_cast<__gm__ ElementC *>(workspaceInfo.ptrC));
        gmPermutedToken.SetGlobalBuffer(reinterpret_cast<__gm__ ElementD1 *>(workspaceInfo.ptrPermutedToken));
        gmC2.SetGlobalBuffer(reinterpret_cast<__gm__ ElementC *>(workspaceInfo.ptrC2));
        gmPerTokenScale1.SetGlobalBuffer(reinterpret_cast<__gm__ ElementPerTokenScale *>(workspaceInfo.ptrPerTokenScale));
        gmPerTokenScale2.SetGlobalBuffer(reinterpret_cast<__gm__ ElementPerTokenScale *>(workspaceInfo.ptrPerTokenScale2));
        tokenPerExpert.SetGlobalBuffer(reinterpret_cast<__gm__ int32_t *>(shmem() + peermemInfo.offsetPeerTokenPerExpert));
        paddedExpertNumAligned = AlignUp(params.EP * params.expertPerRank + 1, ALIGN_128);
        tokenPerExpertLayout = Layout3D(paddedExpertNumAligned, params.expertPerRank);
        preSumBeforeRank.SetGlobalBuffer(reinterpret_cast<__gm__ int32_t*>(workspaceInfo.ptrSumBeforeRank));
        gmXActiveMask.SetGlobalBuffer(reinterpret_cast<__gm__ bool*>(params.ptrXActiveMask));
        
        isCombineV1 = true;
        if (params.problemShape.m() * params.topK <= 4096) {
            isCombineV1 = false;
        }

#if DISPATCH_FFN_COMBINE_PROFILE
        profileStageBuf_ = nullptr;
        if (params.profileGmOffset != 0) {
            profileStageBuf_ =
                reinterpret_cast<__gm__ int32_t*>(params.ptrWorkspace + params.profileGmOffset);
            if (ASCEND_IS_AIV && DffcProfileIsAivWriter(coreIdx)) {
                DffcProfileInit(profileStageBuf_);
            }
        }
#endif
    }

    template<typename T>
    CATLASS_DEVICE void CopyGMToGM(
        AscendC::GlobalTensor<T> dst,
        AscendC::GlobalTensor<T> src,
        int32_t elemNum,
        int32_t ubMoveNum
    )
    {
        AscendC::SetFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID0);
        AscendC::SetFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID1);

        using TType = Gemm::GemmType<T, layout::RowMajor>;
        using CopyGmToUb = Epilogue::Tile::CopyGm2Ub<ArchTag, TType>;
        using CopyUbToGm = Epilogue::Tile::CopyUb2Gm<ArchTag, TType>;
        CopyGmToUb copyGmToUb;
        CopyUbToGm copyUbToGm;
        constexpr int32_t BufferNum = 2;
        int tmpBufferSize = 32 * 1024 / sizeof(T);   // 32 KB
        AscendC::LocalTensor<T> tmpBuffer1 = resource.ubBuf.template GetBufferByByte<T>(0);
        tmpBuffer1.SetSize(tmpBufferSize);
        int tmpBufferOffset = 96 * 1024; // half of UB
        AscendC::LocalTensor<T> tmpBuffer2 = resource.ubBuf.template GetBufferByByte<T>(tmpBufferOffset);
        tmpBuffer2.SetSize(tmpBufferSize);

        // [ReduceScatter] 2. Pre Interface Sync
        int pingpongId = 0;
        auto processCount = CeilDiv(elemNum, ubMoveNum);
        for (uint32_t processIndex = 0; processIndex < processCount; ++processIndex) {
            uint32_t curProcessNum = (processIndex == processCount - 1) ? elemNum - ubMoveNum * (processCount - 1) : ubMoveNum;
            AscendC::TEventID EVENT_ID = pingpongId == 0 ? EVENT_ID0 : EVENT_ID1;
            AscendC::LocalTensor<T> buf = pingpongId == 0 ? tmpBuffer1 : tmpBuffer2;
            auto processOffset = processIndex * ubMoveNum;

            auto inputOffset = processOffset;
            auto outputOffset = processOffset;
            // [ReduceScatter] 2. Pre Interface Sync
            AscendC::WaitFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID);
            // [ReduceScatter] 3. Start shmem_mte_get_mem_nbi
            copyGmToUb(buf, src[inputOffset], layout::RowMajor{ 1, curProcessNum}, layout::RowMajor{1, curProcessNum});
            AscendC::SetFlag<AscendC::HardEvent::MTE2_MTE3>(EVENT_ID);
            AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE3>(EVENT_ID);
            copyUbToGm(dst[outputOffset], buf, layout::RowMajor{ 1, curProcessNum}, layout::RowMajor{1, curProcessNum});

            // [ReduceScatter] 4. Post Interface Sync
            AscendC::SetFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID);
            pingpongId = (pingpongId + 1) % BufferNum;
        }
        // [ReduceScatter] 4. Post Interface Sync

        AscendC::WaitFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID0);
        AscendC::WaitFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID1);
    }

    template<typename T>
    CATLASS_DEVICE void CopyGMToGMPerToken(
        AscendC::GlobalTensor<T> dst,
        AscendC::GlobalTensor<float> dstScale,
        AscendC::GlobalTensor<T> src,
        int32_t rows,
        int32_t hiddenSize,
        int32_t ubMoveNum,
        int32_t& pingpongId
    ) {

        constexpr int32_t BufferNum = 2;
        AscendC::LocalTensor<T> tmpBuffer1 = resource.ubBuf.template GetBufferByByte<T>(0);
        constexpr int tmpBufferOffset = 96 * 1024; // half of UB
        AscendC::LocalTensor<T> tmpBuffer2 = resource.ubBuf.template GetBufferByByte<T>(tmpBufferOffset);
        uint32_t copyInNum = hiddenSize + UB_ALIGN;
        auto processCount = CeilDiv(rows, ubMoveNum);
        for (uint32_t processIndex = 0; processIndex < processCount; ++processIndex) {
            pingpongId = (pingpongId + 1) % BufferNum;
            AscendC::TEventID EVENT_ID = pingpongId == 0 ? EVENT_ID0 : EVENT_ID1;
            AscendC::LocalTensor<T> buf = pingpongId == 0 ? tmpBuffer1 : tmpBuffer2;
            AscendC::LocalTensor<float> bufScale = buf[hiddenSize].template ReinterpretCast<float>();
            auto inputOffset = processIndex * ubMoveNum * copyInNum;
            
            int32_t rowNum = ubMoveNum;
            if (processIndex == processCount - 1) {
                rowNum = rows - processIndex * ubMoveNum;
            }

            AscendC::WaitFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID);
            int64_t dataLen = rowNum * copyInNum;
            AscendC::DataCopy(buf, src[inputOffset], dataLen);

            AscendC::SetFlag<AscendC::HardEvent::MTE2_MTE3>(EVENT_ID);
            AscendC::WaitFlag<AscendC::HardEvent::MTE2_MTE3>(EVENT_ID);
            auto outputOffset = processIndex * ubMoveNum * hiddenSize;
            #define U16(x) static_cast<uint16_t>(x)
            AscendC::DataCopyPad(dst[outputOffset], 
                buf, {U16(rowNum), U16(hiddenSize), 1, 0, 0});
            AscendC::DataCopyPad(dstScale[processIndex * ubMoveNum], 
                bufScale, {U16(rowNum), U16(sizeof(float)), static_cast<uint32_t>(hiddenSize / 32), 0, 0});
            AscendC::SetFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID);
            
        }
    }
    
    // 如果提供了 xActiveMask，让 inactive token 不参与 routing
    CATLASS_DEVICE
    void ApplyXActiveMask(Params const &params) {
        if (params.ptrXActiveMask == nullptr) {
            return;
        }
        int32_t m = params.problemShape.m();
        int32_t topK = params.topK;
        int32_t expertNum = params.expertPerRank * params.EP;
        AscendC::GlobalTensor<int32_t> expertIdxGm;
        expertIdxGm.SetGlobalBuffer(reinterpret_cast<__gm__ int32_t*>(params.expertIdx));

        int32_t totalElements = m * topK;
        int32_t base = totalElements / coreNum;
        int32_t rem = totalElements % coreNum;

        int32_t startIdx = coreIdx * base + min(coreIdx, rem);
        int32_t endIdx = (coreIdx + 1) * base + min(coreIdx + 1, rem);

        AscendC::LocalTensor<int32_t> tmpExpertIdx = resource.ubBuf.template GetBufferByByte<int32_t>(0);
        int32_t copySize = endIdx - startIdx;

        AscendC::DataCopyPad(tmpExpertIdx[0], expertIdxGm[startIdx], 
                    {1, static_cast<uint16_t>(copySize * sizeof(int32_t)), 0, 0}, {}
        );

        AscendC::SetFlag<AscendC::HardEvent::MTE2_S>(EVENT_ID0);
        AscendC::WaitFlag<AscendC::HardEvent::MTE2_S>(EVENT_ID0);

        for (int32_t i = 0; i < copySize; ++i) {
            int32_t tokenIdx = (startIdx + i) / topK;
            bool isActive = gmXActiveMask(tokenIdx);
            if (!isActive) {
                tmpExpertIdx.SetValue(i, expertNum);
            }
        }

        AscendC::SetFlag<AscendC::HardEvent::S_MTE3>(EVENT_ID0);
        AscendC::WaitFlag<AscendC::HardEvent::S_MTE3>(EVENT_ID0);
        AscendC::DataCopyPad(expertIdxGm[startIdx], tmpExpertIdx[0], {1, static_cast<uint16_t>(copySize * sizeof(int32_t)), 0, 0, 0});
        AscendC::SyncAll<true>();
    }
    CATLASS_DEVICE
    void GetCumsumForMMAIV(
        AscendC::GlobalTensor<int32_t> & tokenPerExpert, // 输入：全局内存中的 Token 计数表，形状通常为 [EP, expertPerRank]
        AscendC::GlobalTensor<int32_t> & result,         // 输出：全局内存中的累加前缀和结果
        uint32_t expertPerRank,                          // 每个 Rank 拥有的实际专家数
        uint32_t rankId,                                 // 当前 Rank 的 ID
        uint32_t EP                                      // 整个集群的总专家并行度（Expert Parallelism，即总 Rank 数/总卡数）
    )
    {
        // 1. 将实际专家数向上对齐到 8 的倍数（昇腾 Vector 引擎处理 int32 时的推荐对齐单位，保证指令高效执行）
        int32_t expertPerRankAligned = (expertPerRank + 8 - 1) / 8 * 8;
        
        // 2. 从片上 Unified Buffer (UB) 划分两块临时缓冲区
        // tmpBuffer1: 用于暂存从全局内存搬运上来的、未累加的原始 Token 计数
        AscendC::LocalTensor<int32_t> tmpBuffer1 = resource.ubBuf.template GetBufferByByte<int32_t>(0);
        // tmpResult: 划分出的第二块缓冲区（此处代码声明了但后续未直接使用，可能为预留或通过偏移量隐式管理）
        AscendC::LocalTensor<int32_t> tmpResult = resource.ubBuf.template GetBufferByByte<int32_t>(EP * expertPerRank * sizeof(int32_t));
        
        #define U16(x) static_cast<uint16_t>(x)

        // 3. 异步数据搬运 (MTE2)：从全局内存 (GM) 拷贝当前 Rank 关心的 Token 计数到片上 UB (tmpBuffer1)
        // 使用 DataCopyPad 是因为 GM 上的数据可能存在非连续存储（Padded），搬运时需要自动进行“去填充/对齐”
        AscendC::DataCopyPad(
            tmpBuffer1,
            tokenPerExpert[rankId * expertPerRank], // 起始地址：当前 Rank 对应的专家数据起点
            // DataCopyPadParams 参数设置：
            // U16(EP): 搬运的行数（对应总 Rank 数）
            // U16(expertPerRank * sizeof(int32_t)): 每一行实际要搬运的数据字节数
            // U16((paddedExpertNumAligned - expertPerRank) * sizeof(int32_t)): 源内存中每一行末尾需要跳过的填充（Pad）字节数
            // 0: 目的内存（UB）中每一行末尾需要填充的字节数
            {U16(EP), U16(expertPerRank * sizeof(int32_t)), U16((paddedExpertNumAligned - expertPerRank) * sizeof(int32_t)), 0},
            {}
        );

        // 4. 管道同步：设置并等待 MTE2_V 事件，确保数据已完全从 GM 搬运到片上 UB，Vector 引擎才能开始计算
        AscendC::SetFlag<AscendC::HardEvent::MTE2_V>(EVENT_ID0);
        AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(EVENT_ID0);

        // =====================================================================
        // 【核心计算：跨 Rank 累加 (Cumulative Sum)】
        // 目的：计算每个专家在不同 Rank 之间的累加 Token 数
        // =====================================================================
        for (uint32_t i = 1; i < EP; ++i) {
            // 将当前行（第 i 行）的专家计数，与前一行（第 i-1 行）的累加结果相加，并就地覆盖写入当前行
            // 这里的偏移量使用的是对齐后的 expertPerRankAligned，确保 Vector 引擎访存对齐
            AscendC::Add(
                tmpBuffer1[i * expertPerRankAligned],       // 目的操作数 & 源操作数 1 (当前行)
                tmpBuffer1[i * expertPerRankAligned],       // 源操作数 2 (当前行)
                tmpBuffer1[(i - 1) * expertPerRankAligned], // 源操作数 3 (上一行已累加的结果)
                expertPerRank                               // 实际计算的元素个数（非对齐的实际专家数）
            );
            // 向量指令屏障：确保当前行的加法完全执行完毕，下一轮循环才能安全读取这一行的结果
            AscendC::PipeBarrier<PIPE_V>();
        }

        // 5. 管道同步：设置并等待 V_MTE3 事件，确保 Vector 引擎的累加计算全部完成，MTE3 引擎才能向外写回
        AscendC::SetFlag<AscendC::HardEvent::V_MTE3>(EVENT_ID0);
        AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(EVENT_ID0);

        // 6. 异步数据搬运 (MTE3)：将计算好的累加前缀和结果从片上 UB 写回到全局内存 (result)
        AscendC::DataCopyPad(
            result,
            tmpBuffer1,
            // {行数, 每行写回字节数, 源跳过, 目的填充}
            {U16(EP), U16((expertPerRank) * sizeof(int32_t)), 0, 0}
        );
    }


    // AIC 侧 FFN 第一层 GEMM：gmA × w1 → gmC。
    // 按本地 expert 组（groupIdx）循环；每组 M 维由 cumsumMM 决定。
    // 与 AIV 通过 syncgmmIdx 握手：AIV Pull 完一组 token 后 SetFlag，AIC 才能读 gmA 做该组 GEMM。
    CATLASS_DEVICE
    void GMM1(Params const &params){
        DFFC_PROFILE_STAGE_BEGIN(profileStageBuf_, DFFC_PHASE_GMM1);
        icache_preload(8);
        BlockScheduler blockScheduler;   // 将每组 GEMM 切成 L1Tile 并分配给多 AIC core
        BlockMmad blockMmad(resource);   // 异步 Cube matmul 封装
        float aivFinishGroups = 0.0f;
        __gm__ float* aivFinishPtr = workspaceInfo.ptrSoftFlagBase + params.EP * FLAGSTRIDE;

        // 跨 expert 组累加的 GM 偏移：A/B/C 在 workspace 中按组连续存放
        int64_t gmGroupOffsetA = 0;
        int64_t gmGroupOffsetB = 0;
        int64_t gmGroupOffsetC = 0;
        uint32_t startCoreIdx = 0;       // BlockScheduler 轮转起点，保证各 core 负载均衡
        uint32_t syncGroupIdx = 0;       // 已收到 AIV Pull 完成的 group 数（与 syncgmmIdx 对应）
        int64_t preCurrentmSum = 0;      // 已写入 gmA/gmC 的 token 行累计数，用于 maxOutputSize 截断
        int32_t syncLoopIdx = -1;        // 传给 Finalize 的 SwiGLU 波次编号

        // --- 等待 AIV 完成 cumsumMM（对应 AIV 侧 CrossCoreSetFlag(0)）---
        uint16_t syncgmmIdx = 0;
        AscendC::CrossCoreWaitFlag<0x2>(syncgmmIdx / CROSS_CORE_FLAG_MAX_SET_COUNT);
        syncgmmIdx++;

        // 逐本地 expert 组做 GMM1：每组 problemShape.m = 所有 rank 发往本 rank 该 expert 的 token 总数
        for (uint32_t groupIdx = 0; groupIdx < params.expertPerRank; ++groupIdx) {
            // cumsum 末行 = 该 expert 组的全局 M 维
            uint32_t currentM = cumsumMM((params.EP - 1) * params.expertPerRank + groupIdx);
            // 超出 maxOutputSize 时截断或跳过，防止 workspace 越界
            if (preCurrentmSum >= params.maxOutputSize) {
                currentM = 0;
            } else if (preCurrentmSum + currentM >= params.maxOutputSize) {
                currentM = params.maxOutputSize - preCurrentmSum;
            }
            AscendC::GlobalTensor<ElementB> gmB1;
            AscendC::GlobalTensor<ElementScale> gmS;
            // listLen==1 时所有 expert 共享同一份 w1；否则每组独立权重
            int32_t arrayGroupIdx = params.listLen == 1 ? 0 : groupIdx;
            gmB1.SetGlobalBuffer(reinterpret_cast<__gm__ ElementB *>(GetTensorAddr<int8_t>(arrayGroupIdx, params.ptrB1)));
            gmS.SetGlobalBuffer(reinterpret_cast<__gm__ ElementScale *>(GetTensorAddr<int64_t>(arrayGroupIdx, params.ptrScale1)));
            // M 较小时禁用 B 的 L2 cache，避免污染
            if (currentM <= L1TileShape::M) {
                gmB1.SetL2CacheHint(AscendC::CacheMode::CACHE_MODE_DISABLE);
            }
            GemmCoord inGroupProblemShape{currentM, params.problemShape.n(), params.problemShape.k()};
            LayoutA layoutA = params.layoutA.GetTileLayout(inGroupProblemShape.GetCoordMK());
            LayoutB layoutB1 = params.layoutB1;
            LayoutScale layoutScale = params.layoutScale1;
            LayoutC layoutC = LayoutC(inGroupProblemShape.m(), inGroupProblemShape.n());
            blockScheduler.Update(inGroupProblemShape, MakeCoord(L1TileShape::M, L1TileShape::N));
            uint32_t coreLoops = blockScheduler.GetCoreLoops();
            // 当前 core 在本 group 内的起始 tile 编号（多 core 按 loopIdx += coreNum 分片）
            uint32_t startLoopIdx = ((coreIdx < startCoreIdx) ? (coreIdx + coreNum) : coreIdx) - startCoreIdx;

            for (uint32_t loopIdx = startLoopIdx; loopIdx < coreLoops; loopIdx += coreNum) {
                // 追平 AIV Pull 进度：groupIdx 组 token 未 pull 完则阻塞
                // syncGroupIdx 从 0 递增，每收到一次 AIV SetFlag 前进一组
                for(;syncGroupIdx <= groupIdx; syncGroupIdx++) {
                    AscendC::CrossCoreWaitFlag<0x2>(syncgmmIdx / CROSS_CORE_FLAG_MAX_SET_COUNT);
                    syncgmmIdx ++;
                }

                // 当前 tile 在组内 M/N/K 方向的逻辑坐标
                GemmCoord blockCoord = blockScheduler.GetBlockCoord(loopIdx);
                GemmCoord actualBlockShape = blockScheduler.GetActualBlockShape(blockCoord);
                MatrixCoord offsetA{blockCoord.m() * L1TileShape::M, blockCoord.k() * L1TileShape::K};
                MatrixCoord offsetB{blockCoord.k() * L1TileShape::K, blockCoord.n() * L1TileShape::N};
                MatrixCoord offsetC{blockCoord.m() * L1TileShape::M, blockCoord.n() * L1TileShape::N};
                int64_t gmOffsetA = layoutA.GetOffset(offsetA);
                int64_t gmOffsetB = layoutB1.GetOffset(offsetB);
                int64_t gmOffsetC = layoutC.GetOffset(offsetC);
                // scale 按 N tile 索引；共享 w1 时需加上 groupIdx 在 N 维的偏移
                int64_t gmOffsetS = blockCoord.n() * L1TileShape::N + (params.listLen == 1 ? groupIdx * params.problemShape.n() : 0);
                if (currentM > 0) {
                    // gmA：AIV Pull 后的量化 token；gmC：GMM1 输出，供 AIV SwiGLU 消费
                    blockMmad(
                        gmA[gmGroupOffsetA + gmOffsetA], layoutA,
                        gmB1[gmGroupOffsetB + gmOffsetB], layoutB1,
                        gmC[gmGroupOffsetC + gmOffsetC], layoutC,
                        gmS[gmOffsetS], layoutScale,
                        actualBlockShape
                    );
                }
            }

            // epilogueGranularity 将 expert 组分两波：第一波 GMM1 完成后提前通知 AIV 做 SwiGLU，与后续 GMM1 重叠
            if ((groupIdx + 1) == params.epilogueGranularity  && (groupIdx < params.expertPerRank - 1)) {
                syncLoopIdx ++;
                if constexpr (BlockMmad::DispatchPolicy::ASYNC) {
                    blockMmad.SynchronizeBlock();
                }
                // SYNCFLAGC2V：AIC → AIV，第一波 GMM1 输出 gmC 就绪
                blockMmad.Finalize(syncLoopIdx, SYNCFLAGC2V);
            }

            preCurrentmSum += currentM;
            gmGroupOffsetA += inGroupProblemShape.m() * inGroupProblemShape.k();
            if (params.listLen == 1) {
                gmGroupOffsetB += inGroupProblemShape.k() * inGroupProblemShape.n();
            }
            gmGroupOffsetC += inGroupProblemShape.m() * inGroupProblemShape.n();
            startCoreIdx = (startCoreIdx  + coreLoops) % coreNum;
        }

        // 补等尚未 Pull 完成的尾部 expert 组（若 GEMM tile 先于 Pull 跑完）
        for(;syncGroupIdx < params.expertPerRank; syncGroupIdx++) {
            AscendC::CrossCoreWaitFlag<0x2>(syncgmmIdx / CROSS_CORE_FLAG_MAX_SET_COUNT);
            syncgmmIdx ++;
        }

        if constexpr (BlockMmad::DispatchPolicy::ASYNC) {
            blockMmad.SynchronizeBlock();
        }
        // SYNCFLAGC2V：全部 GMM1 完成（或第二波），通知 AIV SwiGLU
        blockMmad.Finalize(syncLoopIdx + 1, SYNCFLAGC2V);
        DFFC_PROFILE_STAGE_END(profileStageBuf_, DFFC_PHASE_GMM1);
    }

    CATLASS_DEVICE
    void GMM2(Params const &params) {
        DFFC_PROFILE_STAGE_BEGIN(profileStageBuf_, DFFC_PHASE_GMM2);
        icache_preload(8);
        BlockScheduler blockScheduler;
        BlockMmad blockMmad(resource);

        uint32_t n2 = params.problemShape.k();
        uint32_t k2 = params.problemShape.n() / 2;

        int64_t gmGroupOffsetA = 0;
        int64_t gmGroupOffsetB = 0;
        int64_t gmGroupOffsetC = 0;

        uint32_t startCoreIdx = 0;

        int64_t preCurrentmSum = 0;
        int32_t syncLoopIdx = -1;
        uint32_t lastDequantExpertNum = params.expertPerRank;

        if (params.epilogueGranularity < params.expertPerRank) {
            lastDequantExpertNum = params.expertPerRank - params.epilogueGranularity;
        }

        for (uint32_t groupIdx = 0; groupIdx < params.expertPerRank; ++groupIdx) {
            uint32_t currentM = cumsumMM((params.EP - 1) * params.expertPerRank + groupIdx);
            if (preCurrentmSum >= params.maxOutputSize) {
                currentM = 0;
            } else if (preCurrentmSum + currentM > params.maxOutputSize) {
                currentM = params.maxOutputSize - preCurrentmSum;
            } 
            AscendC::GlobalTensor<ElementB> gmB2;
            AscendC::GlobalTensor<ElementScale> gmS2;
            int32_t arrayGroupIdx = params.listLen == 1 ? 0 : groupIdx;
            gmB2.SetGlobalBuffer(reinterpret_cast<__gm__ ElementB *>(GetTensorAddr<int8_t>(arrayGroupIdx, params.ptrB2)));
            gmS2.SetGlobalBuffer(reinterpret_cast<__gm__ ElementScale *>(GetTensorAddr<int64_t>(arrayGroupIdx, params.ptrScale2)));
            if (currentM <= L1TileShape::M) {
                gmB2.SetL2CacheHint(AscendC::CacheMode::CACHE_MODE_DISABLE);
            }
            GemmCoord inGroupProblemShape{currentM, n2, k2}; // M N K

            LayoutA layoutA = params.layoutA2.GetTileLayout(inGroupProblemShape.GetCoordMK());
            LayoutB layoutB2 = params.layoutB2;
            LayoutScale layoutScale = params.layoutScale2;
            LayoutC layoutC = LayoutC(inGroupProblemShape.m(), inGroupProblemShape.n());

            blockScheduler.Update(inGroupProblemShape, MakeCoord(L1TileShape::M, L1TileShape::N));
            uint32_t coreLoops = blockScheduler.GetCoreLoops();

            // Determine the starting loopIdx of the current core under the current groupIdx
            uint32_t startLoopIdx = ((coreIdx < startCoreIdx) ? (coreIdx + coreNum) : coreIdx) - startCoreIdx;
            // Loop through the matmul of each groupIdx
            if (params.expertPerRank > lastDequantExpertNum && groupIdx + 1 == params.expertPerRank - lastDequantExpertNum) {
                AscendC::CrossCoreWaitFlag<0x2>(SYNCFLAGV2C);
            }

            for (uint32_t loopIdx = startLoopIdx; loopIdx < coreLoops; loopIdx += coreNum) {
                if (loopIdx + coreNum >= coreLoops) {
                    syncLoopIdx = groupIdx;
                }

                // Compute block location
                GemmCoord blockCoord = blockScheduler.GetBlockCoord(loopIdx);
                GemmCoord actualBlockShape = blockScheduler.GetActualBlockShape(blockCoord);

                // Compute initial location in logical coordinates
                MatrixCoord offsetA{blockCoord.m() * L1TileShape::M, blockCoord.k() * L1TileShape::K};
                MatrixCoord offsetB{blockCoord.k() * L1TileShape::K, blockCoord.n() * L1TileShape::N};
                MatrixCoord offsetC{blockCoord.m() * L1TileShape::M, blockCoord.n() * L1TileShape::N};

                int64_t gmOffsetA = layoutA.GetOffset(offsetA);
                int64_t gmOffsetB = layoutB2.GetOffset(offsetB);
                int64_t gmOffsetC = layoutC.GetOffset(offsetC);
                int64_t gmOffsetS = blockCoord.n() * L1TileShape::N + (params.listLen == 1 ? groupIdx * n2 : 0);   // One scale group per expert
                if (currentM > 0) {
                    blockMmad(
                            gmPermutedToken[gmGroupOffsetA + gmOffsetA], layoutA,
                            gmB2[gmGroupOffsetB + gmOffsetB], layoutB2,
                            gmC2[gmGroupOffsetC + gmOffsetC], layoutC,
                            gmS2[gmOffsetS], layoutScale,
                            actualBlockShape, syncLoopIdx, 0
                        );
                }
            }
            preCurrentmSum += currentM;
            gmGroupOffsetA += inGroupProblemShape.m() * inGroupProblemShape.k();
            if (params.listLen == 1) {
                gmGroupOffsetB += inGroupProblemShape.k() * inGroupProblemShape.n();
            }
            gmGroupOffsetC += inGroupProblemShape.m() * inGroupProblemShape.n();

            startCoreIdx = (startCoreIdx + coreLoops) % coreNum;
        }
        if constexpr (BlockMmad::DispatchPolicy::ASYNC) {
            blockMmad.SynchronizeBlock();
        }
        if (isCombineV1) {
            blockMmad.Finalize(params.expertPerRank - 1, 0);
        }
        DFFC_PROFILE_STAGE_END(profileStageBuf_, DFFC_PHASE_GMM2);
    }


    CATLASS_DEVICE 
    void InitArithProgress(Params const &params) {
        AscendC::LocalTensor<float> tmpBuffer1 = resource.ubBuf.template GetBufferByByte<float>(0);
        AscendC::SetFlag<AscendC::HardEvent::MTE3_V>(EVENT_ID0);
        AscendC::WaitFlag<AscendC::HardEvent::MTE3_V>(EVENT_ID0);
        AscendC::Duplicate(tmpBuffer1, 0.0f, (params.EP + 1) * FLAGSTRIDE);
        AscendC::SetFlag<AscendC::HardEvent::V_MTE3>(EVENT_ID0);
        AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(EVENT_ID0);

        AscendC::GlobalTensor<float> flagGlobalBase;
        flagGlobalBase.SetGlobalBuffer(workspaceInfo.ptrSoftFlagBase);
        AscendC::DataCopy(flagGlobalBase, tmpBuffer1, (params.EP + 1) * FLAGSTRIDE);
    }

    CATLASS_DEVICE
    void CrossRankSyncAndlocalTokenPerExpertAllGatherAndGetSumPreRankV2(Params const &params, int64_t localTokenPerExpertOffset){
        // 每个 Core 负责处理对齐后的专家数 (paddedExpertNumAligned)
        uint32_t numPerCore = paddedExpertNumAligned;
        
        // 从 Unified Buffer (UB) 中划分临时缓冲区
        // tmpBuffer: 用于暂存从 GM 搬运上来的 tokenPerExpert 计数
        AscendC::LocalTensor<int32_t> tmpBuffer = resource.ubBuf.template GetBufferByByte<int32_t>(0);
        // prevSumBuf: 用于暂存计算得到的前缀和结果
        AscendC::LocalTensor<int32_t> prevSumBuf = tmpBuffer[numPerCore];

        // =====================================================================
        // 【阶段一：推送阶段 (Push)】
        // 将本卡统计的本地 Token 计数加上魔数标记，直接推送到其他所有 Rank 的 Peer Memory (跨卡直接写入)
        // 不使用all2all的原因：内存对齐与硬件搬运的“硬限制”；计算前缀和（Prefix Sum）的“全局依赖性”；
        // =====================================================================
        for(int32_t dstEpIdx = coreIdx; dstEpIdx < params.EP; dstEpIdx += coreNum) {
            // 排除自身，只向其他 Rank 推送数据
            if (dstEpIdx == params.rank) {
                continue;
            }
            
            // 定义源地址：本卡本地统计的 tokenPerExpert 数据的 Global Memory (GM) 地址
            AscendC::GlobalTensor<int32_t> srcAddress;
            srcAddress.SetGlobalBuffer(reinterpret_cast<__gm__ int32_t*>(shmem() + localTokenPerExpertOffset));
            
            // 定义目的地址：目标 Rank 的 Peer Memory 地址 (通过 shmem 接口获取对端物理指针)
            AscendC::GlobalTensor<int32_t> dstAddress;
            __gm__ void* dstPeermemPtr = shmem(localTokenPerExpertOffset, coreIdx);
            dstAddress.SetGlobalBuffer((__gm__ int32_t * )dstPeermemPtr);

            // 设置 MTE3(写) 与 MTE2(读) 之间的硬件事件同步，防止读写冲突
            AscendC::SetFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID0);
            
            // 声明用于在 GM 和 UB 之间拷贝数据的辅助类
            using TType = Gemm::GemmType<int32_t, layout::RowMajor>;
            using CopyGmToUb = Epilogue::Tile::CopyGm2Ub<ArchTag, TType>;
            using CopyUbToGm = Epilogue::Tile::CopyUb2Gm<ArchTag, TType>;
            CopyGmToUb copyGmToUb;
            CopyUbToGm copyUbToGm;
            
            // 等待 MTE3_MTE2 事件完成，确保可以安全读取
            AscendC::WaitFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID0);
            
            // 1. 将本地的 token 计数从 GM 读入片上 UB (tmpBuffer)
            copyGmToUb(tmpBuffer, srcAddress[0], 
                layout::RowMajor{ 1, numPerCore}, 
                layout::RowMajor{1, numPerCore});

            // 管道同步：通知 Vector 引擎，MTE2 读入的数据已就绪
            AscendC::SetFlag<AscendC::HardEvent::MTE2_V>(EVENT_ID0);
            AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(EVENT_ID0);
            
            // 2. 核心同步设计：给计数值加上魔数 0x800000 (代表数据已就绪的 Signal Flag)
            // 接收方通过检测该地址是否非 0 来确认发送方是否已完成写入
            AscendC::Adds(tmpBuffer, tmpBuffer, 0x800000, numPerCore);
            
            // 管道同步：通知 MTE3 引擎，Vector 引擎的加法计算已完成，可以开始向外写数据
            AscendC::SetFlag<AscendC::HardEvent::V_MTE3>(EVENT_ID0);
            AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(EVENT_ID0);
            
            // 3. 将带魔数标记的数据通过 RDMA 直接写入目标 Rank 的 Peer Memory 中
            copyUbToGm(dstAddress[0], tmpBuffer, 
                layout::RowMajor{ 1, numPerCore}, 
                layout::RowMajor{1, numPerCore});
                
            // 再次同步，确保当前 Core 的写操作完全投递
            AscendC::SetFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID0);
            AscendC::WaitFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID0);
        }

        // =====================================================================
        // 【阶段二：接收、校验与前缀和计算阶段 (Wait, Clean & Prefix Sum)】
        // 等待接收其他 Rank 推送过来的数据，校验到达后减去魔数恢复原值，并计算前缀和
        // =====================================================================
        // 将负载分摊给所有的core，从而实现负载均衡（访存的负载和搬运+计算的负载）
        for(int32_t dstEpIdx = coreIdx; dstEpIdx < params.EP; dstEpIdx += coreNum) {
            if (dstEpIdx != params.rank) {
                // 1. 轮询校验：以 Cache Line (512字节) 为步长检查目标 Rank 写入的数据
                int32_t intPer512 = CACHE_LINE / sizeof(int);
                for(int32_t checkIdx = 0; checkIdx < paddedExpertNumAligned; checkIdx += intPer512) {
                    __gm__ int32_t* sync_check = reinterpret_cast<__gm__ int32_t*>(shmem() + peermemInfo.offsetPeerTokenPerExpert) + tokenPerExpertLayout(dstEpIdx, 0, checkIdx);
                    // 阻塞等待，直到该同步指针的值不为 0 (即对端 Rank 已经成功写入了带魔数的数据)
                    gm_signal_wait_until_ne(sync_check, 0);
                }
                
                // 2. 数据确认到达，将接收到的带魔数数据从 GM 读入 UB (tmpBuffer)
                AscendC::DataCopy(tmpBuffer, tokenPerExpert[tokenPerExpertLayout(dstEpIdx, 0, 0)], numPerCore);
                
                // 管道同步：确保 MTE2 读入完毕，Vector 引擎才能开始计算
                AscendC::SetFlag<AscendC::HardEvent::MTE2_V>(EVENT_ID0);
                AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(EVENT_ID0);
                
                // 3. 恢复数据：减去魔数 0x800000，还原出真实的 Token 计数值
                AscendC::Adds(tmpBuffer, tmpBuffer, -0x800000, numPerCore);
                AscendC::PipeBarrier<PIPE_V>(); // 确保 Vector 减法指令完全执行完毕
                
                // 管道同步：通知 MTE3 引擎，数据已还原，可以写回
                AscendC::SetFlag<AscendC::HardEvent::V_MTE3>(EVENT_ID0);
                AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(EVENT_ID0);
                
                // 将还原后的真实 Token 计数写回到本地的 tokenPerExpert 存储区
                AscendC::DataCopy(tokenPerExpert[tokenPerExpertLayout(dstEpIdx, 0, 0)], tmpBuffer, numPerCore);
            } else {
                // 如果是本卡自身的数据，无需轮询和减魔数，直接读入 UB 参与前缀和计算
                AscendC::DataCopy(tmpBuffer, tokenPerExpert[tokenPerExpertLayout(dstEpIdx, 0, 0)], numPerCore);
                AscendC::SetFlag<AscendC::HardEvent::MTE2_V>(EVENT_ID0);
                AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(EVENT_ID0);
            }
            
            // 内存屏障：确保当前所有引擎 (MTE1/MTE2/V/MTE3) 的读写全部对齐
            AscendC::PipeBarrier<PIPE_ALL>();
            
            // 4. 串行计算前缀和 (Prefix Sum)
            // 目的：计算当前 Rank 在全局 Expert 数据排布中的起始偏移量，为随后的 All-to-All 数据路由提供寻址依据
            int32_t prevSum = 0;
            int32_t j = 0;
            for (int32_t i = 0; i < (params.rank + 1) * params.expertPerRank; i++) {
                // 仅记录当前 Rank 之前的所有 Rank 累加的 Token 总数
                if (i >= params.rank * params.expertPerRank) {
                    prevSumBuf(j) = prevSum;
                    j++;
                }
                prevSum += tmpBuffer(i);
            }
            
            // 管道同步：Scalar(标量) 寄存器计算完毕，通知 MTE3 引擎写回 GM
            AscendC::SetFlag<AscendC::HardEvent::S_MTE3>(EVENT_ID0);
            AscendC::WaitFlag<AscendC::HardEvent::S_MTE3>(EVENT_ID0);
            
            // 将计算好的前缀和写回全局内存 preSumBeforeRank
            AscendC::DataCopyPad(preSumBeforeRank[dstEpIdx * params.expertPerRank], prevSumBuf,
            AscendC::DataCopyParams{1, static_cast<uint16_t>(params.expertPerRank * sizeof(int32_t)), 0, 0});
        }

        // 全局同步：确保所有 Core、所有 Rank 的 All-Gather 和前缀和计算完全同步，准备进入下一步计算
        AscendC::SyncAll<true>();
    }


    CATLASS_DEVICE
    void ResetTokenPerExpert(int32_t num)
    {
        if (coreIdx != coreNum - 1) {
            return;
        }
        AscendC::SetFlag<AscendC::HardEvent::MTE3_V>(EVENT_ID0);
        AscendC::WaitFlag<AscendC::HardEvent::MTE3_V>(EVENT_ID0);
        AscendC::LocalTensor<int32_t> tmp = resource.ubBuf.template GetBufferByByte<int32_t>(0);
        AscendC::Duplicate(tmp, 0, num);
        AscendC::SetFlag<AscendC::HardEvent::V_MTE3>(EVENT_ID0);
        AscendC::WaitFlag<AscendC::HardEvent::V_MTE3>(EVENT_ID0);
        AscendC::DataCopy(tokenPerExpert, tmp, num);
    }

    CATLASS_DEVICE
    void UpdateAicFlags(const Params &params)
    {
        float flagBase = 1.0f * params.expertPerRank;
        __gm__ float* aicFinishPtr = workspaceInfo.ptrSoftFlagBase + params.EP * FLAGSTRIDE;
        float flag = 0.0f;
        float lastflag = -1.0f;
        AscendC::LocalTensor<float> tmpBuffer1 = resource.ubBuf.template GetBufferByByte<float>(0);
        __gm__ float* flagPtr = workspaceInfo.ptrSoftFlagBase;
        AscendC::GlobalTensor<float> flagGM;
        flagGM.SetGlobalBuffer(flagPtr);
        int32_t flagBufferSize = max(4, params.EP) * FLAGSTRIDE;
        AscendC::LocalTensor<float> dstValueBuffer = resource.ubBuf.template GetBufferByByte<float>(flagBufferSize);
        AscendC::LocalTensor<float> sharedTmpBuffer = resource.ubBuf.template GetBufferByByte<float>((flagBufferSize + 64));
        uint64_t mask[1] = {0};
        uint32_t repeatNum = (flagBufferSize / (4 * FLAGSTRIDE));
        for (int32_t i = 0; i < 4; i ++) {
            if (i < params.EP) {
                mask[0] |= 1ull * (1ull << (i * 16));
            }
        }
        AscendC::SetFlag<AscendC::HardEvent::S_V>(EVENT_ID0);
        AscendC::WaitFlag<AscendC::HardEvent::S_V>(EVENT_ID0);
        while (flag < flagBase) {
            flag = flagBase;
            AscendC::DataCopy(tmpBuffer1, flagGM, params.EP * FLAGSTRIDE);
            AscendC::SetFlag<AscendC::HardEvent::MTE2_V>(EVENT_ID0);
            AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(EVENT_ID0);

            AscendC::ReduceMin<float>(dstValueBuffer, tmpBuffer1, sharedTmpBuffer, mask, repeatNum, 8, false);

            AscendC::SetFlag<AscendC::HardEvent::V_S>(EVENT_ID0);
            AscendC::WaitFlag<AscendC::HardEvent::V_S>(EVENT_ID0);
            flag = min(flag, dstValueBuffer.GetValue(0));

            if (flag > lastflag) {
                *aicFinishPtr = flag;
                gm_dcci(aicFinishPtr);
                lastflag = flag;
            }
        }
    }


    // AIV 核主路径：路由 → 跨卡同步 → 按 expert 组 Pull token → 与 AIC 流水线配合做 SwiGLU/Combine → Unpermute。
    // 与 AIC 侧 GMM1/GMM2 通过 SYNCFLAGC2V(AIC→AIV)、SYNCFLAGV2C(AIV→AIC) 及 syncgmmIdx 握手。
    CATLASS_DEVICE
    void DispatchAndCombine(Params const &params) {
        DFFC_PROFILE_STAGE_BEGIN(profileStageBuf_, DFFC_PHASE_PREP);
        icache_preload(8);
        // peermem 中 tokenPerExpert 矩阵：本 rank 行、各 dst rank 列、各本地 expert 的深度
        int64_t localTokenPerExpertOffset = peermemInfo.offsetPeerTokenPerExpert + tokenPerExpertLayout(params.rank, 0, 0) * sizeof(int32_t);
        GM_ADDR localTokenPerExpert = shmem() + localTokenPerExpertOffset;
        // expandedRowIdx 放在 workspace 头部，256 对齐后留给 initRouting 的临时区
        uint32_t expandedRowIdxOffset = AlignUp(params.problemShape.m(), 256) * params.topK * sizeof(int32_t);

        // ApplyXActiveMask：若传入 x_active_mask，将 inactive token 的 expert_idx 置为 sentinel（跳过路由）
        ApplyXActiveMask(params);

        // --- Phase 1: InitRouting + 动态量化 ---
        // moe_init_routing_quant_v2：按 expert_idx 排序/映射，量化 x 写入 peermem(offsetA)，排序是为了保证数据的连续性，从而保障GEMM的性能
        // 统计 tokenPerExpert，生成 expandedRowIdx（unpermute 用），per-token scale 写入 offsetPeerPerTokenScale
        moe_init_routing_quant_v2<ElementD2>(reinterpret_cast<GM_ADDR> (params.ptrA), params.expertIdx, 
        params.moeInitRoutingQuantV2Scale, params.moeInitRoutingQuantV2Offset, shmem() + peermemInfo.offsetA, 
        workspaceInfo.expandedRowIdx, localTokenPerExpert, params.expertTokensBeforeCapacity, 
        shmem() + peermemInfo.offsetPeerPerTokenScale, 
        params.ptrWorkspace + expandedRowIdxOffset, 
        &params.moeInitRoutingQuantV2TilingData, params.initRoutingQuantTilingKey);

        AscendC::SyncAll<true>();

        // --- Phase 2: 跨 rank 交换 token 计数 ---
        // CrossRankSyncAnd...AllGather：各 rank 把 tokenPerExpert 写入远端 peermem，自旋等信号后读回；
        // 同时计算 preSumBeforeRank（combine 阶段写回 peermem 的行偏移）
        CrossRankSyncAndlocalTokenPerExpertAllGatherAndGetSumPreRankV2(params, localTokenPerExpertOffset);

        // GetCumsumForMMAIV：对 tokenPerExpert 按 rank 维前缀和 → cumsumMM，供 GMM1/GMM2 确定每组 M 与行偏移
        // 计算得到：到 rank ep 为止，发往本 rank 的 expert groupIdx 的 累计 token 数。
        if (coreIdx == 0) {
            GetCumsumForMMAIV(tokenPerExpert, cumsumMM, params.expertPerRank, params.rank, params.EP);
        }
        
        uint32_t curGroupOffset = 0;
        int32_t prevSumBeforeRank = 0;
        // prevSum：本 rank 在 peermem 源 buffer 中已消费的 token 行数（Pull 读指针）
        // 每个 AIV core（coreIdx < EP）从 Phase 2 写好的 preSumBeforeRank 里，读取 自己负责的那个 rank 分片 的起始偏移。
        int32_t prevSum = 0;
        if (coreIdx < params.EP) {
            prevSum = preSumBeforeRank(coreIdx * params.expertPerRank);
        }
        AscendC::SyncAll<true>();
        
        // 输出每个本地 expert 收到的全局 token 总数（最后一行 cumsum）
        AscendC::GlobalTensor<int32_t> ExpertTokenNums;
        ExpertTokenNums.SetGlobalBuffer(reinterpret_cast<__gm__ int32_t*>(params.ptrExpertTokenNums));
        if(coreIdx == 0)
        {
            // CopyGMToGM：UB ping-pong 搬运 GM→GM（此处为 cumsum 末行 → expert_token_nums）
            // // 把每个本地 expert 收到的全局 token 总数，从内部 workspace 拷到算子对外的输出张量 expert_token_nums
            CopyGMToGM(ExpertTokenNums, cumsumMM[(params.EP - 1) * params.expertPerRank], params.expertPerRank, params.ubMoveNum);
        }
        // 首个 CrossCoreSetFlag：通知 AIC 侧 cumsum 已完成，GMM1 可以开始等 Pull
        uint16_t syncgmm1Idx = 0;
        AscendC::CrossCoreSetFlag<0x2, PIPE_MTE3>(syncgmm1Idx / CROSS_CORE_FLAG_MAX_SET_COUNT);
        syncgmm1Idx++;
        AscendC::SyncAll<true>();
        DFFC_PROFILE_STAGE_END(profileStageBuf_, DFFC_PHASE_PREP);

        // dequantSum1/2：两波 SwiGLU epilogue 各自处理的 token 行数（由 epilogueGranularity 切分）
        uint32_t prevGroupSum1 = 0, dequantSum1 = 0, dequantSum2 = 0;
        uint32_t dequantSum = 0;

        // --- Phase 3: 按本地 expert 组 Pull（Dispatch 侧，与 AIC GMM1 流水线重叠）---
        DFFC_PROFILE_STAGE_BEGIN(profileStageBuf_, DFFC_PHASE_DISPATCH);
        icache_preload(8);
        // ping-pang buffer
        AscendC::SetFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID0);
        AscendC::SetFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID1);
        int32_t pingpongIdx = 0;
        // groupIdx根据expert分组，即循环串行处理每个expert
        for (int32_t groupIdx = 0; groupIdx < params.expertPerRank; ++groupIdx) {
            // currentM：所有 rank 在该 expert 组上的 token 总数（全局 cumsum 末行）
            uint32_t currentM = cumsumMM((params.EP - 1) * params.expertPerRank + groupIdx);
            // AIV 多核按 rank 分片：core i 负责 dstEpIdx = i, i+coreNum, ...
            for(int32_t dstEpIdx = coreIdx; dstEpIdx < params.EP; dstEpIdx += coreNum) {
                // rowStart：该 rank 在本 expert 组内，写入本地 gmA 的起始行（全局 pool 偏移）
                uint32_t rowStart = (dstEpIdx == 0 ? 0 : cumsumMM((dstEpIdx - 1) * params.expertPerRank + groupIdx)) + prevGroupSum1;
                if (rowStart < params.maxOutputSize) {
                    // rows：dstEpIdx 发往本 rank 的该 expert 组 token 数
                    uint32_t rows = tokenPerExpert(tokenPerExpertLayout(dstEpIdx, params.rank, groupIdx));
                    if (rowStart + rows > params.maxOutputSize) {
                        rows = params.maxOutputSize - rowStart;
                    }
                    uint32_t rowSrc = prevSum;
                    prevSum += rows;
                    // 从 dstEpIdx 的 peermem 读量化 token（AllToAll 的 pull 侧）
                    // 拿到了远端rank的peer memory地址
                    GM_ADDR otherRankPtr = shmem(0, dstEpIdx);
                    AscendC::GlobalTensor<ElementA> gmRemoteA;
                    gmRemoteA.SetGlobalBuffer(reinterpret_cast<__gm__ ElementA*>(otherRankPtr + peermemInfo.offsetA));
                    MatrixCoord offsetA{rowStart, 0};
                    int64_t gmOffsetA = params.layoutA.GetOffset(offsetA);
                    // peermem 每 token 带 UB_ALIGN 对齐的 per-token scale
                    int64_t gmOffsetPeer = rowSrc * (params.problemShape.k() + UB_ALIGN);
                    int32_t ubMoveNum = 2;
                    // CopyGMToGMPerToken：UB 双缓冲，逐 token 搬 hidden + scale 到本地 gmA / gmPerTokenScale1
                    // 从远端 Rank 的 gmRemoteA 中，把属于当前 expert 组的 token 数据拉到本地 gmA 中。
                    CopyGMToGMPerToken(gmA[gmOffsetA], gmPerTokenScale1[rowStart], gmRemoteA[gmOffsetPeer],  rows, params.problemShape.k(), ubMoveNum, pingpongIdx);
                }

            }
            AscendC::SyncAll<true>();
            // 该 expert 组 Pull 完成 → 通知 AIC 可对该组做 GMM1（GMM1 内 CrossCoreWaitFlag 对应 syncgmmIdx）
            AscendC::CrossCoreSetFlag<0x2, PIPE_MTE3>(syncgmm1Idx / CROSS_CORE_FLAG_MAX_SET_COUNT);
            syncgmm1Idx ++;

            prevGroupSum1 += currentM;

            // 累计第一波 SwiGLU 覆盖的行数（groupIdx < epilogueGranularity）
            if (groupIdx + 1 <= params.epilogueGranularity) {
                if (dequantSum1 + currentM <= params.maxOutputSize) {
                    dequantSum1 += currentM;
                } else if (dequantSum1 < params.maxOutputSize) {
                    dequantSum1 = params.maxOutputSize;
                }
            }

            // 累计第二波 SwiGLU 覆盖的行数（剩余 expert 组）
            // 是为了让 AIC 在完成第一波 GMM1 后，提前 Finalize(..., SYNCFLAGC2V) 通知 AIV 消费 gmC，而不是等所有 expert 的 GMM1 全部完成
            if (groupIdx + 1 > params.epilogueGranularity && dequantSum1 < params.maxOutputSize) {
                if (dequantSum1 + dequantSum2 + currentM <= params.maxOutputSize) {
                    dequantSum2 += currentM;
                } else if (dequantSum1 + dequantSum2 < params.maxOutputSize) {
                    dequantSum2 += params.maxOutputSize - dequantSum1 - dequantSum2;
                }
            }
        }
        AscendC::WaitFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID0);
        AscendC::WaitFlag<AscendC::HardEvent::MTE3_MTE2>(EVENT_ID1);
        AscendC::SyncAll<true>();
        DFFC_PROFILE_STAGE_END(profileStageBuf_, DFFC_PHASE_DISPATCH);

        uint32_t n2 = params.problemShape.k();

        // Combine epilogue 参数：V1 按 expert 组整组 scatter；V2 按 GEMM tile 细粒度 scatter
        typename BlockEpilogue2::Params epilogueParams2{
            static_cast<int32_t>(params.EP),
            static_cast<int32_t>(params.expertPerRank),
            reinterpret_cast<__gm__ int32_t *>(shmem() + peermemInfo.offsetPeerTokenPerExpert),
            static_cast<int32_t>(n2)
        };
        //  V2 要 按 GEMM tile + AIV subblock 细粒度
        typename BlockEpilogue3::Params epilogueParams3{
            static_cast<int32_t>(params.EP),
            static_cast<int32_t>(params.expertPerRank),
            static_cast<int32_t>(params.rank),
            reinterpret_cast<__gm__ int32_t *>(shmem() + peermemInfo.offsetPeerTokenPerExpert),
            params.layoutD2,
            static_cast<int32_t>(n2),
            static_cast<int32_t>(L1TileShape::N),
            shmem,
            static_cast<int32_t>(peermemInfo.offsetD),
            tokenPerExpertLayout
        };
        
        uint32_t n = params.problemShape.n();
        BlockEpilogue2 blockEpilogue2(resource, epilogueParams2);
        BlockEpilogue3 blockEpilogue3(resource, epilogueParams3);
        // BlockEpilogue1：GMM1 输出 gmC → 反量化 + SwiGLU + 再量化 → gmPermutedToken（GMM2 输入）
        BlockEpilogue1 blockEpilogue1(resource, n);

        // --- Phase 4: 第一波 SwiGLU（等 AIC GMM1 第一波 via SYNCFLAGC2V）---
        DFFC_PROFILE_STAGE_BEGIN(profileStageBuf_, DFFC_PHASE_SWIGLU);
        AscendC::CrossCoreWaitFlag<0x2>(SYNCFLAGC2V);
        AscendC::SyncAll<true>();
        if (dequantSum1 > 0) { 
            uint32_t rowStartThisCore = 0;
            MatrixCoord offsetC{0U, 0};
            MatrixCoord shapeC{dequantSum1, params.problemShape.n()};
            LayoutC layoutC{dequantSum1, params.problemShape.n()};
            int64_t gmOffsetC = layoutC.GetOffset(offsetC);
            int64_t gmOffsetD = params.layoutD1.GetOffset(offsetC);
            blockEpilogue1(gmC[gmOffsetC], shapeC, gmPerTokenScale1[rowStartThisCore], gmPermutedToken[gmOffsetD], gmPerTokenScale2[rowStartThisCore], params.epilogueCoreNum);
        }
        AscendC::SyncAll<true>();
        // 第一波 SwiGLU 完成 → 通知 AIC 开始对应组的 GMM2
        AscendC::CrossCoreSetFlag<0x2, PIPE_MTE3>(SYNCFLAGV2C);
        
        // --- Phase 4b: 第二波 SwiGLU（epilogueGranularity 将 expert 组分两波流水线）---
        if ((params.epilogueGranularity < params.expertPerRank && params.epilogueGranularity > 0)) {
            AscendC::CrossCoreWaitFlag<0x2>(SYNCFLAGC2V);
            AscendC::SyncAll<true>();
            if (dequantSum2 > 0) {
                uint32_t rowStartThisCore = dequantSum1;
                MatrixCoord offsetC{rowStartThisCore, 0};
                uint32_t dequantLen = dequantSum2;
                MatrixCoord shapeC{dequantLen, params.problemShape.n()};
                LayoutC layoutC{dequantLen, params.problemShape.n()};
                int64_t gmOffsetC = layoutC.GetOffset(offsetC);
                int64_t gmOffsetD = params.layoutD1.GetOffset(offsetC);
                blockEpilogue1(gmC[gmOffsetC], shapeC, gmPerTokenScale1[rowStartThisCore], gmPermutedToken[gmOffsetD], gmPerTokenScale2[rowStartThisCore], coreNum);
            }
            AscendC::SyncAll<true>();
            AscendC::CrossCoreSetFlag<0x2, PIPE_MTE3>(SYNCFLAGV2C);
        }

        blockEpilogue1.Finalize();
        AscendC::SyncAll<true>();
        DFFC_PROFILE_STAGE_END(profileStageBuf_, DFFC_PHASE_SWIGLU);
        // --- Phase 5: Combine（GMM2 输出 gmC2 写回各 rank 的 peermem offsetD）---
        DFFC_PROFILE_STAGE_BEGIN(profileStageBuf_, DFFC_PHASE_COMBINE);
        // CombineV1：M*topK>4096，按 expert 组等 AIC flag 后整组 dequant+scatter，大batch
        // CombineV2：小 batch，按 GEMM tile + AIV subblock 切 M 行 scatter，小batch
        if (isCombineV1) {
            blockEpilogue2.SetFlag();
            CombineV1(params, blockEpilogue2);
        } else {
            blockEpilogue3.SetFlag();
            CombineV2(params, blockEpilogue3);
        }

        AscendC::SyncAll<true>();
        DFFC_PROFILE_STAGE_END(profileStageBuf_, DFFC_PHASE_COMBINE);
#if DISPATCH_FFN_COMBINE_PROFILE
        if (DffcProfileIsAivWriter(coreIdx)) {
            DffcProfileExportToExpertNums(
                params.ptrExpertTokenNums, params.expertPerRank, profileStageBuf_);
        }
#endif
        // ResetTokenPerExpert：最后一个 AIV core 清零 peermem 中的 tokenPerExpert，供下次调用
        ResetTokenPerExpert(params.EP * paddedExpertNumAligned);

        // CrossRankSync：全 rank 栅栏，确保 combine 写入对所有 rank 可见后再 unpermute
        shmem.CrossRankSync();

        // --- Phase 6: Unpermute ---
        // MoeTokenUnpermuteTiling：Host 侧 tiling 参数；KernelMoeTokenUnpermute：按 expandedRowIdx
        // 从 peermem(offsetD) 读 combine 结果，乘 probs 加权，写最终 out
        MoeTokenUnpermuteTilingData tilingData;
        MoeTokenUnpermuteTiling(params.problemShape.m() * params.topK, n2, params.topK, tilingData, coreNum);
        KernelMoeTokenUnpermute<ElementD2, int32_t, float, true> kernelMoeTokenUnpermuteOp;
        kernelMoeTokenUnpermuteOp.Init(shmem() + peermemInfo.offsetD, workspaceInfo.expandedRowIdx, params.probs, reinterpret_cast<GM_ADDR>(params.ptrOutput), &tilingData);
        kernelMoeTokenUnpermuteOp.Process();
    }

    CATLASS_DEVICE
    void CombineV1(Params const &params, BlockEpilogue2 & blockEpilogue) {
        // 它先按 groupIdx 依次遍历每个 rank 内的 expert，也就是先处理所有 rank 上的第 0 个 expert，再处理所有 rank 上的第 1 个 expert，以此类推。对于当前这个 groupIdx，不同的 core 会按照 dstEpIdx = coreIdx; dstEpIdx < EP; dstEpIdx += coreNum 的方式，分别负责一部分目标 EP rank。每个 core 会找到自己负责的目标 rank 的 peer memory，然后根据 cumsumMM、tokenPerExpert 和 preSumBeforeRank 计算源数据在本地 gmC2 里的起始位置、要搬多少行，以及目标 peer memory 里的写入位置，最后调用 blockEpilogue 把这一段连续数据处理后写到对应的远端 peer memory。简单说，V1 是固定一个 expert group 后，让不同 core 分别处理不同目标 EP rank 的数据搬运和写回。

        //EP 数量不小；
        // 每个 dstEpIdx 的数据量相对均匀；
        // 数据量不大；
        // 不需要特别细粒度的 tile 并行。

        uint32_t n2 = params.problemShape.k();
        int32_t prevGroupSum2 = 0;

        icache_preload(8);
        for (uint32_t t_groupIdx = 0; t_groupIdx < params.expertPerRank; ++t_groupIdx) {
            int32_t flagId = t_groupIdx / CROSS_CORE_FLAG_MAX_SET_COUNT;
            AscendC::CrossCoreWaitFlag<0x2>(flagId);
            AscendC::SyncAll<true>();

            uint32_t groupIdx = t_groupIdx;

            for(int32_t dstEpIdx = coreIdx; dstEpIdx < params.EP; dstEpIdx += coreNum) {
                __gm__ void* dstPeermemPtr = shmem(peermemInfo.offsetD, dstEpIdx);
                AscendC::GlobalTensor<ElementD2> gmRemotePeer;
                gmRemotePeer.SetGlobalBuffer(reinterpret_cast<__gm__ ElementD2*>(dstPeermemPtr));
                uint32_t srcRowOffset = (dstEpIdx == 0 ? 0 : cumsumMM((dstEpIdx - 1) * params.expertPerRank + groupIdx)) + prevGroupSum2;
                if (srcRowOffset < params.maxOutputSize) {
                    uint32_t dataRows = tokenPerExpert(tokenPerExpertLayout(dstEpIdx, params.rank, groupIdx));
                    if (srcRowOffset + dataRows > params.maxOutputSize) {
                        dataRows = params.maxOutputSize - srcRowOffset;
                    }
                    //uint32_t dstRowOffset = preSumBeforeRank(2 * dstEpIdx * FLAGSTRIDE + groupIdx);
                    int32_t tmpBlock = AlignUp(params.expertPerRank, FLAGSTRIDE);
                    //uint32_t dstRowOffset = preSumBeforeRank(dstEpIdx * tmpBlock + groupIdx);
                    uint32_t dstRowOffset = preSumBeforeRank(dstEpIdx * params.expertPerRank + groupIdx);
                    MatrixCoord offsetC{srcRowOffset, 0};
                    MatrixCoord offsetPeer{dstRowOffset, 0};
                    MatrixCoord shapeC{dataRows, n2};
                    int64_t gmOffsetC = params.layoutD2.GetOffset(offsetC);
                    int64_t gmOffsetPeer = params.layoutD2.GetOffset(offsetPeer);
                    if constexpr (std::is_same_v<ElementA, int8_t>) {
                        blockEpilogue(gmC2[gmOffsetC], shapeC, gmPerTokenScale2[srcRowOffset], gmRemotePeer[gmOffsetPeer]);
                    } else {
                        blockEpilogue(gmC2[gmOffsetC], shapeC, gmRemotePeer[gmOffsetPeer]);
                    }
                }
            }
            prevGroupSum2 += cumsumMM((params.EP - 1) * params.expertPerRank + groupIdx);
        }
        blockEpilogue.Finalize();
    }

    CATLASS_DEVICE
    void CombineV2(Params const &params, BlockEpilogue3 & blockEpilogue) {
        // 它同样按 groupIdx 遍历每个 rank 内的 expert，但它不会在外层逐个 dstEpIdx 去处理目标 EP rank，而是先通过 cumsumMM 得到当前 groupIdx 跨所有 EP rank 后一共有多少行数据，也就是 currentExpertM，然后把这部分数据看成一个整体的矩阵，形状大致是 M = currentExpertM, N = n2。接着 BlockScheduler 会按照 L1TileShape::M 和 L1TileShape::N 把这个矩阵切成多个 tile，并把这些 tile 分配给不同的 AIC core；每个 tile 内部又会按 m0 = 16 行继续切小块，由两个 AIV sub-core 分摊处理。最后每个 sub-core 调用 BlockEpilogue3，根据 tile 坐标、groupIdx、preSrcExpertSum 和 preSumBeforeRank 去完成具体的数据读取、位置映射和写回。简单说，V2 是固定一个 expert group 后，把这个 group 的数据整体看成矩阵，再切成小 tile 分给 core/sub-core 并行处理。

        // 并行粒度更细
        // 更能应对 token 分布不均
        // 适合大数据量
        BlockScheduler blockScheduler;
        int32_t syncLoopIdx = 0;
        uint32_t startCoreIdx = 0;
        uint32_t aicCoreNum = coreNum / 2;
        uint32_t aicCoreIdx = get_block_idx();
        uint32_t aivSubCoreIdx = get_subblockid();
        uint32_t preSrcExpertSum = 0;
        uint32_t n2 = params.problemShape.k();
        uint32_t k2 = params.problemShape.n() / 2;
        icache_preload(8);
        for (uint32_t groupIdx = 0; groupIdx < params.expertPerRank; ++groupIdx) {
            uint32_t currentExpertM = cumsumMM((params.EP - 1) * params.expertPerRank + groupIdx);
            if (preSrcExpertSum >= params.maxOutputSize) {
                currentExpertM = 0;
            } else if (preSrcExpertSum + currentExpertM > params.maxOutputSize) {
                currentExpertM = params.maxOutputSize - preSrcExpertSum;
            }
            GemmCoord inGroupProblemShape{currentExpertM, n2, k2}; // M N K
            blockScheduler.Update(inGroupProblemShape, MakeCoord(L1TileShape::M, L1TileShape::N));
            uint32_t coreLoops = blockScheduler.GetCoreLoops();
            uint32_t startLoopIdx = ((aicCoreIdx < startCoreIdx) ? (aicCoreIdx + aicCoreNum) : aicCoreIdx) - startCoreIdx;

            for (uint32_t loopIdx = startLoopIdx; loopIdx < coreLoops; loopIdx += aicCoreNum) {
                GemmCoord blockCoord = blockScheduler.GetBlockCoord(loopIdx);
                GemmCoord actualBlockShape = blockScheduler.GetActualBlockShape(blockCoord);
                int32_t m0 = 16;
                //  Block count, the shape of each block is (m0, actualBlockShape.n())
                int32_t m_rows = (actualBlockShape.m() + m0 - 1) / m0;
                int32_t aiv_m_rows = m_rows / 2;
                if (aivSubCoreIdx == 1 && aiv_m_rows * 2 < m_rows) {
                    aiv_m_rows += 1;
                }
                uint32_t m_offset = blockCoord.m() * L1TileShape::M;//blockOffset
                if(aivSubCoreIdx == 1) {
                    m_offset += (m_rows / 2) * m0;
                }


                for (;syncLoopIdx <= groupIdx; syncLoopIdx ++) {
                    int32_t flag_id = syncLoopIdx / CROSS_CORE_FLAG_MAX_SET_COUNT;
                    AscendC::CrossCoreWaitFlag<0x2>(flag_id);
                }

                for (int32_t cur_row = 0; cur_row < aiv_m_rows; cur_row ++) {
                    GemmCoord realTileCoord{m_offset, blockCoord.n() * L1TileShape::N, 1};
                    uint32_t actualm = m0;
                    if(aivSubCoreIdx == 1 && cur_row == aiv_m_rows - 1){
                        actualm = actualBlockShape.m() - (m_rows / 2) * m0 - cur_row * m0;
                    }
                    GemmCoord realTileShape{actualm, actualBlockShape.n(), 1};
                    blockEpilogue(gmC2, gmPerTokenScale2, realTileCoord, realTileShape, groupIdx, preSrcExpertSum, preSumBeforeRank);
                    m_offset += m0;
                }
            }
            preSrcExpertSum += currentExpertM;
            startCoreIdx = (startCoreIdx + coreLoops) % aicCoreNum;
        }
        blockEpilogue.Finalize();
    }

private:
  struct WorkspaceInfo {
        GM_ADDR ptrA;
        GM_ADDR ptrPerTokenScale;
        GM_ADDR ptrcumsumMM;
        GM_ADDR ptrC;
        GM_ADDR ptrC2;
        GM_ADDR ptrPermutedToken;
        GM_ADDR ptrPerTokenScale2;
        GM_ADDR expandedRowIdx;
        GM_ADDR ptrTokenPerExpert;
        GM_ADDR ptrSumBeforeRank;
        __gm__ float* ptrSoftFlagBase;


        CATLASS_DEVICE
        WorkspaceInfo(){}

        CATLASS_DEVICE
        WorkspaceInfo(const Params & params) {
            uint32_t k2 = params.problemShape.n() / 2;
            uint32_t n2 = params.problemShape.k();
            int64_t workspaceOffset = 0;
            expandedRowIdx = params.ptrWorkspace;

            workspaceOffset += AlignUp(params.problemShape.m(), 256) * params.topK * sizeof(int32_t);
            ptrcumsumMM = params.ptrWorkspace + workspaceOffset;

            workspaceOffset += (params.EP * params.EP * params.expertPerRank) * sizeof(int32_t);

            workspaceOffset += (params.EP * params.EP * params.expertPerRank) * sizeof(int32_t);
            ptrPerTokenScale = params.ptrWorkspace + workspaceOffset;

            workspaceOffset += params.maxOutputSize * sizeof(ElementPerTokenScale);
            ptrPerTokenScale2 = params.ptrWorkspace + workspaceOffset;

            workspaceOffset += params.maxOutputSize * sizeof(ElementPerTokenScale);
            ptrTokenPerExpert =  params.ptrWorkspace + workspaceOffset;

            workspaceOffset += (params.EP * params.EP * params.expertPerRank) * sizeof(int32_t);
            ptrC = params.ptrWorkspace + workspaceOffset;

            workspaceOffset += params.maxOutputSize * params.problemShape.n() * sizeof(ElementC);
            ptrC2 = params.ptrWorkspace + workspaceOffset;

            workspaceOffset += params.maxOutputSize * n2 * sizeof(ElementC);
            ptrA = params.ptrWorkspace + workspaceOffset;

            workspaceOffset += params.maxOutputSize * params.problemShape.k() * sizeof(ElementA);
            ptrPermutedToken = params.ptrWorkspace + workspaceOffset;

            workspaceOffset += params.maxOutputSize * k2 * sizeof(ElementA);
            ptrSumBeforeRank = params.ptrWorkspace + workspaceOffset;

            workspaceOffset += params.EP * sizeof(int32_t) * FLAGSTRIDE;
            ptrSoftFlagBase = reinterpret_cast<__gm__ float*>(params.ptrWorkspace + workspaceOffset);
        }
    };

    struct PeermemInfo {
        int64_t offsetA;
        int64_t offsetPeerPerTokenScale;
        int64_t offsetPeerTokenPerExpert;
        int64_t offsetD;

        CATLASS_DEVICE
        PeermemInfo(){}

        CATLASS_DEVICE
        PeermemInfo(const Params & params, const HcclShmem & shmem) {
            offsetA = 0;    // Occupies one third of BUFFSIZE
            offsetPeerPerTokenScale = offsetA + AlignUp(shmem.SegmentSize() / 3, 512); // Occupies 1 MB
            offsetD = offsetPeerPerTokenScale + MB_SIZE;    // Occupies the remaining space
            offsetPeerTokenPerExpert = shmem.SegmentSize() - 2 * MB_SIZE;     // Occupies the final 2 MB
        }
    };

    Arch::Resource<ArchTag> resource;

    uint32_t coreIdx;
    uint32_t coreNum;

    WorkspaceInfo workspaceInfo;
    PeermemInfo peermemInfo;

    AscendC::GlobalTensor<ElementA> gmA;
    AscendC::GlobalTensor<ElementC> gmC;

    AscendC::GlobalTensor<ElementD1> gmPermutedToken;
    AscendC::GlobalTensor<ElementC> gmC2;

    AscendC::GlobalTensor<ElementPerTokenScale> gmPerTokenScale1;
    AscendC::GlobalTensor<ElementPerTokenScale> gmPerTokenScale2;

    AscendC::GlobalTensor<bool> gmXActiveMask;

    AscendC::GlobalTensor<int32_t> tokenPerExpert;
    AscendC::GlobalTensor<int32_t> cumsumMM;
    AscendC::GlobalTensor<int32_t> preSumBeforeRank;
    Layout3D tokenPerExpertLayout;
    HcclShmem shmem;
    int32_t paddedExpertNumAligned;
    bool isCombineV1;
#if DISPATCH_FFN_COMBINE_PROFILE
    __gm__ int32_t* profileStageBuf_ = nullptr;
#endif
};

} // namespace Catlass::Gemm::Kernel

#endif // DISPATCH_FFN_COMBINE_KERNEL_HPP