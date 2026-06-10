# dispatch/combine 有效带宽

- hidden (K): 6144, imhidden: 3072, numtokens: 8192, topk: 8
- bytes/token dispatch: 6176, combine: 12288

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 3,238,002,688 | 3983.0 | 812.96 |
| combine | 6,442,450,944 | 6008.0 | 1072.31 |

## Per-rank 带宽 (GB/s)

- dispatch: median=102.10, min=101.59, max=102.48
- combine: median=136.71, min=133.58, max=189.52
