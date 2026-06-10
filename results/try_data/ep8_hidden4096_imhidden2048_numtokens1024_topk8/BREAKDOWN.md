# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 5
- timeline 起点: prep=0；AIC 阶段用 min(begin)/max(end) 墙钟

| phase | median dur (µs) | max dur (µs) | timeline start (µs) | timeline block (µs) |
|-------|-----------------|--------------|---------------------|---------------------|
| prep | 3991.5 | 23652.0 | 0.0 | 23652.0 |
| dispatch | 398.0 | 407.0 | 3991.5 | 407.0 |
| swiglu | 198.5 | 217.0 | 4490.5 | 217.0 |
| combine | 677.0 | 696.0 | 5036.0 | 696.0 |
| gmm1 | 0.0 | 0.0 | 0.0 | 0.0 |
| gmm2 | 0.0 | 0.0 | 0.0 | 0.0 |

## 异常阶段

- `gmm1`: duration < 1µs
- `gmm2`: duration < 1µs
