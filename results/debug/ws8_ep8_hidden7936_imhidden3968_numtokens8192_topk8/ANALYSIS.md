# Combine barrier 探针分析

- baseline: `/home/u2200013153/vllm-ascend/results/debug/ws8_ep8_hidden7936_imhidden3968_numtokens8192_topk8/baseline`
- probe: `/home/u2200013153/vllm-ascend/results/debug/ws8_ep8_hidden7936_imhidden3968_numtokens8192_topk8/barrier_v11`

## Rank 0

- baseline combine expert 间 gap（中位）: 1694.0 µs
- probe version: 11
- median gap_viz: 1683.0 µs
- median barrier_width: 1682.0 µs
- median tail_gap: 1.0 µs
- median head_mismatch: 0.0 µs
- **verdict**: 空隙主要由真实 barrier（CrossCoreWait+SyncAll，含等 GMM2）构成，原先 timeline 未画出 barrier 段。

| expert | gap_viz | barrier_w | tail_gap | head_mm | active |
|--------|---------|-----------|----------|---------|--------|
| e0 | 0 | 1007 | 0 | 0.0 | 372 |
| e1 | 1774 | 1773 | 1 | 0.0 | 375 |
| e2 | 1755 | 1754 | 1 | 0.0 | 395 |
| e3 | 1683 | 1682 | 1 | 0.0 | 341 |
| e4 | 1752 | 1751 | 1 | 0.0 | 372 |
| e5 | 1644 | 1643 | 1 | 0.0 | 357 |
| e6 | 1629 | 1628 | 1 | 0.0 | 331 |
| e7 | 1649 | 1648 | 1 | 0.0 | 321 |

## Rank 1

- baseline combine expert 间 gap（中位）: 1679.0 µs
- probe version: 11
- median gap_viz: 1690.0 µs
- median barrier_width: 1689.0 µs
- median tail_gap: 1.0 µs
- median head_mismatch: 0.0 µs
- **verdict**: 空隙主要由真实 barrier（CrossCoreWait+SyncAll，含等 GMM2）构成，原先 timeline 未画出 barrier 段。

| expert | gap_viz | barrier_w | tail_gap | head_mm | active |
|--------|---------|-----------|----------|---------|--------|
| e0 | 0 | 983 | 0 | 0.0 | 360 |
| e1 | 1779 | 1779 | 0 | 0.0 | 367 |
| e2 | 1749 | 1748 | 1 | 0.0 | 383 |
| e3 | 1751 | 1751 | 0 | 0.0 | 373 |
| e4 | 1690 | 1689 | 1 | 0.0 | 388 |
| e5 | 1649 | 1649 | 0 | 0.0 | 330 |
| e6 | 1684 | 1684 | 0 | 0.0 | 360 |
| e7 | 1628 | 1628 | 0 | 0.0 | 346 |

## Rank 6

- baseline combine expert 间 gap（中位）: 1242.0 µs
- probe version: 11
- median gap_viz: 1196.0 µs
- median barrier_width: 1195.0 µs
- median tail_gap: 1.0 µs
- median head_mismatch: 0.0 µs
- **verdict**: 空隙主要由真实 barrier（CrossCoreWait+SyncAll，含等 GMM2）构成，原先 timeline 未画出 barrier 段。

| expert | gap_viz | barrier_w | tail_gap | head_mm | active |
|--------|---------|-----------|----------|---------|--------|
| e0 | 0 | 982 | 0 | 0.0 | 815 |
| e1 | 1208 | 1207 | 1 | 0.0 | 860 |
| e2 | 1188 | 1187 | 1 | 0.0 | 831 |
| e3 | 1203 | 1202 | 1 | 0.0 | 826 |
| e4 | 1276 | 1275 | 1 | 0.0 | 790 |
| e5 | 1196 | 1195 | 1 | 0.0 | 864 |
| e6 | 1094 | 1094 | 0 | 0.0 | 887 |
| e7 | 1059 | 1058 | 1 | 0.0 | 782 |

