# dispatch/combine 有效带宽

- hidden (K): 7168, imhidden: 3584, numtokens: 8192, topk: 8
- bytes/token dispatch: 7200, combine: 14336

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 1,887,436,800 | 7463.0 | 252.91 |
| combine | 3,758,096,384 | 11922.0 | 315.22 |

## Per-rank 带宽 (GB/s)

- dispatch: median=63.45, min=63.19, max=63.51
- combine: median=116.02, min=78.62, max=154.13
