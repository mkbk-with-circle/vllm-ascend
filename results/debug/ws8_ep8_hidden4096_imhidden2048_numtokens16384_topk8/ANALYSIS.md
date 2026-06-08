# Combine barrier 探针分析

- baseline: `/home/u2200013153/vllm-ascend/results/debug/ws8_ep8_hidden4096_imhidden2048_numtokens16384_topk8/baseline`
- probe: `/home/u2200013153/vllm-ascend/results/debug/ws8_ep8_hidden4096_imhidden2048_numtokens16384_topk8/barrier_v11`

## Rank 0

- baseline combine expert 间 gap（中位）: 801.0 µs
- probe version: 11
- median gap_viz: 834.0 µs
- median barrier_width: 834.0 µs
- median tail_gap: 1.0 µs
- median head_mismatch: 0.0 µs
- **verdict**: 空隙主要由真实 barrier（CrossCoreWait+SyncAll，含等 GMM2）构成，原先 timeline 未画出 barrier 段。

| expert | gap_viz | barrier_w | tail_gap | head_mm | active |
|--------|---------|-----------|----------|---------|--------|
| e0 | 0 | 4 | 0 | 0.0 | 618 |
| e1 | 797 | 796 | 1 | 0.0 | 622 |
| e2 | 786 | 785 | 1 | 0.0 | 614 |
| e3 | 834 | 834 | 1 | -1.0 | 589 |
| e4 | 815 | 814 | 1 | 0.0 | 553 |
| e5 | 855 | 855 | 0 | 0.0 | 520 |
| e6 | 852 | 851 | 1 | 0.0 | 505 |
| e7 | 886 | 886 | 0 | 0.0 | 491 |

## Rank 1

- baseline combine expert 间 gap（中位）: 826.0 µs
- probe version: 11
- median gap_viz: 847.0 µs
- median barrier_width: 846.0 µs
- median tail_gap: 1.0 µs
- median head_mismatch: 0.0 µs
- **verdict**: 空隙主要由真实 barrier（CrossCoreWait+SyncAll，含等 GMM2）构成，原先 timeline 未画出 barrier 段。

| expert | gap_viz | barrier_w | tail_gap | head_mm | active |
|--------|---------|-----------|----------|---------|--------|
| e0 | 0 | 6 | 0 | 0.0 | 603 |
| e1 | 808 | 807 | 1 | 0.0 | 628 |
| e2 | 805 | 805 | 0 | 0.0 | 654 |
| e3 | 793 | 792 | 1 | 0.0 | 561 |
| e4 | 847 | 846 | 1 | 0.0 | 541 |
| e5 | 878 | 877 | 1 | 0.0 | 500 |
| e6 | 916 | 916 | 0 | 0.0 | 498 |
| e7 | 880 | 879 | 1 | 0.0 | 506 |

## Rank 6

- baseline combine expert 间 gap（中位）: 86.0 µs
- probe version: 11
- median gap_viz: 70.0 µs
- median barrier_width: 69.0 µs
- median tail_gap: 1.0 µs
- median head_mismatch: 1.0 µs
- **verdict**: 空隙主要由真实 barrier（CrossCoreWait+SyncAll，含等 GMM2）构成，原先 timeline 未画出 barrier 段。

| expert | gap_viz | barrier_w | tail_gap | head_mm | active |
|--------|---------|-----------|----------|---------|--------|
| e0 | 0 | 4 | 0 | 0.0 | 1359 |
| e1 | 70 | 69 | 1 | 0.0 | 1350 |
| e2 | 66 | 65 | 1 | 0.0 | 1304 |
| e3 | 99 | 98 | 1 | 0.0 | 1330 |
| e4 | 94 | 92 | 1 | 1.0 | 1321 |
| e5 | 38 | 36 | 1 | 1.0 | 1388 |
| e6 | 48 | 47 | 1 | 0.0 | 1306 |
| e7 | 70 | 69 | 1 | 0.0 | 1292 |

