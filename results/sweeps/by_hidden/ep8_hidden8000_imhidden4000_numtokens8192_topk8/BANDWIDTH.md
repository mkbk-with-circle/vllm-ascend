# dispatch/combine 有效带宽

- hidden (K): 8000, imhidden: 4000, numtokens: 8192, topk: 8
- bytes/token dispatch: 8032, combine: 16000

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,211,081,216 | 4352.0 | 967.62 |
| combine | 8,388,608,000 | 7480.0 | 1121.47 |

## Per-rank 带宽 (GB/s)

- dispatch: median=121.50, min=121.00, max=122.84
- combine: median=143.20, min=140.29, max=202.17
