# dispatch/combine 有效带宽

- hidden (K): 8032, imhidden: 4016, numtokens: 8192, topk: 8
- bytes/token dispatch: 8064, combine: 16064

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,227,858,432 | 4327.0 | 977.09 |
| combine | 8,422,162,432 | 7403.0 | 1137.67 |

## Per-rank 带宽 (GB/s)

- dispatch: median=123.56, min=121.91, max=123.97
- combine: median=144.48, min=142.68, max=200.51
