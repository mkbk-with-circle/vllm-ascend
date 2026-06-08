# dispatch/combine 有效带宽

- hidden (K): 8000, imhidden: 4000, numtokens: 8192, topk: 8
- bytes/token dispatch: 8032, combine: 16000

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,105,540,608 | 7586.0 | 277.56 |
| combine | 4,194,304,000 | 12721.0 | 329.71 |

## Per-rank 带宽 (GB/s)

- dispatch: median=70.23, min=69.70, max=70.38
- combine: median=119.94, min=82.48, max=158.21
