# VOXSHIELD × AIKosh — Integration Research, Catalogue & Runbook
### IndiaAI National AI Repository → VoxShield (roadmap §38). Companion to `VOXSHIELD_ROADMAP.md`.

**AIKosh** = India's national AI dataset/model repository (MeitY / IndiaAI / NeGD). For VoxShield it is a **source** — Indic speech data, Indic TTS/ASR/NMT models, and annotation tooling — **not** a detector and **not** a place to upload consented audio.

> ✅ **Catalogue fully enumerated + verified live via the AIKosh MCP (2026-09-30).**
> Sweep: **94 speech/audio models** (13 model-types) and **3,929 dataset hits** → **124 curated speech datasets** after de-duplication/classification. Ids, licences and access types below were read from the platform; licences are re-checked per asset at ingest.

---

## 1 · Connection surfaces

### 1.1 MCP (connected, verified)
- **Endpoint** `https://aikosh.indiaai.gov.in/aikoshmcp/mcp` — **Streamable HTTP** (not stdio).
- **Auth** OAuth 2.1 + PKCE **or** `Authorization: Bearer <AIKosh_API_KEY>`. Verified: unauth POST → `401` + `WWW-Authenticate`; scopes `mcp:tools`, `mcp:tools:dataset`, `mcp:tools:download`, `mcp:tools:models`.
- **Tools (15):** `get_dataset_filters` · `list_datasets_tool` · `get_dataset_metadata` · `get_dataset_file_structure` · `get_dataset_download_url_tool` · `get_file_download_url_tool` · `search_datasets_and_get_download_urls` · `search_datasets_with_signed_urls` · `ping` · `get_model_filters_tool` · `list_models_tool` · `get_model_metadata_tool` · `get_model_file_structure_tool` · `get_model_download_url_tool` · `get_model_file_download_url_tool`.
- **opencode wiring** (`~/.config/opencode/opencode.jsonc`):
```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "aikosh": {
      "type": "remote",
      "url": "https://aikosh.indiaai.gov.in/aikoshmcp/mcp",
      "oauth": false,
      "headers": { "Authorization": "Bearer {env:AIKOSH_API_KEY}" },
      "enabled": true
    }
  }
}
```

### 1.2 Python SDK (automated ingest)
- `pip install aikosh` (Apache-2.0); `aikosh.set_api_key(...)` (env `AIKOSH_API_KEY`).
- Base API `https://aikosh-api.indiaai.gov.in/akp/idp/api/v1`, header `access-key` (did not resolve from this network → use MCP here).

### 1.3 Raw research artifacts (on the KIOXIA SSD)
`/Volumes/KIOXIA/voxshield/aikosh_research/` → `models_enriched.json` (94) · `datasets_enriched.json` (124) · `models_raw.json` · `datasets_raw.json` · `filters.json` · `AIKOSH_CATALOG.md` · `mcp.py` (MCP client).

---

## 2 · Commands

### 2.1 Make the API key permanent in opencode
```bash
# add the key to your zsh profile (do not paste it into chat again)
echo 'export AIKOSH_API_KEY=YOUR_KEY_HERE' >> ~/.zshrc
source ~/.zshrc
# verify
echo "${AIKOSH_API_KEY:0:6}…"
# restart opencode, then:
opencode mcp list            # should show aikosh as connected
# (or) authenticate via OAuth instead of a static key:
opencode mcp auth aikosh
```
> The opencode config reads `{env:AIKOSH_API_KEY}` — no secret is stored in the config file.

### 2.2 Run everything off the KIOXIA SSD
```bash
# 1. workspace + caches on KIOXIA
mkdir -p /Volumes/KIOXIA/voxshield/{data,models,hf_cache,tmp,logs}
export VOXSHIELD_ROOT=/Volumes/KIOXIA/voxshield
export HF_HOME=$VOXSHIELD_ROOT/hf_cache
export TMPDIR=$VOXSHIELD_ROOT/tmp
export TORCH_HOME=$VOXSHIELD_ROOT/models
export PIP_CACHE_DIR=$VOXSHIELD_ROOT/tmp/pip
export HF_HUB_ENABLE_HF_TRANSFER=1
# 2. persist for every future shell
cat >> ~/.zshrc <<'EOF'
export AIKOSH_API_KEY=YOUR_KEY_HERE
export VOXSHIELD_ROOT=/Volumes/KIOXIA/voxshield
export HF_HOME=$VOXSHIELD_ROOT/hf_cache
export TMPDIR=$VOXSHIELD_ROOT/tmp
export TORCH_HOME=$VOXSHIELD_ROOT/models
export PIP_CACHE_DIR=$VOXSHIELD_ROOT/tmp/pip
export HF_HUB_ENABLE_HF_TRANSFER=1
EOF
source ~/.zshrc
```

### 2.3 Pull an asset (signed URL) via the MCP
```bash
BASE=https://aikosh.indiaai.gov.in/aikoshmcp/mcp
curl -s "$BASE" -H "Authorization: Bearer $AIKOSH_API_KEY" \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_dataset_download_url_tool","arguments":{"dataset_id":"c112ce47-770c-47f3-80be-09b5afec8bc5"}}}'
```
Or use the helper: `python3 /Volumes/KIOXIA/voxshield/aikosh_research/mcp.py <tool> '<json-args>'`.

