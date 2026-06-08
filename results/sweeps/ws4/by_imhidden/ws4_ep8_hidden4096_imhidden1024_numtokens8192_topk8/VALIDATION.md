# Profile validation

## PASS
- 因果序检查通过

## WARN
- job: combine∥gmm2 overlap 2232µs (combine [8611,15873), gmm2 [7944,10844))
- rank0: gmm2 e1 wall_begin < prev wall_end
- rank0: gmm2 e2 wall_begin < prev wall_end
- rank0: gmm2 e3 wall_begin < prev wall_end
- rank0: gmm2 e4 wall_begin < prev wall_end
- rank0: gmm2 e5 wall_begin < prev wall_end
- rank0: gmm2 e6 wall_begin < prev wall_end
- rank0: gmm2 e7 wall_begin < prev wall_end
- rank1: gmm2 e1 wall_begin < prev wall_end
- rank1: gmm2 e2 wall_begin < prev wall_end
- rank1: gmm2 e3 wall_begin < prev wall_end
- rank1: gmm2 e4 wall_begin < prev wall_end
- rank1: gmm2 e5 wall_begin < prev wall_end
- rank1: gmm2 e6 wall_begin < prev wall_end
- rank1: gmm2 e7 wall_begin < prev wall_end
- rank1: gmm2 sum(active_us)=3413 > phase dur 2868
- rank2: gmm2 e1 wall_begin < prev wall_end
- rank2: gmm2 e2 wall_begin < prev wall_end
- rank2: gmm2 e3 wall_begin < prev wall_end
- rank2: gmm2 e4 wall_begin < prev wall_end
- rank2: gmm2 e5 wall_begin < prev wall_end
- rank2: gmm2 e6 wall_begin < prev wall_end
- rank2: gmm2 e7 wall_begin < prev wall_end
- rank2: gmm2 sum(active_us)=3342 > phase dur 2846
- rank3: gmm2 e1 wall_begin < prev wall_end
- rank3: gmm2 e2 wall_begin < prev wall_end
- rank3: gmm2 e3 wall_begin < prev wall_end
- rank3: gmm2 e4 wall_begin < prev wall_end
- rank3: gmm2 e5 wall_begin < prev wall_end
- rank3: gmm2 e6 wall_begin < prev wall_end
- rank3: gmm2 e7 wall_begin < prev wall_end
- rank3: gmm2 sum(active_us)=3446 > phase dur 2931

## Job timeline (µs)
- prep: [0, 562) dur=562
- dispatch: [562, 7080) dur=6519
- swiglu: [7040, 8554) dur=1514
- combine: [8611, 15873) dur=7262
- gmm1: [1307, 7510) dur=6202
- gmm2: [7944, 10844) dur=2900
