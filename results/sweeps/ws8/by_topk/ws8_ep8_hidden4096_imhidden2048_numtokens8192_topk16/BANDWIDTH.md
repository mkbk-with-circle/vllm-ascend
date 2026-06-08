# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 16
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,328,521,728 | 7400.0 | 584.94 |
| combine | 8,589,934,592 | 11017.0 | 779.70 |

## Per-rank 带宽 (GB/s)

- dispatch: median=74.10, min=73.37, max=74.41
- combine: median=99.22, min=97.72, max=187.03