### 2.4 Ingest through VoxShield (licence-gated)
```bash
cd <repo>/backend
python3 aikosh_ingest.py        # self-test: catalogue + licence gate + offline ingest
```

---

## 3 · Verified catalogue
## Models

### A. Attack-generation models (32)
| Model | Licence | Access | id |
|---|---|---|---|
| A2TTS-Bengali Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `f0843b23-b6bd-41af-98f5-904376352a7f` |
| A2TTS-Gujarati Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `f565334a-89a5-4803-b116-5e9198704758` |
| A2TTS-Kannada Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `275b79db-df65-4707-bc52-7bff67ad4b03` |
| A2TTS-Malayalam Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `09cdfb55-5a02-4e7d-92da-149d424b2727` |
| A2TTS-Marathi Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `d9eff220-fbf7-433f-bffa-427921ae92fe` |
| A2TTS-Punjabi Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `589dee3c-166a-4762-8cb3-6de1a9e4df29` |
| A2TTS-Tamil Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `43cf4382-3bda-474a-8a3f-d77c1a3414f1` |
| A2TTS-Telugu Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `393dadb3-e1dc-4740-aec0-7171d9241ea7` |
| AI4Bharat - Airavata: Large-Scale Multilingual Model for Indic Languages | MIT | REDIRECT | `8aec27c5-8c21-43c9-b541-a25e95276e0f` |
| AI4Bharat - Fastspeech2 Model using Hybrid Segmentation (HS): Text to Speech Model | MIT | REDIRECT | `7685d825-7944-4b46-adb4-25d103bf5420` |
| AI4Bharat-Indic-Parler-TTS-Pretrained: Text to Speech Model | MIT | REDIRECT | `e2e3f2a1-64f6-4068-a7c1-18958776538c` |
| AI4Bharat-Indic-Parler-TTS: Text to Speech Model | MIT | REDIRECT | `cd234a42-7ab9-44fe-afc3-eb58b675a9e3` |
| AI4Bharat-VITS-Rasa-13: Text to Speech Model | MIT | REDIRECT | `1cf3fe67-1264-4774-849f-3346a9cf1f7b` |
| AIBharat - IndicF5 | MIT | REDIRECT | `0be4d5ff-17cf-40ad-ac3c-43ec0b0a0724` |
| BHASHINI IISC Sourashtra Vits TTS Models | CC-BY-4.0 | REDIRECT | `d2ae7340-fdf5-4ce5-8929-a9f07ef4d568` |
| Bengali vb | MIT | RESTRICTED | `914e62cc-6df8-483c-8567-f19e227bd55d` |
| BharatGen - A2TTS-v0.5 : Speaker Adaptive TTS Model (Hindi) | MIT | HOSTED | `838baccc-0b09-4e31-aa54-6862b973b1fa` |
| Bhashini - Fastspeech2 Model using (HS) | MIT | HOSTED | `7677ccaf-c070-40b1-892d-1b564e2d824d` |
| Hindi vb | MIT | RESTRICTED | `7068707c-b221-4bf0-aa68-cde350905b47` |
| Indic-Speak | Other | HOSTED | `c0e5c4f2-3270-4bf2-94d3-6e5b43f6fe24` |
| Marathi vb | MIT | RESTRICTED | `6595067b-0e33-4f8a-aa8a-dcb948fe9c88` |
| SpeechT5 (voice conversion task) | MIT | REDIRECT | `92ae4761-46cc-4ca8-8809-0da7b412c0d9` |
| SpeechT5 HiFi-GAN Vocoder | MIT | REDIRECT | `0b66a816-150e-4a9c-9573-9f137b5dcc0d` |
| SpeechT5 Text to Speech model | MIT | REDIRECT | `007a38ad-34a7-4c53-a61c-eb9471a2e8f4` |
| SpeechT5: Unified-Modal Encoder-Decoder Pre-Training for Spoken Language Processing | MIT | REDIRECT | `02987fa5-db21-4eb4-88fe-f865d98c1754` |
| Tamil vb | MIT | RESTRICTED | `a9f706cf-9cec-4fef-a5c0-6bbeda1834b3` |
| Telugu vb | MIT | RESTRICTED | `975915bd-406a-4594-848c-ef8daf8151d7` |
| spk cond tts pflow Bengali | MIT | RESTRICTED | `25d79a17-596b-4f1a-ac26-c535d9793a8b` |
| spk cond tts pflow Hindi | MIT | RESTRICTED | `fd0773b1-4e33-4df7-bddf-bc0e32e299f1` |
| spk cond tts pflow Marathi | MIT | RESTRICTED | `2d8c50ea-e562-40df-a548-1db596c287e7` |
| spk cond tts pflow Tamil | MIT | RESTRICTED | `e2890257-8013-4744-9c67-75c718d42b7a` |
| spk cond tts pflow Telugu | MIT | RESTRICTED | `db1fd2b6-b694-4b09-8d16-bb9d382b2ea5` |

