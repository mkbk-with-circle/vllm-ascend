# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,164,260,864 | 3546.0 | 610.34 |
| combine | 4,294,967,296 | 5510.0 | 779.49 |

## Per-rank 带宽 (GB/s)

- dispatch: median=76.61, min=76.35, max=76.80
- combine: median=98.36, min=97.64, max=139.38
