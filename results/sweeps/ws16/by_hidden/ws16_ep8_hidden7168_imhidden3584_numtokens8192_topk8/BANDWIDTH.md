# dispatch/combine 有效带宽

- hidden (K): 7168, imhidden: 3584, numtokens: 8192, topk: 8
- bytes/token dispatch: 7200, combine: 14336

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 7,549,747,200 | 3514.0 | 2148.48 |
| combine | 15,032,385,536 | 6074.0 | 2474.87 |

## Per-rank 带宽 (GB/s)

- dispatch: median=135.23, min=134.33, max=136.17
- combine: median=159.26, min=153.72, max=473.15