### B. Detection-support models (60)
| Model | Licence | Access | id |
|---|---|---|---|
| AI FRAUD DETECTION | Apache 2.0 | REDIRECT | `6445fbae-6b99-4165-a4e8-d1ebfdfbcffc` |
| AI4Bharat - Bengali IndicWav2Vec Speech Model | MIT | REDIRECT | `53693a49-9793-43b0-a5ac-8c1d426e0d9c` |
| AI4Bharat - Gujarati IndicWav2Vec Speech Model | MIT | REDIRECT | `3fae271b-7146-4803-bc42-4eeea8891b1a` |
| AI4Bharat - Hindi IndicWav2Vec Speech Model | MIT | REDIRECT | `490137c0-1bd6-4606-b95b-573c3848c955` |
| AI4Bharat - IndicBART-XXEN: Multilingual to English Text Generation Model | MIT | REDIRECT | `5f48c3e4-6987-4df7-8d64-e148ab435198` |
| AI4Bharat - IndicConformer Automatic Speech Recognition (ASR) Model for Nepali | MIT | REDIRECT | `5efac8bd-8636-4cfb-9862-d1e83f109acc` |
| AI4Bharat - IndicWav2Vec-Hindi: Hindi Speech Recognition Model | MIT | REDIRECT | `7ec092a5-d98f-41b1-bb49-3719e2cc425c` |
| AI4Bharat - IndicWav2Vec-Odia: Odia Speech Recognition Model | MIT | REDIRECT | `6794c718-ba8b-42bf-9e79-3f3e69055844` |
| AI4Bharat - Marathi IndicWav2Vec Speech Model | MIT | REDIRECT | `3643efc0-c6f3-495d-8e38-c3ecfb160020` |
| AI4Bharat - Odia IndicWav2Vec Speech Model | MIT | REDIRECT | `7e88527a-7a50-4b56-a636-64860b008f04` |
| AI4Bharat - Tamil IndicWav2Vec Speech Model | MIT | REDIRECT | `bf88ea99-dd23-4dcb-aad7-983fcc012a23` |
| AI4Bharat - Telugu IndicWav2Vec Speech Model | MIT | REDIRECT | `f475da27-f60e-4db6-81bc-b72af18c9065` |
| AI4Bharat Textual Language Detection | MIT | REDIRECT | `77d4d686-4c3c-47d0-a034-279f17711791` |
| AI4Bharat- Assamese - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `2f76d2e3-2d49-4e24-8aec-e34d512df939` |
| AI4Bharat- Bengali - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `cba49888-e5a4-4e9b-93f8-f86da38ef1c2` |
| AI4Bharat- Bodo - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `77bc7b04-ddce-4324-86b4-034e7cd1e17b` |
| AI4Bharat- Gujarati - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `7992c3e4-02e5-4298-be1d-d2fdff1111ac` |
| AI4Bharat- Hindi - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `2209b8a4-506e-44cf-877d-44017179ef6d` |
| AI4Bharat- IndicConformerAutomatic Speech Recognition (ASR) Model for Dogri | MIT | REDIRECT | `aa178a77-ecbf-48d2-9341-6e9c872aff0b` |
| AI4Bharat- IndicSeamless | CC-BY-NC-4.0 | REDIRECT | `cfa0ca56-f061-49f3-a883-05788d1bc5e8` |
| AI4Bharat- Kannada - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `1a95b822-5fdc-47bf-9821-7837ae5eec11` |
| AI4Bharat- Kashmiri - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `455001ae-677d-4d27-98c7-b90ec4e88fec` |
| AI4Bharat- Konkani - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `775c6bb9-4822-4e1c-903b-5176030cb53a` |
| AI4Bharat- Maithili - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `6d73beb7-0234-471d-a333-ca56a91dddd9` |
| AI4Bharat-IndicConformer-STT-ML-Hybrid-CTC-RNNT-Large (Malayalam): Automatic Speech Recognition Model | MIT | REDIRECT | `1cd438b9-8437-4694-af08-5e09419b2568` |
| AI4Bharat-IndicConformer-STT-MNI-Hybrid-CTC-RNNT-Large (Manipuri): Automatic Speech Recognition Model | MIT | REDIRECT | `f7653b15-9c30-4353-b8f8-1b1d1ce43068` |
| AI4Bharat-IndicConformer-STT-MR-Hybrid-CTC-RNNT-Large (Marathi): Automatic Speech Recognition Model | MIT | REDIRECT | `e9136217-f02e-4da4-8506-3402c0bbf4e3` |
| AI4Bharat-IndicConformer-STT-OR-Hybrid-CTC-RNNT-Large (Oriya): Automatic Speech Recognition Model | MIT | REDIRECT | `e3ca361f-34e6-4414-87b1-174d781f164d` |
| AI4Bharat-IndicConformer-STT-PA-Hybrid-CTC-RNNT-Large (Punjabi): Automatic Speech Recognition Model | MIT | REDIRECT | `28bdddb9-5198-43f5-a96e-2e3885256c92` |
| AI4Bharat-IndicConformer-STT-SA-Hybrid-CTC-RNNT-Large (Sanskrit): Automatic Speech Recognition Model | MIT | REDIRECT | `73b4093e-773c-4643-a86a-a3a34e21b01b` |
| AI4Bharat-IndicConformer-STT-SAT-Hybrid-CTC-RNNT-Large (Santali): Automatic Speech Recognition Model | MIT | REDIRECT | `02a214bf-6de6-41d9-adec-724ed802404c` |
| AI4Bharat-IndicConformer-STT-SD-Hybrid-CTC-RNNT-Large (Sindhi): Automatic Speech Recognition Model | MIT | REDIRECT | `835c7e39-7b07-4244-809e-e0eb1122ad27` |
| AI4Bharat-IndicConformer-STT-TA-Hybrid-CTC-RNNT-Large (Tamil): Autmatic Speech Recognition Model | MIT | REDIRECT | `70835646-5c85-43f7-a0bc-e2dc5b44246a` |
| AI4Bharat-IndicConformer-STT-TE-Hybrid-CTC-RNNT-Large (Telugu): Automatic Speech Recognition Model | MIT | REDIRECT | `8ca45cbc-928e-4ec9-92d9-18eab95dd31c` |
| AI4Bharat-IndicConformer-STT-UR-Hybrid-CTC-RNNT-Large (Urdu): Automatic Speech Recognition Model | MIT | REDIRECT | `56cd30d4-ec42-4cbe-9fbb-173ed4301abe` |
| AIBharat - IndicConformer | MIT | REDIRECT | `82adc49a-e64c-4afe-8c42-da5e8be1993a` |
| AIBharat - IndicConformer-600M-Multi | MIT | REDIRECT | `8c4a77ae-cd9c-4d25-83bf-9a455ce73e98` |
| BharatGen - ASR: Hindi | MIT | RESTRICTED | `f03cc563-4af1-452e-a0e4-8b39fb34277a` |
| Dhwani - Multilingual Speech LLM | Krutrim Community License Agreement Version 1.0 | REDIRECT | `1fa1f0d5-5316-417f-9dca-a78077acb9c8` |
| Indic Trans2 | MIT | HOSTED | `6f174fcc-5470-42ff-aa38-fd0816731110` |
| Indic-Conformer model for ASR | MIT | HOSTED | `95ccc49e-8cb6-46b3-ba44-e8cfc9bd6333` |
| Indic-Transcribe-Core | Other | HOSTED | `0d317d58-00dc-4d6b-9d87-6cd4877d64d8` |
| Indic-Transcribe-Flex | Other | HOSTED | `d4ab7339-a5fd-43d0-8bd8-b37d7d8f3747` |
| Indic-Translate | Other | HOSTED | `b7a77674-9f38-4d4c-8943-ef4497a1b59c` |
| IndicXlit | MIT | HOSTED | `418f9c74-0e4a-4ba4-bb70-10faa1f4408f` |
| Krutrim Translate - Indic Language Translation Model | Krutrim Community License Agreement Version 1.0 | REDIRECT | `441d6913-e1a1-4cfe-9d2f-0aac19bed0e7` |
| Northeast STT Multilingual Speech to Text Model | CC-BY-4.0 | REDIRECT | `d1c60b96-dad9-454e-b25c-3484efebe908` |
| Parrotlet-A-2p5-Pro | Other | REDIRECT | `e4dc82ac-e307-4b1c-839c-951acda621f3` |
| SPRING LAB ASSAMESE-STREAMING | CC-BY-4.0 | HOSTED | `e8656888-4610-4d17-bb8f-a503b77bc3e9` |
| SPRING LAB BENGALI-STREAMING | CC-BY-4.0 | HOSTED | `03ed38b3-bd34-4268-8d78-d851455a6892` |
| SPRING LAB GUJARATI-STREAMING | CC-BY-4.0 | HOSTED | `004fa0f6-970a-459b-a2ea-48ea344e1f9e` |
| SPRING LAB HINDI-STREAMING | CC-BY-4.0 | HOSTED | `ca75d802-04e0-4afa-8c08-9ac59b1e3b71` |
| SPRING LAB KANNADA STREAMING | CC-BY-4.0 | HOSTED | `0026f8b8-b104-468b-90ec-ba7384435c5d` |
| SPRING LAB MARATHI-STREAMING | CC-BY-4.0 | HOSTED | `bcf6905f-c147-4b19-86d7-4b7805827f71` |
| SPRING LAB ODIA-STREAMING | CC-BY-4.0 | HOSTED | `b1fd112e-9443-44da-b062-ad3777feada2` |
| SPRING LAB PUNJABI-STREAMING | CC-BY-4.0 | HOSTED | `d74df3d9-7823-4091-9207-9a25d708d654` |
| SPRING LAB TAMIL-STREAMING | CC-BY-4.0 | HOSTED | `39fb5739-f609-4c34-9a21-53e7b7f12c8d` |
| Shrutam-2 | CC-BY-NC-4.0 | RESTRICTED | `10f8bfa3-5f2a-49de-a69a-d275d33239db` |
| Thore Bhasha-Setu | CC-BY-4.0 | HOSTED | `2f0e2bb4-0564-4409-ace8-de7cf98d2d33` |
| shuka-v1 | CC0-1.0 | REDIRECT | `33e17bd9-01d0-48f0-98d8-f5d5861ad981` |

