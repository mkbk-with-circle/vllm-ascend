# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 1024, numtokens: 8192, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,164,260,864 | 3586.0 | 603.53 |
| combine | 4,294,967,296 | 5539.0 | 775.40 |

## Per-rank 带宽 (GB/s)

- dispatch: median=76.11, min=75.51, max=76.69
- combine: median=98.01, min=97.02, max=138.09
