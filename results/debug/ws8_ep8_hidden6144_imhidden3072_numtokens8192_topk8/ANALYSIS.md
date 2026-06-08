# Combine barrier 探针分析

- baseline: `/home/u2200013153/vllm-ascend/results/debug/ws8_ep8_hidden6144_imhidden3072_numtokens8192_topk8/baseline`
- probe: `/home/u2200013153/vllm-ascend/results/debug/ws8_ep8_hidden6144_imhidden3072_numtokens8192_topk8/barrier_v11`

## Rank 0

- baseline combine expert 间 gap（中位）: 974.0 µs
- probe version: 11
- median gap_viz: 1001.0 µs
- median barrier_width: 1001.0 µs
- median tail_gap: 1.0 µs
- median head_mismatch: 1.0 µs
- **verdict**: 空隙主要由真实 barrier（CrossCoreWait+SyncAll，含等 GMM2）构成，原先 timeline 未画出 barrier 段。

| expert | gap_viz | barrier_w | tail_gap | head_mm | active |
|--------|---------|-----------|----------|---------|--------|
| e0 | 0 | 384 | 0 | 0.0 | 321 |
| e1 | 1020 | 1019 | 0 | 1.0 | 343 |
| e2 | 1007 | 1006 | 1 | 0.0 | 347 |
| e3 | 1001 | 1001 | 1 | -1.0 | 334 |
| e4 | 1016 | 1017 | 0 | -1.0 | 343 |
| e5 | 968 | 967 | 1 | 0.0 | 279 |
| e6 | 992 | 992 | 0 | 0.0 | 275 |
| e7 | 994 | 994 | 0 | 0.0 | 251 |

## Rank 1

- baseline combine expert 间 gap（中位）: 1001.0 µs
- probe version: 11
- median gap_viz: 1014.0 µs
- median barrier_width: 1014.0 µs
- median tail_gap: 1.0 µs
- median head_mismatch: 0.0 µs
- **verdict**: 空隙主要由真实 barrier（CrossCoreWait+SyncAll，含等 GMM2）构成，原先 timeline 未画出 barrier 段。

| expert | gap_viz | barrier_w | tail_gap | head_mm | active |
|--------|---------|-----------|----------|---------|--------|
| e0 | 0 | 355 | 0 | 0.0 | 312 |
| e1 | 1044 | 1044 | 1 | -1.0 | 347 |
| e2 | 977 | 977 | 0 | 0.0 | 336 |
| e3 | 1036 | 1035 | 1 | 0.0 | 360 |
| e4 | 1021 | 1020 | 1 | 0.0 | 341 |
| e5 | 990 | 989 | 1 | 0.0 | 267 |
| e6 | 1014 | 1014 | 0 | 0.0 | 263 |
| e7 | 1011 | 1011 | 0 | 0.0 | 280 |

## Rank 6

- baseline combine expert 间 gap（中位）: 509.0 µs
- probe version: 11
- median gap_viz: 519.0 µs
- median barrier_width: 518.0 µs
- median tail_gap: 1.0 µs
- median head_mismatch: 0.0 µs
- **verdict**: 空隙主要由真实 barrier（CrossCoreWait+SyncAll，含等 GMM2）构成，原先 timeline 未画出 barrier 段。

| expert | gap_viz | barrier_w | tail_gap | head_mm | active |
|--------|---------|-----------|----------|---------|--------|
| e0 | 0 | 333 | 0 | 0.0 | 794 |
| e1 | 503 | 503 | 0 | 0.0 | 786 |
| e2 | 532 | 532 | 0 | 0.0 | 793 |
| e3 | 540 | 539 | 1 | 0.0 | 772 |
| e4 | 569 | 568 | 1 | 0.0 | 791 |
| e5 | 519 | 518 | 1 | 0.0 | 753 |
| e6 | 514 | 513 | 1 | 0.0 | 798 |
| e7 | 492 | 492 | 0 | 0.0 | 744 |

