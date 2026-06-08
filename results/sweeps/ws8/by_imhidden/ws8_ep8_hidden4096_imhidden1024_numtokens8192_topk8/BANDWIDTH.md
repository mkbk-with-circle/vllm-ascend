# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 1024, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,164,260,864 | 3770.0 | 574.07 |
| combine | 4,294,967,296 | 5521.0 | 777.93 |

## Per-rank 带宽 (GB/s)

- dispatch: median=72.66, min=72.10, max=73.56
- combine: median=98.58, min=97.24, max=211.44
