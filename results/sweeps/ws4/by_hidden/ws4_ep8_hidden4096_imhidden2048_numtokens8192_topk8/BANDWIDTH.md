# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 1,082,130,432 | 6881.0 | 157.26 |
| combine | 2,147,483,648 | 9759.0 | 220.05 |

## Per-rank 带宽 (GB/s)

- dispatch: median=39.56, min=39.47, max=39.81
- combine: median=83.13, min=54.82, max=111.98
