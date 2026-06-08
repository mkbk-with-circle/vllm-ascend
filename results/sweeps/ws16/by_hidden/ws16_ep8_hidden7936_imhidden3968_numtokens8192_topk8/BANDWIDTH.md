# dispatch/combine 有效带宽

- hidden (K): 7936, imhidden: 3968, numtokens: 8192, topk: 8
- bytes/token dispatch: 7968, combine: 15872

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 8,355,053,568 | 3840.0 | 2175.80 |
| combine | 16,642,998,272 | 6758.0 | 2462.71 |

## Per-rank 带宽 (GB/s)

- dispatch: median=136.55, min=135.99, max=137.17
- combine: median=157.85, min=154.07, max=481.67
