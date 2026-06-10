# dispatch/combine 有效带宽

- hidden (K): 7968, imhidden: 3984, numtokens: 8192, topk: 8
- bytes/token dispatch: 8000, combine: 15936

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 4,194,304,000 | 4308.0 | 973.61 |
| combine | 8,355,053,568 | 7328.0 | 1140.15 |

## Per-rank 带宽 (GB/s)

- dispatch: median=122.86, min=121.81, max=123.80
- combine: median=146.28, min=142.41, max=204.53
