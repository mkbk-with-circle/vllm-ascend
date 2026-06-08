# dispatch/combine 有效带宽

- hidden (K): 7968, imhidden: 3984, numtokens: 8192, topk: 8
- bytes/token dispatch: 8000, combine: 15936

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 8,388,608,000 | 3838.0 | 2185.67 |
| combine | 16,710,107,136 | 6860.0 | 2435.88 |

## Per-rank 带宽 (GB/s)

- dispatch: median=137.66, min=136.45, max=138.41
- combine: median=155.33, min=152.02, max=471.14
