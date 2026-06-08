# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 2048, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 1,082,130,432 | 635.0 | 1704.14 |
| combine | 2,147,483,648 | 908.0 | 2365.07 |

## Per-rank 带宽 (GB/s)

- dispatch: median=109.70, min=107.99, max=110.92
- combine: median=151.25, min=148.11, max=417.28
