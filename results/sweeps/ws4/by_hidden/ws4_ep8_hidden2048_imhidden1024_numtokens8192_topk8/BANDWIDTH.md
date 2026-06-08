# dispatch/combine 有效带宽

- hidden (K): 2048, imhidden: 1024, numtokens: 8192, topk: 8
- bytes/token dispatch: 2080, combine: 4096

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 545,259,520 | 6084.0 | 89.62 |
| combine | 1,073,741,824 | 8631.0 | 124.41 |

## Per-rank 带宽 (GB/s)

- dispatch: median=22.52, min=22.43, max=22.67
- combine: median=49.30, min=31.01, max=68.24
