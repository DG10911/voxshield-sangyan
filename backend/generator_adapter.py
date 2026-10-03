"""
VoxShield — Generator Adapter interface (roadmap §25, VoiceStudio drop-in).

One uniform interface to every AI-voice generator so the Attack/Benchmark lab can call
any of them the same way. The generation backend itself is external (API keys and/or
GPU) and stays parked — but the ADAPTER LAYER is built now so real generators plug in
without touching the pipeline. Each adapter is cross-referenced to the Generator
Capability Registry (§4) and its output is rendered into scenarios via scenario_render (§25).

Flow: GeneratorAdapter.generate() → clip → scenario_render → VoxShield → benchmark.
A StubAdapter (deterministic synthetic-ish audio) lets the whole lab run offline/tested.
numpy + registries + scenario_render.
"""
from __future__ import annotations
import numpy as np
from typing import Dict, List, Optional


class GeneratorAdapter:
    """Base interface. Real adapters (ElevenLabs/Fish/XTTS/F5/CosyVoice…) subclass and
    implement generate(). API adapters need keys; open models need the GPU."""
    name: str = "base"
    requires: str = "none"          # "api_key" | "gpu" | "none"
    registry_model: Optional[str] = None   # links to registries/generators.json

    def generate(self, text: str, language: str = "hi", voice_ref: Optional[np.ndarray] = None,
                 sr: int = 16000) -> np.ndarray:
        raise NotImplementedError("real adapter must implement generate()")

    def available(self) -> bool:
        return True

    def info(self) -> Dict:
        return {"name": self.name, "requires": self.requires,
                "registry_model": self.registry_model, "available": self.available()}


class StubAdapter(GeneratorAdapter):
    """Offline, deterministic 'synthetic-ish' audio for testing the lab end-to-end.
    NOT a real generator — clearly labelled; produces an over-smooth harmonic tone."""
    name = "stub"; requires = "none"; registry_model = None

    def generate(self, text, language="hi", voice_ref=None, sr=16000):
        seed = abs(hash((text, language))) % (2**32)
        rng = np.random.default_rng(seed)
        dur = max(1.0, min(6.0, 0.06 * len(text) + 1.0))
        t = np.linspace(0, dur, int(sr*dur), endpoint=False)
        f0 = 150 + 10*np.sin(2*np.pi*0.3*t)                    # too-regular pitch (synthetic hint)
        y = sum(np.sin(2*np.pi*k*f0*t)/k for k in range(1, 6)) / 3
        return (y + 0.005*rng.standard_normal(len(t))).astype(np.float32)


# --- template for a REAL API adapter (parked until keys) ---
class _ApiAdapterTemplate(GeneratorAdapter):
    name = "elevenlabs"; requires = "api_key"; registry_model = "elevenlabs"
    def available(self):
        import os; return bool(os.environ.get("ELEVENLABS_API_KEY"))
    def generate(self, text, language="hi", voice_ref=None, sr=16000):  # pragma: no cover
        raise NotImplementedError("plug in ElevenLabs API here; needs ELEVENLABS_API_KEY")


_REGISTRY: Dict[str, GeneratorAdapter] = {}


def register(adapter: GeneratorAdapter):
    _REGISTRY[adapter.name] = adapter


def get(name: str) -> GeneratorAdapter:
    if name not in _REGISTRY:
        raise KeyError(f"no adapter '{name}' (registered: {list(_REGISTRY)})")
    return _REGISTRY[name]


def list_adapters() -> List[Dict]:
    return [a.info() for a in _REGISTRY.values()]


register(StubAdapter())
register(_ApiAdapterTemplate())


def _selftest():
    print("adapters:", [a["name"] for a in list_adapters()])
    stub = get("stub"); y = stub.generate("नमस्ते यह एक परीक्षण है", "hi")
    print("stub gen :", "len", len(y), "sr-equiv", round(len(y)/16000, 2), "s | available", stub.available())
    # determinism
    y2 = get("stub").generate("नमस्ते यह एक परीक्षण है", "hi")
    assert np.allclose(y, y2) and len(y) > 16000
    # parked API adapter reports unavailable without keys, doesn't crash
    api = get("elevenlabs"); print("elevenlabs available (no key):", api.available())
    assert api.available() is False
    # renders through the scenario pipeline (the local half)
    from scenario_render import render
    teleph = render(y, 16000, {"codec": "g711_ulaw", "snr_db": 20})
    assert np.isfinite(teleph["audio"]).all()
    print("rendered via scenario_render:", teleph["steps"])
    print("\n[selftest] PASS — uniform adapter interface; stub generates offline; real adapters plug in with keys/GPU.")


if __name__ == "__main__":
    _selftest()
