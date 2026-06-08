# dispatch/combine 有效带宽

- hidden (K): 6144, imhidden: 3072, numtokens: 8192, topk: 8
- bytes/token dispatch: 6176, combine: 12288

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 1,619,001,344 | 7221.0 | 224.21 |
| combine | 3,221,225,472 | 10769.0 | 299.12 |

## Per-rank 带宽 (GB/s)

- dispatch: median=56.26, min=56.06, max=56.36
- combine: median=110.34, min=74.85, max=146.56
