# dispatch/combine 有效带宽

- hidden (K): 7680, imhidden: 3840, numtokens: 8192, topk: 8
- bytes/token dispatch: 7712, combine: 15360

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 8,086,618,112 | 3734.0 | 2165.67 |
| combine | 16,106,127,360 | 6655.0 | 2420.15 |

## Per-rank 带宽 (GB/s)

- dispatch: median=136.37, min=135.47, max=136.92
- combine: median=156.58, min=150.95, max=470.90
