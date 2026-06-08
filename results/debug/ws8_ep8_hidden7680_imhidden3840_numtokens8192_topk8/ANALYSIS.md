# Combine barrier 探针分析

- baseline: `/home/u2200013153/vllm-ascend/results/debug/ws8_ep8_hidden7680_imhidden3840_numtokens8192_topk8/baseline`
- probe: `/home/u2200013153/vllm-ascend/results/debug/ws8_ep8_hidden7680_imhidden3840_numtokens8192_topk8/barrier_v11`

## Rank 0

- baseline combine expert 间 gap（中位）: 1586.0 µs
- probe version: 11
- median gap_viz: 1544.0 µs
- median barrier_width: 1544.0 µs
- median tail_gap: 1.0 µs
- median head_mismatch: 0.0 µs
- **verdict**: 空隙主要由真实 barrier（CrossCoreWait+SyncAll，含等 GMM2）构成，原先 timeline 未画出 barrier 段。

| expert | gap_viz | barrier_w | tail_gap | head_mm | active |
|--------|---------|-----------|----------|---------|--------|
| e0 | 0 | 854 | 0 | 0.0 | 391 |
| e1 | 1601 | 1600 | 1 | 0.0 | 380 |
| e2 | 1588 | 1588 | 0 | 0.0 | 429 |
| e3 | 1526 | 1525 | 1 | 0.0 | 416 |
| e4 | 1544 | 1544 | 0 | 0.0 | 392 |
| e5 | 1580 | 1579 | 1 | 0.0 | 372 |
| e6 | 1524 | 1524 | 0 | 0.0 | 337 |
| e7 | 1517 | 1516 | 1 | 0.0 | 347 |

## Rank 1

- baseline combine expert 间 gap（中位）: 1629.0 µs
- probe version: 11
- median gap_viz: 1574.0 µs
- median barrier_width: 1574.0 µs
- median tail_gap: 1.0 µs
- median head_mismatch: 0.0 µs
- **verdict**: 空隙主要由真实 barrier（CrossCoreWait+SyncAll，含等 GMM2）构成，原先 timeline 未画出 barrier 段。

| expert | gap_viz | barrier_w | tail_gap | head_mm | active |
|--------|---------|-----------|----------|---------|--------|
| e0 | 0 | 834 | 0 | 0.0 | 381 |
| e1 | 1604 | 1603 | 1 | 0.0 | 392 |
| e2 | 1616 | 1615 | 1 | 0.0 | 374 |
| e3 | 1596 | 1596 | 0 | 0.0 | 407 |
| e4 | 1574 | 1574 | 0 | 0.0 | 396 |
| e5 | 1519 | 1518 | 1 | 0.0 | 350 |
| e6 | 1531 | 1530 | 1 | 0.0 | 335 |
| e7 | 1517 | 1517 | 0 | 0.0 | 344 |

## Rank 6

- baseline combine expert 间 gap（中位）: 1075.0 µs
- probe version: 11
- median gap_viz: 1123.0 µs
- median barrier_width: 1123.0 µs
- median tail_gap: 1.0 µs
- median head_mismatch: 0.0 µs
- **verdict**: 空隙主要由真实 barrier（CrossCoreWait+SyncAll，含等 GMM2）构成，原先 timeline 未画出 barrier 段。

| expert | gap_viz | barrier_w | tail_gap | head_mm | active |
|--------|---------|-----------|----------|---------|--------|
| e0 | 0 | 895 | 0 | 0.0 | 825 |
| e1 | 1169 | 1169 | 0 | 0.0 | 823 |
| e2 | 1123 | 1123 | 0 | 0.0 | 783 |
| e3 | 1181 | 1180 | 1 | 0.0 | 831 |
| e4 | 1131 | 1131 | 1 | -1.0 | 829 |
| e5 | 1096 | 1096 | 0 | 0.0 | 834 |
| e6 | 1015 | 1014 | 1 | 0.0 | 823 |
| e7 | 1019 | 1018 | 1 | 0.0 | 795 |

