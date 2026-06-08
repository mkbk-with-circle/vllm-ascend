# dispatch/combine 有效带宽

- hidden (K): 6144, imhidden: 3072, numtokens: 8192, topk: 8
- bytes/token dispatch: 6176, combine: 12288

## Job 级（sum(bytes) / max(time)）

| 阶段 | 总字节 | max 耗时 (µs) | 有效带宽 (GB/s) |
|------|--------|---------------|-----------------|
| dispatch | 3,238,002,688 | 4184.0 | 773.90 |
| combine | 6,442,450,944 | 5961.0 | 1080.77 |

## Per-rank 带宽 (GB/s)

- dispatch: median=98.02, min=96.69, max=98.69
- combine: median=137.11, min=135.15, max=280.08
