# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,164,260,864 | 3757.0 | 576.06 |
| combine | 4,294,967,296 | 5476.0 | 784.33 |

## Per-rank 带宽 (GB/s)

- dispatch: median=72.71, min=72.12, max=73.34
- combine: median=99.62, min=97.81, max=207.56
