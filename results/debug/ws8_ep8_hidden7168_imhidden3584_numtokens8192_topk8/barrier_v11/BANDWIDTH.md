# dispatch/combine 有效带宽

- hidden (K): 7168, imhidden: 3584, numtokens: 8192, topk: 8
- bytes/token dispatch: 7200, combine: 14336

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 3,774,873,600 | 4380.0 | 861.84 |
| combine | 7,516,192,768 | 6503.0 | 1155.80 |

## Per-rank 带宽 (GB/s)

- dispatch: median=109.02, min=108.20, max=109.66
- combine: median=148.25, min=145.17, max=291.05
