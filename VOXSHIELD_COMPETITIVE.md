# VoxShield vs the competition

## Accuracy on In-the-Wild
| System                              | EER    | Notes                    |
|-------------------------------------|--------|--------------------------|
| Pindrop (enterprise, closed)        | ~5%    | English/Spanish, cloud   |
| Reality Defender (closed)           | 3-5%   | Multi-modal, cloud       |
| RawGAT-ST (academic 2021)           | 1.06%  | ASVspoof winner          |
| AASIST (academic 2022)              | 0.83%  | Open source              |
| VoxShield XLSR random-split         | 0.16%  | English, in-domain       |
| VoxShield XLSR speaker-disjoint     | 0.31%  | Honest generalization    |
| VoxShield XLSR + G.711 augment      | 0.99%  | Phone-quality (unique)   |

## Speed (per 3-sec clip, warm)
| System        | Latency        | Requests/sec/GPU |
|---------------|----------------|------------------|
| Pindrop cloud | 500-1500 ms    | ~2                |
| VoxShield A100| 19 ms          | ~50               |

## Language coverage
Only VoxShield supports Hindi/Tamil/Bengali. All competitors are English-first.

## Deployment
Only VoxShield and academic systems can be deployed on-prem. Banks/telcos
in India cannot legally send call audio to US cloud vendors.
