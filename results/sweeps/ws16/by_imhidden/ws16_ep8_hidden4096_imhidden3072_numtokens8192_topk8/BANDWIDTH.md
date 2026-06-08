# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 3072, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,328,521,728 | 2309.0 | 1874.63 |
| combine | 8,589,934,592 | 3714.0 | 2312.85 |

## Per-rank 带宽 (GB/s)

- dispatch: median=118.07, min=117.33, max=119.88
- combine: median=149.11, min=144.66, max=409.98
