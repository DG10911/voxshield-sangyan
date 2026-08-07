# MODULE 10 — Deployment, Production and the API

A model on a laptop wins nothing.

A model a bank can actually run, inside its own walls, at the speed of a live call — that is a product.

This module is about the unglamorous, essential half of the work: shipping VoxShield so a real bank can use it.

LEARN:
- Why banks insist the software runs inside their own building
- The real machine VoxShield runs on, and what it costs
- The models loaded, their sizes, and why they run fine on plain CPUs
- How a bank drops VoxShield in with a single web request

## Chapter 10.1 — Why On-Premise Matters

Start with a rule that shapes everything: **banks will not let customer audio leave their data centre.**

A customer's voice is personal data. A recording of them discussing their account is sensitive. Sending that to some outside cloud service is, for many banks, simply not allowed.

> In simple words: the audio must stay inside the bank's own building. It cannot be shipped to someone else's computer.

So VoxShield is built to run **entirely inside the bank's own network**. This is called **on-premise** deployment — "on the premises," on the bank's own machines.

The audio arrives, gets analysed, and the answer comes back, all without a single byte leaving the bank.

### No runtime downloads

There is a trap here. AI models are large files. Normally a program downloads them the first time it runs.

But a bank's secure machine may have no open internet at all. A download would simply fail.

So VoxShield uses **Docker**. Docker is a way of packing a program and *all its parts* into one sealed box that runs the same everywhere.

Crucially, all the AI models are **baked into that box at build time**. When VoxShield starts, everything it needs is already inside. **No runtime downloads.** Nothing to fetch.

> In simple words: VoxShield arrives with all its models already packed in the box, so it never has to phone home.

### Stateless by design

One more design choice makes life easy: VoxShield is **stateless**.

Stateless means each request stands alone. The server does not need to remember your last call to handle your next one. Every request carries everything it needs.

Why does that matter? Because **any server can handle any request.** If one machine is busy, send the call to another — they are interchangeable.

That is what lets a bank grow simply by adding more machines, all doing the same job, side by side.

## Chapter 10.2 — The Real Numbers for Judges

Let us be concrete. VoxShield is not a slide. It is live, right now, on a real machine you can visit.

Here is the honest specification.

| Item | Detail |
| Live URL | https://64.177.121.208.sslip.io |
| Host | Vultr VPS (a rented cloud server) |
| Operating system | Ubuntu |
| Processor | AMD EPYC, 4 vCPU |
| Memory | 7.2 GB RAM + 8 GB swap |
| Cost | about $25 per month |
| RAM in use | about 4–5 GB with all models loaded |
| Model footprint | about 2 GB baked in + 1.2 GB for our Indic model |
| Detection latency | ~1 s on GPU, 3-8 s on CPU (measured) |
| Speaker verification latency | about 1.5 seconds |
| HTTPS + calling | Caddy auto-HTTPS + coturn TURN relay |
| Web server | single-process FastAPI / uvicorn |
| Reliability | systemd auto-restart |

Read that table slowly, because it makes a quiet but strong point.

> In simple words: the whole live system runs on one modest $25-a-month server — no supercomputer, no GPU farm.

A few of those rows deserve a word.

**Caddy** is a small web server that automatically turns on HTTPS — the padlock in your browser — so traffic is encrypted. **coturn** is a TURN relay, a helper that lets two phones connect for a live call even through tricky networks.

**systemd auto-restart** means if the program ever crashes — say it runs out of memory — the machine restarts it on its own. No human needed at 3 a.m.

And **single-process** is an honest limit worth stating: right now VoxShield runs as one process. Handling many banks at true scale — multiple workers behind a load balancer — is on the roadmap, not built today.

### The models, and their sizes

VoxShield is not one model. It is a small team of them. Here is the roster.

