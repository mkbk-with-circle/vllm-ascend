"""与 dispatch_ffn_combine_profile.h 保持一致的 host 侧常量。"""

DFFC_PROFILE_MAGIC = 0x44504643
DFFC_PROFILE_VERSION = 1
DFFC_PROFILE_NUM_PHASES = 6
DFFC_PROFILE_WORDS = 2 + 2 * DFFC_PROFILE_NUM_PHASES

PHASE_NAMES = ("prep", "dispatch", "swiglu", "combine", "gmm1", "gmm2")
AIV_PHASES = frozenset({"prep", "dispatch", "swiglu", "combine"})
AIC_PHASES = frozenset({"gmm1", "gmm2"})
