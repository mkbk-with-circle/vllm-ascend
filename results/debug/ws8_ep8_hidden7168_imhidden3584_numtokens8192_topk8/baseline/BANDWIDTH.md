# dispatch/combine 有效带宽

- hidden (K): 7168, imhidden: 3584, numtokens: 8192, topk: 8
- bytes/token dispatch: 7200, combine: 14336

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 3,774,873,600 | 4373.0 | 863.22 |
| combine | 7,516,192,768 | 6538.0 | 1149.62 |

## Per-rank 带宽 (GB/s)

- dispatch: median=109.12, min=108.37, max=109.62
- combine: median=146.64, min=143.42, max=291.14
