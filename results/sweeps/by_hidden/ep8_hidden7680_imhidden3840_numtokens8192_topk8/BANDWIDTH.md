# dispatch/combine 有效带宽

- hidden (K): 7680, imhidden: 3840, numtokens: 8192, topk: 8
- bytes/token dispatch: 7712, combine: 15360

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,043,309,056 | 4335.0 | 932.71 |
| combine | 8,053,063,680 | 7281.0 | 1106.04 |

## Per-rank 带宽 (GB/s)

- dispatch: median=117.61, min=116.78, max=118.40
- combine: median=139.43, min=138.79, max=196.82
