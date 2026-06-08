# dispatch/combine 有效带宽

- hidden (K): 7936, imhidden: 3968, numtokens: 8192, topk: 8
- bytes/token dispatch: 7968, combine: 15872

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,177,526,784 | 4518.0 | 924.64 |
| combine | 8,321,499,136 | 6910.0 | 1204.27 |

## Per-rank 带宽 (GB/s)

- dispatch: median=116.47, min=115.80, max=117.11
- combine: median=156.20, min=151.16, max=299.31
