# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 4096, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 541,065,216 | 3430.0 | 157.74 |
| combine | 1,073,741,824 | 4911.0 | 218.64 |

## Per-rank 带宽 (GB/s)

- dispatch: median=39.93, min=39.59, max=40.18
- combine: median=80.74, min=54.87, max=106.56
