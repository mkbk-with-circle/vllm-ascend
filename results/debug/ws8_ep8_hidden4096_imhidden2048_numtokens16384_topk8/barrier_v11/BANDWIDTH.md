# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 16384, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,328,521,728 | 7361.0 | 588.03 |
| combine | 8,589,934,592 | 10978.0 | 782.47 |

## Per-rank 带宽 (GB/s)

- dispatch: median=74.09, min=73.52, max=74.39
- combine: median=98.73, min=98.08, max=205.84
