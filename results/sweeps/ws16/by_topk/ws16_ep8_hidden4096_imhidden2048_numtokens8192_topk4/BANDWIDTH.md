# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 4
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,164,260,864 | 1199.0 | 1805.05 |
| combine | 4,294,967,296 | 1840.0 | 2334.22 |

## Per-rank 带宽 (GB/s)

- dispatch: median=114.82, min=113.66, max=117.25
- combine: median=150.08, min=145.47, max=379.52
