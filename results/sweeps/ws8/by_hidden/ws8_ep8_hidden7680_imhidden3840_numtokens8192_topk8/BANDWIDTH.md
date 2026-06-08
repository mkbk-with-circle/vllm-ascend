# dispatch/combine 有效带宽

- hidden (K): 7680, imhidden: 3840, numtokens: 8192, topk: 8
- bytes/token dispatch: 7712, combine: 15360

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,043,309,056 | 4498.0 | 898.91 |
| combine | 8,053,063,680 | 6640.0 | 1212.81 |

## Per-rank 带宽 (GB/s)

- dispatch: median=113.57, min=112.41, max=114.89
- combine: median=154.11, min=151.20, max=296.14
