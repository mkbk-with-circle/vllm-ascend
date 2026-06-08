# Profile validation

## PASS
- 因果序检查通过

## WARN
- job: combine∥gmm2 overlap 858µs (combine [8050,14294), gmm2 [7442,8908))
- rank0: gmm2 e1 wall_begin < prev wall_end
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
- rank2: gmm2 e1 wall_begin < prev wall_end
- rank2: gmm2 e2 wall_begin < prev wall_end
- rank2: gmm2 e3 wall_begin < prev wall_end
- rank2: gmm2 e4 wall_begin < prev wall_end
- rank2: gmm2 e5 wall_begin < prev wall_end
- rank2: gmm2 e6 wall_begin < prev wall_end
- rank2: gmm2 e7 wall_begin < prev wall_end
- rank3: gmm2 e1 wall_begin < prev wall_end
- rank3: gmm2 e2 wall_begin < prev wall_end
- rank3: gmm2 e3 wall_begin < prev wall_end
- rank3: gmm2 e4 wall_begin < prev wall_end
- rank3: gmm2 e5 wall_begin < prev wall_end
- rank3: gmm2 e6 wall_begin < prev wall_end

## Job timeline (µs)
- prep: [0, 466) dur=466
- dispatch: [466, 6536) dur=6070
- swiglu: [6541, 8042) dur=1500
- combine: [8050, 14294) dur=6244
- gmm1: [1188, 6794) dur=5606
- gmm2: [7442, 8908) dur=1466
