# Profile validation

## PASS
- 因果序检查通过

## WARN
- job: combine∥gmm2 overlap 274µs (combine [1194,2066), gmm2 [1117,1468))
- rank0: gmm1 e1 wall_begin < prev wall_end
- rank0: gmm2 e1 wall_begin < prev wall_end
- rank0: gmm2 e2 wall_begin < prev wall_end
- rank0: gmm2 e3 wall_begin < prev wall_end
- rank0: gmm2 e4 wall_begin < prev wall_end
- rank0: gmm2 e5 wall_begin < prev wall_end
- rank0: gmm2 e6 wall_begin < prev wall_end
- rank0: gmm2 e7 wall_begin < prev wall_end
- rank1: gmm1 e2 wall_begin < prev wall_end
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
- rank3: gmm2 e7 wall_begin < prev wall_end

## Job timeline (µs)
- prep: [0, 161) dur=161
- dispatch: [161, 939) dur=778
- swiglu: [968, 1212) dur=244
- combine: [1194, 2066) dur=873
- gmm1: [276, 1042) dur=767
- gmm2: [1117, 1468) dur=351
