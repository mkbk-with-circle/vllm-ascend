# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 1,082,130,432 | 6882.0 | 157.24 |
| combine | 2,147,483,648 | 9746.0 | 220.35 |

## Per-rank 带宽 (GB/s)

- dispatch: median=39.63, min=39.46, max=39.75
- combine: median=83.01, min=54.89, max=112.03