## Datasets

### C. Attack / deepfake / anti-spoofing (1)
| Dataset | Licence | Access | id |
|---|---|---|---|
| IndicSynth | CC-BY-NC-4.0 | REDIRECT | `02269826-db98-43f2-bb51-c3644ea801ec` |
### D. Telephony / IVR (5)
| Dataset | Licence | Access | id |
|---|---|---|---|
| Gram Vaani Hindi ASR Dataset | CC-BY-NC-4.0 | REDIRECT | `308f00aa-0e2e-4341-967c-40bf60ad63d2` |
| Month-wise Telephone Subscribers Rural vs Urban Wireless vs Wireline April 2014 to March 2023 | GODL license | HOSTED | `4315ec50-a8c1-48d0-9fef-5cf6f6655914` |
| Month-wise Telephones (Public Vs Private) from April 2009 to Feb 2015 | GODL license | HOSTED | `0392aa46-3188-402b-9a6b-7b2beacdbb52` |
| SARTHI AgriData | CC-BY-4.0 | REDIRECT | `f2e739e3-cebe-4021-a05d-26745c38acc8` |
| Service Area-wise Telephone from Mar 2002 to February 15 | GODL license | HOSTED | `ff0499f8-36ac-4cb5-8798-4c3099080fe3` |
### E. TTS / voice corpora (65)
| Dataset | Licence | Access | id |
|---|---|---|---|
| Assamese Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `b35af3d8-0a76-4ff0-8e19-4e26246ec919` |
| Assamese Male Mono (indicTTS phase3) | CC-BY-4.0 | HOSTED | `65633497-2803-4bfb-aa09-2f9be7f5ad69` |
| Bengali ASR Benchmark Dataset (IndicTTS Bengali) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `8bf87591-85e1-4b57-bdf2-03291281db7e` |
| Bengali Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `5fc1c118-3306-46b0-9b71-c698dc895b21` |
| Bengali Male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `eb64d933-a940-487b-8e9b-ae072980580e` |
| Bodo Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `08113a94-44c1-46b3-8cda-471b083e6137` |
| Bodo Male Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `95f7cd1f-87a6-4de1-b931-219e12c9afc8` |
| Dogri Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `fc697e74-00f8-412b-b9a3-db12569f39c4` |
| Dogri Male Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `bce58775-6245-492b-a6aa-0c3304e32061` |
| Gujarati ASR Benchmark Dataset for Diverse Domains (IndicTTS Gujarati) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `ee096546-2dc3-4bca-8849-0258aaed6eb7` |
| Gujarati Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `0df6148f-4cbd-4992-962e-fc65afb3a4e3` |
| Gujarati Male Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `8ffd893e-d269-4de5-b46c-9298edc6b4f4` |
| Hindi ASR Benchmark Dataset for Diverse Domains (IndicTTS Hindi) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `f9415f9c-483e-4632-b0e5-b8139eae383f` |
| Hindi Female Mono (IndicTTS Phase3) | CC-BY-4.0 | HOSTED | `086a5b17-39c0-407d-9def-bcf9a87faf15` |
| IISc SYSPIN_S1.0 Corpus | CC-BY-4.0 | REDIRECT | `a4446683-6d08-42af-966f-e1ecf2ea4825` |
| IndicSynth | CC-BY-NC-4.0 | REDIRECT | `02269826-db98-43f2-bb51-c3644ea801ec` |
| IndicVoices-R | CC-BY-ND-4.0 | REDIRECT | `bb368065-7ea7-422f-a7af-57666717ca44` |
| Kannada ASR Benchmark Dataset (IndicTTS Kannada) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `b8f113e1-880d-4529-9f92-60f9639cfa7a` |
| Kannada Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `0459e517-774b-4a30-81fe-e3cfcefeb145` |
| Kannada Male Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `b24fc273-baea-4e92-aa81-bff3adf78832` |
| Kashmiri TTS Single Speaker Dataset | Attribution 3.0 Unported (CC BY 3.0) | HOSTED | `a940d4fe-0934-4e59-874f-edf5c8a876b1` |
| Konkani Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `244fc9d6-588b-4fe0-a5d7-0ffe7011e173` |
| Konkani Male Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `2da16d38-a452-4897-b306-26ba81b51336` |
| LJSpeech-1 | CC-BY-4.0 | REDIRECT | `14efee51-11a6-4bf3-9197-6469ecb02608` |
| MANGO TTS | CC-BY-4.0 | REDIRECT | `7f5c1b81-5a5f-4c67-a9d3-2cc0b58ef8ac` |
| MIZO Language TTS and ASR segmented | CC-BY-NC-4.0 | RESTRICTED | `5252fe39-915f-4348-bbb1-7d5a0a63e0cd` |
| Maithili Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `8f16af0f-9d3b-4c1f-9fe4-5dda3f55af92` |
| Maithili male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `04f14f98-33b5-4b3c-ad21-b593d2e70417` |
| Malayalam ASR Benchmark Dataset for Diverse Domains (IndicTTS Malayalam) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `8dbb3db5-e05f-48b4-a890-4af25b775700` |
| Malayalam female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `15a0a906-d0fa-4b52-9c8c-05eeabe6aba6` |
| Malayalam male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `c008702f-36c5-4285-859a-c91db9d00aee` |
| Manipuri Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `a6c81d1b-e02a-4d83-8105-397fd5b33d6e` |
| Manipuri male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `cef41a65-82ea-4fac-ab55-96c54d3d9d28` |
| Marathi ASR Benchmark Dataset for Diverse Domains (IndicTTS Marathi) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `c1549d79-2bae-4fa3-af76-1d2d3d9aba8d` |
| Marathi Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `7da27b19-d3d9-45a6-8f5b-ad2b9ab0c0f7` |
| Marathi male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `2dc49b90-d1fe-453d-b858-bcdd04b5c19e` |
| Mizo audio segmented ASR and TTS | CC-BY-NC-4.0 | RESTRICTED | `fa7c661f-3b6a-4962-82ca-510d2a90fd33` |
| Nepali Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `0e2484ab-f62b-4aa0-bf2f-4e390e8f75d4` |
| Nepali male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `718adff4-6506-457e-8d0d-fdf687cba809` |
| Odia (Oriya) Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `ea046f17-4a12-433a-97c8-20a340309dc7` |
| Odia (Oriya) male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `5e66144e-9c10-43d3-aa39-cc834c0189e0` |
| Odia ASR Benchmark Dataset for Diverse Domains (IndicTTS Odia) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `2d250e35-c1d8-4034-8a61-dd4c4e8eb159` |
| Punjabi Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `36d9e328-f9bb-4897-bf2c-465af6a81872` |
| Punjabi male mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `1a546b97-13f0-41fb-9801-c1e35aa78e33` |
| Rajasthani Male mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `5d7cd0bf-48fe-43e9-9a6a-a877865adc65` |
| Rajasthani female mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `b6046517-0f82-4caa-8dd7-77d63a3634ee` |
| RasaTTS | CC-BY-ND-4.0 | REDIRECT | `cf8c6bb6-010b-46bf-9601-43a53bcc0701` |
| SPICOR TTS_1.0 Indian English Corpus | CC-BY-4.0 | REDIRECT | `20ec1d28-a1a5-4442-b0e7-7e1810a438df` |
| SPICOR TTS_2.0 Gujarati Corpus | CC-BY-4.0 | REDIRECT | `5cfebe30-7886-4c76-a637-ec453ccf2861` |
| SPICOR TTS_3.0 Sourashtra Corpus | CC-BY-4.0 | REDIRECT | `92868771-dfc5-48dc-a20b-81dcafb4b0cb` |
| Sanskrit Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `757f9ef9-eb44-4f06-983b-489d0d390d94` |
| Sanskrit Male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `6d17f817-7035-4cb3-936d-1672acad5949` |
| Santali Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `f42e8fa1-62b2-436c-be2b-89516a92c9fa` |
| Santali Male Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `5c6b86ec-457e-48db-a5cf-ae04b976de3e` |
| Sindhi female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `3823c351-c42a-4ea5-97a0-8a54736bf44d` |
| Sindhi male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `a2f98961-f5f5-4878-8b7b-a09ae606070c` |
| Tamil ASR Benchmark Dataset for Diverse Domains (IndicTTS Tamil) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `458bf3d5-96b6-47cf-91f3-2ab4ace5fdaf` |
| Tamil Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `e9c6d414-cfab-42fa-8cc4-fadd9fbca9b4` |
| Tamil Male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `c095b3e9-b3b0-45ba-bcc6-807907eb4c85` |
| Tawng Mizo Speech Dataset | CC-BY-NC-4.0 | RESTRICTED | `b57b0878-3b20-4824-a327-6d6cf639bcd6` |
| Tawng Mizo Speech Dataset 2 | CC-BY-NC-4.0 | RESTRICTED | `0ac02934-54aa-450f-a32f-8d4f1e1fca57` |
| Telugu ASR Benchmark Dataset (Indictts Telugu) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `122a794f-b315-4e96-b0ee-acb5fc14368e` |
| Telugu Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `b2f84d9a-61dd-4e96-bd20-36c1ba0b532e` |
| Telugu Male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `80a75616-9b57-4279-95ec-1c547fcf807f` |
| VCTK Corpus - Accent and Voice Cloning | Other | REDIRECT | `b8fd001a-c12a-4365-b7f9-d1037150803f` |
### F. ASR / speech corpora (base, non-benchmark-slice) (37)
| Dataset | Licence | Access | id |
|---|---|---|---|
| Bengali (Kathbath) Multilingual Speech Recognition Dataset | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `e474a2e1-e394-4aa3-8a68-2f1a96322171` |
| BhasaAnuvaad | CC-BY-4.0 | REDIRECT | `e378c256-9206-4108-ae7d-3e32de02dd1d` |
| Common Voice | CC0-1.0 | REDIRECT | `60bf61e1-84ea-4bd8-8f8f-4a289bb1e403` |
| Dehwali Bhili Conversational Dataset | CC-BY-4.0 | HOSTED | `9bcec89c-9e84-445b-81bf-ed81aaf350ab` |
| Dehwali Bhili Spontaneous Speech Dataset | CC-BY-4.0 | HOSTED | `69d3cd29-186a-4e8c-8a6a-1aebab01e56c` |
| Dehwali Bhili Studio Recording and Transcription Dataset | CC-BY-4.0 | HOSTED | `437eb57a-bab8-473f-b880-9b80bf379ae2` |
| Gram Vaani Hindi ASR Dataset | CC-BY-NC-4.0 | REDIRECT | `308f00aa-0e2e-4341-967c-40bf60ad63d2` |
| IISc IndicDLPRESPIN_S1.0 Corpus | CC-BY-4.0 | REDIRECT | `8b4fe62e-b5b6-4ded-953f-64bee875357d` |
| IndicST - Indian Multilingual Speech Translation Corpus | Krutrim Community License Agreement Version 1.0 | REDIRECT | `e25f556c-cc97-4586-9272-f78d476d699b` |
| IndicVoices | CC-BY-4.0 | REDIRECT | `c112ce47-770c-47f3-80be-09b5afec8bc5` |
| Lahaja | CC-BY-4.0 | REDIRECT | `4bca2bda-4ae7-4533-826b-30af6b8e2607` |
| LibriSpeech | Other | REDIRECT | `eec5ff28-3dd2-4bc2-a491-242c50cc88ca` |
| MIZO Language TTS and ASR segmented | CC-BY-NC-4.0 | RESTRICTED | `5252fe39-915f-4348-bbb1-7d5a0a63e0cd` |
| Mizo audio segmented ASR and TTS | CC-BY-NC-4.0 | RESTRICTED | `fa7c661f-3b6a-4962-82ca-510d2a90fd33` |
| Multidialectal Pradesh Odia Speech Repository MPOSR | Open Government License, India | HOSTED | `aa50055d-01af-4f06-95d3-926bc372860b` |
| Rural_Women_Bhojpuri | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | REDIRECT | `f195d578-acf3-44be-86df-cf625ac29238` |
| SPRING INX BENGALI | CC-BY-4.0 | HOSTED | `e2c487f9-1767-41f5-83bc-8889dd0b2956` |
| SPRING-INX-ASSAMESE | CC-BY-4.0 | HOSTED | `668836c9-6849-4531-8f23-2c0cd3108405` |
| SPRING-INX-GUJARATI | CC-BY-4.0 | HOSTED | `16394adf-ff0a-4a58-9875-e906af45e88a` |
| SPRING-INX-HINDI | CC-BY-4.0 | HOSTED | `92029f1b-67e9-4118-83fb-04c90271611e` |
| SPRING-INX-KANNADA | CC-BY-4.0 | HOSTED | `8c98c1f0-f9c0-4f38-94aa-2e2eabb1aad5` |
| SPRING-INX-MALAYALAM | CC-BY-4.0 | HOSTED | `2b630d5c-e363-4620-a0bd-73fb0b47f4f6` |
| SPRING-INX-MARATHI | CC-BY-4.0 | HOSTED | `26ddef40-9b24-451c-bbfb-5daeb0627ebe` |
| SPRING-INX-ODIA | CC-BY-4.0 | HOSTED | `4156308a-69d3-432c-84ee-967aca1ccc78` |
| SPRING-INX-TAMIL | CC-BY-4.0 | HOSTED | `d1426eea-9d43-455c-8351-5c66bf994f2d` |
| SPRING-LAB-PUNJABI | CC-BY-4.0 | HOSTED | `9d25de25-5b9d-48ef-bf2b-7d52dfde5bff` |
| Shrutilipi | CC-BY-4.0 | REDIRECT | `20d804c8-b8e5-44d8-b34e-7b3a1ec05394` |
| Shrutilipi (AI4Bharat) | CC-BY-4.0 | REDIRECT | `6fd05842-9454-4aed-b283-ff6842dc731f` |
| SpeeD-TB - Kokborok | CC-BY-4.0 | HOSTED | `3f46c900-66e1-4976-af48-2c51aa9721a3` |
| SpeeD-TB - Meitei | CC-BY-4.0 | HOSTED | `c8ceda14-d8d1-4477-9f8f-52297f44e5ac` |
| Speed-IA Speech Datasets and Models for Indo-Aryan languages | Attribution-Non-Commercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) | REDIRECT | `eeb022aa-b8f0-4737-a97e-d063bbc160cd` |
| Svarah | CC-BY-4.0 | REDIRECT | `5d2836b2-1020-4e86-a264-21a834dda906` |
| Tawng Mizo Speech Dataset | CC-BY-NC-4.0 | RESTRICTED | `b57b0878-3b20-4824-a327-6d6cf639bcd6` |
| Tawng Mizo Speech Dataset 2 | CC-BY-NC-4.0 | RESTRICTED | `0ac02934-54aa-450f-a32f-8d4f1e1fca57` |
| Vāksañcayaḥ - Sanskrit_ASR_Corpus | CC0-1.0 | HOSTED | `bc0bd104-f01c-41ea-8147-76adf1db32ba` |
| bhasha-sft_aya_dataset | CC-BY-4.0 | HOSTED | `18c2ecf8-ccc8-456a-8a06-e39369a8498a` |
| eka-medical-asr-evaluation-dataset | MIT | REDIRECT | `e3feb413-0dd4-4b4e-a30f-d4a4ace32b12` |
### G. Conversational / meeting (19)
| Dataset | Licence | Access | id |
|---|---|---|---|
| AMI Meeting Corpus - Dialogue and Multi-Speaker Conversations | Other | REDIRECT | `303b2d54-5656-4ef9-babe-6e152307ab7c` |
| AntEngage Empathy Conversation Dataset | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `17c43348-e87b-47b4-b9f8-3fcf237dc1dd` |
| Chitchat Constitutional AI | CC-BY-4.0 | HOSTED | `4d745dd4-828c-4d0e-b315-57eadf3b0fb9` |
| Chitchat India Style | CC-BY-4.0 | HOSTED | `bac8d11f-f5da-4cf1-9600-7f8f426f4435` |
| Climate Resilient Agriculture - Instruction QA | CC-BY-NC-4.0 | REDIRECT | `02b7c311-f466-42cc-9017-2da79bc34253` |
| Climate Resilient Agriculture - Reasoning | CC-BY-NC-4.0 | REDIRECT | `214420fb-c1ac-486c-8bf5-c96e1d1ad703` |
| Dehwali Bhili Conversational Dataset | CC-BY-4.0 | HOSTED | `9bcec89c-9e84-445b-81bf-ed81aaf350ab` |
| Dehwali Bhili Spontaneous Speech Dataset | CC-BY-4.0 | HOSTED | `69d3cd29-186a-4e8c-8a6a-1aebab01e56c` |
| IEMOCAP - Interactive Emotional Dyadic Motion Capture Database | Other | REDIRECT | `e24acbac-414b-410c-a218-1bdbb15a3837` |
| Kirana Chain | CC-BY-4.0 | REDIRECT | `6c6db8c8-f2c7-4f4b-b622-d4930b00f492` |
| Llama Wildchat Lmsys | CC-BY-4.0 | HOSTED | `224cd126-7feb-42a5-9cdd-630c71975a2a` |
| NagaNLP Conversational Corpus | CC-BY-NC-4.0 | REDIRECT | `602764c1-3df1-4305-946f-d61b8cd11853` |
| OpenAssistant Conversations | Apache 2.0 | REDIRECT | `f03e27c8-2714-4498-a873-059aa5aad35b` |
| OpenSubtitles | Other | REDIRECT | `bb120955-b2f5-40c2-80df-ea645fa06cf2` |
| Reddit Comments Dataset | Other | REDIRECT | `5559dccb-d67a-413f-9c19-7c1f285c91a0` |
| ShareGPT Conversations | Apache 2.0 | REDIRECT | `20af627e-d527-4d0e-af12-2243a4735d0b` |
| TED-LIUM Release 3 - Transcribed TED Talks | CC-BY-4.0 | REDIRECT | `6bd7066f-5a94-45f6-9998-3f331bf58191` |
| UltraChat | MIT | REDIRECT | `c3ce7a15-704e-4f8a-a645-0d0ed2387ee2` |
| VAANI: Multi-modal, Multi-lingual Dataset | CC-BY-4.0 | REDIRECT | `40a87486-9632-4024-a665-c9938b39e355` |
### H. Language-ID / transliteration (5)
| Dataset | Licence | Access | id |
|---|---|---|---|
| Aksharantar | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | REDIRECT | `c448d941-fbba-4607-bd33-ba489bd22bf5` |
| Indo-Aryan Language Identification Shared Task Dataset | Apache 2.0 | REDIRECT | `6ed22d44-f602-4764-9954-2326751dedfb` |
| ModeScript Synthetic Dataset | MIT | REDIRECT | `b2368fa3-1f9e-426e-a687-46e976ef09c6` |
| ModeTrans | MIT | REDIRECT | `3bc4aef3-7306-45ff-aaaf-f96a4892ab18` |
| PahariLI - Pahari Language Identification Corpus | Apache 2.0 | REDIRECT | `253ab174-7911-49fb-bc8e-62fe1e17bb04` |
### I. Toolkit / compute
Shoonya (Indic text+speech annotation → Golden/Worst-Human/Zero-Day) · Label Studio · DataPrep · DataCleaner · AIKosh Jupyter sandbox.

