# Combine barrier 探针分析

- baseline: `/home/u2200013153/vllm-ascend/results/debug/ws8_ep8_hidden7168_imhidden3584_numtokens8192_topk8/baseline`
- probe: `/home/u2200013153/vllm-ascend/results/debug/ws8_ep8_hidden7168_imhidden3584_numtokens8192_topk8/barrier_v11`

## Rank 0

- baseline combine expert 间 gap（中位）: 1327.0 µs
- probe version: 11
- median gap_viz: 1348.0 µs
- median barrier_width: 1347.0 µs
- median tail_gap: 1.0 µs
- median head_mismatch: 0.0 µs
- **verdict**: 空隙主要由真实 barrier（CrossCoreWait+SyncAll，含等 GMM2）构成，原先 timeline 未画出 barrier 段。

| expert | gap_viz | barrier_w | tail_gap | head_mm | active |
|--------|---------|-----------|----------|---------|--------|
| e0 | 0 | 600 | 0 | 0.0 | 352 |
| e1 | 1348 | 1347 | 1 | 0.0 | 348 |
| e2 | 1390 | 1390 | 1 | -1.0 | 360 |
| e3 | 1378 | 1378 | 0 | 0.0 | 370 |
| e4 | 1352 | 1351 | 1 | 0.0 | 394 |
| e5 | 1285 | 1284 | 1 | 0.0 | 306 |
| e6 | 1327 | 1327 | 0 | 0.0 | 318 |
| e7 | 1328 | 1327 | 1 | 0.0 | 307 |

## Rank 1

- baseline combine expert 间 gap（中位）: 1349.0 µs
- probe version: 11
- median gap_viz: 1338.0 µs
- median barrier_width: 1337.0 µs
- median tail_gap: 1.0 µs
- median head_mismatch: 0.0 µs
- **verdict**: 空隙主要由真实 barrier（CrossCoreWait+SyncAll，含等 GMM2）构成，原先 timeline 未画出 barrier 段。

| expert | gap_viz | barrier_w | tail_gap | head_mm | active |
|--------|---------|-----------|----------|---------|--------|
| e0 | 0 | 583 | 0 | 0.0 | 355 |
| e1 | 1354 | 1354 | 0 | 0.0 | 391 |
| e2 | 1329 | 1328 | 1 | 0.0 | 387 |
| e3 | 1307 | 1306 | 1 | 0.0 | 376 |
| e4 | 1355 | 1354 | 1 | 0.0 | 380 |
| e5 | 1338 | 1337 | 1 | 0.0 | 366 |
| e6 | 1301 | 1300 | 1 | 0.0 | 305 |
| e7 | 1349 | 1348 | 1 | 0.0 | 321 |

## Rank 6

- baseline combine expert 间 gap（中位）: 895.0 µs
- probe version: 11
- median gap_viz: 913.0 µs
- median barrier_width: 912.0 µs
- median tail_gap: 1.0 µs
- median head_mismatch: 1.0 µs
- **verdict**: 空隙主要由真实 barrier（CrossCoreWait+SyncAll，含等 GMM2）构成，原先 timeline 未画出 barrier 段。

| expert | gap_viz | barrier_w | tail_gap | head_mm | active |
|--------|---------|-----------|----------|---------|--------|
| e0 | 0 | 652 | 0 | -1.0 | 844 |
| e1 | 913 | 912 | 1 | 0.0 | 788 |
| e2 | 957 | 955 | 1 | 1.0 | 817 |
| e3 | 918 | 917 | 1 | 0.0 | 789 |
| e4 | 921 | 921 | 1 | -1.0 | 797 |
| e5 | 828 | 828 | 0 | 0.0 | 788 |
| e6 | 864 | 863 | 1 | 0.0 | 822 |
| e7 | 811 | 811 | 0 | 0.0 | 748 |

