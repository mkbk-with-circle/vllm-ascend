# Profile validation

## FAIL
- job: gmm2.start (196) < gmm1.start (353)

## WARN
- job: gmm2 insufficient_ranks (n=0)

## Job timeline (µs)
- prep: [0, 196) dur=196
- dispatch: [196, 595) dur=399
- swiglu: [662, 1050) dur=388
- combine: [1250, 1935) dur=686
- gmm1: [353, 950) dur=596
- gmm2: [196, 196) dur=0
