# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 1024, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,328,521,728 | 2346.0 | 1845.06 |
| combine | 8,589,934,592 | 3759.0 | 2285.16 |

## Per-rank 带宽 (GB/s)

- dispatch: median=117.83, min=115.50, max=119.98
- combine: median=147.60, min=142.40, max=363.44
