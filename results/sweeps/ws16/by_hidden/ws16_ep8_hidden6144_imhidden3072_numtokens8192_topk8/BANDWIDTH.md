# dispatch/combine 有效带宽

- hidden (K): 6144, imhidden: 3072, numtokens: 8192, topk: 8
- bytes/token dispatch: 6176, combine: 12288

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 6,476,005,376 | 3091.0 | 2095.12 |
| combine | 12,884,901,888 | 5272.0 | 2444.03 |

## Per-rank 带宽 (GB/s)

- dispatch: median=132.64, min=131.06, max=133.39
- combine: median=157.90, min=152.87, max=456.42
