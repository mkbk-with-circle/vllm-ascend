# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,328,521,728 | 2320.0 | 1865.74 |
| combine | 8,589,934,592 | 3717.0 | 2310.99 |

## Per-rank 带宽 (GB/s)

- dispatch: median=118.36, min=117.03, max=119.35
- combine: median=148.50, min=144.11, max=387.52
