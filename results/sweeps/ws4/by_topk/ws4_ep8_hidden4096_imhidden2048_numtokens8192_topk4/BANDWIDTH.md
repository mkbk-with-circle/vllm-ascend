# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 4
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 541,065,216 | 3451.0 | 156.79 |
| combine | 1,073,741,824 | 4861.0 | 220.89 |

## Per-rank 带宽 (GB/s)

- dispatch: median=39.82, min=39.52, max=40.22
- combine: median=81.10, min=54.86, max=107.75
