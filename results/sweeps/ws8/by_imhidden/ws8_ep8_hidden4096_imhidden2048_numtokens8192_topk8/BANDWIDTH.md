# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,164,260,864 | 3757.0 | 576.06 |
| combine | 4,294,967,296 | 5470.0 | 785.19 |

## Per-rank 带宽 (GB/s)

- dispatch: median=72.75, min=72.09, max=73.28
- combine: median=99.62, min=97.79, max=208.12
