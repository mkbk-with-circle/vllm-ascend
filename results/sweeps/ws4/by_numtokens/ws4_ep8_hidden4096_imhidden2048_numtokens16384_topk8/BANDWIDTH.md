# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 16384, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,164,260,864 | 13481.0 | 160.54 |
| combine | 4,294,967,296 | 19491.0 | 220.36 |

## Per-rank 带宽 (GB/s)

- dispatch: median=40.16, min=40.12, max=40.23
- combine: median=80.33, min=55.11, max=105.69
