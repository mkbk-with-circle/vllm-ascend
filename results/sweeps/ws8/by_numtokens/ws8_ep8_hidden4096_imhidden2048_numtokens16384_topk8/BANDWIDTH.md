# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 16384, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,328,521,728 | 7367.0 | 587.56 |
| combine | 8,589,934,592 | 10964.0 | 783.47 |

## Per-rank 带宽 (GB/s)

- dispatch: median=74.07, min=73.49, max=74.38
- combine: median=98.88, min=98.20, max=188.09
