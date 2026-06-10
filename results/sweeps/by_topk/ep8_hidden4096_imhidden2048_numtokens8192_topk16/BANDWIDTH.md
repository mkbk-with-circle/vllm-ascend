# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 16
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,328,521,728 | 7101.0 | 609.57 |
| combine | 8,589,934,592 | 10950.0 | 784.47 |

## Per-rank 带宽 (GB/s)

- dispatch: median=76.69, min=76.37, max=76.93
- combine: median=98.61, min=98.02, max=130.72
