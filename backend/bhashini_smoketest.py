#!/usr/bin/env python3
"""
Bhashini LIVE smoke test — proves your userID + ulcaApiKey work end-to-end.
Usage:
  export BHASHINI_USER_ID='<your ULCA user id>'
  export BHASHINI_API_KEY='<your ULCA api key>'
  python backend/bhashini_smoketest.py
Does: 1) Pipeline Config (shows serviceIds + inference endpoint), 2) Text-Language-Detection
compute on a sample, 3) optional TTS compute. Uses ~3 of your 2,000 calls.
"""
from __future__ import annotations
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bhashini as B


def main():
    st = B.status()
    print("mode:", st["mode"])
    if not st["have_keys"]:
        print("\n!! set BHASHINI_USER_ID and BHASHINI_API_KEY first (ULCA → My Profile).")
        print("   export BHASHINI_USER_ID='...'\n   export BHASHINI_API_KEY='...'")
        return 1
    try:
        print("\n[1] Pipeline Config (asr + translation + tts) …")
        cfg = B.config([{"taskType": "asr"}, {"taskType": "translation"}, {"taskType": "tts"}])
        ep = cfg.get("pipelineInferenceAPIEndPoint", {})
        print("    callbackUrl :", ep.get("callbackUrl"))
        print("    auth header :", (ep.get("inferenceApiKey") or {}).get("name"))
        for blk in cfg.get("pipelineResponseConfig", []):
            svc = (blk.get("config") or [{}])[0]
            print(f"    {blk.get('taskType'):22} serviceId={svc.get('serviceId')}")

        print("\n[2] Text Language Detection on 'नमस्ते दुनिया' …")
        tld = B.detect_text_language("नमस्ते दुनिया")
        print("   ", json.dumps(tld.get("pipelineResponse", tld))[:300])

        if os.environ.get("BHASHINI_TEST_TTS") == "1":
            print("\n[3] TTS 'नमस्ते' (hi, female) …")
            tts = B.synthesize("नमस्ते", "hi")
            out = tts.get("pipelineResponse", tts)
            print("    keys:", list(out[0].keys()) if isinstance(out, list) else type(out))
        print("\nDONE — Bhashini is connected.")
        return 0
    except Exception as e:
        print("\n!! failed:", str(e)[:300])
        print("   check userID/ulcaApiKey and that your account is approved.")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
