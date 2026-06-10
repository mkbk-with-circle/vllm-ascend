# dispatch/combine 有效带宽

- hidden (K): 7168, imhidden: 3584, numtokens: 8192, topk: 8
- bytes/token dispatch: 7200, combine: 14336

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 3,774,873,600 | 4210.0 | 896.64 |
| combine | 7,516,192,768 | 6935.0 | 1083.81 |

## Per-rank 带宽 (GB/s)

- dispatch: median=112.48, min=112.06, max=112.80
- combine: median=136.97, min=135.20, max=193.86
