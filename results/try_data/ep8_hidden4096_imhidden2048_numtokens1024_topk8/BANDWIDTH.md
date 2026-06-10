# dispatch/combine 有效带宽

- hidden (K): 4096, imhidden: 2048, numtokens: 1024, topk: 8
- bytes/token dispatch: 4128, combine: 8192

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 270,532,608 | 406.0 | 666.34 |
| combine | 536,870,912 | 696.0 | 771.37 |

## Per-rank 带宽 (GB/s)

- dispatch: median=84.82, min=83.18, max=87.59
- combine: median=98.75, min=96.02, max=144.60
