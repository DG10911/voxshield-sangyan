import csv, time
import numpy as np, torch, soundfile as sf
from torch.utils.data import Dataset, DataLoader
from transformers import Wav2Vec2ForSequenceClassification
from sklearn.metrics import roc_auc_score, roc_curve

SR, CLIP_LEN = 16000, 16000 * 3

def load_clip(path):
    y, sr = sf.read(path)
    if y.ndim > 1: y = y.mean(1)
    y = y.astype("float32")
    if len(y) < CLIP_LEN:
        y = np.pad(y, (0, CLIP_LEN - len(y)))
    elif len(y) > CLIP_LEN:
        y = y[:CLIP_LEN]
    return y

class DS(Dataset):
    def __init__(self, csv_path):
        self.rows = list(csv.DictReader(open(csv_path)))
    def __len__(self): return len(self.rows)
    def __getitem__(self, i):
        r = self.rows[i]
        try: y = load_clip(r["path"])
        except Exception: y = np.zeros(CLIP_LEN, np.float32)
        return torch.from_numpy(y), int(r["label"])

def eer(y_true, y_score):
    fpr, tpr, _ = roc_curve(y_true, y_score)
    fnr = 1 - tpr
    idx = np.nanargmin(np.abs(fpr - fnr))
    return float((fpr[idx] + fnr[idx]) / 2)

device = torch.device("cuda")
print("[eval] loading XLSR base...")
model = Wav2Vec2ForSequenceClassification.from_pretrained(
    "facebook/wav2vec2-large-xlsr-53", num_labels=2, ignore_mismatched_sizes=True)
print("[eval] loading fine-tuned weights...")
ck = torch.load("/home/srmist2/checkpoints/voxshield/wav2vec2_xlsr_itw/best.pt",
                map_location=device, weights_only=False)
model.load_state_dict(ck["model"])
model.to(device).eval()
print(f"[eval] baseline (random-split) EER = {ck['eer']*100:.2f}%")

ds = DS("manifests_dgx/itw_test_speakerdisjoint.csv")
dl = DataLoader(ds, batch_size=32, shuffle=False, num_workers=8, pin_memory=True)
print(f"[eval] scoring {len(ds)} clips from unseen speakers...")

scores, ys, t0 = [], [], time.time()
with torch.no_grad():
    for x, y in dl:
        x = x.to(device, non_blocking=True)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            logits = model(input_values=x).logits
        p = torch.softmax(logits, -1)[:, 1].float().cpu().numpy()
        scores.extend(p.tolist()); ys.extend(y.numpy().tolist())

y_true, y_scr = np.array(ys), np.array(scores)
e = eer(y_true, y_scr)
a = roc_auc_score(y_true, y_scr)
print("")
print("=" * 60)
print(f"SPEAKER-DISJOINT EER = {e*100:.2f}%   AUC = {a*100:.2f}%")
print(f"Random-split baseline was 0.16% — degradation = {(e - 0.0016)*100:+.2f} pts")
print(f"time = {time.time()-t0:.0f}s   n = {len(ds)}")
print("=" * 60)
