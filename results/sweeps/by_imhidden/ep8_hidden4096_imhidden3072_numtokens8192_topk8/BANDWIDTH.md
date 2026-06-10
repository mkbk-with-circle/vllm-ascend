# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 3072, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,164,260,864 | 3597.0 | 601.68 |
| combine | 4,294,967,296 | 5550.0 | 773.87 |

## Per-rank 带宽 (GB/s)

- dispatch: median=76.41, min=75.35, max=76.59
- combine: median=98.32, min=96.61, max=140.27
