# Verified profile + papers for Prof. Hemant A. Patil (DA-IICT), confirmed via
# ISCA Archive, IEEE Xplore, Cambridge Core, Google Scholar (2026-09-17).
from gbt_refs import REFS as _BASE

PATIL_INTERESTS = ("anti-spoofing countermeasures for automatic speaker verification, novel spoof-detection "
                   "features (cochlear-filter and instantaneous-frequency cues, and group-delay methods), "
                   "replay-attack and voice-liveness detection, and cross-attack generalisation across the "
                   "ASVspoof series")

# Patil-specific verified references, numbered continuing from the shared list ([1]-[14]).
_PATIL = [
 "[15] T. B. Patel and H. A. Patil, “Combining evidences from mel cepstral, cochlear filter cepstral and instantaneous frequency features for detection of natural vs. spoofed speech,” Interspeech 2015 (a top-performing ASVspoof 2015 system). ISCA Archive.",
 "[16] T. B. Patel and H. A. Patil, “Cochlear Filter and Instantaneous Frequency Based Features for Spoofed Speech Detection,” IEEE Signal Processing Letters, 2017.",
 "[17] M. R. Kamble, H. B. Sailor, H. A. Patil, H. Li, “Advances in anti-spoofing: from the perspective of ASVspoof challenges,” APSIPA Transactions on Signal and Information Processing, 2020.",
 "[18] H. A. Patil et al., “Energy Separation-Based Instantaneous Frequency Estimation for Cochlear Cepstral Feature for Replay Spoof Detection,” Interspeech 2019 (ASVspoof 2017 v2.0).",
 "[19] H. A. Patil et al., “Significance of Distance on Pop Noise for Voice Liveness Detection,” Springer, 2022 (voice-liveness line).",
]
REFS = list(_BASE) + _PATIL

# Bulleted, human-readable form for the "why we are writing" section.
PATIL_PAPERS = [
 "Instantaneous-frequency / cochlear-filter spoof features (CFCCIF), Interspeech 2015 &amp; IEEE SPL 2017 [15,16] — directly relevant to our 89-dim phase / group-delay and HF cues.",
 "ASVspoof-generalisation survey, APSIPA 2020 [17] — bears on our central cross-generator question (Q1).",
 "Energy-separation instantaneous-frequency features for replay detection, Interspeech 2019 [18] — relevant to channel/replay robustness (Q2, Q3).",
 "Pop-noise voice-liveness detection, Springer 2022 [19] — directly relevant to our liveness option and its validation.",
]
