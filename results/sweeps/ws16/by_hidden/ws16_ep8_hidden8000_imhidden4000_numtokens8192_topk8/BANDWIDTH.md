# dispatch/combine 有效带宽

- hidden (K): 8000, imhidden: 4000, numtokens: 8192, topk: 8
- bytes/token dispatch: 8032, combine: 16000

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 8,422,162,432 | 3861.0 | 2181.34 |
| combine | 16,777,216,000 | 6755.0 | 2483.67 |

## Per-rank 带宽 (GB/s)

- dispatch: median=136.67, min=135.70, max=138.10
- combine: median=160.33, min=154.17, max=476.19
