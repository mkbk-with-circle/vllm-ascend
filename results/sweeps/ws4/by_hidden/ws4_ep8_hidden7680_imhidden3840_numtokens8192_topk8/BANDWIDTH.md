# dispatch/combine 有效带宽

- hidden (K): 7680, imhidden: 3840, numtokens: 8192, topk: 8
- bytes/token dispatch: 7712, combine: 15360

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,021,654,528 | 7658.0 | 263.99 |
| combine | 4,026,531,840 | 12261.0 | 328.40 |

## Per-rank 带宽 (GB/s)

- dispatch: median=66.22, min=65.96, max=66.56
- combine: median=118.88, min=82.53, max=157.24