---

## 4 · Governance & security
- **Ingest-only.** Never upload real/consented human audio to AIKosh or any shared host.
- **Licence/consent enforced at ingest** (`security.privacy_check` + `corpus_ingest` + `aikosh_ingest` licence gate). AIKosh access entitlement ≠ permission to train; the dataset licence governs.
- **Non-commercial / no-derivatives hold-list** (kept off the commercial training corpus, research/eval only): **IndicSynth** (CC-BY-NC-4.0) · **Gram Vaani Hindi ASR** (CC-BY-NC-4.0) · **NagaNLP Conversational** (CC-BY-NC-4.0) · **Tawng Mizo / MIZO TTS+ASR** (CC-BY-NC-4.0) · **Speed-IA** (CC-BY-NC-SA) · **IndicVoices-R / RasaTTS** (CC-BY-**ND**-4.0) · **Shrutam-2** (CC-BY-NC) · **"Other"** licences (VCTK, AMI, LibriSpeech, IEMOCAP, Indic-Speak, Indic-Transcribe, Parrotlet).
- **RESTRICTED** assets (A2TTS non-Hindi, spk-cond-tts-pflow, "vb" TTS, BharatGen ASR-Hindi) may refuse download → request entitlement.
- **Signed URLs expire fast** — resolve per-run, never cache.
- **Data residency:** India-hosted govt platform; favourable provenance for a fraud-detection product.
- **Never paste the API key into chat** — set `AIKOSH_API_KEY` in the environment.

