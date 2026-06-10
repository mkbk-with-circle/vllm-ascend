# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 5
- timeline 起点: prep=0；AIC 阶段用 min(begin)/max(end) 墙钟

| phase | median dur (µs) | max dur (µs) | timeline start (µs) | timeline block (µs) |
|-------|-----------------|--------------|---------------------|---------------------|
| prep | 19012.0 | 32490.0 | 0.0 | 32490.0 |
| dispatch | 3110.5 | 3129.0 | 19012.0 | 3129.0 |
| swiglu | 1888.5 | 1899.0 | 22887.0 | 1899.0 |
| combine | 5421.0 | 5457.0 | 42019.0 | 5457.0 |
| gmm1 | 3966.0 | 3980.0 | 3688.0 | 35881.0 |
| gmm2 | 2464.5 | 2471.0 | 7654.0 | 34365.0 |
