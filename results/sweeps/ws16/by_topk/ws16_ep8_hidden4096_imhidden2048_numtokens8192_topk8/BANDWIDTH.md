# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,328,521,728 | 2323.0 | 1863.33 |
| combine | 8,589,934,592 | 3713.0 | 2313.48 |

## Per-rank 带宽 (GB/s)

- dispatch: median=118.36, min=116.87, max=119.13
- combine: median=148.30, min=144.46, max=385.58
