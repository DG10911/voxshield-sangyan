# VoxShield — Audio Forensics for Voice Security (Fusion Edition)

Real-time detection of AI-cloned / synthetic voices for banking & call-centre fraud.
Reads a call's **spectrogram + acoustic artifacts**, fuses **multiple detector families**,
and returns a calibrated **risk verdict (Low / Medium / High)** with **explainable reason
codes** — with a sliding-window mode that flags a call **within the first 10 seconds**.

Built for **Team DigiSeva (SRM IST)** · Problem Statement PS2.

```
voxshield/
├── backend/
│   ├── app.py            FastAPI: /analyze (clip) + /stream-analyze (sliding window)
│   ├── fusion.py         multi-model fusion + calibration + reason codes + streaming
│   ├── models.py         detector registry: acoustic DSP + N HuggingFace models
│   ├── features.py       LFCC, CQCC, group-delay(phase), prosody, mel-spectrogram, feature vector
│   ├── augment.py        RawBoost + 8kHz/G.711 codec + noise/pitch/stretch augmentation
│   ├── metrics.py        EER, min t-DCF, Platt calibration, numpy logistic fusion head
│   ├── train_fusion.py   super-dataset training + cross-dataset EER (+ --selftest)
│   ├── artifacts/        trained fusion_head.json + calibrator.json (auto-loaded by API)
│   └── requirements.txt
├── frontend/             bank-grade dashboard (index.html, styles.css, app.js)
├── run.sh · README.md
```

## One command — everything
```bash
bash run.sh                    # install + train (self-test) + launch the UI
bash run.sh --get-data --ml    # DOWNLOAD real datasets + neural models, train, launch
bash run.sh /path/to/data      # ALSO auto-builds manifests + trains on your merged super-dataset
bash run.sh /path/to/data --ml # ALSO installs torch+transformers (neural model ensemble)
```

### Download the real datasets (so you can defend a real EER)
```bash
cd backend
python download_data.py --itw                # In-the-Wild  (~7.5 GB, real+fake, the test set)
python download_data.py --itw --asvspoof      # + ASVspoof 2019 LA (~7.1 GB, standard train)
python download_data.py --all                 # + WaveFake (~30 GB)
```
Verified sources: In-the-Wild → HuggingFace `mueller91/In-The-Wild`; ASVspoof LA →
Edinburgh DataShare `10283/3336`; WaveFake → Zenodo `4904579`. The script arranges files into
`data/<dataset>/real|fake/` (ASVspoof protocol files are parsed automatically). Then just
`bash run.sh data --ml`.

> Note: datasets are large and must download to *your* machine. `--get-data` grabs In-the-Wild +
> ASVspoof for you; add WaveFake manually if you want it.
`run.sh` creates a venv, installs deps, (if you pass a data folder) scans it, auto-labels
real vs fake, writes per-dataset manifests, trains the fusion head with RawBoost + 8 kHz codec
augmentation, holds out In-the-Wild for a cross-dataset EER, then starts the API + dashboard at
**http://localhost:8000**.

**Data folder layout** (any of these keywords in folder names are auto-detected):
```
data/<dataset>/real|bonafide|genuine/*.wav
data/<dataset>/fake|spoof|synthetic|deepfake/*.wav
```
ASVspoof-style protocol `.txt` files are parsed automatically too.

### Manual (if you prefer the steps)
```bash
cd voxshield/backend && pip install -r requirements.txt
python make_manifests.py /path/to/data --out manifests   # build CSVs
python train_fusion.py --manifests-dir manifests --augment
uvicorn app:app --reload --port 8000
```
Then open **http://localhost:8000** → choose **Live streaming** or **Whole-clip fusion**, drop an
audio file (or record), and read the verdict, the per-detector fusion breakdown, the reason
codes, and (in streaming mode) the decision timeline with time-to-flag.

## The fusion system (what makes it the best version)

**1. Model fusion — diverse families, decorrelated errors.** `models.py` runs an ensemble:
the always-on **explainable acoustic detector** plus, when `torch`+`transformers` are
installed, three HuggingFace neural models (wav2vec2-base, XLS-R, DistilHuBERT-In-the-Wild).
Their probabilities are combined with calibrated weights.
```bash
pip install torch transformers        # enables the neural ensemble
export VOXSHIELD_MODELS="MelodyMachine/Deepfake-audio-detection-V2,Gustking/wav2vec2-large-xlsr-deepfake-audio-classification,Om-Parab/distilhubert-finetuned-audio-deepfake-in-the-wild"
```

