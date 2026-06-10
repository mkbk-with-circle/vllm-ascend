# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 4096, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 1,082,130,432 | 1773.0 | 610.34 |
| combine | 2,147,483,648 | 2766.0 | 776.39 |

## Per-rank 带宽 (GB/s)

- dispatch: median=77.20, min=76.74, max=77.38
- combine: median=97.58, min=97.21, max=134.77
