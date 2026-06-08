# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 1024, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 541,065,216 | 333.0 | 1624.82 |
| combine | 1,073,741,824 | 452.0 | 2375.54 |

## Per-rank 带宽 (GB/s)

- dispatch: median=104.11, min=101.87, max=106.97
- combine: median=156.80, min=146.48, max=391.34
