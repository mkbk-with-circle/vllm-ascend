# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 4096, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,164,260,864 | 1201.0 | 1802.05 |
| combine | 4,294,967,296 | 1876.0 | 2289.43 |

## Per-rank 带宽 (GB/s)

- dispatch: median=114.01, min=112.33, max=116.15
- combine: median=148.52, min=142.65, max=385.73