**2. Best feature set** (`features.py`): **LFCC + CQCC** (top hand-crafted anti-spoofing
features), **group-delay phase** regularity, **prosody** (F0 jitter / shimmer / voiced ratio),
HF vocoder-fingerprint energy & regularity, spectral flatness, breath/silence cues — all
fed to a **trainable fusion head**.

**3. Trainable fusion head + calibration** (`metrics.py`): a logistic head over the LFCC/CQCC
feature vector, plus **Platt calibration** so scores are probabilities, not just rankings.

**4. Robustness augmentation** (`augment.py`): **RawBoost** (convolutive + impulsive +
stationary noise), **8 kHz / G.711 mu-law codec** simulation (telephony), noise, pitch, stretch.

**5. Sliding-window streaming** (`fusion.stream_analyze`): scores 3 s windows every 1 s,
accumulates evidence, and **fires the High-Risk flag as soon as the running score crosses
threshold** — returns the timeline and `flagged_at_s` (verified: synthetic clip flagged at 3.0 s).

## Train on the super-dataset (merge everything) & report cross-dataset EER

Make CSV manifests (`path,label,dataset`; label 1=fake, 0=bonafide) for each dataset, then:
```bash
# merge ASVspoof19 + WaveFake + CodecFake for training; hold out In-the-Wild for testing
python train_fusion.py \
  --train asvspoof19.csv wavefake.csv codecfake.csv \
  --test  in_the_wild.csv \
  --augment            # applies RawBoost + 8kHz codec copies to training data
```
Prints **in-domain EER** and **out-of-domain (In-the-Wild) EER + min t-DCF** — the protocol
that wins. Trained artifacts drop into `artifacts/` and the API uses them on next start.

No datasets yet? Prove the whole pipeline runs:
```bash
python train_fusion.py --selftest      # synthesises clips, trains, reports held-out EER
```

## API
| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | status + active detector ensemble |
| POST | `/api/analyze` | clip → `{score,label,confidence,reasons,per_model,fusion,features,spectrogram,latency_s,audio_sha256}` |
| POST | `/api/stream-analyze?threshold=0.70` | adds `timeline`, `flagged_at_s`, `decided_within_10s` |
| GET | `/api/audit` | recent decisions (hash-keyed) |
| GET | `/docs` | OpenAPI |

## Reason codes (explainability)
| Code | Reads | Artifact |
|---|---|---|
| SSL | neural/blended prob | overall synthesis likelihood |
| PH | group-delay + spectral flatness | unnaturally regular **phase** of synthesis |
| HF | >6 kHz energy + regularity | neural **vocoder fingerprint** |
| PR | F0 jitter / shimmer / voiced ratio | missing **prosody / pitch micro-variation** |
| BR | silence ratio + breath-band energy | TTS inserts **silence, not breath** |

## Security & deployment (banking/government)
- Raw audio **SHA-256 hashed** for the audit trail, **not stored in clear** (swap to AES-256 at rest with PyCryptodome to persist).
- Decisions **route to step-up verification, never auto-block** — anti-spoofing is a *layered* fraud signal feeding the existing flow alongside CNAP/caller-ID.
- Stateless API → scale horizontally (Render/Railway); static frontend on Vercel; on-prem/air-gapped for real banks.
- Built to GOV.UK / USWDS patterns, WCAG 2.1 AA (risk by icon+text, not colour alone).

## Roadmap
ONNX/quantised AASIST-L for CPU <10 s streaming · continual learning for new generators ·
source attribution · multilingual/Indic fine-tuning · adversarial-robust training (Malafide/Malacopula).

## Verified
`train_fusion.py --selftest` → held-out EER 0.00% on separable synthetic data (89-dim features).
API: fake clip → HIGH (0.73), genuine → LOW (0.12); streaming flagged the fake at **3.0 s (within 10 s)**.
(With `torch transformers` installed the neural ensemble joins automatically and raises real-world accuracy.)