- Detection ensemble — about **420 million** parameters in total (the several deepfake detectors working together)
- Our custom **Indic model** — about **300 million** parameters (fine-tuned for Indian languages, trained by the team)
- **ECAPA-TDNN** speaker verification — about **22 million** parameters
- **Whisper** speech-to-text — about **74 million** (base) or **244 million** (small)

> In simple words: several specialist models, each with its own job, all loaded at once inside that 4–5 GB of memory.

### Why plain CPUs are enough

Most AI you read about needs a **GPU** — a special, expensive, power-hungry chip built for AI maths.

VoxShield does not. **Every model runs on ordinary CPUs at inference** — the same kind of processor in a normal server.

Here is the key honest point: a GPU would make it *faster*, but it would **not make it more accurate**. Same answer, same quality, on a plain CPU. That is exactly why a $25 server can host the whole thing.

For a bank, cheaper and simpler hardware, with no loss of accuracy, is a very easy story to say yes to.

## Chapter 10.3 — Using VoxShield as an API

Now the part that makes VoxShield *usable*: the **API**.

An **API** (Application Programming Interface) is simply a way for one program to ask another program a question. The bank's software sends a request; VoxShield sends an answer.

> In simple words: the bank's computer sends VoxShield some audio and gets back a plain answer — no human, no website, just one program asking another.

The whole thing is **one HTTP call**. HTTP is the same language your browser speaks to websites. You send **JSON in** (a simple, structured text format), and you get **JSON out**.

### The key endpoints

An **endpoint** is one specific address you can call, each doing one job. Here are the important ones and what each hands back.

| Endpoint | What it does | What it returns |
| /api/analyze | Analyse a recording for fakery | score, label, reasons, per_model, spectrogram, sha256 |
| /api/verify-speaker | Check identity against an enrolled voice | decision, similarity |
| /api/liveness/new + /api/liveness/verify | Issue and check a random-number challenge | challenge, then pass/fail |
| /api/analyze-call | Digital Arrest Shield scam-intent read | scam stage and warning |
| /api/stream-analyze | Score a live call as it happens | a live timeline of scores |
| /docs | Human-readable list of every endpoint | OpenAPI documentation |

Notice how each answer is rich, not just a yes or no. The `/api/analyze` reply, for example, gives a **score**, a **label**, the human-readable **reasons**, a **per_model** breakdown of what each detector thought, a **spectrogram** picture, and a **sha256** audit hash so the decision can be checked later.

That `/docs` address is worth knowing. It is auto-generated **OpenAPI** documentation — a live, browsable menu of every endpoint. A developer can explore the whole system without reading a manual.

### Dropping it into a bank

So how does a real bank actually use this?

A bank already has systems that touch calls: a **dialer** (which places and receives calls), an **IVR** (the "press 1 for balance" menu), and **core-banking** (the master system holding accounts).

To add VoxShield, the bank's software simply makes one API call at the right moment — when a call comes in, it sends the audio to `/api/analyze` and reads the answer.

> In simple words: the bank does not rebuild anything. It just adds one phone call, from its software to VoxShield, at the moment it matters.

No rip-and-replace. VoxShield slots alongside what the bank already runs.

### Scaling and safety, honestly

Two closing points, told straight.

Because VoxShield is **stateless**, it **scales behind a load balancer**. A load balancer is a traffic officer that spreads incoming calls across many identical VoxShield servers. Need more capacity? Add more servers. Since no server remembers anything, any of them can take any call.

And because VoxShield is **on-premise**, the **audio never leaves** the bank. The two design choices from Chapter 10.1 — stateless and on-premise — are exactly what make this final chapter possible.

One last honesty note, kept from earlier modules: today there is no built-in authentication, no rate-limiting, and no database. Those are real production needs, and they are on the roadmap — not finished yet. We would rather you know that than be surprised by it.

That is Module 10. A working detector became a deployable product: sealed in Docker, running cheaply on plain CPUs inside the bank's own walls, and offered to the bank's existing systems through one simple, well-documented web call.
