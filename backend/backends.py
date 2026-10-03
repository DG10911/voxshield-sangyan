"""
VoxShield — alternative detector back-ends ("AASIST3 / adversarial / distillation" work).

Three compact architectures that take a RAW waveform and return 2-class logits:
  * LCNN      — light CNN on log-mel (MobileNet-ish MaxFeatureMap)
  * Conformer — conv + self-attention encoder on log-mel
  * AASIST    — AASIST-style spectro-temporal graph-attention back-end
                (compact re-implementation; not the official AASIST3 release)

Used by `train_backend.py` (supervised + adversarial) and `distill.py`.
Self-test builds each net and runs a random batch on CPU.
"""
from __future__ import annotations
import torch, torch.nn as nn, torch.nn.functional as F

SR = 16000


def logmel(x, sr=SR, n_mels=64, n_fft=512, hop=160):
    """x: [B, T] or [B,1,T] waveform -> [B,1,n_mels,T'] log-mel."""
    import torchaudio
    if x.dim() == 2:
        x = x.unsqueeze(1)
    m = torchaudio.transforms.MelSpectrogram(
        sample_rate=sr, n_fft=n_fft, hop_length=hop, n_mels=n_mels).to(x.device)
    return torch.log(m(x) + 1e-6)


class MFM(nn.Module):                       # Max-Feature-Map
    def forward(self, x):
        a, b = x.chunk(2, dim=1)
        return torch.maximum(a, b)


class LCNN(nn.Module):
    def __init__(self, n_mels=64, nclass=2):
        super().__init__()
        def blk(i, o): return nn.Sequential(nn.Conv2d(i, o * 2, 3, padding=1), nn.BatchNorm2d(o * 2), MFM())
        self.net = nn.Sequential(blk(1, 16), nn.MaxPool2d(2), blk(16, 24), nn.MaxPool2d(2),
                                 blk(24, 32), nn.MaxPool2d(2), blk(32, 32), nn.AdaptiveAvgPool2d(1))
        self.fc = nn.Linear(32, nclass)

    def forward(self, x, sr=SR):
        h = self.net(logmel(x, sr)).flatten(1)
        return self.fc(h)


class Conformer(nn.Module):
    def __init__(self, n_mels=64, d=96, nclass=2, layers=2):
        super().__init__()
        self.proj = nn.Linear(n_mels, d)
        self.enc = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d, 4, dim_feedforward=2 * d, batch_first=True, dropout=0.1), layers)
        self.pool = nn.Linear(d, nclass)

    def forward(self, x, sr=SR):
        m = logmel(x, sr)                                   # [B,1,F,T]
        m = m.squeeze(1).transpose(1, 2)                    # [B,T,F]
        h = self.enc(self.proj(m)).mean(1)
        return self.pool(h)


class _ResBlock(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.c1 = nn.Conv2d(c, c, 3, padding=1); self.b1 = nn.BatchNorm2d(c)
        self.c2 = nn.Conv2d(c, c, 3, padding=1); self.b2 = nn.BatchNorm2d(c)
        self.act = nn.LeakyReLU(0.2)

    def forward(self, x):
        h = self.act(self.b1(self.c1(x)))
        h = self.b2(self.c2(h))
        return self.act(x + h)


class AASIST(nn.Module):
    """Compact AASIST-style: spectro-temporal conv encoder -> frame self-attention
    (graph) -> attentive statistics pooling -> logits."""
    def __init__(self, n_mels=64, hidden=48, nclass=2, blocks=3, heads=4):
        super().__init__()
        self.front = nn.Sequential(nn.Conv2d(1, hidden, 3, padding=1), nn.BatchNorm2d(hidden), nn.LeakyReLU(0.2))
        self.enc = nn.Sequential(*[_ResBlock(hidden) for _ in range(blocks)])
        self.attn = nn.MultiheadAttention(hidden, heads, batch_first=True)
        self.norm = nn.LayerNorm(hidden)
        self.att = nn.Linear(hidden, 1)
        self.fc = nn.Linear(2 * hidden, nclass)

    def forward(self, x, sr=SR):
        m = logmel(x, sr)                          # [B,1,F,T]
        h = self.enc(self.front(m))                # [B,H,F,T]
        B, H, Fr, T = h.shape
        seq = h.mean(2).transpose(1, 2)            # [B,T,H]
        a, _ = self.attn(seq, seq, seq)
        seq = self.norm(seq + a)
        w = torch.softmax(self.att(seq).squeeze(-1), -1)     # [B,T]
        mu = (seq * w.unsqueeze(-1)).sum(1)
        var = ((seq - mu.unsqueeze(1)) ** 2 * w.unsqueeze(-1)).sum(1).clamp_min(1e-6).sqrt()
        return self.fc(torch.cat([mu, var], -1))


ARCH = {"lcnn": LCNN, "conformer": Conformer, "aasist": AASIST}


def build(arch="aasist", nclass=2, **kw):
    return ARCH[arch](nclass=nclass, **kw)


def _selftest():
    x = torch.randn(4, 16000 * 3)
    for name in ARCH:
        m = build(name).eval()
        with torch.no_grad():
            out = m(x)
        assert out.shape == (4, 2), (name, out.shape)
        n = sum(p.numel() for p in m.parameters())
        print(f"  {name:<10} out={tuple(out.shape)} params={n/1e6:.2f}M")
    print("\n[selftest] PASS — LCNN / Conformer / AASIST build and run on a random batch.")


if __name__ == "__main__":
    _selftest()