---

## 5 · Priority (mapped to roadmap §38)
1. `P1` — Ingest **IndicVoices** (genuine → FP ↓) + **IndicSynth** (attack eval); install **Fastspeech2 / Indic-Parler-TTS / IndicF5 / Sooktam2** + **A2TTS / SpeechT5-VC / spk-cond-tts-pflow** (clone/VC attacks); wire **AI4Bharat Textual LID**.
2. `P2` — **IndicTrans2 + IndicXlit + Aksharantar** (cross-lingual clone text); **IndicConformer / IndicWav2Vec / SPRING-INX** (transcription + SSL); **Shoonya** (annotation); **Gram Vaani** (real telephony genuine).
3. `P3` — Jupyter-sandbox eval; **Vaani / Shrutilipi / Lahaja / Svarah / IISc SYSPIN+IndicDLPRESPIN / Vāksañcayaḥ** for diversity; **RasaTTS / MANGO TTS / SPICOR / IndicTTS Phase-3** corpora for clone sources.

**One-line:** AIKosh gives VoxShield governed, India-hosted access to both the Indic *voices* (genuine + generative — including the exact **IndicSynth** attack dataset and **speaker-adaptive / voice-conversion TTS**) and the *models* (LID / ASR / NMT / transliteration) it needs; ingest genuine data to cut false alarms, install the generators to manufacture the Worst-AI set, and use LID/ASR to power the 23-language scorecard.
