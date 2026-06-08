# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 3072, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,164,260,864 | 3747.0 | 577.60 |
| combine | 4,294,967,296 | 5414.0 | 793.31 |

## Per-rank 带宽 (GB/s)

- dispatch: median=72.59, min=72.14, max=72.96
- combine: median=101.67, min=98.93, max=209.32
