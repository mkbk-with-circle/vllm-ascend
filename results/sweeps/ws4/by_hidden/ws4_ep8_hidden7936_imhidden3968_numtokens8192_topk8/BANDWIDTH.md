# dispatch/combine 有效带宽

- hidden (K): 7936, imhidden: 3968, numtokens: 8192, topk: 8
- bytes/token dispatch: 7968, combine: 15872

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 2,088,763,392 | 7536.0 | 277.17 |
| combine | 4,160,749,568 | 12446.0 | 334.30 |

## Per-rank 带宽 (GB/s)

- dispatch: median=69.50, min=69.25, max=69.70
- combine: median=121.23, min=83.91, max=159.16
