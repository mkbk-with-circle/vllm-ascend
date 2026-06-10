# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,164,260,864 | 3549.0 | 609.82 |
| combine | 4,294,967,296 | 5501.0 | 780.76 |

## Per-rank 带宽 (GB/s)

- dispatch: median=76.63, min=76.37, max=76.87
- combine: median=98.32, min=97.80, max=139.45
