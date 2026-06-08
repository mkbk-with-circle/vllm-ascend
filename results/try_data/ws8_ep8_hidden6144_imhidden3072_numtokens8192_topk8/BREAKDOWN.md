# dispatch_ffn_combine BREAKDOWN

- valid ranks: 8 [0, 1, 2, 3, 4, 5, 6, 7]
- profile version: 5
- timeline 起点: prep=0；AIC 阶段用 min(begin)/max(end) 墙钟

| phase | median dur (µs) | max dur (µs) | timeline start (µs) | timeline block (µs) |
|-------|-----------------|--------------|---------------------|---------------------|
| prep | 9200.0 | 21351.0 | 0.0 | 21351.0 |
| dispatch | 3569.0 | 3586.0 | 9200.5 | 3586.0 |
| swiglu | 2347.5 | 2360.0 | 16492.0 | 2360.0 |
| combine | 6219.5 | 6367.0 | 40293.0 | 6367.0 |
| gmm1 | 9925.5 | 9968.0 | 4245.0 | 30593.0 |
| gmm2 | 5443.5 | 5462.0 | 14140.0 | 26153.0 |
