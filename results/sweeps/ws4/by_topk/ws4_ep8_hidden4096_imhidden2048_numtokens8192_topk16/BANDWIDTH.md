# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 8192, topk: 16
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,164,260,864 | 13552.0 | 159.70 |
| combine | 4,294,967,296 | 19409.0 | 221.29 |

## Per-rank 带宽 (GB/s)

- dispatch: median=40.13, min=39.99, max=40.21
- combine: median=79.91, min=55.25, max=105.57
