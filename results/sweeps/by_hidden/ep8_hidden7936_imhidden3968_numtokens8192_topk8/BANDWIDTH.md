# dispatch/combine 有效带宽

- hidden (K): 7936, imhidden: 3968, numtokens: 8192, topk: 8
- bytes/token dispatch: 7968, combine: 15872

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,177,526,784 | 4382.0 | 953.34 |
| combine | 8,321,499,136 | 7329.0 | 1135.42 |

## Per-rank 带宽 (GB/s)

- dispatch: median=121.34, min=119.67, max=122.48
- combine: median=144.08, min=141.82, max=202.87
