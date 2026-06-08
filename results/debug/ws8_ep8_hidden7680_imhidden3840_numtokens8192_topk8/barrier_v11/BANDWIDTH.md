# dispatch/combine 有效带宽

- hidden (K): 7680, imhidden: 3840, numtokens: 8192, topk: 8
- bytes/token dispatch: 7712, combine: 15360

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,043,309,056 | 4505.0 | 897.52 |
| combine | 8,053,063,680 | 6651.0 | 1210.80 |

## Per-rank 带宽 (GB/s)

- dispatch: median=113.46, min=112.17, max=114.65
- combine: median=154.74, min=150.92, max=297.02
