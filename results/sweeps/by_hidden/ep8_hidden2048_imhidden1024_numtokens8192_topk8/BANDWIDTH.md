# dispatch/combine 有效带宽

- hidden (K): 2048, imhidden: 1024, numtokens: 8192, topk: 8
- bytes/token dispatch: 2080, combine: 4096

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 1,090,519,040 | 3129.0 | 348.52 |
| combine | 2,147,483,648 | 4706.0 | 456.33 |

## Per-rank 带宽 (GB/s)

- dispatch: median=43.80, min=43.62, max=44.32
- combine: median=58.15, min=57.22, max=82.45
