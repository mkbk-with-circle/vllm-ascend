# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,328,521,728 | 2316.0 | 1868.96 |
| combine | 8,589,934,592 | 3720.0 | 2309.12 |

## Per-rank 带宽 (GB/s)

- dispatch: median=118.31, min=117.04, max=119.19
- combine: median=148.52, min=143.99, max=388.08
