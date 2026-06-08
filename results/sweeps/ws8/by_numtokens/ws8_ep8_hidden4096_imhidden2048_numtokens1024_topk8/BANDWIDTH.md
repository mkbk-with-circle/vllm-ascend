# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 1024, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 270,532,608 | 485.0 | 557.80 |
| combine | 536,870,912 | 688.0 | 780.34 |

## Per-rank 带宽 (GB/s)

- dispatch: median=72.05, min=69.89, max=73.09
- combine: median=102.27, min=97.27, max=230.36
