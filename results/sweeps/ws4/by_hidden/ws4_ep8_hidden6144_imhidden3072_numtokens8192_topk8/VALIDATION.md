# Profile validation

## FAIL
- rank0: swiglu_w2.begin < gmm1.end (wait GMM1)

## WARN
- job: combine∥gmm2 overlap 4064µs (combine [26361,34466), gmm2 [18274,30426))
- rank0: gmm1 e1 wall_begin < prev wall_end
- rank0: gmm1 e2 wall_begin < prev wall_end
- rank0: gmm1 e3 wall_begin < prev wall_end
- rank0: gmm1 e4 wall_begin < prev wall_end
- rank0: gmm1 e5 wall_begin < prev wall_end
- rank0: gmm2 e1 wall_begin < prev wall_end
- rank0: gmm2 e2 wall_begin < prev wall_end
- rank0: gmm2 e7 wall_begin < prev wall_end
- rank1: gmm1 e1 wall_begin < prev wall_end
- rank1: gmm1 e2 wall_begin < prev wall_end
- rank1: gmm1 e3 wall_begin < prev wall_end
- rank1: gmm1 e4 wall_begin < prev wall_end
- rank1: gmm1 e5 wall_begin < prev wall_end
- rank1: gmm1 e6 wall_begin < prev wall_end
- rank1: gmm1 e7 wall_begin < prev wall_end
- rank1: gmm1 sum(active_us)=24085 > phase dur 16206
- rank1: gmm2 e1 wall_begin < prev wall_end
- rank1: gmm2 e2 wall_begin < prev wall_end
- rank1: gmm2 e3 wall_begin < prev wall_end
- rank1: gmm2 e4 wall_begin < prev wall_end
- rank1: gmm2 e5 wall_begin < prev wall_end
- rank1: gmm2 e6 wall_begin < prev wall_end
- rank1: gmm2 e7 wall_begin < prev wall_end
- rank1: gmm2 sum(active_us)=12645 > phase dur 11647
- rank2: gmm1 e1 wall_begin < prev wall_end
- rank2: gmm1 e2 wall_begin < prev wall_end
- rank2: gmm1 e3 wall_begin < prev wall_end
- rank2: gmm1 e4 wall_begin < prev wall_end
- rank2: gmm1 e5 wall_begin < prev wall_end
- rank2: gmm1 e6 wall_begin < prev wall_end
- rank2: gmm1 e7 wall_begin < prev wall_end
- rank2: gmm1 sum(active_us)=23607 > phase dur 16549
- rank2: gmm2 e1 wall_begin < prev wall_end
- rank2: gmm2 e2 wall_begin < prev wall_end
- rank2: gmm2 e3 wall_begin < prev wall_end
- rank2: gmm2 e4 wall_begin < prev wall_end
- rank2: gmm2 e5 wall_begin < prev wall_end
- rank2: gmm2 e6 wall_begin < prev wall_end
- rank2: gmm2 e7 wall_begin < prev wall_end
- rank3: gmm1 e1 wall_begin < prev wall_end
- rank3: gmm1 e2 wall_begin < prev wall_end
- rank3: gmm1 e3 wall_begin < prev wall_end
- rank3: gmm1 e4 wall_begin < prev wall_end
- rank3: gmm1 e5 wall_begin < prev wall_end
- rank3: gmm1 e6 wall_begin < prev wall_end
- rank3: gmm1 e7 wall_begin < prev wall_end
- rank3: gmm1 sum(active_us)=23799 > phase dur 16485
- rank3: gmm2 e1 wall_begin < prev wall_end
- rank3: gmm2 e2 wall_begin < prev wall_end
- rank3: gmm2 e3 wall_begin < prev wall_end
- rank3: gmm2 e4 wall_begin < prev wall_end
- rank3: gmm2 e5 wall_begin < prev wall_end
- rank3: gmm2 e6 wall_begin < prev wall_end
- rank3: gmm2 e7 wall_begin < prev wall_end
- rank3: gmm2 sum(active_us)=12502 > phase dur 11591

## Job timeline (µs)
- prep: [0, 986) dur=986
- dispatch: [986, 8184) dur=7198
- swiglu: [17039, 25896) dur=8857
- combine: [26361, 34466) dur=8106
- gmm1: [1536, 18053) dur=16517
- gmm2: [18274, 30426) dur=12152
