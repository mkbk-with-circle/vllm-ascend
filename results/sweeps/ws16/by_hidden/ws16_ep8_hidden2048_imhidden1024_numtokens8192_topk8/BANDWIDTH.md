# dispatch/combine 有效带宽

- hidden (K): 2048, imhidden: 1024, numtokens: 8192, topk: 8
- bytes/token dispatch: 2080, combine: 4096

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,181,038,080 | 1871.0 | 1165.71 |
| combine | 4,294,967,296 | 2640.0 | 1626.88 |

## Per-rank 带宽 (GB/s)

- dispatch: median=73.58, min=73.22, max=74.49
- combine: median=103.81, min=100.96, max=232.23
