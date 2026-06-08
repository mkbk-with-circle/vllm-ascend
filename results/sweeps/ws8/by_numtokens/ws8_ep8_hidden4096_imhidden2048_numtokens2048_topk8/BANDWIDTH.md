# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 2048, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 541,065,216 | 978.0 | 553.24 |
| combine | 1,073,741,824 | 1402.0 | 765.86 |

## Per-rank 带宽 (GB/s)

- dispatch: median=70.63, min=68.99, max=71.14
- combine: median=100.30, min=96.65, max=211.86
