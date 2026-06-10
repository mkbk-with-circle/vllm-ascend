# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 16384, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,328,521,728 | 7091.0 | 610.42 |
| combine | 8,589,934,592 | 11012.0 | 780.05 |

## Per-rank 带宽 (GB/s)

- dispatch: median=76.63, min=76.30, max=77.01
- combine: median=98.00, min=97.29, max=129.85
