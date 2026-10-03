"""
VoxShield — adversarial training (FGSM / PGD) of a detector back-end.
Thin wrapper over `train_backend.train` with adversarial defaults.

Usage (DGX):
    python adversarial_train.py --arch aasist --data-root data/hindi --langs hindi \
        --holdout vits --attack pgd --eps 0.005 --steps 5 --out checkpoints/aasist_adv_hindi
"""
from __future__ import annotations
import argparse
import train_backend as TB


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", default="aasist", choices=["lcnn", "conformer", "aasist"])
    ap.add_argument("--data-root"); ap.add_argument("--langs", default="hindi"); ap.add_argument("--holdout", default="vits")
    ap.add_argument("--attack", default="pgd", choices=["fgsm", "pgd", "none"])
    ap.add_argument("--eps", type=float, default=0.005); ap.add_argument("--alpha", type=float, default=0.001)
    ap.add_argument("--steps", type=int, default=5); ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--limit-per", type=int, default=None); ap.add_argument("--out", default="checkpoints/backend_adv")
    a = ap.parse_args()
    if not a.data_root:
        ap.error("--data-root required")
    TB.train(a.arch, a.data_root, a.langs, a.holdout, a.epochs, a.out,
             adv=a.attack, eps=a.eps, alpha=a.alpha, steps=a.steps, limit_per=a.limit_per)
    print(f"[adv] adversarial ({a.attack}) checkpoint -> {a.out}/last.pt")


if __name__ == "__main__":
    main()
