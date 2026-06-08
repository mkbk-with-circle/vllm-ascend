# dispatch/combine 有效带宽

- hidden (K): 6144, imhidden: 3072, numtokens: 8192, topk: 8
- bytes/token dispatch: 6176, combine: 12288

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 3,238,002,688 | 4179.0 | 774.83 |
| combine | 6,442,450,944 | 5955.0 | 1081.86 |

## Per-rank 带宽 (GB/s)

- dispatch: median=98.03, min=96.81, max=98.74
- combine: median=137.34, min=135.61, max=277.66
