#!/usr/bin/env python3
"""AIKosh HOSTED speech-corpus puller for the DGX. Usage: python dgx_aikosh_pull.py <dest_dir>
Reads AIKOSH_API_KEY from env. Safe to re-run (skips existing)."""
import json, os, re, sys, urllib.request
DEST = sys.argv[1] if len(sys.argv) > 1 else "/raid/srmist2/voxshield/data/aikosh_hosted"
MCP = "https://aikosh.indiaai.gov.in/aikoshmcp/mcp"
KEY = os.environ.get("AIKOSH_API_KEY", "")
ASSETS = [
[
"Month-wise Telephone Subscribers Rural vs Urban Wireless vs Wireline April 2014 to March 2023",
"4315ec50-a8c1-48d0-9fef-5cf6f6655914"
],
[
"SPRING-INX-MARATHI",
"26ddef40-9b24-451c-bbfb-5daeb0627ebe"
],
[
"SPRING-INX-TAMIL",
"d1426eea-9d43-455c-8351-5c66bf994f2d"
],
[
"SPRING-INX-KANNADA",
"8c98c1f0-f9c0-4f38-94aa-2e2eabb1aad5"
],
[
"SPRING-INX-ODIA",
"4156308a-69d3-432c-84ee-967aca1ccc78"
],
[
"Dehwali Bhili Studio Recording and Transcription Dataset",
"437eb57a-bab8-473f-b880-9b80bf379ae2"
],
[
"Marathi male Mono (indicTTS Phase 3)",
"2dc49b90-d1fe-453d-b858-bcdd04b5c19e"
],
[
"Assamese Female Mono (IndicTTS Phase 3)",
"b35af3d8-0a76-4ff0-8e19-4e26246ec919"
],
[
"Odia (Oriya) Female Mono (IndicTTS Phase 3)",
"ea046f17-4a12-433a-97c8-20a340309dc7"
],
[
"Punjabi Female Mono (indicTTS Phase 3)",
"36d9e328-f9bb-4897-bf2c-465af6a81872"
],
[
"Odia (Oriya) male Mono (indicTTS Phase 3)",
"5e66144e-9c10-43d3-aa39-cc834c0189e0"
],
[
"Gujarati Female Mono (IndicTTS Phase 3)",
"0df6148f-4cbd-4992-962e-fc65afb3a4e3"
],
[
"Punjabi male mono (IndicTTS Phase 3)",
"1a546b97-13f0-41fb-9801-c1e35aa78e33"
],
[
"Malayalam female Mono (indicTTS Phase 3)",
"15a0a906-d0fa-4b52-9c8c-05eeabe6aba6"
],
[
"Nepali Female Mono (indicTTS Phase 3)",
"0e2484ab-f62b-4aa0-bf2f-4e390e8f75d4"
],
[
"Kannada Female Mono (IndicTTS Phase 3)",
"0459e517-774b-4a30-81fe-e3cfcefeb145"
],
[
"Bengali Female Mono (indicTTS Phase 3)",
"5fc1c118-3306-46b0-9b71-c698dc895b21"
],
[
"Tamil Male Mono (indicTTS Phase 3)",
"c095b3e9-b3b0-45ba-bcc6-807907eb4c85"
],
[
"Santali Female Mono (IndicTTS Phase 3)",
"f42e8fa1-62b2-436c-be2b-89516a92c9fa"
],
[
"Telugu Female Mono (indicTTS Phase 3)",
"b2f84d9a-61dd-4e96-bd20-36c1ba0b532e"
],
[
"Maithili Female Mono (indicTTS Phase 3)",
"8f16af0f-9d3b-4c1f-9fe4-5dda3f55af92"
],
[
"Santali Male Mono (IndicTTS Phase 3)",
"5c6b86ec-457e-48db-a5cf-ae04b976de3e"
],
[
"Bengali Male Mono (indicTTS Phase 3)",
"eb64d933-a940-487b-8e9b-ae072980580e"
],
[
"Maithili male Mono (indicTTS Phase 3)",
"04f14f98-33b5-4b3c-ad21-b593d2e70417"
],
[
"Konkani Female Mono (IndicTTS Phase 3)",
"244fc9d6-588b-4fe0-a5d7-0ffe7011e173"
],
[
"Marathi Female Mono (indicTTS Phase 3)",
"7da27b19-d3d9-45a6-8f5b-ad2b9ab0c0f7"
],
[
"Kannada Male Mono (IndicTTS Phase 3)",
"b24fc273-baea-4e92-aa81-bff3adf78832"
],
[
"Sanskrit Female Mono (IndicTTS Phase 3)",
"757f9ef9-eb44-4f06-983b-489d0d390d94"
],
[
"SpeeD-TB - Meitei",
"c8ceda14-d8d1-4477-9f8f-52297f44e5ac"
],
[
"Konkani Male Mono (IndicTTS Phase 3)",
"2da16d38-a452-4897-b306-26ba81b51336"
],
[
"SpeeD-TB - Kokborok",
"3f46c900-66e1-4976-af48-2c51aa9721a3"
],
[
"Sindhi female Mono (indicTTS Phase 3)",
"3823c351-c42a-4ea5-97a0-8a54736bf44d"
],
[
"Assamese Male Mono (indicTTS phase3)",
"65633497-2803-4bfb-aa09-2f9be7f5ad69"
],
[
"Bodo Female Mono (IndicTTS Phase 3)",
"08113a94-44c1-46b3-8cda-471b083e6137"
],
[
"Gujarati Male Mono (IndicTTS Phase 3)",
"8ffd893e-d269-4de5-b46c-9298edc6b4f4"
],
[
"Sindhi male Mono (indicTTS Phase 3)",
"a2f98961-f5f5-4878-8b7b-a09ae606070c"
],
[
"Nepali male Mono (indicTTS Phase 3)",
"718adff4-6506-457e-8d0d-fdf687cba809"
],
[
"V\u0101ksa\u00f1caya\u1e25 - Sanskrit_ASR_Corpus",
"bc0bd104-f01c-41ea-8147-76adf1db32ba"
],
[
"Bodo Male Mono (IndicTTS Phase 3)",
"95f7cd1f-87a6-4de1-b931-219e12c9afc8"
],
[
"Manipuri Female Mono (indicTTS Phase 3)",
"a6c81d1b-e02a-4d83-8105-397fd5b33d6e"
],
[
"Dogri Female Mono (IndicTTS Phase 3)",
"fc697e74-00f8-412b-b9a3-db12569f39c4"
],
[
"Hindi Female Mono (IndicTTS Phase3)",
"086a5b17-39c0-407d-9def-bcf9a87faf15"
],
[
"Manipuri male Mono (indicTTS Phase 3)",
"cef41a65-82ea-4fac-ab55-96c54d3d9d28"
],
[
"Dogri Male Mono (IndicTTS Phase 3)",
"bce58775-6245-492b-a6aa-0c3304e32061"
],
[
"Multidialectal Pradesh Odia Speech Repository MPOSR",
"aa50055d-01af-4f06-95d3-926bc372860b"
],
[
"Gujarati ASR Benchmark Dataset for Diverse Domains (IndicTTS Gujarati)",
"ee096546-2dc3-4bca-8849-0258aaed6eb7"
],
[
"Hindi ASR Benchmark Dataset for Diverse Domains (IndicTTS Hindi)",
"f9415f9c-483e-4632-b0e5-b8139eae383f"
],
[
"Telugu ASR Benchmark Dataset (Indictts Telugu)",
"122a794f-b315-4e96-b0ee-acb5fc14368e"
],
[
"Odia ASR Benchmark Dataset for Diverse Domains (IndicTTS Odia)",
"2d250e35-c1d8-4034-8a61-dd4c4e8eb159"
],
[
"Bengali ASR Benchmark Dataset (IndicTTS Bengali)",
"8bf87591-85e1-4b57-bdf2-03291281db7e"
],
[
"Tamil ASR Benchmark Dataset for Diverse Domains (IndicTTS Tamil)",
"458bf3d5-96b6-47cf-91f3-2ab4ace5fdaf"
],
[
"Kannada ASR Benchmark Dataset (IndicTTS Kannada)",
"b8f113e1-880d-4529-9f92-60f9639cfa7a"
],
[
"Marathi ASR Benchmark Dataset for Diverse Domains (IndicTTS Marathi)",
"c1549d79-2bae-4fa3-af76-1d2d3d9aba8d"
],
[
"SPRING-INX-ASSAMESE",
"668836c9-6849-4531-8f23-2c0cd3108405"
],
[
"SPRING-INX-GUJARATI",
"16394adf-ff0a-4a58-9875-e906af45e88a"
],
[
"Dehwali Bhili Conversational Dataset",
"9bcec89c-9e84-445b-81bf-ed81aaf350ab"
],
[
"Dehwali Bhili Spontaneous Speech Dataset",
"69d3cd29-186a-4e8c-8a6a-1aebab01e56c"
],
[
"Kashmiri TTS Single Speaker Dataset",
"a940d4fe-0934-4e59-874f-edf5c8a876b1"
],
[
"Malayalam male Mono (indicTTS Phase 3)",
"c008702f-36c5-4285-859a-c91db9d00aee"
],
[
"Rajasthani Male mono (indicTTS Phase 3)",
"5d7cd0bf-48fe-43e9-9a6a-a877865adc65"
],
[
"Sanskrit Male Mono (indicTTS Phase 3)",
"6d17f817-7035-4cb3-936d-1672acad5949"
],
[
"Telugu Male Mono (indicTTS Phase 3)",
"80a75616-9b57-4279-95ec-1c547fcf807f"
],
[
"Rajasthani female mono (IndicTTS Phase 3)",
"b6046517-0f82-4caa-8dd7-77d63a3634ee"
],
[
"Tamil Female Mono (indicTTS Phase 3)",
"e9c6d414-cfab-42fa-8cc4-fadd9fbca9b4"
],
[
"Malayalam ASR Benchmark Dataset for Diverse Domains (IndicTTS Malayalam)",
"8dbb3db5-e05f-48b4-a890-4af25b775700"
],
[
"SPRING-INX-MALAYALAM",
"2b630d5c-e363-4620-a0bd-73fb0b47f4f6"
],
[
"SPRING-INX-HINDI",
"92029f1b-67e9-4118-83fb-04c90271611e"
],
[
"SPRING LAB BENGALI-STREAMING",
"03ed38b3-bd34-4268-8d78-d851455a6892"
],
[
"SPRING LAB HINDI-STREAMING",
"ca75d802-04e0-4afa-8c08-9ac59b1e3b71"
],
[
"SPRING LAB MARATHI-STREAMING",
"bcf6905f-c147-4b19-86d7-4b7805827f71"
],
[
"SPRING LAB PUNJABI-STREAMING",
"d74df3d9-7823-4091-9207-9a25d708d654"
],
[
"SPRING LAB TAMIL-STREAMING",
"39fb5739-f609-4c34-9a21-53e7b7f12c8d"
],
[
"SPRING LAB KANNADA STREAMING",
"0026f8b8-b104-468b-90ec-ba7384435c5d"
],
[
"SPRING LAB ODIA-STREAMING",
"b1fd112e-9443-44da-b062-ad3777feada2"
],
[
"SPRING LAB GUJARATI-STREAMING",
"004fa0f6-970a-459b-a2ea-48ea344e1f9e"
],
[
"SPRING LAB ASSAMESE-STREAMING",
"e8656888-4610-4d17-bb8f-a503b77bc3e9"
]
]
def safe(n): return re.sub(r"[^A-Za-z0-9._-]+", "_", n)[:80]
def call(name, args):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                       "params": {"name": name, "arguments": args}}).encode()
    req = urllib.request.Request(MCP, data=body, headers={
        "Authorization": "Bearer " + KEY, "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"})
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read().decode()
    for line in raw.splitlines():
        if line.startswith("data: "):
            e = json.loads(line[6:])
            if e.get("id") == 1:
                return e
    return {}
def main():
    if not KEY: print("!! AIKOSH_API_KEY not set"); return
    os.makedirs(DEST, exist_ok=True)
    print(f"{len(ASSETS)} HOSTED assets -> {DEST}")
    for name, aid in ASSETS:
        out = os.path.join(DEST, safe(name) + ".zip")
        if os.path.exists(out): print("skip", name[:50]); continue
        try:
            r = call("get_dataset_download_url_tool", {"dataset_id": aid})
            d = r.get("result", {}).get("content", [{}])[0].get("text", "")
            d = json.loads(d).get("data") if d else None
            url = d if isinstance(d, str) else (d or {}).get("externalUrl")
            if not url or not str(url).startswith("http"): print("no-url", name[:40]); continue
            print("dl", name[:45], flush=True)
            urllib.request.urlretrieve(url, out)
            print(f"   done {os.path.getsize(out)/1e6:.1f} MB", flush=True)
        except Exception as e:
            print("ERR", name[:40], str(e)[:70])
    print("HOSTED DONE")
if __name__ == "__main__": main()
