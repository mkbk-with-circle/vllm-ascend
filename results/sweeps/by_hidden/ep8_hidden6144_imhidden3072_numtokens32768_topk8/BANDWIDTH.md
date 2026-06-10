# dispatch/combine 有效带宽

- hidden (K): 6144, imhidden: 3072, numtokens: 32768, topk: 8
- bytes/token dispatch: 6176, combine: 12288

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 12,952,010,752 | 15939.0 | 812.60 |
| combine | 25,769,803,776 | 25346.0 | 1016.72 |

## Per-rank 带宽 (GB/s)

- dispatch: median=102.92, min=101.81, max=103.67
- combine: median=128.85, min=126.72, max=174.28
