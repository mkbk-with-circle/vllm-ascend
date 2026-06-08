# dispatch/combine 有效带宽

- hidden (K): 7968, imhidden: 3984, numtokens: 8192, topk: 8
- bytes/token dispatch: 8000, combine: 15936

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,097,152,000 | 7519.0 | 278.91 |
| combine | 4,177,526,784 | 13040.0 | 320.36 |

## Per-rank 带宽 (GB/s)

- dispatch: median=70.27, min=69.83, max=70.88
- combine: median=118.51, min=80.16, max=156.49
