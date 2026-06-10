# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,164,260,864 | 3551.0 | 609.48 |
| combine | 4,294,967,296 | 5526.0 | 777.23 |

## Per-rank 带宽 (GB/s)

- dispatch: median=76.64, min=76.13, max=76.80
- combine: median=97.87, min=97.36, max=139.20
