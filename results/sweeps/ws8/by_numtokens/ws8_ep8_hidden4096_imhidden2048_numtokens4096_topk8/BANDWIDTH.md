# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 4096, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 1,082,130,432 | 1909.0 | 566.86 |
| combine | 2,147,483,648 | 2763.0 | 777.23 |

## Per-rank 带宽 (GB/s)

- dispatch: median=71.74, min=71.05, max=72.39
- combine: median=98.66, min=97.19, max=196.16
