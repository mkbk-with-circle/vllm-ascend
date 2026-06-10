# dispatch/combine 有效带宽

- hidden (K): 6144, imhidden: 3072, numtokens: 49152, topk: 8
- bytes/token dispatch: 6176, combine: 12288

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 19,428,016,128 | 23898.0 | 812.96 |
| combine | 38,654,705,664 | 36240.0 | 1066.63 |

## Per-rank 带宽 (GB/s)

- dispatch: median=102.47, min=101.65, max=102.85
- combine: median=135.36, min=133.28, max=188.20
